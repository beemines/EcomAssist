"""公开选单生命周期：真实 HTTP、图与磁盘 saver，仅替换外部模型/SQL。"""
import json
from contextlib import asynccontextmanager

import httpx
import pytest
from langchain_core.messages import AIMessage

from app.main import create_app
from app.retrieval.multi import WorkflowRetrieval
from app.workflow.persistence import checkpoint_config
from tests.fakes import FAQStub, decode_sse, fake_settings
from tests.test_workflow_api import Store, intent
from tests.workflow_fakes import ScriptedWorkflowModel


class OwnerStore(Store):
    """模拟已存在的 SQL owner 权威，不接受 HTTP 自报身份。"""
    async def get_user_id(self, conversation_id):
        """按已存在会话返回演示身份。"""
        await self.require_open(conversation_id)
        return 'demo-user'


class Retrieve:
    """只替换外部知识检索，保留图闸与原轮流水。"""
    async def retrieve(self, *, question, queries, category):
        """空证据令真实图完成固定拒答，不调用最终收费模型。"""
        return WorkflowRetrieval({'found': False, 'matches': [],
            'retrieval': {'strategy': 'hybrid_rerank', 'match_count': 0}}, {})


def reply(data):
    """构造严格原始结构化模型响应。"""
    return AIMessage(json.dumps(data, ensure_ascii=False), response_metadata={'finish_reason': 'stop'})


@asynccontextmanager
async def app_context(tmp_path, *, store=None, model=None, **settings):
    """生产接线启动真实持久化服务，重启复用同一临时文件。"""
    store = store or OwnerStore()
    app = create_app(fake_settings(workflow_checkpoint_path=tmp_path / 'resume.sqlite', **settings),
        model=model or ScriptedWorkflowModel(intent_replies=[reply({'query': '这个能退吗？'}),
            intent('退款退货'), reply({'queries': ['这个能退吗？', 'MH-LP200退货政策']})]),
        repository=store, faq_repository=FAQStub(), quality_repository=store)
    async with app.router.lifespan_context(app):
        app.state.chat_service.workflow_retriever = Retrieve()
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://localhost') as client:
            yield app, client


async def pause(client):
    """完整消费普通 HTTP 后取得可恢复卡片。"""
    response = await client.post('/api/chat', json={'conversation_id': '1', 'message': '这个能退吗？'})
    frames = decode_sse(response.text)
    assert frames[-1][0] == 'paused', frames
    return next(data for name, data in frames if name == 'order_selection'), frames


def selection(card, order='1001'):
    """仅传公开四字段，金额与身份保持服务器权威。"""
    return {key: card[key] for key in ('turn_id', 'selection_id', 'checkpoint_id')} | {'order_id': order}


async def test_paused_sse_closes_and_releases_lock(tmp_path):
    """未完成图必须作为已持久化暂停结束HTTP，不能错误或假done。"""
    async with app_context(tmp_path) as (app, client):
        card, frames = await pause(client)
        assert not {'done', 'delta'} & {name for name, _ in frames}
        assert 'final_message_id' not in frames[-1][1]
        assert all('user_id' not in item for item in card['cards'])
        assert (await client.get('/api/conversations/1/pending-order')).json() == {'pending': card}
        app.state.chat_service.locks.acquire('1').release()


async def test_resume_does_not_append_user_or_reclassify(tmp_path):
    """恢复沿用原消息及理解结果；重复完成选单只重放保存结果。"""
    store = OwnerStore()
    async with app_context(tmp_path, store=store) as (app, client):
        card, _ = await pause(client)
        model = app.state.chat_service.model
        before = model.intents
        response = await client.post('/api/conversations/1/actions/select-order', json=selection(card))
        frames = decode_sse(response.text)
        assert frames[-1][0] == 'done', response.text
        assert model.intents == before + 1  # 仅扩写；理解与分类不重跑
        assert sum(row.role == 'user' for row in store.rows['1']) == 1
        saved = await app.state.chat_service.graph.aget_state(checkpoint_config('1'))
        assert saved.values['order_selection']['pause_checkpoint_id'] == card['checkpoint_id']
        repeated = await client.post('/api/conversations/1/actions/select-order', json=selection(card))
        assert decode_sse(repeated.text)[-1] == frames[-1]
        assert model.intents == before + 1
        changed = await client.post('/api/conversations/1/actions/select-order', json=selection(card, '1002'))
        assert changed.status_code == 409


async def test_restart_reads_pending_and_resumes_current_root(tmp_path):
    """关闭重开实际SQLite仍保留暂停身份，恢复不能依赖进程内对象。"""
    store = OwnerStore()
    async with app_context(tmp_path, store=store) as (_, client):
        card, _ = await pause(client)
    model = ScriptedWorkflowModel(intent_replies=[reply({'queries': ['这个能退吗？', 'MH-LP200退货政策']})])
    async with app_context(tmp_path, store=store, model=model) as (_, client):
        assert (await client.get('/api/conversations/1/pending-order')).json() == {'pending': card}
        resumed = await client.post('/api/conversations/1/actions/select-order', json=selection(card))
        assert decode_sse(resumed.text)[-1][0] == 'done'
        assert model.intents == 1


async def test_new_message_supersedes_old_card(tmp_path):
    """新轮普通输入从START执行，旧卡或旧完成回执均不可重新执行。"""
    async with app_context(tmp_path) as (app, client):
        card, _ = await pause(client)
        result = await client.post('/api/chat', json={'conversation_id': '1', 'message': '你好'})
        assert decode_sse(result.text)[-1][0] == 'done'
        root = await app.state.chat_service.graph.aget_state(checkpoint_config('1'))
        assert root.values['supersedes_turn_id'] == card['turn_id']
        assert (await client.get('/api/conversations/1/pending-order')).json() == {'pending': None}
        stale = await client.post('/api/conversations/1/actions/select-order', json=selection(card))
        assert stale.status_code == 409


async def test_resume_budget_uses_saved_active_time(tmp_path):
    """暂停前消耗持久化，重新准备后的deadline只剩原轮余量。"""
    import time
    from app.schemas.order_actions import OrderSelectionRequest
    async with app_context(tmp_path) as (app, client):
        card, _ = await pause(client)
        service = app.state.chat_service
        root = await service.graph.aget_state(checkpoint_config('1'))
        elapsed = root.values['active_elapsed_seconds']
        assert elapsed > 0
        prepared = await service.prepare_resume('1', OrderSelectionRequest(**selection(card)))
        try:
            assert prepared.runtime.active_elapsed_baseline == elapsed
            assert prepared.deadline - time.monotonic() <= service.settings.chat_timeout_seconds - elapsed
        finally:
            service.release(prepared)
        service.settings.chat_timeout_seconds = elapsed / 2
        expired = await client.post('/api/conversations/1/actions/select-order', json=selection(card))
        assert expired.status_code == 504
        service.locks.acquire('1').release()


async def test_failed_stage_usage_is_internal_and_nonzero(tmp_path):
    """无效付费阶段不能在终态审计清零，也不能原样泄漏内部usage事件。"""
    model = ScriptedWorkflowModel(intent_replies=[AIMessage('{"bad":"SECRET"}',
        response_metadata={'finish_reason': 'stop'},
        usage_metadata={'input_tokens': 12, 'output_tokens': 8, 'total_tokens': 20})])
    async with app_context(tmp_path, model=model) as (app, _):
        service = app.state.chat_service
        prepared = await service.prepare('1', '这个能退吗？')
        try:
            frames = [event async for event in service.stream(prepared)]
            assert frames[-1].event == 'error'
            assert not any(event.event == 'usage' for event in frames)
            assert prepared.audit['usage']['actual'] == 20
            assert prepared.audit['stage_usage']['understanding']['actual'] == 20
        finally:
            service.release(prepared)


async def test_concurrent_click_executes_one_resume(tmp_path):
    """恢复活动段占用同一会话，第二次真实HTTP点击必须409。"""
    import asyncio
    from app.workflow.expansion import QueryExpander
    class BlockingExpand(QueryExpander):
        """外部模型门禁保留真实扩写协议及图执行。"""
        async def expand(self, question, order, **kwargs):
            """停在扩写边界以制造真实HTTP竞争窗口。"""
            entered.set()
            await gate.wait()
            return await super().expand(question, order, **kwargs)
    entered, gate = asyncio.Event(), asyncio.Event()
    from unittest.mock import patch
    async with app_context(tmp_path) as (app, client):
        card, _ = await pause(client)
        with patch('app.workflow.service.QueryExpander', BlockingExpand):
            first = asyncio.create_task(client.post('/api/conversations/1/actions/select-order', json=selection(card)))
            await asyncio.wait_for(entered.wait(), 3)
            second = await client.post('/api/conversations/1/actions/select-order', json=selection(card))
            assert second.status_code == 409
            gate.set()
            assert decode_sse((await first).text)[-1][0] == 'done'
        assert sum(row.role == 'user' for row in app.state.repository.rows['1']) == 1


@pytest.mark.parametrize('change', ['turn', 'selection', 'root', 'conversation'])
async def test_foreign_or_stale_identity_is_rejected(tmp_path, change):
    """任一身份错配都不可从历史根分叉或跨会话恢复。"""
    from uuid import uuid4
    async with app_context(tmp_path) as (app, client):
        card, _ = await pause(client)
        body = selection(card)
        path = '/api/conversations/1/actions/select-order'
        if change == 'turn':
            body['turn_id'] = '2'
        elif change == 'selection':
            body['selection_id'] = str(uuid4())
        elif change == 'root':
            body['checkpoint_id'] = str(uuid4())
        else:
            app.state.repository.users['2'] = 'demo-user'
            path = '/api/conversations/2/actions/select-order'
        response = await client.post(path, json=body)
        assert response.status_code == 409
        assert (await client.get('/api/conversations/1/pending-order')).json()['pending'] == card


@pytest.mark.parametrize('fail_checkpoint', [False, True])
async def test_refund_offer_only_after_sql_and_completed_root(tmp_path, fail_checkpoint):
    """SQL写入后saver故障不能发许可或done；正常许可只展示订单摘要。"""
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    from langchain_core.messages import AIMessageChunk
    from app.core.sufficiency import QualityDecision
    from tests.test_evidence import payload
    class Saver(AsyncSqliteSaver):
        """仅在原始SQL答复之后故障，保留实际SQLite读写行为。"""
        async def aput(self, config, checkpoint, metadata, new_versions):
            """拒绝最终根写入，验证许可不能早于持久化。"""
            if fail_checkpoint and checkpoint['channel_values'].get('turn_status') == 'completed':
                raise RuntimeError('SECRET saver failure')
            return await super().aput(config, checkpoint, metadata, new_versions)
    class Policy:
        """达标政策边界，真正Agent检查引用并冻结许可。"""
        async def retrieve(self, **kwargs):
            """提供实际证据协议，避免绕过闸。"""
            return WorkflowRetrieval(payload(('七天内退货需完好，特殊商品需审核。',)), {})
    class Assessment:
        """替换外部充分性模型，不替换图判断与Agent。"""
        async def check(self, question, evidence, *, order_context=None):
            """返回有证据覆盖判断。"""
            return QualityDecision(useful=True, reason='覆盖', response_kind='knowledge', source=None)
    model = ScriptedWorkflowModel([reply({'reply_mode': 'answer', 'suggested_actions': [],
        'refund_decision': 'needs_review', 'decision_reason': '商品状态需审核'})],
        final_chunks=[AIMessageChunk('演示订单可按政策提交待审核申请[1]。'),
            AIMessageChunk('', response_metadata={'finish_reason': 'stop'})],
        intent_replies=[reply({'query': '这个能退吗？'}), intent('退款退货'),
            reply({'queries': ['这个能退吗？', 'MH-LP200退货政策']})])
    store = OwnerStore()
    async with Saver.from_conn_string(str(tmp_path / 'final.sqlite')) as saver:
        app = create_app(fake_settings(workflow_checkpoint_path=tmp_path / 'unused.sqlite'), model=model,
            repository=store, faq_repository=FAQStub(), quality_repository=store, checkpointer=saver,
            sufficiency_service=Assessment(), workflow_retriever=Policy())
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://localhost') as client:
                card, _ = await pause(client)
                response = await client.post('/api/conversations/1/actions/select-order', json=selection(card))
                frames = decode_sse(response.text)
                assert store.commits == 1
                if fail_checkpoint:
                    assert frames[-1][0] == 'error'
                    assert not {'done', 'refund_offer'} & {name for name, _ in frames}
                    assert 'SECRET' not in response.text
                    assert (await client.post('/api/conversations/1/actions/select-order', json=selection(card))).status_code == 409
                else:
                    assert frames[-1][0] == 'done'
                    offer = next(data for name, data in frames if name == 'refund_offer')
                    root = await app.state.chat_service.graph.aget_state(checkpoint_config('1'))
                    assert offer['checkpoint_id'] == root.config['configurable']['checkpoint_id']
                    assert offer['assistant_message_id'] == root.values['final_message_id']
                    assert offer['order']['amount_cents'] == 19900
                    assert 'user_id' not in offer['order'] and 'policy_snapshot' not in offer
                    assert len(offer['reasons']) == 6
                    repeated = await client.post('/api/conversations/1/actions/select-order', json=selection(card))
                    assert next(data for name, data in decode_sse(repeated.text) if name == 'refund_offer') == offer


async def test_resume_disconnect_after_partial_delta_invalidates_card(tmp_path):
    """恢复后部分正文断连必须关闭模型/释放锁，原卡不能盲目重放图。"""
    import asyncio
    from langchain_core.messages import AIMessageChunk
    from app.api.streaming import ManagedChatResponse
    from app.core.sufficiency import QualityDecision
    from app.schemas.order_actions import OrderSelectionRequest
    from tests.test_evidence import payload
    from tests.test_stream_lifecycle import call_response
    class Model(ScriptedWorkflowModel):
        """仅最终付费流首片后阻塞，真实Agent继续负责控制协议。"""
        async def astream(self, messages, **kwargs):
            """取消必须进入finally，不能保存最终答案。"""
            try:
                yield AIMessageChunk('模拟申请需审核[1]。')
                waiting.set()
                await asyncio.Event().wait()
            finally:
                self.closed = True
    class Policy:
        """只替换知识外部边界。"""
        async def retrieve(self, **kwargs):
            """提供真实证据。"""
            return WorkflowRetrieval(payload(('退货需审核。',)), {})
    class Assessment:
        """只替换内容充分性外部模型。"""
        async def check(self, question, evidence, *, order_context=None):
            """允许真实Agent处理已覆盖证据。"""
            return QualityDecision(useful=True, reason='覆盖', response_kind='knowledge', source=None)
    waiting, disconnected = asyncio.Event(), asyncio.Event()
    model = Model([reply({'reply_mode': 'answer', 'suggested_actions': [],
        'refund_decision': 'needs_review', 'decision_reason': '需审核'})], intent_replies=[
        reply({'query': '这个能退吗？'}), intent('退款退货'), reply({'queries': ['这个能退吗？', 'MH-LP200退货政策']})])
    async with app_context(tmp_path, model=model) as (app, client):
        card, _ = await pause(client)
        service = app.state.chat_service
        service.workflow_retriever, service.sufficiency_service = Policy(), Assessment()
        prepared = await service.prepare_resume('1', OrderSelectionRequest(**selection(card)))
        sent = []
        async def send(message):
            """记录实际ASGI正文以证明断连前已有delta。"""
            sent.append(message)
        response = ManagedChatResponse(service, prepared)
        task = asyncio.create_task(call_response(response, send, disconnected))
        await asyncio.wait_for(waiting.wait(), 3)
        await asyncio.sleep(.02)
        assert any(b'event: delta' in item.get('body', b'') for item in sent)
        disconnected.set()
        await asyncio.wait_for(task, 3)
        assert model.closed and not service._tasks and app.state.repository.commits == 0
        service.locks.acquire('1').release()
        repeat = await client.post('/api/conversations/1/actions/select-order', json=selection(card))
        assert repeat.status_code == 409
        assert (await client.get('/api/conversations/1/pending-order')).json() == {'pending': None}


async def test_resume_preflight_owner_lookup_respects_remaining_budget(tmp_path):
    """恢复SQL owner读取也属于原轮活动段，超时必须在SSE前504并释放锁。"""
    import asyncio
    async with app_context(tmp_path) as (app, client):
        card, _ = await pause(client)
        service = app.state.chat_service
        state = (await service.graph.aget_state(checkpoint_config('1'))).values
        service.settings.chat_timeout_seconds = state['active_elapsed_seconds'] + .03
        original = service.repository.get_user_id
        async def slow_owner(conversation_id):
            """只延迟SQL边界，避免真实数据库或模型等待。"""
            await asyncio.sleep(.1)
            return await original(conversation_id)
        service.repository.get_user_id = slow_owner
        response = await client.post('/api/conversations/1/actions/select-order', json=selection(card))
        assert response.status_code == 504
        assert response.json()['code'] == 'upstream_timeout'
        service.locks.acquire('1').release()


@pytest.mark.parametrize(('stage', 'schema_name'), [('understanding', '_UnderstandingOutput'),
    ('classification', '_IntentOutput'), ('expansion', '_ExpansionOutput'), ('sufficiency', '_Assessment')])
async def test_cancelled_model_stage_retains_attempted_usage(tmp_path, stage, schema_name):
    """取消外层astream不能丢失已尝试收费阶段的终态审计，也不能污染另一个Runtime。"""
    import asyncio
    from app.schemas.order_actions import OrderSelectionRequest
    from tests.test_evidence import payload
    entered = asyncio.Event()
    class Model(ScriptedWorkflowModel):
        """在指定真实结构化模型调用处阻塞，之前节点照常执行。"""
        def with_structured_output(self, schema, **kwargs):
            """只替换外部调用等待，不替换服务或节点。"""
            delegate = super().with_structured_output(schema, **kwargs)
            class Call:
                async def ainvoke(self, messages, **kwargs):
                    """被取消阶段已经进入真实usage预记账之后。"""
                    if schema.__name__ == schema_name:
                        entered.set()
                        await asyncio.Event().wait()
                    return await delegate.ainvoke(messages, **kwargs)
            return Call()
    class Policy:
        """充分性取消样例提供真实可达标证据。"""
        async def retrieve(self, **kwargs):
            """避免低分闸提前结束。"""
            return WorkflowRetrieval(payload(('七天内需审核退货。',)), {})
    model = Model(intent_replies=[reply({'query': '这个能退吗？'}), intent('退款退货'),
        reply({'queries': ['这个能退吗？', 'MH-LP200退货政策']})])
    async with app_context(tmp_path, model=model) as (app, client):
        service = app.state.chat_service
        if stage in ('expansion', 'sufficiency'):
            card, _ = await pause(client)
            service.workflow_retriever = Policy()
            prepared = await service.prepare_resume('1', OrderSelectionRequest(**selection(card)))
        else:
            prepared = await service.prepare('1', '这个能退吗？')
        async def consume():
            """按真实断连路径取消外层消费者并归还租约。"""
            try:
                async for event in service.stream(prepared):
                    pass
            finally:
                service.release(prepared)
        task = asyncio.create_task(consume())
        await asyncio.wait_for(entered.wait(), 3)
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        assert prepared.audit['stage_usage'][stage]['estimated_calls'] == 1
        assert prepared.audit['stage_usage'][stage]['estimated'] > 2048
        assert not service._tasks
        service.locks.acquire('1').release()


async def test_cancelled_stage_audit_is_isolated_from_other_conversation(tmp_path):
    """A已开始后B实测20，随后A取消仍保留自己的估算而非B的实际用量。"""
    import asyncio
    entered = asyncio.Event()
    class Model(ScriptedWorkflowModel):
        """共享无状态模型边界，只阻塞A的理解请求。"""
        def with_structured_output(self, schema, **kwargs):
            """两个Runtime使用相同客户端，调用计数必须隔离。"""
            delegate = super().with_structured_output(schema, **kwargs)
            class Call:
                async def ainvoke(self, messages, **kwargs):
                    """控制A等待→B失败实测→A取消的确定顺序。"""
                    if schema.__name__ == '_UnderstandingOutput' and messages[-1].content == '这个能退吗？':
                        entered.set()
                        await asyncio.Event().wait()
                    return await delegate.ainvoke(messages, **kwargs)
            return Call()
    model = Model(intent_replies=[AIMessage('{"invalid":true}', response_metadata={'finish_reason': 'stop'},
        usage_metadata={'input_tokens': 12, 'output_tokens': 8, 'total_tokens': 20})])
    async with app_context(tmp_path, model=model) as (app, _):
        service = app.state.chat_service
        service.repository.users['2'] = 'demo-user'
        first = await service.prepare('1', '这个能退吗？')
        async def consume():
            """清理被取消的A流和租约。"""
            try:
                async for event in service.stream(first):
                    pass
            finally:
                service.release(first)
        task = asyncio.create_task(consume())
        await asyncio.wait_for(entered.wait(), 3)
        second = await service.prepare('2', '请帮我看看退货条件')
        # Isolate cancellation accounting from B's independent recovery policy.
        second.runtime.model_recovery_used = True
        try:
            frames = [event async for event in service.stream(second)]
            assert frames[-1].event == 'error'
        finally:
            service.release(second)
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        assert first.audit['stage_usage']['understanding']['actual'] == 0
        assert first.audit['stage_usage']['understanding']['estimated_calls'] == 1
        assert second.audit['stage_usage']['understanding']['actual'] == 20
        assert second.audit['stage_usage']['understanding']['estimated_calls'] == 0
        assert second.audit['usage']['actual'] == 20  # 同步接收与custom事件不能双记40
        assert not service._tasks
        service.locks.acquire('1').release()
        service.locks.acquire('2').release()


async def test_resume_sql_turn_validation_respects_saved_remaining_budget(tmp_path):
    """原轮SQL流水读取必须按保存余量取消，不能等完整新期限才返回504。"""
    import asyncio
    import time
    async with app_context(tmp_path) as (app, client):
        service = app.state.chat_service
        original_owner = service.repository.get_user_id
        async def initial_owner(conversation_id):
            """确定消费0.200秒原轮活动，保证错误的新全额期限明显长于余量。"""
            await asyncio.sleep(.2)
            return await original_owner(conversation_id)
        service.repository.get_user_id = initial_owner
        card, _ = await pause(client)
        service.repository.get_user_id = original_owner
        state = (await service.graph.aget_state(checkpoint_config('1'))).values
        assert state['active_elapsed_seconds'] >= .2
        # 已消费基线由真实预检计时持久化，不改暂停根/中断。
        service.settings.chat_timeout_seconds = state['active_elapsed_seconds'] + .03
        original = service.repository.load_messages
        entered, cancelled = asyncio.Event(), asyncio.Event()
        owner_calls = 0
        async def slow_messages(conversation_id):
            """记录SQL读取是否在原轮余量结束时被取消。"""
            entered.set()
            try:
                await asyncio.sleep(.15)
            except asyncio.CancelledError:
                cancelled.set()
                raise
            return await original(conversation_id)
        async def owner(conversation_id):
            """超时后不可再开始下一步owner查询。"""
            nonlocal owner_calls
            owner_calls += 1
            return await original_owner(conversation_id)
        service.repository.load_messages = slow_messages
        service.repository.get_user_id = owner
        started = time.monotonic()
        response = await client.post('/api/conversations/1/actions/select-order', json=selection(card))
        elapsed = time.monotonic() - started
        assert response.status_code == 504
        assert response.json()['code'] == 'upstream_timeout'
        assert entered.is_set() and cancelled.is_set()
        assert elapsed < .09, f'原轮仅余0.030秒，SQL预检却执行了{elapsed:.3f}秒'
        assert owner_calls == 0
        service.locks.acquire('1').release()
