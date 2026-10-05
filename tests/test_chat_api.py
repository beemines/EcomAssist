import importlib
import sys

import httpx
import pytest
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from openai import APITimeoutError

from app.core.memory import SessionStore
from tests.fakes import StreamingModel, decode_sse, fake_settings, implementations


def client_for(model=None, memory=None, **settings):
    _, _, create_app = implementations()
    app = create_app(fake_settings(**settings), model=model or StreamingModel(), memory=memory)
    return httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url="http://test")


async def test_health_returns_liveness_without_model_work():
    model = StreamingModel(failure=AssertionError("health invoked provider"))
    async with client_for(model) as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert model.calls == []


@pytest.mark.parametrize("payload", [
    {}, {"session_id": "s", "message": " "},
    {"session_id": " ", "message": "valid"},
    {"session_id": "s" * 129, "message": "valid"},
    {"session_id": "s", "message": "m" * 20001},
    {"session_id": "s", "message": "valid", "extra": True},
])
async def test_invalid_request_is_rejected_before_model_or_sse(payload):
    model = StreamingModel()
    async with client_for(model) as client:
        response = await client.post("/api/chat", json=payload)
    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/json")
    assert model.calls == []


async def test_budget_error_is_http_422_and_releases_acquired_session():
    model, memory = StreamingModel(), SessionStore()
    async with client_for(model, memory, input_token_budget=1) as client:
        response = await client.post("/api/chat", json={"session_id": "s", "message": "hello"})
    assert response.status_code == 422
    assert response.json() == {"code": "input_too_long", "message": "Input exceeds the context budget."}
    assert model.calls == []
    memory.release(memory.acquire("s"))


async def test_session_busy_is_http_409_before_response_start():
    model, memory = StreamingModel(), SessionStore()
    lease = memory.acquire("s")
    try:
        async with client_for(model, memory) as client:
            response = await client.post("/api/chat", json={"session_id": "s", "message": "hello"})
        assert response.status_code == 409
        assert response.json() == {"code": "session_busy", "message": "Session is processing another request."}
        assert model.calls == []
    finally:
        memory.release(lease)


async def test_raw_deltas_headers_and_complete_second_turn_history():
    model = StreamingModel([
        AIMessageChunk(content=""),
        AIMessageChunk(content=[{"type": "reasoning", "reasoning": "private"}]),
        AIMessageChunk(content='您好，\n"订单"'),
        AIMessageChunk(content=[{"type": "text", "text": "可以咨询。"}]),
        AIMessageChunk(content="", response_metadata={"finish_reason": "stop"}),
        AIMessageChunk(content="", chunk_position="last"),
    ])
    memory = SessionStore()
    async with client_for(model, memory) as client:
        first = await client.post("/api/chat", json={"session_id": "s", "message": "first"})
        model.chunks = [
            AIMessageChunk(content="second answer"),
            AIMessageChunk(content="", response_metadata={"finish_reason": "stop"}),
        ]
        second = await client.post("/api/chat", json={"session_id": "s", "message": "second"})
    assert first.headers["content-type"].startswith("text/event-stream")
    assert first.headers["cache-control"] == "no-cache"
    assert first.headers["x-accel-buffering"] == "no"
    assert decode_sse(first.text) == [
        ("delta", {"delta": '您好，\n"订单"'}),
        ("delta", {"delta": "可以咨询。"}),
        ("done", {"session_id": "s"}),
    ]
    assert [item.content for item in model.calls[1][1:]] == ["first", '您好，\n"订单"可以咨询。', "second"]
    assert decode_sse(second.text)[-1] == ("done", {"session_id": "s"})
    assert [item.content for item in memory.snapshot("s")] == ["first", '您好，\n"订单"可以咨询。', "second", "second answer"]


@pytest.mark.parametrize("failure", [
    RuntimeError("SECRET upstream details"), TimeoutError("SECRET timeout"),
    httpx.ReadTimeout("SECRET timeout"),
    APITimeoutError(request=httpx.Request("POST", "https://upstream.invalid")),
])
async def test_upstream_failure_sends_safe_error_once_and_preserves_history(failure):
    model = StreamingModel([AIMessageChunk(content="partial")], failure=failure)
    memory = SessionStore()
    lease = memory.acquire("s")
    memory.commit(lease, [HumanMessage(content="old"), AIMessage(content="answer")])
    memory.release(lease)
    async with client_for(model, memory) as client:
        response = await client.post("/api/chat", json={"session_id": "s", "message": "new"})
    events = decode_sse(response.text)
    assert [event for event, _ in events] == ["delta", "error"]
    assert set(events[-1][1]) == {"code", "message"}
    assert events[-1][1]["code"] == ("upstream_error" if isinstance(failure, RuntimeError) else "upstream_timeout")
    assert "SECRET" not in response.text
    assert [item.content for item in memory.snapshot("s")] == ["old", "answer"]
    assert model.closed.is_set()
    memory.release(memory.acquire("s"))


@pytest.mark.parametrize("chunks", [
    [], [AIMessageChunk(content="")], [AIMessageChunk(content="   ")],
    [AIMessageChunk(content="partial"), AIMessageChunk(content="", response_metadata={"finish_reason": "length"})],
])
async def test_empty_or_explicitly_truncated_response_errors_without_commit(chunks):
    memory, model = SessionStore(), StreamingModel(chunks)
    async with client_for(model, memory) as client:
        response = await client.post("/api/chat", json={"session_id": "s", "message": "hello"})
    events = decode_sse(response.text)
    assert events[-1][0] == "error"
    assert sum(event == "error" for event, _ in events) == 1
    assert not any(event == "done" for event, _ in events)
    assert memory.snapshot("s") == ()
    memory.release(memory.acquire("s"))


def test_import_and_injected_lifespan_do_not_load_settings_or_own_injected_model(monkeypatch):
    implementations()
    import app.config
    import app.core.llm

    def forbidden(*args, **kwargs):
        raise AssertionError("import or injected app read credentials/created provider")

    monkeypatch.setattr(app.config, "load_settings", forbidden)
    monkeypatch.setattr(app.core.llm, "create_model", forbidden)
    sys.modules.pop("app.main", None)
    main = importlib.import_module("app.main")
    from fastapi.testclient import TestClient

    model = StreamingModel()
    model.root_async_client = type("Client", (), {"close": forbidden})()
    model.root_client = type("Client", (), {"close": forbidden})()
    with TestClient(main.create_app(fake_settings(), model=model)) as client:
        assert client.get("/health").json() == {"status": "ok"}


async def test_owned_factory_resource_closes_on_lifespan_exit(monkeypatch):
    _, _, create_app = implementations()
    import app.main

    class Resource:
        closed = False

        async def close(self):
            self.closed = True

    resource = Resource()
    class SyncResource:
        closed = False

        def close(self):
            self.closed = True

    sync_resource = SyncResource()
    model = StreamingModel()
    model.root_async_client = resource
    model.root_client = sync_resource
    monkeypatch.setattr(app.main, "create_model", lambda settings: model)
    app = create_app(fake_settings())
    async with app.router.lifespan_context(app):
        assert resource.closed is False
    assert resource.closed is True
    assert sync_resource.closed is True
