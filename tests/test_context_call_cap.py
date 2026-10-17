"""Physical HTTP attempts, including summaries, share a durable run allowance."""
import asyncio
import importlib
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest


def api():
    try:
        return importlib.import_module('app.context.acceptance')
    except ImportError:
        pytest.fail('AcceptanceCallCap and profile factory are missing')


async def test_chat_and_two_summaries_compete_for_last_physical_dispatch(tmp_path):
    module = api()
    cap = module.AcceptanceCallCap('race', {'glm': 1, 'embedding': 0, 'rerank': 0}, tmp_path/'cap.sqlite')
    dispatched = []
    async def send(request):
        dispatched.append(request)
        return httpx.Response(503, json={'error': 'controlled failure'})
    async with httpx.AsyncClient(transport=httpx.MockTransport(send),
            event_hooks={'request': [cap.async_hook('glm')]}) as client:
        outcomes = await asyncio.gather(*(client.post('https://controlled.invalid/'+phase)
            for phase in ('chat', 'summary-a', 'summary-b')), return_exceptions=True)
    assert len(dispatched) == 1
    assert sum(isinstance(item, module.AcceptanceLimitExceeded) for item in outcomes) == 2
    assert cap.status()['counts']['glm'] == 1
    restarted = module.AcceptanceCallCap('race', cap.limits, tmp_path/'cap.sqlite')
    with pytest.raises(module.AcceptanceLimitExceeded):
        restarted.reserve('glm')
    with pytest.raises(ValueError, match='limits'):
        module.AcceptanceCallCap('race', {'glm': 2, 'embedding': 0, 'rerank': 0}, tmp_path/'cap.sqlite')


def test_atomic_across_independent_instances_and_sync_hooks(tmp_path):
    module = api()
    caps = [module.AcceptanceCallCap('shared', {'glm': 5, 'embedding': 0, 'rerank': 0}, tmp_path/'cap.sqlite') for _ in range(12)]
    def reserve(cap):
        try:
            cap.reserve('glm')
            return True
        except module.AcceptanceLimitExceeded:
            return False
    with ThreadPoolExecutor(max_workers=12) as pool:
        assert sum(pool.map(reserve, caps)) == 5
    assert caps[0].status()['counts']['glm'] == 5
    with httpx.Client(transport=httpx.MockTransport(lambda request: pytest.fail('uncounted dispatch')),
            event_hooks={'request': [caps[0].sync_hook('glm')]}) as client:
        with pytest.raises(module.AcceptanceLimitExceeded):
            client.get('https://controlled.invalid')


def test_profiles_ignore_conflicting_legacy_alias_and_fee_without_mutating_environment(monkeypatch):
    module = api()
    monkeypatch.setenv('AGENT_MAX_TOOL_CALLS', '4')
    monkeypatch.setenv('AGENT_TOTAL_TOKEN_BUDGET', '32000')
    settings = module.profile_settings('demo', offline=True)
    assert settings.max_agent_steps == settings.agent_max_tool_calls == 3
    assert not settings.agent_total_token_budget_explicit
    assert module.profile_budget('demo')['budget']['history'] == 2770
    import os
    assert os.environ['AGENT_TOTAL_TOKEN_BUDGET'] == '32000'


async def test_real_glm_summary_and_bge_clients_are_capped_before_transport(tmp_path):
    module = api()
    from app.core.llm import create_model
    from app.context.summarizer import SummaryGenerator
    from app.context.types import SummaryBatch, FrozenMessage
    from app.knowledge.embeddings import SiliconFlowEmbedder
    from app.retrieval.rerank import SiliconFlowReranker
    settings = module.profile_settings('demo', offline=True).model_copy(update={'siliconflow_api_key': __import__('pydantic').SecretStr('controlled')})
    cap = module.AcceptanceCallCap('clients', {'glm': 1, 'embedding': 1, 'rerank': 1}, tmp_path/'cap.sqlite')
    sent = []
    async def dispatch(request):
        sent.append(request.url.path)
        return httpx.Response(503, json={'error': {'message': 'controlled failure'}})
    async with httpx.AsyncClient(transport=httpx.MockTransport(dispatch), event_hooks={'request': [cap.async_hook('glm')]}) as glm:
        with httpx.Client(transport=httpx.MockTransport(lambda r: pytest.fail('sync fallback')),
                         event_hooks={'request': [cap.sync_hook('glm')]}) as sync:
            model = create_model(settings, http_async_client=glm, http_client=sync)
            generator = SummaryGenerator(model, settings)
            batch = SummaryBatch('1', None, 0, 1, 2,
                (FrozenMessage('1','user','我还没找到包裹',None,None), FrozenMessage('2','assistant','尚待核实',None,None)), 'hash')
            outcomes = await asyncio.gather(model.ainvoke('controlled chat'), generator.summarize(batch),
                                            generator.summarize(batch), return_exceptions=True)
            assert all(isinstance(value, Exception) for value in outcomes)
            assert len(sent) == 1
            assert model.http_async_client is glm and model.http_client is sync
    for provider, cls in [('embedding', SiliconFlowEmbedder), ('rerank', SiliconFlowReranker)]:
        async with httpx.AsyncClient(transport=httpx.MockTransport(dispatch), event_hooks={'request': [cap.async_hook(provider)]}) as client:
            adapter = cls(settings, http_client=client)
            call = (lambda: adapter.embed(['controlled'])) if provider == 'embedding' else (lambda: adapter.rank('controlled', ['document']))
            with pytest.raises(httpx.HTTPStatusError):
                await call()
            with pytest.raises(module.AcceptanceLimitExceeded):
                await call()
            await adapter.aclose()
            assert not client.is_closed
    assert len(sent) == sum(cap.status()['counts'].values()) == 3


async def test_application_owned_clients_share_one_cap_and_close_on_shutdown(tmp_path, monkeypatch):
    """Removing any main.py client injection permits an uncapped physical attempt."""
    import app.main as main
    from types import SimpleNamespace
    from tests.test_workflow_api import Store
    from app.core.llm import create_model as actual_model
    from app.knowledge.embeddings import SiliconFlowEmbedder as ActualEmbedder
    from app.retrieval.rerank import SiliconFlowReranker as ActualReranker
    from app.context.summarizer import SummaryGenerator
    from app.context.types import SummaryBatch, FrozenMessage
    from pydantic import SecretStr
    module = api()
    cap = module.AcceptanceCallCap('server', dict(glm=0,embedding=0,rerank=0), tmp_path/'ledger.sqlite')
    config = module.profile_settings('demo', offline=True, workflow_checkpoint_path=tmp_path/'root.sqlite')
    config = config.model_copy(update={'siliconflow_api_key': SecretStr('controlled')})
    captured = {}
    def model_factory(settings, **kwargs):
        assert set(kwargs) == {'http_client','http_async_client'}
        captured['model'] = actual_model(settings, **kwargs)
        captured.update(kwargs)
        return captured['model']
    def embedding(settings, **kwargs):
        captured['embedding'] = ActualEmbedder(settings, **kwargs)
        return captured['embedding']
    def rerank(settings, **kwargs):
        captured['rerank'] = ActualReranker(settings, **kwargs)
        return captured['rerank']
    class Index:
        def __init__(self, *args, **kwargs): pass
        async def ensure_collection(self, **kwargs): pass
        async def aclose(self): pass
    monkeypatch.setattr(main, 'create_model', model_factory)
    monkeypatch.setattr(main, 'SiliconFlowEmbedder', embedding)
    monkeypatch.setattr(main, 'SiliconFlowReranker', rerank)
    monkeypatch.setattr(main, 'HybridMilvusIndex', Index)
    monkeypatch.setattr(main, 'FAQRepository', lambda *args, **kwargs: SimpleNamespace())
    # No transport may execute: zero cap must reject every server-owned path.
    async def forbidden(*args, **kwargs): pytest.fail('uncapped async physical dispatch')
    def sync_forbidden(*args, **kwargs): pytest.fail('uncapped sync physical dispatch')
    monkeypatch.setattr(httpx.AsyncClient, '_send_single_request', forbidden)
    monkeypatch.setattr(httpx.Client, '_send_single_request', sync_forbidden)
    app = main.create_app(config, repository=Store(), acceptance_call_cap=cap, acceptance_profile='demo')
    async with app.router.lifespan_context(app):
        batch = SummaryBatch('1',None,0,1,2,(FrozenMessage('1','user','请查包裹',None,None),FrozenMessage('2','assistant','尚待核实',None,None)), 'hash')
        results = await asyncio.gather(captured['model'].ainvoke('chat'),
            SummaryGenerator(captured['model'], config).summarize(batch),
            captured['embedding'].embed(['text']), captured['rerank'].rank('query',['doc']), return_exceptions=True)
        assert all(isinstance(item, Exception) for item in results)
        with pytest.raises(Exception): captured['model'].invoke('sync')
        assert cap.status()['counts'] == {'glm':0,'embedding':0,'rerank':0}
        assert not captured['http_async_client'].is_closed
    assert captured['http_async_client'].is_closed and captured['http_client'].is_closed
    assert captured['embedding']._client.is_closed and captured['rerank']._client.is_closed


def test_ledger_reopened_in_fresh_process_keeps_exhausted_count(tmp_path):
    import subprocess
    import sys
    module = api()
    path = tmp_path/'restart.sqlite'
    cap = module.AcceptanceCallCap('restart', dict(glm=1,embedding=0,rerank=0), path)
    cap.reserve('glm')
    code = "from pathlib import Path; import sys; from app.context.acceptance import AcceptanceCallCap; AcceptanceCallCap('restart', dict(glm=1,embedding=0,rerank=0), Path(sys.argv[1])).reserve('glm')"
    result = subprocess.run([sys.executable,'-c',code,str(path)], capture_output=True, text=True)
    assert result.returncode != 0 and 'AcceptanceLimitExceeded' in result.stderr
    assert cap.status()['counts']['glm'] == 1
