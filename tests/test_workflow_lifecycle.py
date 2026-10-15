"""真实 Workflow 断连、关闭重启以及新输入边界。"""
import asyncio

import pytest
from langchain_core.messages import AIMessageChunk

from app.api.streaming import ManagedChatResponse
from app.workflow.persistence import checkpoint_config
from tests.test_stream_lifecycle import call_response
from tests.test_workflow_api import Store, workflow_app, request, intent, service_type
from tests.test_workflow_agent import control
from tests.workflow_fakes import ScriptedWorkflowModel
from tests.fakes import decode_sse


class BlockedModel(ScriptedWorkflowModel):
    """真实最终流在首片后阻塞，供断连与关闭验证。"""
    def __init__(self):
        """模型仅执行一次意图和一次澄清决策。"""
        super().__init__([control('clarification')], intent_replies=[intent('订单')])
        self.waiting, self.gate = asyncio.Event(), asyncio.Event()

    async def astream(self, messages, **kwargs):
        """首片已可见时保持收费流打开，取消必须进入 finally。"""
        self.streams += 1
        try:
            yield AIMessageChunk('请提供订单号。')
            self.waiting.set()
            await self.gate.wait()
            yield AIMessageChunk('', response_metadata={'finish_reason': 'stop'})
        finally:
            self.closed = True


@pytest.mark.parametrize('spec', ['2.3', '2.4'])
async def test_disconnect_releases_every_resource(tmp_path, spec):
    """断连必须取消图任务和上游流，未完成轮次不能提交。"""
    service_type()
    store, model = Store(), BlockedModel()
    async with workflow_app(tmp_path, model=model, store=store) as app:
        service = app.state.chat_service
        prepared = await service.prepare('1', '我的订单')
        response = ManagedChatResponse(service, prepared)
        disconnect, sent = asyncio.Event(), []
        async def send(message):
            """记录实际首增量，阻止通过缓存全量答案伪装流式。"""
            sent.append(message)
        task = asyncio.create_task(call_response(response, send, disconnect, spec))
        await asyncio.wait_for(model.waiting.wait(), 3)
        await asyncio.sleep(.02)
        assert not any(b'event: delta' in item.get('body', b'') for item in sent)
        disconnect.set()
        await asyncio.wait_for(task, 3)
        assert model.closed and store.commits == 0
        assert prepared.audit['usage']['actual_calls'] + prepared.audit['usage']['estimated_calls'] == 4
        assert not service._tasks
        service.locks.acquire('1').release()


async def test_shutdown_cancels_stream_before_closing_saver(tmp_path):
    """寿命结束应先取消实际图任务，再关闭官方 SQLite。"""
    service_type()
    model, store = BlockedModel(), Store()
    async with workflow_app(tmp_path, model=model, store=store) as app:
        service = app.state.chat_service
        prepared = await service.prepare('1', '订单在哪')
        async def consume():
            """消费真实流，停机取消通过消费者 finally 释放租约。"""
            try:
                async for event in service.stream(prepared):
                    pass
            finally:
                service.release(prepared)
        task = asyncio.create_task(consume())
        await asyncio.wait_for(model.waiting.wait(), 3)
    await asyncio.wait_for(asyncio.gather(task, return_exceptions=True), 3)
    assert model.closed and not service._tasks and store.commits == 0
    service.locks.acquire('1').release()


async def test_restart_new_input_never_resumes_failed_tools(tmp_path):
    """重新打开 SQLite 后必须新输入 START，不能重放失败节点的收费工具。"""
    service_type()
    from tests.fakes import FAQStub
    faq, store = FAQStub(failure=RuntimeError('controlled retrieval failure')), Store()
    model = ScriptedWorkflowModel(intent_replies=[intent('商品咨询')])
    async with workflow_app(tmp_path, model=model, store=store, faq=faq) as app:
        assert decode_sse((await request(app, '商品政策')).text)[-1][0] == 'error'
        failed = await app.state.chat_service.graph.aget_state(checkpoint_config('1'))
        assert failed.next
    calls = len(faq.keywords)
    async with workflow_app(tmp_path, model=ScriptedWorkflowModel(), store=store, faq=faq) as app:
        assert decode_sse((await request(app, '你好')).text)[-1][0] == 'done'
        snapshot = await app.state.chat_service.graph.aget_state(checkpoint_config('1'))
        assert snapshot.next == () and snapshot.values['turn_status'] == 'completed'
        assert snapshot.values['tool_call_count'] == 0
    assert store.commits == 1 and len(faq.keywords) == calls


@pytest.mark.parametrize('stage', ['start', 'delta', 'done'])
async def test_send_failure_releases_workflow_lease(tmp_path, stage):
    """任意发送边界故障均归还锁，done 阶段故障保留已完成 SQL。"""
    from starlette.requests import ClientDisconnect
    store = Store()
    async with workflow_app(tmp_path, store=store) as app:
        service = app.state.chat_service
        response = ManagedChatResponse(service, await service.prepare('1', '你好'))
        async def send(message):
            """模拟网络发送失败，实际托管响应负责关闭图任务。"""
            body = message.get('body', b'')
            if ((stage == 'start' and message['type'] == 'http.response.start')
                    or (stage == 'delta' and b'event: delta' in body)
                    or (stage == 'done' and b'event: done' in body)):
                raise OSError('controlled socket failure')
        with pytest.raises(ClientDisconnect):
            await call_response(response, send)
        service.locks.acquire('1').release()
        assert not service._tasks
        if stage == 'done':
            assert store.commits == 1
        if stage == 'start':
            assert store.commits == 0


async def test_injected_saver_and_service_remain_caller_owned(tmp_path):
    """寿命结束不能关闭注入检查点或调用注入服务的关闭接口。"""
    from app.main import create_app
    from app.workflow.persistence import open_checkpointer
    from tests.fakes import fake_settings, FAQStub, legacy_app
    async with open_checkpointer(tmp_path / 'external.sqlite') as saver:
        async with workflow_app(tmp_path, saver=saver) as app:
            await request(app, '你好')
        saved = await saver.aget_tuple(checkpoint_config('1'))
        assert saved.checkpoint['channel_values']['turn_status'] == 'completed'
    legacy = legacy_app(fake_settings(), model=ScriptedWorkflowModel(), repository=Store(), faq_repository=FAQStub()).state.chat_service
    async def forbidden():
        """外部服务所有者未授权应用关闭其资源。"""
        raise AssertionError('injected service shutdown')
    legacy.shutdown = forbidden
    app = create_app(fake_settings(workflow_checkpoint_path=tmp_path / 'unused.sqlite'), chat_service=legacy,
        model=ScriptedWorkflowModel(), repository=Store(), faq_repository=FAQStub())
    async with app.router.lifespan_context(app):
        assert app.state.chat_service is legacy
    assert not (tmp_path / 'unused.sqlite').exists()


async def test_slow_upstream_close_is_bounded_and_releases_lease(tmp_path):
    """上游关闭永久等待时，五秒屏蔽清理仍必须结束并归还会话。"""
    class SlowStream:
        """模拟可取消读取但关闭极慢的模型连接。"""
        def __aiter__(self):
            """返回唯一连接迭代器。"""
            return self
        async def __anext__(self):
            """使模型连接保持打开直到断连取消。"""
            waiting.set()
            await asyncio.Event().wait()
        async def aclose(self):
            """关闭永久等待，记录 finally 证明有界取消回收。"""
            try:
                await asyncio.Event().wait()
            finally:
                closed.set()
    class SlowModel(BlockedModel):
        """沿用真实意图与决策，只替换最终连接。"""
        def astream(self, messages, **kwargs):
            """返回必须显式关闭的连接。"""
            return SlowStream()
    waiting, closed = asyncio.Event(), asyncio.Event()
    async with workflow_app(tmp_path, model=SlowModel()) as app:
        service = app.state.chat_service
        response = ManagedChatResponse(service, await service.prepare('1', '我的订单'))
        disconnect = asyncio.Event()
        async def send(message):
            """发送正常，单独验证断连和慢关闭。"""
            pass
        task = asyncio.create_task(call_response(response, send, disconnect))
        await asyncio.wait_for(waiting.wait(), 3)
        disconnect.set()
        await asyncio.wait_for(task, 7)
        service.locks.acquire('1').release()
        await asyncio.wait_for(closed.wait(), 1)
        assert not service._tasks
