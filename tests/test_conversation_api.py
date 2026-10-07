import asyncio

import httpx
import pytest
from langchain_core.messages import AIMessage

from app.main import create_app
from tests.fakes import FAQStub, ConversationStore, StreamingModel, decode_sse, fake_settings


def client_for(model, repository):
    app = create_app(fake_settings(), faq_repository=FAQStub(), model=model, repository=repository)
    return httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url="http://test")


async def test_create_conversation_returns_large_string_identity():
    repository = ConversationStore("9007199254740993")
    async with client_for(StreamingModel(), repository) as client:
        response = await client.post("/api/conversations", json={"user_id": "用户" * 32})
    assert response.status_code == 200
    assert response.json() == {"conversation_id": "9007199254740993"}
    assert repository.users[repository.identifier] == "用户" * 32


@pytest.mark.parametrize("user_id", ["", " ", "x" * 65, 1, True])
async def test_invalid_user_identity(user_id):
    async with client_for(StreamingModel(), ConversationStore()) as client:
        response = await client.post("/api/conversations", json={"user_id": user_id})
    assert response.status_code == 422


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


@pytest.mark.parametrize("identity", ["6c570bd6-f75a-4774-9b51-fb6f899932e0", 1, True, "0", "01", "18446744073709551616", 1.0, ""])
async def test_invalid_identity_before_model(identity):
    model = StreamingModel()
    async with client_for(model, ConversationStore()) as client:
        response = await client.post("/api/chat", json={"conversation_id": identity, "message": "你好"})
    assert response.status_code == 422
    assert model.requests == 0


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


@pytest.mark.parametrize("operation", ["create", "prepare"])
async def test_database_fault_before_stream_is_safe_http_error(operation):
    class BrokenRepository(ConversationStore):
        async def create(self, user_id):
            raise RuntimeError("SECRET database credential")
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


@pytest.mark.parametrize("source", ["explicit", "explicit_only", "repository"])
async def test_injected_database_is_caller_owned_without_startup_probe(monkeypatch, source):
    import app.main
    class Database:
        def session(self):
            raise AssertionError("health probed database")
        async def dispose(self):
            raise AssertionError("closed injected database")
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


@pytest.mark.parametrize("close_failure", [False, True])
async def test_owned_database_and_model_close_once_even_if_model_close_fails(monkeypatch, close_failure):
    import app.main
    closed = []
    class Database:
        def __init__(self, url):
            pass
        async def dispose(self):
            closed.append("database")
    class AsyncClient:
        async def close(self):
            closed.append("async_model")
            if close_failure:
                raise RuntimeError("close failure")
    class SyncClient:
        def close(self):
            closed.append("sync_model")
    model = StreamingModel()
    model.root_async_client, model.root_client = AsyncClient(), SyncClient()
    monkeypatch.setattr(app.main, "Database", Database)
    monkeypatch.setattr(app.main, "create_model", lambda settings: model)
    app = create_app(fake_settings(mysql_password="fake-only"), faq_repository=FAQStub())
    async def run():
        async with app.router.lifespan_context(app):
            assert closed == []
    if close_failure:
        with pytest.raises(RuntimeError, match="close failure"):
            await run()
    else:
        await run()
    assert closed == ["async_model", "sync_model", "database"]


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
