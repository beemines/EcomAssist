"""Atomic private manifests plus a run-key receipt and terminal scores in MySQL."""
import asyncio
import copy
import json
import os
from pathlib import Path
from uuid import UUID, uuid4
from weakref import WeakValueDictionary
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.core.errors import ServiceError
from app.flywheel.leases import LeaseLost
from app.eval_pipeline.types import PipelineReport, PipelineCaseResult, TERMINAL, run_key
from app.quality.evidence_confidence import canonical_hash
from app.rag_evaluation.store import canonical_root, guarded_path, _ownership

_LOCKS=WeakValueDictionary()


def checked_report(report):
    value=PipelineReport.model_validate_json(report.model_dump_json())
    if canonical_hash(value.config)!=value.config_fingerprint:
        raise ServiceError('eval_conflict','评估配置指纹不一致。',409)
    if (len(value.case_ids)!=value.dataset_size or len(set(value.case_ids))!=value.dataset_size
            or {row.eval_id for row in value.records}!=set(value.case_ids)
            or len(value.records)!=value.dataset_size):
        raise ValueError('Evaluation planned case identity mismatch')
    if (value.case_ids!=value.config['case_ids'] or value.scope!=value.config['scope']
            or value.dataset_size!=({'smoke_20':20,'full_300':300}[value.scope])):
        raise ValueError('Evaluation frozen scope mismatch')
    _ownership(value.ownership,UUID(value.run_key).hex)
    return value


class PipelineStore:
    def __init__(self, root): self.root=canonical_root(Path(root))
    def _lock(self):
        key=(str(self.root),id(asyncio.get_running_loop()))
        lock=_LOCKS.get(key)
        if lock is None: lock=asyncio.Lock(); _LOCKS[key]=lock
        return lock
    def _path(self, key): return guarded_path(self.root,run_key(key),'report.json')
    def _read(self,key):
        path=self._path(key)
        if not path.exists(): return None
        if path.stat().st_size>64*1024*1024: raise ValueError('Pipeline manifest is oversized')
        value=checked_report(PipelineReport.model_validate_json(path.read_text(encoding='utf-8')))
        if value.run_key!=key: raise ValueError('Pipeline manifest identity mismatch')
        return value
    def _write(self,report):
        report=checked_report(report)
        path=self._path(report.run_key); path.parent.mkdir(parents=True,exist_ok=True)
        temporary=guarded_path(self.root,report.run_key,'report-'+uuid4().hex+'.tmp')
        try:
            with temporary.open('x',encoding='utf-8') as stream:
                stream.write(report.model_dump_json()); stream.flush(); os.fsync(stream.fileno())
            temporary.replace(path)
        finally:
            if temporary.exists(): temporary.unlink()
    async def create(self,report):
        async with self._lock():
            if self._read(report.run_key) is not None: raise ServiceError('eval_conflict','运行已存在。',409)
            self._write(report)
    async def get(self,key):
        async with self._lock(): return self._read(key)
    async def list(self):
        async with self._lock():
            if not self.root.exists(): return []
            values=[]
            for path in self.root.iterdir():
                try: key=run_key(path.name)
                except ValueError: continue
                value=self._read(key)
                if value is not None: values.append(value)
            return values
    async def update(self,key,**patch):
        allowed={'status','records','metrics','usage','ownership','id_map','cleanup','finished_at','published_id','error'}
        if not set(patch)<=allowed: raise ValueError('Unknown pipeline update')
        async with self._lock():
            report=self._read(key)
            if report is None: raise ValueError('Pipeline report missing')
            if report.status in TERMINAL:
                if 'records' in patch or 'metrics' in patch or patch.get('status',report.status)!=report.status:
                    raise LeaseLost('Terminal pipeline rejects stale progress')
                if 'usage' in patch:
                    old_counts=report.usage.get('physical_calls',{})
                    new_counts=patch['usage'].get('physical_calls',{})
                    if any(new_counts.get(name,0)>old_counts.get(name,0) for name in
                            ('rewrite','self_check','answer','judge','embedding','rerank')):
                        raise LeaseLost('Terminal pipeline rejects new paid dispatch')
                if ('cleanup' in patch and report.cleanup is not None and report.cleanup.get('ok') is True
                        and canonical_hash(report.cleanup)!=canonical_hash(patch['cleanup'])):
                    raise LeaseLost('Verified terminal cleanup cannot be replaced')
            if report.ownership is not None and 'ownership' in patch:
                new=patch['ownership']
                if (new is None or not set(report.ownership['owned_ids'])<=set(new['owned_ids'])
                        or any(new['content_hashes'].get(key)!=digest for key,digest in report.ownership['content_hashes'].items())):
                    raise ValueError('Registered ownership cannot be withdrawn or changed')
            if 'usage' in patch:
                old=report.usage.get('physical_calls',{})
                new=patch['usage'].get('physical_calls',{})
                if set(old)!=set(new) or any(type(new[key]) is not int or new[key]<value for key,value in old.items()):
                    raise ValueError('Physical request counters cannot decrease')
            for name,value in patch.items(): setattr(report,name,value)
            self._write(report)
            return report
    async def set_case(self,key,case):
        async with self._lock():
            report=self._read(key)
            if report is None or case.eval_id not in report.case_ids: raise ValueError('Unknown pipeline case')
            if report.status in TERMINAL: raise LeaseLost('Terminal pipeline rejects stale case progress')
            report.records=[case if row.eval_id==case.eval_id else row for row in report.records]
            self._write(report)


class EvalRunRepository:
    def __init__(self,database): self.database=database
    def lease(self):
        from app.flywheel.leases import processing_lease
        return processing_lease(self.database,prefix='ch09-eval:')
    @staticmethod
    def _row(row):
        if row is None: return None
        result=dict(row); result['id']=str(result['id'])
        if isinstance(result['metrics'],str): result['metrics']=json.loads(result['metrics'])
        if result.get('created_at') is not None: result['created_at']=result['created_at'].isoformat()
        return result
    async def get(self,key):
        async with self.database.session() as session:
            row=(await session.execute(text('SELECT * FROM eval_runs WHERE run_key=:key'),
                {'key':run_key(key)})).mappings().one_or_none()
            return self._row(row)
    async def _save(self,session,report,*,final):
        report=checked_report(report)
        if final and report.status not in TERMINAL: raise ValueError('Cannot publish unfinished scores')
        payload=report.metric_payload()
        args={'key':report.run_key,'size':report.dataset_size,'trigger':report.triggered_by,
            'metrics':json.dumps(payload,ensure_ascii=False,sort_keys=True,allow_nan=False)}
        try:
            async with session.begin_nested():
                result=await session.execute(text('INSERT INTO eval_runs(run_key,triggered_by,dataset_size,metrics) '
                    'VALUES(:key,:trigger,:size,:metrics)'),args)
                return str(result.lastrowid),True
        except IntegrityError:
            row=(await session.execute(text('SELECT * FROM eval_runs WHERE run_key=:key FOR UPDATE'),args)).mappings().one_or_none()
            if row is None: raise
            stored=self._row(row)['metrics']
            if (stored.get('config_fingerprint')!=report.config_fingerprint or row['dataset_size']!=report.dataset_size
                    or stored.get('scope')!=report.scope):
                raise ServiceError('eval_conflict','同一运行ID的冻结配置不同。',409) from None
            if final:
                orphan_repair=(stored.get('error') or {}).get('code')=='orphaned_manifest' and report.status=='interrupted'
                if stored.get('status') in TERMINAL and stored!=payload and not orphan_repair:
                    raise ServiceError('eval_conflict','已发布评估不能被不同结果覆盖。',409) from None
                await session.execute(text('UPDATE eval_runs SET metrics=:metrics,created_at=:finished WHERE run_key=:key'),
                    {**args,'finished':report.finished_at.replace(tzinfo=None) if report.finished_at else report.created_at.replace(tzinfo=None)})
            return str(row['id']),False
    async def reserve(self,report,*,lease=None):
        if lease is not None:
            async with lease.transaction() as session: return (await self._save(session,report,final=False))[1]
        async with self.database.session() as session,session.begin():
            return (await self._save(session,report,final=False))[1]
    async def publish(self,report,*,lease=None):
        if lease is not None:
            async with lease.transaction() as session: return (await self._save(session,report,final=True))[0]
        async with self.database.session() as session,session.begin():
            return (await self._save(session,report,final=True))[0]
    async def list(self,*,offset=0,limit=20,scope=None):
        if type(offset) is not int or offset<0 or type(limit) is not int or not 1<=limit<=100:
            raise ValueError('Invalid evaluation pagination')
        if scope not in (None,'smoke_20','full_300'): raise ValueError('Invalid evaluation scope')
        condition=" WHERE JSON_UNQUOTE(JSON_EXTRACT(metrics,'$.scope'))=:scope" if scope else ''
        async with self.database.session() as session:
            args={'offset':offset,'limit':limit,'scope':scope}
            total=await session.scalar(text('SELECT COUNT(*) FROM eval_runs'+condition),args)
            rows=(await session.execute(text('SELECT * FROM eval_runs'+condition+
                ' ORDER BY id DESC LIMIT :limit OFFSET :offset'),args)).mappings().all()
            return {'items':[self._row(row) for row in rows],'total':int(total)}

    async def recover_orphans(self,known_keys,*,lease):
        """Global DB ownership proves no live pipeline; unknown manifests never replay."""
        from datetime import datetime,timezone
        async with lease.transaction() as session:
            rows=(await session.execute(text("SELECT * FROM eval_runs WHERE run_key IS NOT NULL "
                "AND JSON_UNQUOTE(JSON_EXTRACT(metrics,'$.config.pipeline_version'))='ch09-single-strategy-v1' "
                "AND JSON_UNQUOTE(JSON_EXTRACT(metrics,'$.status')) IN ('preparing','running') FOR UPDATE"))).mappings().all()
            for row in rows:
                if row['run_key'] in known_keys: continue
                data=self._row(row)['metrics']
                data.update(status='interrupted',scores=None,finished_at=datetime.now(timezone.utc).isoformat(),
                    usage={'physical_calls':None,'reason':'manifest_unavailable'},
                    error={'code':'orphaned_manifest','stage':'recovery','message':'原运行清单不可用；未重放收费步骤，资源归属待人工核对。'})
                await session.execute(text('UPDATE eval_runs SET metrics=:metrics WHERE id=:id'),
                    {'id':row['id'],'metrics':json.dumps(data,ensure_ascii=False,allow_nan=False)})
