import asyncio
import socket
from contextlib import asynccontextmanager

import httpx
import uvicorn
from langchain_core.messages import AIMessageChunk

from app.core.memory import SessionStore
from tests.fakes import StreamingModel, fake_settings, implementations


@asynccontextmanager
async def local_server(app):
    """A real temporary loopback socket, never a provider or visible console."""
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        port = listener.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(app, log_level="critical", lifespan="on"))
        task = asyncio.create_task(server.serve(sockets=[listener]))
        try:
            async def wait_started():
                while not server.started:
                    if task.done():
                        await task
                        raise AssertionError("Uvicorn exited before startup")
                    await asyncio.sleep(0.01)

            await asyncio.wait_for(wait_started(), 5)
            yield f"http://127.0.0.1:{port}"
        finally:
            server.should_exit = True
            try:
                await asyncio.wait_for(task, 5)
            finally:
                if not task.done():
                    task.cancel()
                    await asyncio.gather(task, return_exceptions=True)


async def test_real_network_first_event_arrives_before_last_chunk_allowed():
    _, _, create_app = implementations()
    model = StreamingModel([
        AIMessageChunk(content="first"), AIMessageChunk(content="last"),
        AIMessageChunk(content="", response_metadata={"finish_reason": "stop"}),
    ], gate_at=1)
    memory = SessionStore()
    app = create_app(fake_settings(), model=model, memory=memory)
    async with local_server(app) as url, httpx.AsyncClient(base_url=url, trust_env=False) as client:
        async with client.stream("POST", "/api/chat", json={"session_id": "s", "message": "hello"}) as response:
            lines = response.aiter_lines()
            assert await asyncio.wait_for(anext(lines), 2) == "event: delta"
            assert await asyncio.wait_for(anext(lines), 2) == 'data: {"delta":"first"}'
            await asyncio.wait_for(model.waiting.wait(), 2)
            assert model.gate.is_set() is False
            assert model.eof.is_set() is False
            model.gate.set()
            remainder = [line async for line in lines]
            assert 'data: {"delta":"last"}' in remainder
            assert remainder.count("event: done") == 1
    assert [item.content for item in memory.snapshot("s")] == ["hello", "firstlast"]


async def test_real_network_disconnect_stops_upstream_and_session_is_reusable():
    _, _, create_app = implementations()
    model = StreamingModel([
        AIMessageChunk(content="first"), AIMessageChunk(content="last"),
        AIMessageChunk(content="", response_metadata={"finish_reason": "stop"}),
    ], gate_at=1)
    memory = SessionStore()
    app = create_app(fake_settings(), model=model, memory=memory)
    async with local_server(app) as url, httpx.AsyncClient(base_url=url, trust_env=False) as client:
        async with client.stream("POST", "/api/chat", json={"session_id": "s", "message": "aborted"}) as response:
            lines = response.aiter_lines()
            assert await asyncio.wait_for(anext(lines), 2) == "event: delta"
            await asyncio.wait_for(model.waiting.wait(), 2)
        await asyncio.wait_for(model.closed.wait(), 2)
        assert model.eof.is_set() is False
        assert memory.snapshot("s") == ()
        # This gate remains shut: successful reuse proves disconnect cancelled
        # the original generation rather than simply finishing it in background.
        assert model.gate.is_set() is False
        model.gate_at = None
        response = await client.post("/api/chat", json={"session_id": "s", "message": "retry"})
        assert response.status_code == 200
        assert "event: done" in response.text
    assert [item.content for item in memory.snapshot("s")] == ["retry", "firstlast"]
