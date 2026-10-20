"""One durable run owner: no network retry or paid replay during recovery."""
import asyncio
import logging
from contextvars import Context
from datetime import datetime, timezone
from dataclasses import asdict
from pathlib import Path
from app.core.errors import ServiceError
from app.eval_pipeline.types import TERMINAL, new_report, report_view, stored_view, run_key
from app.flywheel.types import TaskError

logger=logging.getLogger(__name__)


class EvalPipelineManager:
    def __init__(self,store,repository,settings,rule,*,dataset=None,runner=None,resources_factory=None,
                 acceptance_call_cap=None,observability=None):
        from app.rag_evaluation.dataset import load_dataset, DATASET_ID
        self.dataset=dataset or load_dataset(DATASET_ID,root=Path(__file__).parents[2]/'evals/datasets')
        self.store,self.repository,self.settings,self.rule=store,repository,settings,rule
        self.runner,self.resources_factory=runner,resources_factory
        self.cap,self.observability=acceptance_call_cap,observability
        self.tasks=set(); self._guard=asyncio.Lock(); self._closing=False
        self._cancel=asyncio.Event()

    def _factory(self):
        if self.resources_factory is not None: return self.resources_factory
        from app.eval_pipeline.resources import PipelineResources
        return PipelineResources

    def _resources(self,report,lease):
        return self._factory()(report,settings=self.settings,store=self.store,lease=lease,
            acceptance_call_cap=self.cap,observability=self.observability,cancel_event=self._cancel)

    async def _publish(self,report,lease=None):
        options={'lease':lease} if hasattr(lease,'transaction') else {}
        identifier=await self.repository.publish(report,**options)
        await self.store.update(report.run_key,published_id=identifier)
        return identifier

    async def start(self,*,run_key: str,scope,triggered_by):
        from app.eval_pipeline.types import run_key as validate_key
        key=validate_key(run_key)
        async with self._guard:
            if self._closing: raise ServiceError('service_unavailable','评估服务正在关闭。',503)
            previous=await self.store.get(key)
            stored=await self.repository.get(key)
            if previous is not None:
                if previous.scope!=scope: raise ServiceError('eval_conflict','运行范围已冻结。',409)
                return await self.get_run(key)
            if stored is not None:
                if stored['metrics'].get('scope')!=scope: raise ServiceError('eval_conflict','运行范围已冻结。',409)
                return stored_view(stored)
            if self.tasks: raise ServiceError('eval_busy','已有评估正在运行。',409)
            factory=self._factory()
            report=new_report(key,scope,triggered_by,self.dataset,self.settings,self.rule,
                provider_scope=getattr(factory,'provider_scope','actual'))
            if report.config['provider_scope']=='actual' and self.rule.source.source_kind!='actual':
                raise ValueError('Actual pipeline requires an actual calibration artifact')
            cm=self.repository.lease(); lease=await cm.__aenter__()
            if lease is None:
                await cm.__aexit__(None,None,None)
                raise ServiceError('eval_busy','已有评估持有数据库锁。',409)
            owned=False
            try:
                stored=await self.repository.get(key)
                if stored is not None: return stored_view(stored)
                options={'lease':lease} if hasattr(lease,'transaction') else {}
                if not await self.repository.reserve(report,**options):
                    return stored_view(await self.repository.get(key))
                await self.store.create(report)
                self._cancel=asyncio.Event()
                task=asyncio.create_task(self._execute(report,cm,lease),name='ch09-eval-'+key,context=Context())
                self.tasks.add(task); task.add_done_callback(self._observe)
                owned=True
                return report_view(report)
            finally:
                if not owned: await cm.__aexit__(None,None,None)

    def _observe(self,task):
        self.tasks.discard(task)
        if not task.cancelled() and task.exception() is not None:
            logger.warning('eval_pipeline status=owner_error type=%s',type(task.exception()).__name__)

    async def _execute(self,report,cm,lease):
        resources=None
        terminal={}
        try:
            resources=self._resources(report,lease)
            runner=self.runner
            if runner is None:
                from app.eval_pipeline.runner import PipelineRunner
                runner=PipelineRunner(self.settings,self.store,observability=self.observability)
            result=await runner.run(self.dataset,scope=report.scope,rule=self.rule,resources=resources,cancel_event=self._cancel)
            terminal=dict(status=result.status,records=result.records,
                metrics=result.metrics,finished_at=result.finished_at,error=result.error)
        except asyncio.CancelledError:
            terminal=dict(status='cancelled',finished_at=datetime.now(timezone.utc),
                error=TaskError(code='cancelled',stage='execution',message='本轮评估已取消，未执行题目不补跑。'))
        except Exception as exc:
            terminal=dict(status='failed',finished_at=datetime.now(timezone.utc),
                error=TaskError(code='evaluation_failed',stage='execution',message='评估中断，阶段产物已保留。'))
            logger.warning('eval_pipeline status=failed type=%s',type(exc).__name__)
        finally:
            try:
                cleanup_data={'ok':True,'errors':[],'unverified':[]}
                if resources is not None:
                    cleanup=await resources.cleanup()
                    cleanup_data=asdict(cleanup)
                    if not cleanup.ok:
                        terminal.update(status='failed',
                            error=TaskError(code='cleanup_unverified',stage='cleanup',message='自有资源清理未核验，未重放模型。'))
                report=await self.store.update(report.run_key,cleanup=cleanup_data,**terminal)
                try: await self._publish(report,lease)
                except Exception as exc: logger.warning('eval_pipeline publish=pending type=%s',type(exc).__name__)
            finally:
                await cm.__aexit__(None,None,None)

    async def startup(self):
        async with self._guard:
            if self.tasks: return
            async with self.repository.lease() as lease:
                if lease is None: return
                reports=await self.store.list()
                for report in reports:
                    if report.status not in TERMINAL:
                        resources=self._resources(report,lease)
                        cleanup=await resources.cleanup()
                        report=await self.store.update(report.run_key,status='interrupted',cleanup=asdict(cleanup),
                            finished_at=datetime.now(timezone.utc),error=TaskError(code='interrupted',stage='recovery',
                                message='上次进程中断，仅恢复资源和结果，不重放收费阶段。'))
                    if report.published_id is None:
                        try: await self._publish(report,lease)
                        except Exception as exc: logger.warning('eval_pipeline recovery=publish_pending type=%s',type(exc).__name__)
                options={'lease':lease} if hasattr(lease,'transaction') else {}
                await self.repository.recover_orphans({report.run_key for report in reports},**options)

    async def get_run(self,key):
        key=run_key(key)
        report=await self.store.get(key)
        if report is None:
            row=await self.repository.get(key)
            if row is None: raise ServiceError('eval_not_found','评估不存在。',404)
            return stored_view(row)
        if report.status in TERMINAL and report.cleanup is not None and report.published_id is None:
            try:
                await self._publish(report)
                report=await self.store.get(key)
            except Exception as exc: logger.warning('eval_pipeline read_repair=pending type=%s',type(exc).__name__)
        return report_view(report)

    async def list_runs(self,**kwargs): return await self.repository.list(**kwargs)

    async def get_report(self,key):
        import copy
        report=await self.store.get(run_key(key))
        if report is None: raise ServiceError('eval_not_found','本地逐题报告不可用。',404)
        result=report.metric_payload()
        result['records']=[]
        for value in report.records:
            row=copy.deepcopy(value.model_dump(mode='json'))
            snapshot=row['record'].get('judge_snapshot')
            if snapshot is not None: snapshot.pop('raw_response',None)
            result['records'].append(row)
        return result

    async def close(self,timeout_seconds=30):
        self._closing=True; self._cancel.set()
        tasks=set(self.tasks)
        if not tasks: return
        _,pending=await asyncio.wait(tasks,timeout=timeout_seconds)
        for task in pending: task.cancel()
        if pending:
            _,remaining=await asyncio.wait(pending,timeout=5)
            if remaining: raise RuntimeError('Evaluation tasks remain owned during shutdown')
        await asyncio.gather(*tasks,return_exceptions=True)
