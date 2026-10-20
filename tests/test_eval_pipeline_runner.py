import asyncio
from uuid import uuid4
import pytest
from tests.eval_pipeline_fakes import dataset_and_rule, MockPipelineResources
from tests.test_eval_pipeline_manager import Repository, drain


async def test_two_complete_smoke_roundtrips_preserve_scopes_denominators_and_cleanup(tmp_path):
    from app.eval_pipeline.manager import EvalPipelineManager
    from app.eval_pipeline.store import PipelineStore
    from app.eval_pipeline.runner import PipelineRunner
    dataset,rule,settings=dataset_and_rule()
    store=PipelineStore(tmp_path)
    repo=Repository()
    manager=EvalPipelineManager(store,repo,settings,rule,dataset=dataset,
        runner=PipelineRunner(settings,store),resources_factory=MockPipelineResources)
    keys=[str(uuid4()),str(uuid4())]
    for key in keys:
        await manager.start(run_key=key,scope='smoke_20',triggered_by='手动')
        async with asyncio.timeout(20):
            while manager.tasks: await asyncio.sleep(.01)
        report=await store.get(key)
        assert report.status=='completed'
        assert report.dataset_size==len(report.records)==20
        assert report.metrics['faithfulness']['valid_n']>0
        assert report.cleanup['ok'] and report.config['provider_scope']=='mock'
        assert len(MockPipelineResources.instances[-1].calls)<=80
    assert set(repo.published)==set(keys)
    await manager.close()
