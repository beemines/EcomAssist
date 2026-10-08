# 流式响应生命周期测试，覆盖发送、断连、取消、入库时点和生成器关闭边界。
import asyncio

import pytest
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from starlette.requests import ClientDisconnect

from app.api.streaming import ManagedChatResponse
from tests.fakes import ConversationStore, StreamingModel, decode_sse, fake_settings


# 预置完整历史并构造真实聊天服务、已准备轮次与托管响应，供生命周期边界测试使用。
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


# 用指定 ASGI 版本和发送回调执行响应，并注入可控断连接收通道。
async def call_response(response, send, disconnect=None, spec="2.4"):
    # 等待断连信号或永久阻塞，模拟 ASGI 客户端尚未断开的接收行为。
    async def receive():
        if disconnect is None:
            await asyncio.Event().wait()
        else:
            await disconnect.wait()
        return {"type": "http.disconnect"}

    await response({"type": "http", "asgi": {"spec_version": spec}}, receive, send)


# 断言半轮未加入可回放历史、最终回答未提交且会话锁已释放。
def assert_no_new_completed_turn_and_released(store, response):
    assert [item.content for item in store.snapshot("1")] == ["old", "answer"]
    assert store.commits == 0
    response.service.locks.acquire("1").release()


# 验证终止 SSE 发送前最终回答已提交，响应体正确结束且资源与锁均释放。
async def test_done_send_success_observes_commit_before_send_and_ends_body():
    model = StreamingModel([
        AIMessageChunk(content="A"), AIMessageChunk(content="B"),
        AIMessageChunk(content="", response_metadata={"finish_reason": "stop"}),
    ])
    response, store, prepared = await response_for(model)
    sent = []

    # 记录 ASGI 消息，并在终止帧发送时核对完整回答已经持久化。
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


# 验证首增量前、等待下一片段或最后增量后断连均取消流，并仅保留旧完整历史。
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

    # 记录发送消息，用于精确检查断连前已发送的增量与未终止响应体。
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


# 验证各发送阶段套接字错误关闭流并释放锁，仅完成帧阶段故障保留已提交回答。
@pytest.mark.parametrize("stage", ["start", "delta", "done"])
async def test_send_oserror_closes_iterator_preserves_only_completed_answer(stage):
    model = StreamingModel()
    response, store, _ = await response_for(model)

    # 在响应开始、增量或完成帧的指定阶段抛出套接字错误，模拟发送侧断连。
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


# 验证首增量前外部取消在各 ASGI 版本下均关闭模型流并释放租约。
@pytest.mark.parametrize("spec", ["2.3", "2.4"])
async def test_external_cancellation_before_first_delta_releases_response_lease(spec):
    model = StreamingModel(gate_at=0)
    response, store, _ = await response_for(model)

    # 忽略发送内容，让测试仅控制模型等待期间的外部取消。
    async def send(message):
        pass

    task = asyncio.create_task(call_response(response, send, spec=spec))
    await asyncio.wait_for(model.waiting.wait(), 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert model.closed.is_set()
    assert_no_new_completed_turn_and_released(store, response)


# 验证模型迭代器关闭再失败也不遮蔽断连异常或妨碍锁释放。
async def test_close_failure_does_not_obscure_release():
    class BadCloseModel(StreamingModel):
        # 包装真实替身流，在关闭边界附加故障而保持正常片段行为。
        def astream(self, messages):
            parent = super().astream(messages)

            class Iterator:
                # 返回包装迭代器自身，保持异步迭代协议。
                def __aiter__(self):
                    return self

                # 转发父流下一片段，使测试只改变关闭行为。
                async def __anext__(self):
                    return await parent.__anext__()

                # 先关闭父流再抛出含敏感信息的异常，模拟清理中的二次故障。
                async def aclose(self):
                    await parent.aclose()
                    raise RuntimeError("close failed with sensitive upstream text")

            return Iterator()

    model = BadCloseModel()
    response, store, _ = await response_for(model)

    # 在首增量发送时抛套接字错误，触发带关闭故障的断连清理。
    async def send(message):
        if b"event: delta" in message.get("body", b""):
            raise OSError("closed")

    with pytest.raises(ClientDisconnect):
        await call_response(response, send)
    assert model.closed.is_set()
    assert_no_new_completed_turn_and_released(store, response)


# 验证直接消费服务事件时也会在 done 前提交回答，无需响应层额外提交。
async def test_service_commits_final_answer_before_done_without_response_commit():
    response, store, prepared = await response_for(StreamingModel())
    events = [event async for event in response.events]
    assert [event.event for event in events] == ["status", "status", "delta", "done"]
    assert store.commits == 1
    assert [item.content for item in store.snapshot("1")] == ["old", "answer", "new", "你好"]
    response.service.release(prepared)


# 验证模型输入预算裁掉旧长历史时，持久仓储仍保留原历史并追加新完整轮次。
async def test_response_budget_trimming_preserves_persisted_history():
    store = ConversationStore()
    response, store, _ = await response_for(StreamingModel(), store)
    await store.seed("1", [HumanMessage(content="X" * 15000), AIMessage(content="Y" * 15000)])
    response.service.release(response.prepared)
    response.service.settings = fake_settings(tool_input_token_budget=8000)
    prepared = await response.service.prepare("1", "new")
    response = ManagedChatResponse(response.service, prepared)
    # 忽略传输消息，让测试只观察输入裁剪与持久历史的区别。
    async def send(message):
        pass
    await call_response(response, send)
    assert all("X" * 15000 != item.content for item in response.service.model.calls[-1])
    assert [item.content for item in store.snapshot("1")][-2:] == ["new", "你好"]
    assert len(store.snapshot("1")) == 6


# 验证最终回答落库失败只输出错误，不能发送 done 或形成新完整轮次。
async def test_commit_failure_emits_only_error_and_no_done():
    response, store, _ = await response_for(StreamingModel())
    store.fail_final = True
    sent = []
    # 记录发送内容，供最终提交故障后的事件顺序断言。
    async def send(message):
        sent.append(message)
    await call_response(response, send)
    names = [name for name, _ in decode_sse(b"".join(message.get("body", b"") for message in sent).decode())]
    assert names == ["status", "status", "delta", "error"]
    assert_no_new_completed_turn_and_released(store, response)


# 验证状态帧后立即断连释放租约，且尚未发起模型调用。
@pytest.mark.parametrize("spec", ["2.3", "2.4"])
async def test_disconnect_after_status_releases_lease_without_model_work(spec):
    response, store, _ = await response_for(StreamingModel())
    disconnect = asyncio.Event()
    # 发送状态帧时触发断连并阻塞，制造模型启动前的断连边界。
    async def send(message):
        if b"event: status" in message.get("body", b""):
            disconnect.set()
            await asyncio.Event().wait()
    await asyncio.wait_for(call_response(response, send, disconnect, spec), 2)
    assert response.service.model.requests == 0
    assert_no_new_completed_turn_and_released(store, response)


# 验证模型关闭永久阻塞时清理仍有上限，不会永久占用会话锁。
async def test_slow_close_is_bounded_and_cannot_hold_the_session_forever():
    class SlowCloseModel(StreamingModel):
        # 包装父流，使片段正常但关闭阶段可被永久阻塞。
        def astream(self, messages):
            parent = super().astream(messages)

            class Iterator:
                # 返回关闭阻塞的包装迭代器自身。
                def __aiter__(self):
                    return self

                # 保持父流片段输出，用于单独考察关闭超时。
                async def __anext__(self):
                    return await parent.__anext__()

                # 先关闭父流再永久等待，模拟资源关闭挂起并检验清理期限。
                async def aclose(self):
                    await parent.aclose()
                    await asyncio.Event().wait()

            return Iterator()

    model = SlowCloseModel()
    response, store, _ = await response_for(model)

    # 首增量发送失败以触发慢关闭路径。
    async def send(message):
        if b"event: delta" in message.get("body", b""):
            raise OSError("closed")

    with pytest.raises(ClientDisconnect):
        await asyncio.wait_for(call_response(response, send), 7)
    assert model.closed.is_set()
    assert_no_new_completed_turn_and_released(store, response)


# 验证终止帧发送返回时发生取消，已经提交的完整回答仍被保留且锁释放。
async def test_cancellation_after_terminal_send_return_keeps_committed_history():
    response, store, _ = await response_for(StreamingModel())

    # 在最终响应体发送边界取消当前任务，制造提交后的取消窗口。
    async def send(message):
        if message["type"] == "http.response.body" and not message["more_body"]:
            asyncio.current_task().cancel()

    task = asyncio.create_task(call_response(response, send))
    with pytest.raises(asyncio.CancelledError):
        await task
    assert store.commits == 1
    assert [item.content for item in store.snapshot("1")] == ["old", "answer", "new", "你好"]
    response.service.locks.acquire("1").release()


# 验证完成、断连、关闭故障和慢关闭路径中，模型与事件迭代器及租约各清理一次。
@pytest.mark.parametrize("spec", ["2.3", "2.4"])
@pytest.mark.parametrize("mode", ["complete", "disconnect", "close_error", "slow_close"])
async def test_iterators_and_lease_cleanup_happen_once(spec, mode):
    class CountingModel(StreamingModel):
        close_calls = 0
        # 包装模型流并计数关闭次数，按场景注入关闭异常或永久等待。
        def astream(self, messages):
            parent = super().astream(messages)
            model = self
            class Iterator:
                # 返回计数包装迭代器自身，保持流协议。
                def __aiter__(self):
                    return self
                # 透传父流片段，避免关闭次数测试改变生成过程。
                async def __anext__(self):
                    return await parent.__anext__()
                # 计数并关闭父流，再按场景制造异常或阻塞以检验幂等清理。
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
        # 返回服务事件包装器自身，便于分别计数事件流关闭。
        def __aiter__(self):
            return self
        # 转发服务事件，保持真实事件编排。
        async def __anext__(self):
            return await anext(events)
        # 计数并关闭原事件流，核对响应层只清理一次。
        async def aclose(self):
            self.close_calls += 1
            await events.aclose()
    response.events = wrapper = Events()
    releases = []
    release = response.service.release
    # 记录租约释放请求并调用真实释放，以验证断连竞态下无重复清理。
    def counting_release(prepared):
        releases.append(prepared)
        release(prepared)
    response.service.release = counting_release
    # 非正常完成场景在增量发送时触发断连并阻塞，精确进入响应清理路径。
    async def send(message):
        if mode != "complete" and b"event: delta" in message.get("body", b""):
            disconnect.set()
            await asyncio.Event().wait()
    await asyncio.wait_for(call_response(response, send, disconnect, spec), 7)
    assert model.close_calls == wrapper.close_calls == len(releases) == 1
    assert model.closed.is_set()
    response.service.locks.acquire("1").release()


# 验证模型已 EOF 且最终回答已提交后，done 交付前断连仍保留完整历史。
@pytest.mark.parametrize("spec", ["2.3", "2.4"])
async def test_disconnect_after_eof_before_done_delivery_preserves_committed_answer(spec):
    model = StreamingModel()
    response, store, _ = await response_for(model)
    disconnect = asyncio.Event()
    sent = []
    # 在 done 发送前确认 EOF 与提交状态，再触发断连阻塞交付。
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


# 验证工具执行时断连会取消工具且不重试，不启动最终模型或提交回答。
@pytest.mark.parametrize("spec", ["2.3", "2.4"])
async def test_disconnect_during_tool_execution_does_not_retry(spec):
    from langchain_core.tools import tool
    calls = []
    started = asyncio.Event()
    cancelled = asyncio.Event()
    # 启动后永久等待并记录取消信号，让测试确认断连停止一次工具调用。
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
    # 忽略传输内容，使测试通过工具启动信号精确触发断连。
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
