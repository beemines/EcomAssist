# 应用知识检索依赖的生命周期测试，检查依赖注入、初始化失败及关闭责任。
import httpx
import pytest
from langchain_core.messages import AIMessage

import app.main as main
from tests.fakes import ConversationStore, FAQStub, StreamingModel, decode_sse, fake_settings


# 确认应用支持 FAQ 仓储注入，再使用离线设置创建应用。
def injected_app(**kwargs):
    import inspect
    assert 'faq_repository' in inspect.signature(main.create_app).parameters, 'FAQ injection missing'
    return main.create_app(fake_settings(), **kwargs)


# 验证注入 FAQ 不额外创建检索客户端或关闭外部仓储，且仍参与工具回答。
async def test_injected_faq_avoids_retrieval_clients_and_remains_caller_owned(monkeypatch):
    # 检测为注入 FAQ 创建外部客户端或关闭调用方资源的错误行为。
    def forbidden(*args, **kwargs):
        raise AssertionError('created an external client for an injected FAQ')
    monkeypatch.setattr(main, 'SiliconFlowEmbedder', forbidden, raising=False)
    monkeypatch.setattr(main, 'MilvusIndex', forbidden, raising=False)
    class FAQ(FAQStub):
        # 若应用关闭注入 FAQ 便立即失败，核对资源所有权。
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


# 安装数据库、模型、嵌入与索引替身，记录创建关闭并按阶段注入故障。
def owned_resources(monkeypatch, failure=None):
    closed, created = [], []
    class Database:
        # 记录数据库创建，供部分初始化清理断言使用。
        def __init__(self, url): created.append('database')
        # 记录数据库释放，核对最后一个资源的关闭顺序。
        async def dispose(self): closed.append('database')
    class AsyncModelClient:
        # 记录异步模型关闭，并按场景抛错检验后续资源仍清理。
        async def close(self):
            closed.append('async_model')
            if failure == 'model_close': raise RuntimeError('controlled model close failure')
    class SyncModelClient:
        # 记录同步模型关闭，核对一次性释放行为。
        def close(self): closed.append('sync_model')
    # 模拟模型构造失败或创建带客户端的流替身，以测试初始化边界。
    def model_factory(settings):
        if failure == 'model_init': raise RuntimeError('controlled model init failure')
        created.append('model')
        model = StreamingModel()
        model.root_async_client, model.root_client = AsyncModelClient(), SyncModelClient()
        return model
    class Embedder:
        # 记录嵌入客户端创建，确认索引初始化前已有的资源。
        def __init__(self, settings): created.append('embedder')
        # 记录嵌入关闭并可抛错，检验清理异常下的释放顺序。
        async def aclose(self):
            closed.append('embedder')
            if failure == 'embedder_close': raise RuntimeError('controlled embedder close failure')
    class Index:
        # 检查索引端点和超时，并可在构造阶段失败以测试部分初始化回收。
        def __init__(self, uri, *, timeout):
            if failure == 'index_init': raise RuntimeError('controlled index init failure')
            created.append('index')
            assert uri == 'http://127.0.0.1:19530/' and timeout == 5
        # 记录索引就绪检查，并可注入准备失败检验启动回滚。
        async def ensure_collection(self):
            created.append('ready')
            if failure == 'index_ready': raise RuntimeError('controlled index readiness failure')
        # 记录索引关闭并可抛错，确认它不阻止后续资源清理。
        async def aclose(self):
            closed.append('index')
            if failure == 'index_close': raise RuntimeError('controlled index close failure')
    monkeypatch.setattr(main, 'Database', Database)
    monkeypatch.setattr(main, 'create_model', model_factory)
    monkeypatch.setattr(main, 'SiliconFlowEmbedder', Embedder, raising=False)
    monkeypatch.setattr(main, 'MilvusIndex', Index, raising=False)
    return created, closed


# 验证应用持有的所有依赖按逆初始化顺序关闭一次，单个关闭异常不漏资源。
@pytest.mark.parametrize('failure', [None, 'model_close', 'embedder_close', 'index_close'])
async def test_owned_resources_close_once_even_when_another_close_fails(monkeypatch, failure):
    created, closed = owned_resources(monkeypatch, failure)
    # 模型、数据库和 FAQ 依赖在 lifespan 内初始化，部分初始化失败也应能回收资源。
    app = main.create_app(fake_settings(mysql_password='fake-only'))
    # 执行真实应用生命周期，确认进入时依赖均已创建且尚未关闭。
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


# 验证模型或索引各初始化阶段失败时，只回收已成功创建的资源。
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
