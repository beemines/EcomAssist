import httpx
import pytest
from pathlib import Path
from app.flywheel.acceptance import acceptance_cap,RUN_ID


def test_restart_keeps_used_allowance(tmp_path):
    first=acceptance_cap(RUN_ID,root=tmp_path)
    for provider in ('glm','embedding','rerank'): first.reserve(provider)
    second=acceptance_cap(RUN_ID,root=tmp_path)
    assert second.status()['counts']=={'glm':1,'embedding':1,'rerank':1}
    assert second.limits=={'glm':280,'embedding':450,'rerank':450}
    with pytest.raises(ValueError): acceptance_cap('another-run',root=tmp_path)


@pytest.mark.parametrize('enabled',[False,True])
async def test_ordinary_mode_has_no_acceptance_cap(monkeypatch,tmp_path,enabled):
    from app.observability import demo
    from app.main import create_app
    from tests.fakes import fake_settings
    captured={}
    monkeypatch.setattr(demo,'ROOT',tmp_path)
    monkeypatch.setattr(demo,'load_ch09_settings',lambda root:fake_settings(rag_evaluation_enabled=False))
    monkeypatch.setattr(demo,'rule_for_settings',lambda settings:object())
    def factory(settings,**kwargs):
        from fastapi import FastAPI
        captured.update(kwargs); app=FastAPI()
        @app.get('/health')
        async def health():
            cap=kwargs['acceptance_call_cap']
            return {'status':'ok',**({'acceptance':cap.status()} if cap else {})}
        return app
    monkeypatch.setattr('app.main.create_app',factory)
    if enabled: monkeypatch.setenv('CH09_ACCEPTANCE',RUN_ID)
    else: monkeypatch.delenv('CH09_ACCEPTANCE',raising=False)
    app=demo.create_observability_app()
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app),base_url='http://127.0.0.1:8006') as client:
        response=(await client.get('/health')).json()
    assert ('acceptance' in response)==enabled
    assert captured['context_recover_backlog'] is False


def test_ordinary_mode_requires_acceptance_jobs_to_be_closed(monkeypatch,tmp_path):
    from app.observability import demo
    monkeypatch.setattr(demo,'ROOT',tmp_path)
    monkeypatch.delenv('CH09_ACCEPTANCE',raising=False)
    path=tmp_path/'runtime/ch09-evidence/acceptance-owned-jobs.json'
    path.parent.mkdir(parents=True); path.write_text('{"closed":false}',encoding='utf-8')
    with pytest.raises(ValueError,match='unfinished'): demo.create_observability_app()


def test_settings_load_local_sdk_without_changing_chat_budgets(tmp_path,monkeypatch):
    from app.observability.demo import load_ch09_settings
    monkeypatch.delenv('CH09_SETTINGS_FILE',raising=False)
    (tmp_path/'.env').write_text('LLM_MODEL=unit-test\nLLM_API_KEY=unit-only\nLLM_BASE_URL=https://upstream.invalid/v1/\nMODEL_CONTEXT_WINDOW=18000\nMAX_OUTPUT_TOKENS=2000\n',encoding='utf-8')
    path=tmp_path/'runtime/langfuse/sdk.env';path.parent.mkdir(parents=True)
    path.write_text('LANGFUSE_ENABLED=true\nLANGFUSE_BASE_URL=http://127.0.0.1:3000\nLANGFUSE_PUBLIC_KEY=pk-unit\nLANGFUSE_SECRET_KEY=sk-unit\n',encoding='utf-8')
    settings=load_ch09_settings(tmp_path)
    assert settings.langfuse_base_url=='http://127.0.0.1:3000'
    assert settings.langfuse_secret_key.get_secret_value()=='sk-unit'
    assert settings.model_context_window==18000 and settings.max_output_tokens==2000
    assert settings.flywheel_enabled and settings.eval_pipeline_enabled
    assert not settings.eval_schedule_enabled and not settings.rag_evaluation_enabled
    assert settings.workflow_checkpoint_path==tmp_path/'runtime/workflow/observability-8006.sqlite'
