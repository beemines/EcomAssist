# 会话 API 测试，覆盖创建、查询、身份和状态校验及安全数据库错误响应。
import asyncio

import httpx
import pytest
from langchain_core.messages import AIMessage

from app.main import create_app
from tests.fakes import FAQStub, ConversationStore, StreamingModel, decode_sse, fake_settings


# 用指定模型与会话仓储构造离线 ASGI 客户端。
def client_for(model, repository):
    app = create_app(fake_settings(), faq_repository=FAQStub(), model=model, repository=repository)
    return httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url="http://test")


# 验证创建会话保留合法用户标识，并以字符串无损返回大整数会话编号。
async def test_create_conversation_returns_large_string_identity():
    repository = ConversationStore("9007199254740993")
    async with client_for(StreamingModel(), repository) as client:
        response = await client.post("/api/conversations", json={"user_id": "用户" * 32})
    assert response.status_code == 200
    assert response.json() == {"conversation_id": "9007199254740993"}
    assert repository.users[repository.identifier] == "用户" * 32


# 验证空白、超长或非字符串用户标识返回 HTTP 422。
@pytest.mark.parametrize("user_id", ["", " ", "x" * 65, 1, True])
async def test_invalid_user_identity(user_id):
    async with client_for(StreamingModel(), ConversationStore()) as client:
        response = await client.post("/api/conversations", json={"user_id": user_id})
    assert response.status_code == 422


# 验证工具各阶段状态事件不会提前终止聊天，最后仍返回完整增量与完成编号。
async def test_status_frames_do_not_end_chat():
    model = StreamingModel()
    model.selected = AIMessage("", tool_calls=[{"name": "query_order", "args": {"order_id": "A-42"}, "id": "call_1"}], response_metadata={"finish_reason": "tool_calls"})
    async with client_for(model, ConversationStore("9007199254740993")) as client:
        response = await client.post("/api/chat", json={"conversation_id": "9007199254740993", "message": "查订单 A-42"})
    events = decode_sse(response.text)
    names = [name for name, _ in events]
    assert names == ['status', 'status', 'status', 'status', 'delta', 'done']
    assert events[-1][1]['conversation_id'] == '9007199254740993'
    assert events[2][1] == {"phase": "tool_completed", "tool_name": "query_order", "tool_call_id": "call_1", "status": "success"}


# 验证 UUID、非规范数字、越界或非字符串会话编号在模型调用前被拒绝。
@pytest.mark.parametrize("identity", ["6c570bd6-f75a-4774-9b51-fb6f899932e0", 1, True, "0", "01", "18446744073709551616", 1.0, ""])
async def test_invalid_identity_before_model(identity):
    model = StreamingModel()
    async with client_for(model, ConversationStore()) as client:
        response = await client.post("/api/chat", json={"conversation_id": identity, "message": "你好"})
    assert response.status_code == 422
    assert model.requests == 0


# 验证不存在或已结束的会话分别返回 404 或 409，且不调用模型。
@pytest.mark.parametrize("ended, expected", [(False, 404), (True, 409)])
async def test_missing_or_ended_conversation_before_model(ended, expected):
    repository, model = ConversationStore(), StreamingModel()
    if ended:
        repository.ended.add("2")
        repository.users["2"] = "test"
    async with client_for(model, repository) as client:
        response = await client.post("/api/chat", json={"conversation_id": "2", "message": "你好"})
    assert response.status_code == expected
    assert model.requests == 0


# 验证创建或准备会话时的数据库故障返回脱敏 HTTP 503，并释放已取得的锁。
@pytest.mark.parametrize("operation", ["create", "prepare"])
async def test_database_fault_before_stream_is_safe_http_error(operation):
    class BrokenRepository(ConversationStore):
        # 在会话创建阶段抛出含敏感细节的故障，检验 HTTP 错误脱敏。
        async def create(self, user_id):
            raise RuntimeError("SECRET database credential")
        # 在会话预检查阶段抛出故障，检验响应开始前的数据库错误处理。
        async def require_open(self, conversation_id):
            raise RuntimeError("SECRET database credential")
    model = StreamingModel()
    async with client_for(model, BrokenRepository()) as client:
        response = await client.post("/api/conversations" if operation == "create" else "/api/chat",
            json={"user_id": "test"} if operation == "create" else {"conversation_id": "1", "message": "你好"})
        assert response.status_code == 503
        assert response.json()["code"] == "database_error"
        assert "SECRET" not in response.text
        client._transport.app.state.chat_service.locks.acquire("1").release()
    assert model.requests == 0


# 验证显式或仓储携带的数据库注入不被健康探测、重建或关闭。
@pytest.mark.parametrize("source", ["explicit", "explicit_only", "repository"])
async def test_injected_database_is_caller_owned_without_startup_probe(monkeypatch, source):
    import app.main
    class Database:
        # 若健康检查访问外部数据库便立即失败，确认存活接口无需数据库探测。
        def session(self):
            raise AssertionError("health probed database")
        # 若生命周期关闭调用方数据库便失败，确认注入资源由调用方持有。
        async def dispose(self):
            raise AssertionError("closed injected database")
    # 阻止应用为已注入的数据库另外创建连接资源。
    def forbidden(*args):
        raise AssertionError("created database for injection")
    database, repository = Database(), ConversationStore()
    monkeypatch.setattr(app.main, "Database", forbidden)
    if source == "repository":
        repository.database = database
    app = create_app(fake_settings(), faq_repository=FAQStub(), model=StreamingModel(), repository=repository if source != "explicit_only" else None,
        database=database if source != "repository" else None)
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url="http://test") as client:
            assert (await client.get("/health")).status_code == 200
    assert app.state.database is database


# 验证应用持有的模型与数据库按顺序各关闭一次，即使异步模型关闭发生异常。
@pytest.mark.parametrize("close_failure", [False, True])
async def test_owned_database_and_model_close_once_even_if_model_close_fails(monkeypatch, close_failure):
    import app.main
    closed = []
    class Database:
        # 提供无需连接的数据库构造替身，使测试只观察生命周期释放行为。
        def __init__(self, url):
            pass
        # 记录数据库释放顺序，核对模型关闭异常后的兜底清理。
        async def dispose(self):
            closed.append("database")
    class AsyncClient:
        # 记录异步模型关闭并按场景抛错，以模拟资源释放阶段的故障。
        async def close(self):
            closed.append("async_model")
            if close_failure:
                raise RuntimeError("close failure")
    class SyncClient:
        # 记录同步模型关闭，确认异步关闭失败后仍继续清理。
        def close(self):
            closed.append("sync_model")
    model = StreamingModel()
    model.root_async_client, model.root_client = AsyncClient(), SyncClient()
    monkeypatch.setattr(app.main, "Database", Database)
    monkeypatch.setattr(app.main, "create_model", lambda settings: model)
    app = create_app(fake_settings(mysql_password="fake-only"), faq_repository=FAQStub())
    # 执行应用生命周期并确认资源在退出前保持打开。
    async def run():
        async with app.router.lifespan_context(app):
            assert closed == []
    if close_failure:
        with pytest.raises(RuntimeError, match="close failure"):
            await run()
    else:
        await run()
    assert closed == ["async_model", "sync_model", "database"]


# 验证注入 FAQ 故障产生安全的工具失败状态，聊天仍能完成且不出现依赖属性错误。
async def test_injected_faq_failure_has_safe_tool_error():
    model = StreamingModel()
    model.selected = AIMessage("", tool_calls=[{"name": "query_faq", "args": {"keyword": "退货"}, "id": "faq_call"}], response_metadata={"finish_reason": "tool_calls"})
    app = create_app(fake_settings(), model=model, repository=ConversationStore(),
        faq_repository=FAQStub(failure=RuntimeError("synthetic FAQ failure")))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url="http://test") as client:
        response = await client.post("/api/chat", json={"conversation_id": "1", "message": "如何退货"})
    events = decode_sse(response.text)
    assert events[2][1]["status"] == "error"
    assert events[-1][0] == "done"
    assert "AttributeError" not in response.text
    assert model.requests == 1


# 验证首个流阻塞期间同会话第二次请求返回忙碌错误，且不多调用模型或写消息。
async def test_same_conversation_concurrent_request_is_http_409():
    model = StreamingModel(gate_at=0)
    repository = ConversationStore()
    async with client_for(model, repository) as client:
        first = asyncio.create_task(client.post("/api/chat", json={"conversation_id": "1", "message": "first"}))
        try:
            await asyncio.wait_for(model.waiting.wait(), 2)
            second = await client.post("/api/chat", json={"conversation_id": "1", "message": "second"})
            assert second.status_code == 409
            assert second.json()["code"] == "session_busy"
            assert model.requests == 1
            assert len(repository.rows["1"]) == 1
            model.gate.set()
            assert decode_sse((await first).text)[-1][0] == "done"
        finally:
            first.cancel()
            await asyncio.gather(first, return_exceptions=True)
