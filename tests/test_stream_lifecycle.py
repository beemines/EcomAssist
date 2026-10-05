import asyncio

import pytest
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from starlette.requests import ClientDisconnect

from app.core.memory import SessionStore
from tests.fakes import StreamingModel, decode_sse, implementations


class RecordingStore(SessionStore):
    def __init__(self):
        super().__init__()
        self.commits = 0

    def commit(self, lease, completed_messages):
        self.commits += 1
        super().commit(lease, completed_messages)


def response_for(model, store=None):
    service_class, response_class, _ = implementations()
    store = store if store is not None else RecordingStore()
    lease = store.acquire("same")
    store.commit(lease, [HumanMessage(content="old"), AIMessage(content="answer")])
    store.release(lease)
    store.commits = 0
    service = service_class(model, store, 2000)
    prepared = service.prepare("same", "new")
    return response_class(service, prepared), store, prepared


async def call_response(response, send, disconnect=None, spec="2.4"):
    async def receive():
        if disconnect is None:
            await asyncio.Event().wait()
        else:
            await disconnect.wait()
        return {"type": "http.disconnect"}

    await response({"type": "http", "asgi": {"spec_version": spec}}, receive, send)


def assert_rolled_back_and_released(store):
    assert [item.content for item in store.snapshot("same")] == ["old", "answer"]
    assert store.commits == 0
    lease = store.acquire("same")
    store.release(lease)


async def test_done_send_success_commits_once_after_send_and_ends_body():
    model = StreamingModel([
        AIMessageChunk(content="A"), AIMessageChunk(content="B"),
        AIMessageChunk(content="", response_metadata={"finish_reason": "stop"}),
    ])
    response, store, prepared = response_for(model)
    sent = []

    async def send(message):
        sent.append(message)
        if message["type"] == "http.response.body" and not message["more_body"]:
            assert store.commits == 0
            assert [item.content for item in prepared.pending_completed] == ["old", "answer", "new", "AB"]

    await call_response(response, send)
    bodies = [message for message in sent if message["type"] == "http.response.body"]
    assert [message["more_body"] for message in bodies] == [True, True, False]
    assert [event for event, _ in decode_sse(b"".join(message["body"] for message in bodies).decode())] == ["delta", "delta", "done"]
    assert store.commits == 1
    assert [item.content for item in store.snapshot("same")] == ["old", "answer", "new", "AB"]
    assert model.closed.is_set()
    store.release(store.acquire("same"))


@pytest.mark.parametrize("spec", ["2.3", "2.4"])
@pytest.mark.parametrize("stage", ["before_first", "next_wait", "last_delta", "eof_before_done"])
async def test_disconnect_at_each_precommit_boundary_rolls_back(spec, stage):
    model = StreamingModel(
        [AIMessageChunk(content="A"), AIMessageChunk(content="B"),
         AIMessageChunk(content="", response_metadata={"finish_reason": "stop"})],
        gate_at={"before_first": 0, "next_wait": 1, "last_delta": 3}.get(stage),
    )
    response, store, _ = response_for(model)
    disconnect = asyncio.Event()
    sent = []

    async def send(message):
        body = message.get("body", b"")
        if stage == "eof_before_done" and b"event: done" in body:
            assert model.eof.is_set()
            disconnect.set()
            await asyncio.Event().wait()
        sent.append(message)

    task = asyncio.create_task(call_response(response, send, disconnect, spec))
    if stage in ("before_first", "next_wait", "last_delta"):
        await asyncio.wait_for(model.waiting.wait(), 2)
        if stage == "last_delta":
            assert sum(message["type"] == "http.response.body" for message in sent) == 2
            assert model.eof.is_set() is False
        disconnect.set()
    await asyncio.wait_for(task, 2)
    assert model.closed.is_set()
    assert_rolled_back_and_released(store)
    assert not any(message.get("more_body") is False for message in sent)


@pytest.mark.parametrize("stage", ["start", "delta", "done"])
async def test_send_oserror_closes_iterator_and_never_commits(stage):
    model = StreamingModel()
    response, store, _ = response_for(model)

    async def send(message):
        kind = "start" if message["type"] == "http.response.start" else "done" if not message["more_body"] else "delta"
        if kind == stage:
            raise OSError("socket closed")

    with pytest.raises(ClientDisconnect):
        await call_response(response, send)
    assert stage == "start" or model.closed.is_set()
    assert_rolled_back_and_released(store)


async def test_external_cancellation_before_first_delta_releases_response_lease():
    model = StreamingModel(gate_at=0)
    response, store, _ = response_for(model)

    async def send(message):
        pass

    task = asyncio.create_task(call_response(response, send))
    await asyncio.wait_for(model.waiting.wait(), 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert model.closed.is_set()
    assert_rolled_back_and_released(store)


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
    response, store, _ = response_for(model)

    async def send(message):
        if message["type"] == "http.response.body":
            raise OSError("closed")

    with pytest.raises(ClientDisconnect):
        await call_response(response, send)
    assert model.closed.is_set()
    assert_rolled_back_and_released(store)


async def test_service_only_prepares_pending_history_without_committing():
    service_class, _, _ = implementations()
    store = RecordingStore()
    service = service_class(StreamingModel(), store, 2000)
    prepared = service.prepare("s", "question")
    assert prepared.pending_completed == []
    events = [event async for event in service.stream(prepared)]
    assert [event.event for event in events] == ["delta", "done"]
    assert store.snapshot("s") == ()
    assert store.commits == 0
    assert [item.content for item in prepared.pending_completed] == ["question", "你好"]
    service.release(prepared)


async def test_response_commits_only_the_retained_history_after_budget_trimming():
    service_class, response_class, _ = implementations()
    store = RecordingStore()
    lease = store.acquire("same")
    store.commit(lease, [HumanMessage(content="X" * 1500), AIMessage(content="Y" * 1500)])
    store.release(lease)
    service = service_class(StreamingModel(), store, 1000)
    response = response_class(service, service.prepare("same", "new"))

    async def send(message):
        pass

    await call_response(response, send)
    assert [item.content for item in store.snapshot("same")] == ["new", "你好"]


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
    response, store, _ = response_for(model)

    async def send(message):
        if message["type"] == "http.response.body":
            raise OSError("closed")

    with pytest.raises(ClientDisconnect):
        await asyncio.wait_for(call_response(response, send), 7)
    assert model.closed.is_set()
    assert_rolled_back_and_released(store)


async def test_cancellation_after_terminal_send_return_keeps_committed_history():
    response, store, _ = response_for(StreamingModel())

    async def send(message):
        if message["type"] == "http.response.body" and not message["more_body"]:
            asyncio.current_task().cancel()

    task = asyncio.create_task(call_response(response, send))
    with pytest.raises(asyncio.CancelledError):
        await task
    assert store.commits == 1
    assert [item.content for item in store.snapshot("same")] == ["old", "answer", "new", "你好"]
    store.release(store.acquire("same"))
