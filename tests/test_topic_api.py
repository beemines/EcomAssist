"""Loopback read guards and factory isolation protect the existing chat workflow."""
from types import SimpleNamespace
from unittest.mock import AsyncMock
import httpx
import pytest
from fastapi import FastAPI

from app.api.topics import router


def app():
    result=FastAPI()
    result.state.chat_action_allowed_origins=[]
    result.state.topic_service=SimpleNamespace(summary=AsyncMock(return_value={'status':'unconfigured'}),
        questions=AsyncMock(return_value={'total':0,'items':[]}))
    result.include_router(router)
    return result


async def test_local_read_and_invalid_label_paging_date_or_origin():
    application=app()
    async with httpx.AsyncClient(transport=httpx.ASGITransport(application),base_url='http://127.0.0.1:8007') as client:
        assert (await client.get('/api/topics/summary')).status_code==200
        for query in ('label=未知','label=物流&offset=-1','label=物流&limit=101',
                      'label=物流&source=invalid','label=物流&since=2026-10-21T00:00:00'):
            assert (await client.get('/api/topics/questions?'+query)).status_code==422
        assert (await client.get('/api/topics/summary',headers={'Origin':'https://foreign.invalid'})).status_code==403
        assert (await client.post('/api/topics/summary',json={})).status_code==405


async def test_db_failure_has_no_private_detail_or_fake_success():
    application=app()
    application.state.topic_service.summary.side_effect=RuntimeError('private-database-credential')
    async with httpx.AsyncClient(transport=httpx.ASGITransport(application),base_url='http://127.0.0.1:8007') as client:
        response=await client.get('/api/topics/summary')
    assert response.status_code==503 and 'private-database-credential' not in response.text


async def test_topic_demo_does_not_recover_paid_jobs(tmp_path,monkeypatch):
    from app.topics import demo
    from tests.fakes import fake_settings
    captured={}
    monkeypatch.setenv('CH10_ENV_FILE',str(tmp_path/'test.env'))
    monkeypatch.delenv('CH10_TOPIC_PROFILE',raising=False)
    monkeypatch.setattr(demo,'load_settings',lambda **kwargs:fake_settings(
        flywheel_enabled=True,eval_pipeline_enabled=True,eval_schedule_enabled=True,rag_evaluation_enabled=True))
    def factory(settings,**kwargs):
        captured.update(kwargs)
        captured['settings']=settings
        return FastAPI()
    monkeypatch.setattr('app.main.create_app',factory)
    demo.create_app()
    assert captured['background_tasks_enabled'] is False and captured['context_recover_backlog'] is False
    settings=captured['settings']
    assert not settings.eval_pipeline_enabled and not settings.eval_schedule_enabled and not settings.rag_evaluation_enabled
    assert settings.workflow_checkpoint_path.name=='ch10-checkpoints.sqlite'


async def test_factory_background_false_preserves_borrowed_flywheel_and_disables_recovery(tmp_path,monkeypatch):
    from app.main import create_app
    from tests.fakes import fake_settings,FAQStub
    from tests.test_workflow_api import Store
    from tests.workflow_fakes import ScriptedWorkflowModel
    runtime=SimpleNamespace(start=lambda:pytest.fail('background runtime started'),
        close=AsyncMock(side_effect=AssertionError('borrowed runtime closed')))
    application=create_app(fake_settings(flywheel_enabled=True,workflow_checkpoint_path=tmp_path/'check.sqlite'),
        model=ScriptedWorkflowModel(),repository=Store(),faq_repository=FAQStub(),flywheel_runtime=runtime,
        background_tasks_enabled=False)
    async with application.router.lifespan_context(application):
        assert application.state.background_tasks_enabled is False
    assert not runtime.close.called


@pytest.mark.parametrize('action,body', [('approve',{'approved_answer':'人工答案','category':'商品'}),
    ('reject',{'reason':'测试'}),('retry-publication',{})])
async def test_demo_review_is_read_only_even_with_forged_direct_post(action,body):
    from tests.test_review_queue_api import review_app
    application=review_app()
    application.state.background_tasks_enabled=False
    async with httpx.AsyncClient(transport=httpx.ASGITransport(application),base_url='http://127.0.0.1:8007') as client:
        assert (await client.get('/api/review-queue')).status_code==200
        assert (await client.post('/api/review-queue/1/'+action,json=body)).status_code==503
