from uuid import uuid4
from types import SimpleNamespace
import httpx
import pytest
from fastapi import FastAPI


def app():
    from app.api.eval_runs import router
    value=FastAPI(); value.state.chat_action_allowed_origins=[]
    class Manager:
        async def start(self,**kwargs): return SimpleNamespace(model_dump=lambda **options:{'run_key':kwargs['run_key'],'dataset_size':20,'status':'preparing'})
        async def list_runs(self,**kwargs): return {'items':[],'total':0}
    value.state.eval_pipeline_manager=Manager(); value.include_router(router)
    return value


async def test_eval_post_only_allows_scope_and_canonical_run_key():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app()),base_url='http://127.0.0.1:8006') as client:
        key=str(uuid4())
        good=await client.post('/api/eval-runs',json={'run_key':key,'scope':'smoke_20'})
        evil=await client.post('/api/eval-runs',json={'run_key':key,'scope':'smoke_20','model':'alternate','output':'../../private'})
        origin=await client.post('/api/eval-runs',json={'run_key':key,'scope':'smoke_20'},headers={'origin':'https://evil.invalid'})
    assert good.status_code==202 and good.json()['dataset_size']==20
    assert evil.status_code==422 and origin.status_code==403


async def test_admin_read_is_local_and_disabled_service_is_explicit():
    value=app()
    async with httpx.AsyncClient(transport=httpx.ASGITransport(value),base_url='http://127.0.0.1:8006') as client:
        good=await client.get('/api/eval-runs')
        evil=await client.get('/api/eval-runs',headers={'host':'evil.invalid'})
        value.state.eval_pipeline_manager=None
        disabled=await client.get('/api/eval-runs')
    assert good.status_code==200 and evil.status_code==403 and disabled.status_code==503


def test_eval_cli_dry_run_reads_no_credentials_or_upstream(monkeypatch,capsys):
    from app.eval_pipeline import cli
    monkeypatch.setattr(cli,'load_settings',lambda:pytest.fail('dry-run loaded credentials'))
    cli.main(['run','--scope','smoke_20','--run-key',str(uuid4()),'--acceptance-run','ch09-local-20261019'])
    cli.main(['run','--scope','full_300','--run-key',str(uuid4())])
    output=capsys.readouterr().out
    assert output.count('dry-run')==2 and '20' in output and '300' in output


def test_paid_schedule_is_off_and_cannot_be_enabled_with_acceptance_cap():
    from tests.fakes import fake_settings
    from app.main import create_app
    assert not fake_settings().eval_pipeline_enabled and not fake_settings().eval_schedule_enabled
    settings=fake_settings(eval_pipeline_enabled=True,eval_schedule_enabled=True,rag_evaluation_enabled=False)
    with pytest.raises(ValueError,match='schedule'):
        create_app(settings,acceptance_call_cap=object())
