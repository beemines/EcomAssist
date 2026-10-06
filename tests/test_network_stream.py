import asyncio
import socket
from contextlib import asynccontextmanager

import httpx
import uvicorn
from langchain_core.messages import AIMessageChunk

from tests.fakes import ConversationStore, StreamingModel, fake_settings, implementations


@asynccontextmanager
async def local_server(app):
    """使用真实的临时回环套接字，不连接模型供应方，也不打开可见控制台。"""
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
    repository = ConversationStore()
    app = create_app(fake_settings(), model=model, repository=repository)
    async with local_server(app) as url, httpx.AsyncClient(base_url=url, trust_env=False) as client:
        async with client.stream("POST", "/api/chat", json={"conversation_id": "1", "message": "hello"}) as response:
            lines = response.aiter_lines()
            for _ in range(2):
                assert await asyncio.wait_for(anext(lines), 2) == "event: status"
                await anext(lines)
                await anext(lines)
            assert await asyncio.wait_for(anext(lines), 2) == "event: delta"
            assert await asyncio.wait_for(anext(lines), 2) == 'data: {"delta":"first"}'
            await asyncio.wait_for(model.waiting.wait(), 2)
            assert model.gate.is_set() is False
            assert model.eof.is_set() is False
            model.gate.set()
            remainder = [line async for line in lines]
            assert 'data: {"delta":"last"}' in remainder
            assert remainder.count("event: done") == 1
    assert [item.content for item in repository.snapshot("1")] == ["hello", "firstlast"]


async def test_real_network_disconnect_stops_upstream_and_session_is_reusable():
    _, _, create_app = implementations()
    model = StreamingModel([
        AIMessageChunk(content="first"), AIMessageChunk(content="last"),
        AIMessageChunk(content="", response_metadata={"finish_reason": "stop"}),
    ], gate_at=1)
    repository = ConversationStore()
    app = create_app(fake_settings(), model=model, repository=repository)
    async with local_server(app) as url, httpx.AsyncClient(base_url=url, trust_env=False) as client:
        async with client.stream("POST", "/api/chat", json={"conversation_id": "1", "message": "aborted"}) as response:
            lines = response.aiter_lines()
            for _ in range(2):
                assert await asyncio.wait_for(anext(lines), 2) == "event: status"
                await anext(lines)
                await anext(lines)
            assert await asyncio.wait_for(anext(lines), 2) == "event: delta"
            await asyncio.wait_for(model.waiting.wait(), 2)
        await asyncio.wait_for(model.closed.wait(), 2)
        assert model.eof.is_set() is False
        assert repository.snapshot("1") == ()
        # 此事件门始终保持关闭；会话能成功复用，说明断连取消了原有生成，
        # 而非仅让它在后台继续完成。
        assert model.gate.is_set() is False
        model.gate_at = None
        response = await client.post("/api/chat", json={"conversation_id": "1", "message": "retry"})
        assert response.status_code == 200
        assert "event: done" in response.text
    assert [item.content for item in repository.snapshot("1")] == ["retry", "firstlast"]
