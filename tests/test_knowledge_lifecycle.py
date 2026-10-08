import httpx
import pytest
from langchain_core.messages import AIMessage

import app.main as main
from tests.fakes import ConversationStore, FAQStub, StreamingModel, decode_sse, fake_settings


def injected_app(**kwargs):
    import inspect
    assert 'faq_repository' in inspect.signature(main.create_app).parameters, 'FAQ injection missing'
    return main.create_app(fake_settings(), **kwargs)


async def test_injected_faq_avoids_retrieval_clients_and_remains_caller_owned(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('created an external client for an injected FAQ')
    monkeypatch.setattr(main, 'SiliconFlowEmbedder', forbidden, raising=False)
    monkeypatch.setattr(main, 'MilvusIndex', forbidden, raising=False)
    class FAQ(FAQStub):
        async def aclose(self): forbidden()
    row = {'id': 7, 'question': '运费规则', 'answer': '八元', 'category': '配送'}
    model = StreamingModel()
    model.selected = AIMessage('', tool_calls=[{'name': 'query_faq', 'args': {'keyword': '邮费'}, 'id': 'faq'}],
        response_metadata={'finish_reason': 'tool_calls'})
    faq = FAQ([row])
    app = injected_app(model=model, repository=ConversationStore(), faq_repository=faq)
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://test') as client:
            assert (await client.get('/health')).json() == {'status': 'ok'}
            response = await client.post('/api/chat', json={'conversation_id': '1', 'message': '邮费是多少'})
    assert any(data.get('status') == 'success' for _, data in decode_sse(response.text))
    assert faq.keywords == ['邮费']
    assert '八元' in model.calls[0][-1].content


def owned_resources(monkeypatch, failure=None):
    closed, created = [], []
    class Database:
        def __init__(self, url): created.append('database')
        async def dispose(self): closed.append('database')
    class AsyncModelClient:
        async def close(self):
            closed.append('async_model')
            if failure == 'model_close': raise RuntimeError('controlled model close failure')
    class SyncModelClient:
        def close(self): closed.append('sync_model')
    def model_factory(settings):
        if failure == 'model_init': raise RuntimeError('controlled model init failure')
        created.append('model')
        model = StreamingModel()
        model.root_async_client, model.root_client = AsyncModelClient(), SyncModelClient()
        return model
    class Embedder:
        def __init__(self, settings): created.append('embedder')
        async def aclose(self):
            closed.append('embedder')
            if failure == 'embedder_close': raise RuntimeError('controlled embedder close failure')
    class Index:
        def __init__(self, uri, *, timeout):
            if failure == 'index_init': raise RuntimeError('controlled index init failure')
            created.append('index')
            assert uri == 'http://127.0.0.1:19530/' and timeout == 5
        async def ensure_collection(self):
            created.append('ready')
            if failure == 'index_ready': raise RuntimeError('controlled index readiness failure')
        async def aclose(self):
            closed.append('index')
            if failure == 'index_close': raise RuntimeError('controlled index close failure')
    monkeypatch.setattr(main, 'Database', Database)
    monkeypatch.setattr(main, 'create_model', model_factory)
    monkeypatch.setattr(main, 'SiliconFlowEmbedder', Embedder, raising=False)
    monkeypatch.setattr(main, 'MilvusIndex', Index, raising=False)
    return created, closed


@pytest.mark.parametrize('failure', [None, 'model_close', 'embedder_close', 'index_close'])
async def test_owned_resources_close_once_even_when_another_close_fails(monkeypatch, failure):
    created, closed = owned_resources(monkeypatch, failure)
    # Model/database/FAQ setup belongs in lifespan so partial setup can unwind.
    app = main.create_app(fake_settings(mysql_password='fake-only'))
    async def run():
        async with app.router.lifespan_context(app):
            assert created == ['database', 'model', 'embedder', 'index', 'ready']
            assert closed == []
    if failure:
        with pytest.raises(RuntimeError, match='controlled'):
            await run()
    else:
        await run()
    assert closed == ['index', 'embedder', 'async_model', 'sync_model', 'database']


@pytest.mark.parametrize('failure,expected', [
    ('model_init', ['database']),
    ('index_init', ['embedder', 'async_model', 'sync_model', 'database']),
    ('index_ready', ['index', 'embedder', 'async_model', 'sync_model', 'database']),
])
async def test_initialization_failure_releases_already_owned_resources(monkeypatch, failure, expected):
    _, closed = owned_resources(monkeypatch, failure)
    with pytest.raises(RuntimeError, match='controlled'):
        app = main.create_app(fake_settings(mysql_password='fake-only'))
        async with app.router.lifespan_context(app):
            pytest.fail('failed initialization entered lifespan')
    assert closed == expected
