import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4
import pytest
from tests.eval_pipeline_fakes import dataset_and_rule, seed_report


class Repository:
    def __init__(self): self.rows = {}; self.published = []; self.fail = False; self.busy = False
    @asynccontextmanager
    async def lease(self):
        if self.busy: yield None; return
        self.busy = True
        try: yield object()
        finally: self.busy = False
    async def get(self, run_key): return self.rows.get(run_key)
    async def reserve(self, report):
        if report.run_key in self.rows: return False
        self.rows[report.run_key] = {'id':'1','metrics':report.metric_payload()}
        return True
    async def publish(self, report):
        if self.fail: raise RuntimeError('storage unavailable')
        self.published.append(report.run_key)
        self.rows[report.run_key] = {'id':'1','metrics':report.metric_payload()}
        return '1'
    async def list(self, **kwargs): return {'items':list(self.rows.values()), 'total':len(self.rows)}
    async def recover_orphans(self,known_keys,**kwargs):
        for key,row in self.rows.items():
            if key not in known_keys and row['metrics']['status'] in ('preparing','running'):
                row['metrics']['status']='interrupted'
                row['metrics']['scores']=None


class Runner:
    def __init__(self, blocker=None): self.calls=0; self.blocker=blocker
    async def run(self, dataset, **kwargs):
        self.calls += 1
        if self.blocker: await self.blocker.wait()
        report = kwargs['resources'].report
        report.status = 'failed'
        report.finished_at = datetime.now(timezone.utc)
        return report


class Resources:
    provider_scope = 'mock'
    def __init__(self, report, **kwargs): self.report=report; self.closed=False
    async def cleanup(self):
        from app.rag_evaluation.contracts import CleanupResult
        self.closed=True
        return CleanupResult(True,(),())


def manager(tmp_path, repository=None, runner=None):
    from app.eval_pipeline.manager import EvalPipelineManager
    from app.eval_pipeline.store import PipelineStore
    dataset, rule, settings = dataset_and_rule()
    return EvalPipelineManager(PipelineStore(tmp_path), repository or Repository(), settings, rule,
        dataset=dataset, runner=runner or Runner(), resources_factory=Resources)


async def drain(value):
    async with asyncio.timeout(3):
        while value.tasks: await asyncio.sleep(.005)


async def test_replaying_run_key_does_not_dispatch(tmp_path):
    run_key = str(uuid4()); runner=Runner(); repo=Repository()
    value = manager(tmp_path, repo, runner)
    await value.start(run_key=run_key, scope='smoke_20', triggered_by='手动')
    await drain(value)
    await value.start(run_key=run_key, scope='smoke_20', triggered_by='手动')
    assert runner.calls == 1 and repo.published == [run_key]
    assert (await value.get_run(run_key)).dataset_size == 20
    await value.close()


async def test_terminal_publish_failure_repairs_without_paid_replay(tmp_path):
    repo=Repository(); repo.fail=True; runner=Runner(); value=manager(tmp_path,repo,runner)
    key = str(uuid4())
    await value.start(run_key=key, scope='smoke_20', triggered_by='手动')
    await drain(value)
    repo.fail=False
    await value.get_run(key)
    assert runner.calls == 1 and repo.published == [key]
    await value.close()


async def test_restart_terminalizes_interrupted_without_replaying_models(tmp_path):
    from app.eval_pipeline.store import PipelineStore
    report=seed_report(str(uuid4()),status='running')
    await PipelineStore(tmp_path).create(report)
    runner=Runner(); value=manager(tmp_path,runner=runner)
    await value.startup()
    assert runner.calls == 0
    assert (await value.get_run(report.run_key)).status == 'interrupted'
    await value.close()


async def test_manual_and_scheduled_trigger_share_database_mutex(tmp_path):
    from app.core.errors import ServiceError
    blocker=asyncio.Event(); repo=Repository(); value=manager(tmp_path,repo,Runner(blocker))
    await value.start(run_key=str(uuid4()),scope='smoke_20',triggered_by='手动')
    with pytest.raises(ServiceError) as error:
        await value.start(run_key=str(uuid4()),scope='full_300',triggered_by='定时')
    assert error.value.status_code == 409
    blocker.set(); await drain(value); await value.close()


async def test_other_manifest_root_cannot_dispatch_same_reserved_key(tmp_path):
    repo=Repository(); blocker=asyncio.Event(); first_runner=Runner(blocker); second_runner=Runner()
    first=manager(tmp_path/'one',repo,first_runner); second=manager(tmp_path/'two',repo,second_runner)
    key=str(uuid4())
    await first.start(run_key=key,scope='smoke_20',triggered_by='手动')
    await second.start(run_key=key,scope='smoke_20',triggered_by='手动')
    assert second_runner.calls==0
    blocker.set(); await drain(first); await first.close(); await second.close()


async def test_scores_are_not_published_or_terminal_before_cleanup(tmp_path):
    from app.eval_pipeline.manager import EvalPipelineManager
    from app.eval_pipeline.store import PipelineStore
    started=asyncio.Event(); release=asyncio.Event(); repo=Repository()
    class Delayed(Resources):
        async def cleanup(self):
            started.set(); await release.wait(); return await super().cleanup()
    dataset,rule,settings=dataset_and_rule(); store=PipelineStore(tmp_path)
    value=EvalPipelineManager(store,repo,settings,rule,dataset=dataset,runner=Runner(),resources_factory=Delayed)
    key=str(uuid4()); await value.start(run_key=key,scope='smoke_20',triggered_by='手动')
    await asyncio.wait_for(started.wait(),2)
    view=await value.get_run(key)
    assert view.status in ('preparing','running') and not repo.published
    release.set(); await drain(value); await value.close()


async def test_orphan_receipt_is_interrupted_without_replaying_or_claiming_scores(tmp_path):
    repo=Repository(); report=seed_report(str(uuid4()),status='preparing')
    await repo.reserve(report)
    runner=Runner(); value=manager(tmp_path,repo,runner)
    await value.startup()
    view=await value.get_run(report.run_key)
    assert view.status=='interrupted' and view.metrics is None and runner.calls==0
    await value.close()


async def test_terminal_manifest_rejects_stale_owner_progress_and_new_model_counts(tmp_path):
    from app.eval_pipeline.store import PipelineStore
    report=seed_report(str(uuid4()),status='interrupted')
    report.cleanup={'ok':True,'errors':[],'unverified':[]}
    store=PipelineStore(tmp_path); await store.create(report)
    with pytest.raises(RuntimeError): await store.set_case(report.run_key,report.records[0])
    with pytest.raises(RuntimeError): await store.update(report.run_key,status='running')
    usage={**report.usage,'physical_calls':{**report.usage['physical_calls'],'answer':1}}
    with pytest.raises(RuntimeError): await store.update(report.run_key,usage=usage)
