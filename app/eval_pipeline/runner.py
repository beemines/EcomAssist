"""The Ch04 metric contract, with Ch09's exact prompt evidence selector."""
import hashlib
import asyncio
import json
from datetime import datetime, timezone
from dataclasses import asdict
from uuid import uuid4
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.errors import ServiceError, InputTooLong
from app.core.evidence import prepare_workflow_evidence, EvidencePacket
from app.core.prompts import build_query_messages, build_sufficiency_messages, build_grounded_answer_system_prompt
from app.core.sufficiency import SufficiencyService, QualityDecision
from app.core.answer_validation import REFUSAL_TEXT, FinalAnswerStream, validate_answer, close_answer_stream
from app.context.tokens import estimate_payload
from app.eval_pipeline.types import PipelineCaseResult
from app.flywheel.publication import PublicationWorker
from app.flywheel.processing import PauseWorker
from app.observability.tracing import begin_execution, ExecutionIdentity
from app.quality.evidence_confidence import evaluate_evidence, evidence_budget_fingerprint
from app.rag_evaluation.runner import _seed, _can_degrade_rewrite
from app.rag_evaluation.report import REWRITE_FAILURE_POLICY
from app.rag_evaluation.judgment import GenerationJudge, JudgeError, build_judge_messages
from app.retrieval.service import RetrievalService, faq_payload
from app.retrieval.query import QueryPlanner
from app.retrieval.types import QueryPlan
from app.quality.calibration import build_calibration_split


def select_case_ids(dataset, scope):
    if scope == 'full_300': return tuple(case.eval_id for case in dataset.cases)
    if scope != 'smoke_20': raise ValueError('Unknown evaluation scope')
    split=build_calibration_split(dataset)
    result=[]
    for bucket in sorted({case.bucket for case in dataset.cases}):
        cases=[case for case in dataset.cases if case.bucket==bucket and case.eval_id in split.held_out_ids]
        cases.sort(key=lambda case:(hashlib.sha256((dataset.fingerprint+case.eval_id).encode()).hexdigest(),case.eval_id))
        if len(cases)<4: raise ValueError('Smoke requires four heldout cases per bucket')
        result.extend(case.eval_id for case in cases[:4])
    if len(result)!=20: raise ValueError('Smoke dataset must have exactly five buckets')
    return tuple(result)


def aggregate_metrics(records):
    from app.rag_evaluation.report import summarize_records
    values=[row.record if hasattr(row,'record') else row for row in records]
    summary=summarize_records(values)
    return next(row['metrics'] for row in summary['rows']
        if row['strategy']=='hybrid_rerank' and row['bucket']=='overall')


class PipelineRunner:
    def __init__(self,settings,store,*,observability=None):
        self.settings,self.store,self.observability=settings,store,observability

    @staticmethod
    def _active(cancel_event):
        if cancel_event.is_set() or asyncio.current_task().cancelling(): raise asyncio.CancelledError()

    async def run(self,dataset,*,scope,rule,resources,cancel_event):
        self._active(cancel_event)
        mapping=await resources.prepare(dataset)
        self._active(cancel_event)
        records=[PipelineCaseResult(record=_seed(case,'hybrid_rerank',mapping))
            for case in dataset.cases if case.eval_id in resources.report.case_ids]
        await self.store.update(resources.report.run_key,status='running',records=records,id_map=dict(mapping))
        retrieval=RetrievalService(resources.repository,resources.embedder,resources.index,None,resources.reranker)
        semaphore=asyncio.Semaphore(2)
        async def one(case):
            async with semaphore:
                self._active(cancel_event)
                await self._case(case,mapping,rule,resources,retrieval,cancel_event)
        tasks=[asyncio.create_task(one(case)) for case in dataset.cases if case.eval_id in resources.report.case_ids]
        try:
            await asyncio.gather(*tasks)
        except BaseException:
            cancel_event.set()
            for task in tasks:
                if not task.done(): task.cancel()
            await asyncio.gather(*tasks,return_exceptions=True)
            raise
        result=await self.store.get(resources.report.run_key)
        result.status='completed_with_errors' if any(row.status.endswith('_error') for row in result.records) else 'completed'
        result.finished_at=datetime.now(timezone.utc)
        result.metrics=aggregate_metrics(result.records)
        totals={'actual_tokens':0,'estimated_tokens':0,'actual_calls':0,'estimated_calls':0}
        for row in result.records:
            for phase in row.usage.values():
                for name in totals: totals[name]+=phase.get(name) or 0
        usage={**result.usage,'tokens':totals}
        await self.store.update(result.run_key,usage=usage)
        result.usage=usage
        # The owner publishes the terminal state only after cleanup.
        return result

    async def _case(self,case,mapping,rule,resources,retrieval,cancel_event):
        settings=self.settings
        row=_seed(case,'hybrid_rerank',mapping)
        row['status']='running'
        usage={}; gate=None
        started=asyncio.get_running_loop().time()
        identity=ExecutionIdentity('eval:'+resources.report.run_key,case.eval_id,uuid4().hex,'evaluation')
        async def checkpoint():
            row['elapsed_ms']=(asyncio.get_running_loop().time()-started)*1000
            await self.store.set_case(resources.report.run_key,PipelineCaseResult(
                record=row,evidence_decision=gate,usage=dict(usage)))
        async def invoke(stage,messages,output_tokens,operation):
            self._active(cancel_event)
            safety=max(256,(settings.model_context_window*3+99)//100)
            estimated=estimate_payload(messages)
            if estimated+output_tokens+safety>settings.model_context_window: raise InputTooLong()
            model,collector=resources.phase_model(output_tokens)
            try:
                with resources.requests.stage(stage): return await operation(model)
            finally:
                usage[stage]=collector.summary(estimated_input=estimated,output_tokens=output_tokens)
        with begin_execution(self.observability,identity) as trace:
            try:
                async with asyncio.timeout(settings.chat_timeout_seconds):
                    await checkpoint()
                    try:
                        plan=await invoke('rewrite',build_query_messages(case.query),settings.query_max_output_tokens,
                            lambda model:QueryPlanner(model,settings.model_context_window-settings.query_max_output_tokens-
                                max(256,(settings.model_context_window*3+99)//100),timeout=settings.query_timeout_seconds,
                                output_tokens=settings.query_max_output_tokens).plan(case.query))
                        rewrite={'policy_version':REWRITE_FAILURE_POLICY,'status':'success','error':None}
                    except Exception as exc:
                        if not _can_degrade_rewrite(exc): raise
                        plan=QueryPlan(standard=case.query,expansions=[])
                        rewrite={'policy_version':REWRITE_FAILURE_POLICY,'status':'degraded',
                            'error':{'code':'invalid_structured_output','type':type(exc).__name__,'message':'改写结构无效，使用原话。'}}
                    self._active(cancel_event)
                    row.update(query_plan=plan.model_dump(),rewrite=rewrite,stage='retrieval')
                    await checkpoint()
                    async with asyncio.timeout(settings.faq_timeout_seconds):
                        bundle=await retrieval.retrieve(case.query,category=case.category,strategy='hybrid_rerank',
                            query_plan=plan,top_k=settings.rerank_top_k)
                    self._active(cancel_event)
                    selected=prepare_workflow_evidence([faq_payload(bundle)],top_k=settings.rerank_top_k,
                        token_budget=resources.report.config['evidence_token_budget'])
                    messages=[SystemMessage(build_grounded_answer_system_prompt()),HumanMessage(case.query),
                        HumanMessage(json.dumps({'evidence':selected.payload},ensure_ascii=False,separators=(',',':')))]
                    packet=EvidencePacket(selected.payload,list(selected.citations),messages,selected.best_score,selected.strategy)
                    row.update(candidate_ids=[hit.id for hit in bundle.candidates],final_ids=[item.chunk.id for item in bundle.matches],
                        prompt_citations=[asdict(citation) for citation in packet.citations],stage='self_check')
                    await checkpoint()
                    decision=evaluate_evidence(packet.payload,rule,top_k=settings.rerank_top_k,
                        budget_fingerprint=evidence_budget_fingerprint(top_k=settings.rerank_top_k,
                            token_budget=resources.report.config['evidence_token_budget']))
                    gate=decision.model_dump(mode='json')
                    if not decision.useful:
                        quality=QualityDecision(useful=False,reason=decision.reason,response_kind='knowledge',source='retrieval_low_conf')
                    else:
                        quality=await invoke('self_check',build_sufficiency_messages(case.query,packet.payload),
                            settings.sufficiency_max_output_tokens,lambda model:SufficiencyService(model,
                                input_budget=settings.model_context_window-settings.sufficiency_max_output_tokens,
                                timeout=settings.sufficiency_timeout_seconds,minimum_rerank_score=None,
                                mode='content_ablation').check(case.query,packet,output_tokens=settings.sufficiency_max_output_tokens))
                    self._active(cancel_event)
                    row.update(decision=quality.model_dump(),stage='answer')
                    await checkpoint()
                    if quality.useful:
                        async def generate(model):
                            stream=FinalAnswerStream()
                            upstream=model.astream(messages)
                            try:
                                async for chunk in upstream:
                                    self._active(cancel_event); stream.accept(chunk)
                                answer=stream.complete()
                                validate_answer(answer,stream.reasons,packet,quality)
                                return answer
                            finally: await close_answer_stream(upstream)
                        answer=await invoke('answer',messages,settings.max_output_tokens,generate)
                    else: answer=REFUSAL_TEXT
                    self._active(cancel_event)
                    row.update(answer=answer,refused=not quality.useful,stage='judgment')
                    await checkpoint()
                    judgment=await invoke('judge',build_judge_messages(case.query,answer,packet.citations,case.points),
                        settings.faith_judge_max_output_tokens,lambda model:GenerationJudge(model,
                            settings.faith_judge_input_token_budget,timeout=settings.llm_timeout_seconds).judge(
                            case.query,answer,packet.citations,case.points))
                    self._active(cancel_event)
                    row.update(status='completed',stage='complete',point_verdicts=[asdict(item) for item in judgment.points],
                        claim_verdicts=[asdict(item) for item in judgment.claims],judge_snapshot={
                            'prompt_version':judgment.prompt_version,'finish_reason':judgment.finish_reason,
                            'raw_response':judgment.raw_response})
                    trace.finish('success')
            except asyncio.CancelledError:
                row['status']='cancelled'; trace.finish('cancelled'); raise
            except Exception as exc:
                if cancel_event.is_set():
                    row['status']='cancelled'; trace.finish('cancelled')
                    raise asyncio.CancelledError() from None
                code,_,pause,_=PublicationWorker._error(exc)
                stage=row['stage']
                row.update(status={'rewrite':'rewrite_error','retrieval':'retrieval_error','self_check':'self_check_error',
                    'answer':'answer_error','judgment':'judge_error'}[stage],
                    error={'code':code if pause else stage+'_error','type':type(exc).__name__,'message':'该阶段执行失败'})
                if stage=='rewrite': row['rewrite']={'policy_version':REWRITE_FAILURE_POLICY,'status':'error','error':row['error']}
                if isinstance(exc,JudgeError): row['judge_snapshot']={
                    'prompt_version':exc.prompt_version,'finish_reason':exc.finish_reason,'raw_response':exc.raw_response}
                trace.finish('error')
                if pause:
                    cancel_event.set(); raise PauseWorker(code) from None
            finally:
                await checkpoint()
