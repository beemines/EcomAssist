import asyncio

import pytest
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from starlette.requests import ClientDisconnect

from app.api.streaming import ManagedChatResponse
from tests.fakes import ConversationStore, StreamingModel, decode_sse, fake_settings


async def response_for(model, store=None):
    from app.core.tool_chat import ToolChatService
    from app.core.conversation_locks import ConversationLocks
    from app.tools.registry import build_registry
    from tests.tool_fakes import FAQ, Tickets
    store = store if store is not None else ConversationStore()
    await store.seed("1", [HumanMessage(content="old"), AIMessage(content="answer")])
    service = ToolChatService(model, store, lambda context: build_registry(FAQ(), Tickets(), context), ConversationLocks(), fake_settings())
    prepared = await service.prepare("1", "new")
    return ManagedChatResponse(service, prepared), store, prepared


async def call_response(response, send, disconnect=None, spec="2.4"):
    async def receive():
        if disconnect is None:
            await asyncio.Event().wait()
        else:
            await disconnect.wait()
        return {"type": "http.disconnect"}

    await response({"type": "http", "asgi": {"spec_version": spec}}, receive, send)


def assert_no_new_completed_turn_and_released(store, response):
    assert [item.content for item in store.snapshot("1")] == ["old", "answer"]
    assert store.commits == 0
    response.service.locks.acquire("1").release()


async def test_done_send_success_observes_commit_before_send_and_ends_body():
    model = StreamingModel([
        AIMessageChunk(content="A"), AIMessageChunk(content="B"),
        AIMessageChunk(content="", response_metadata={"finish_reason": "stop"}),
    ])
    response, store, prepared = await response_for(model)
    sent = []

    async def send(message):
        sent.append(message)
        if message["type"] == "http.response.body" and not message["more_body"]:
            assert store.commits == 1
            assert [item.content for item in store.snapshot("1")] == ["old", "answer", "new", "AB"]

    await call_response(response, send)
    bodies = [message for message in sent if message["type"] == "http.response.body"]
    assert [message["more_body"] for message in bodies] == [True, True, True, True, False]
    assert [event for event, _ in decode_sse(b"".join(message["body"] for message in bodies).decode())] == ["status", "status", "delta", "delta", "done"]
    assert store.commits == 1
    assert [item.content for item in store.snapshot("1")] == ["old", "answer", "new", "AB"]
    assert model.closed.is_set()
    response.service.locks.acquire("1").release()


@pytest.mark.parametrize("spec", ["2.3", "2.4"])
@pytest.mark.parametrize("stage", ["before_first", "next_wait", "last_delta"])
async def test_disconnect_at_each_precommit_boundary_preserves_completed_history(spec, stage):
    model = StreamingModel(
        [AIMessageChunk(content="A"), AIMessageChunk(content="B"),
         AIMessageChunk(content="", response_metadata={"finish_reason": "stop"})],
        gate_at={"before_first": 0, "next_wait": 1, "last_delta": 3}.get(stage),
    )
    response, store, _ = await response_for(model)
    disconnect = asyncio.Event()
    sent = []

    async def send(message):
        sent.append(message)

    task = asyncio.create_task(call_response(response, send, disconnect, spec))
    if stage in ("before_first", "next_wait", "last_delta"):
        await asyncio.wait_for(model.waiting.wait(), 2)
        if stage == "last_delta":
            assert sum(message["type"] == "http.response.body" for message in sent) == 4
            assert model.eof.is_set() is False
        disconnect.set()
    await asyncio.wait_for(task, 2)
    assert model.closed.is_set()
    assert_no_new_completed_turn_and_released(store, response)
    assert not any(message.get("more_body") is False for message in sent)


@pytest.mark.parametrize("stage", ["start", "delta", "done"])
async def test_send_oserror_closes_iterator_preserves_only_completed_answer(stage):
    model = StreamingModel()
    response, store, _ = await response_for(model)

    async def send(message):
        body = message.get("body", b"")
        kind = "start" if message["type"] == "http.response.start" else "done" if b"event: done" in body else "delta" if b"event: delta" in body else "status"
        if kind == stage:
            raise OSError("socket closed")

    with pytest.raises(ClientDisconnect):
        await call_response(response, send)
    assert stage == "start" or model.closed.is_set()
    if stage == "done":
        assert store.commits == 1
        assert [item.content for item in store.snapshot("1")] == ["old", "answer", "new", "你好"]
        response.service.locks.acquire("1").release()
    else:
        assert_no_new_completed_turn_and_released(store, response)


@pytest.mark.parametrize("spec", ["2.3", "2.4"])
async def test_external_cancellation_before_first_delta_releases_response_lease(spec):
    model = StreamingModel(gate_at=0)
    response, store, _ = await response_for(model)

    async def send(message):
        pass

    task = asyncio.create_task(call_response(response, send, spec=spec))
    await asyncio.wait_for(model.waiting.wait(), 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert model.closed.is_set()
    assert_no_new_completed_turn_and_released(store, response)


async def test_close_failure_does_not_obscure_release():
    class BadCloseModel(StreamingModel):
        def astream(self, messages):
            parent = super().astream(messages)

            class Iterator:
                def __aiter__(self):
                    return self

                async def __anext__(self):
                    return await parent.__anext__()

                async def aclose(self):
                    await parent.aclose()
                    raise RuntimeError("close failed with sensitive upstream text")

            return Iterator()

    model = BadCloseModel()
    response, store, _ = await response_for(model)

    async def send(message):
        if b"event: delta" in message.get("body", b""):
            raise OSError("closed")

    with pytest.raises(ClientDisconnect):
        await call_response(response, send)
    assert model.closed.is_set()
    assert_no_new_completed_turn_and_released(store, response)


async def test_service_commits_final_answer_before_done_without_response_commit():
    response, store, prepared = await response_for(StreamingModel())
    events = [event async for event in response.events]
    assert [event.event for event in events] == ["status", "status", "delta", "done"]
    assert store.commits == 1
    assert [item.content for item in store.snapshot("1")] == ["old", "answer", "new", "你好"]
    response.service.release(prepared)


async def test_response_budget_trimming_preserves_persisted_history():
    store = ConversationStore()
    response, store, _ = await response_for(StreamingModel(), store)
    await store.seed("1", [HumanMessage(content="X" * 15000), AIMessage(content="Y" * 15000)])
    response.service.release(response.prepared)
    response.service.settings = fake_settings(tool_input_token_budget=8000)
    prepared = await response.service.prepare("1", "new")
    response = ManagedChatResponse(response.service, prepared)
    async def send(message):
        pass
    await call_response(response, send)
    assert all("X" * 15000 != item.content for item in response.service.model.calls[-1])
    assert [item.content for item in store.snapshot("1")][-2:] == ["new", "你好"]
    assert len(store.snapshot("1")) == 6


async def test_commit_failure_emits_only_error_and_no_done():
    response, store, _ = await response_for(StreamingModel())
    store.fail_final = True
    sent = []
    async def send(message):
        sent.append(message)
    await call_response(response, send)
    names = [name for name, _ in decode_sse(b"".join(message.get("body", b"") for message in sent).decode())]
    assert names == ["status", "status", "delta", "error"]
    assert_no_new_completed_turn_and_released(store, response)


@pytest.mark.parametrize("spec", ["2.3", "2.4"])
async def test_disconnect_after_status_releases_lease_without_model_work(spec):
    response, store, _ = await response_for(StreamingModel())
    disconnect = asyncio.Event()
    async def send(message):
        if b"event: status" in message.get("body", b""):
            disconnect.set()
            await asyncio.Event().wait()
    await asyncio.wait_for(call_response(response, send, disconnect, spec), 2)
    assert response.service.model.requests == 0
    assert_no_new_completed_turn_and_released(store, response)


async def test_slow_close_is_bounded_and_cannot_hold_the_session_forever():
    class SlowCloseModel(StreamingModel):
        def astream(self, messages):
            parent = super().astream(messages)

            class Iterator:
                def __aiter__(self):
                    return self

                async def __anext__(self):
                    return await parent.__anext__()

                async def aclose(self):
                    await parent.aclose()
                    await asyncio.Event().wait()

            return Iterator()

    model = SlowCloseModel()
    response, store, _ = await response_for(model)

    async def send(message):
        if b"event: delta" in message.get("body", b""):
            raise OSError("closed")

    with pytest.raises(ClientDisconnect):
        await asyncio.wait_for(call_response(response, send), 7)
    assert model.closed.is_set()
    assert_no_new_completed_turn_and_released(store, response)


async def test_cancellation_after_terminal_send_return_keeps_committed_history():
    response, store, _ = await response_for(StreamingModel())

    async def send(message):
        if message["type"] == "http.response.body" and not message["more_body"]:
            asyncio.current_task().cancel()

    task = asyncio.create_task(call_response(response, send))
    with pytest.raises(asyncio.CancelledError):
        await task
    assert store.commits == 1
    assert [item.content for item in store.snapshot("1")] == ["old", "answer", "new", "你好"]
    response.service.locks.acquire("1").release()


@pytest.mark.parametrize("spec", ["2.3", "2.4"])
@pytest.mark.parametrize("mode", ["complete", "disconnect", "close_error", "slow_close"])
async def test_iterators_and_lease_cleanup_happen_once(spec, mode):
    class CountingModel(StreamingModel):
        close_calls = 0
        def astream(self, messages):
            parent = super().astream(messages)
            model = self
            class Iterator:
                def __aiter__(self):
                    return self
                async def __anext__(self):
                    return await parent.__anext__()
                async def aclose(self):
                    model.close_calls += 1
                    await parent.aclose()
                    if mode == "close_error":
                        raise RuntimeError("SECRET close error")
                    if mode == "slow_close":
                        await asyncio.Event().wait()
            return Iterator()
    model = CountingModel()
    response, store, _ = await response_for(model)
    disconnect = asyncio.Event()
    events = response.events
    class Events:
        close_calls = 0
        def __aiter__(self):
            return self
        async def __anext__(self):
            return await anext(events)
        async def aclose(self):
            self.close_calls += 1
            await events.aclose()
    response.events = wrapper = Events()
    releases = []
    release = response.service.release
    def counting_release(prepared):
        releases.append(prepared)
        release(prepared)
    response.service.release = counting_release
    async def send(message):
        if mode != "complete" and b"event: delta" in message.get("body", b""):
            disconnect.set()
            await asyncio.Event().wait()
    await asyncio.wait_for(call_response(response, send, disconnect, spec), 7)
    assert model.close_calls == wrapper.close_calls == len(releases) == 1
    assert model.closed.is_set()
    response.service.locks.acquire("1").release()


@pytest.mark.parametrize("spec", ["2.3", "2.4"])
async def test_disconnect_after_eof_before_done_delivery_preserves_committed_answer(spec):
    model = StreamingModel()
    response, store, _ = await response_for(model)
    disconnect = asyncio.Event()
    sent = []
    async def send(message):
        if b"event: done" in message.get("body", b""):
            assert model.eof.is_set()
            assert store.commits == 1
            disconnect.set()
            await asyncio.Event().wait()
        sent.append(message)
    await asyncio.wait_for(call_response(response, send, disconnect, spec), 2)
    assert store.commits == 1
    assert [item.content for item in store.snapshot("1")] == ["old", "answer", "new", "你好"]
    assert not any(message.get("more_body") is False for message in sent)
    assert model.closed.is_set()
    response.service.locks.acquire("1").release()


@pytest.mark.parametrize("spec", ["2.3", "2.4"])
async def test_disconnect_during_tool_execution_does_not_retry(spec):
    from langchain_core.tools import tool
    calls = []
    started = asyncio.Event()
    cancelled = asyncio.Event()
    @tool
    async def query_order(order_id: str) -> dict:
        """验证取消后的工具不重试。"""
        calls.append(order_id)
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()
    model = StreamingModel()
    model.selected = AIMessage("", tool_calls=[{"name": "query_order", "args": {"order_id": "A-42"}, "id": "call_1"}], response_metadata={"finish_reason": "tool_calls"})
    response, store, _ = await response_for(model)
    response.service.release(response.prepared)
    response.service.registry_factory = lambda context: {"query_order": query_order}
    prepared = await response.service.prepare("1", "查订单 A-42")
    response = ManagedChatResponse(response.service, prepared)
    disconnect = asyncio.Event()
    async def send(message):
        pass
    task = asyncio.create_task(call_response(response, send, disconnect, spec))
    await asyncio.wait_for(started.wait(), 2)
    disconnect.set()
    await asyncio.wait_for(task, 2)
    assert cancelled.is_set()
    assert calls == ["A-42"]
    assert model.requests == 1 and model.calls == []
    assert_no_new_completed_turn_and_released(store, response)
