"""真实 HTTP、官方 SQLite 根许可；仅替换 MySQL 边界。"""
from contextlib import asynccontextmanager
from dataclasses import replace
from uuid import uuid4

import httpx
import pytest
from langchain_core.messages import AIMessage, HumanMessage

from app.orders.demo import DemoOrderProvider
from app.workflow.after_sales import make_refund_offer
from app.workflow.persistence import checkpoint_config
from tests.test_order_resume_lifecycle import OwnerStore
from tests.test_workflow_api import workflow_app


class Pending:
    """外部 SQL 边界保存草稿，真实服务负责所有权限判断。"""
    def __init__(self):
        """初始化尚无申请的边界。"""
        self.calls = []

    async def create_pending(self, draft, reason):
        """返回可展示的待审核收据。"""
        from app.refunds.types import RefundReceipt
        self.calls.append((draft, reason))
        return RefundReceipt(request_no='R' + 'a' * 64, status='待审核', order_id=draft.order_id,
            amount_cents=draft.amount_cents, currency=draft.currency)


@asynccontextmanager
async def offered(tmp_path, **patch):
    """按真实生产格式持久化完整根，隔离外部模型与 MySQL。"""
    store, pending = OwnerStore(), Pending()
    async with workflow_app(tmp_path, store=store) as app:
        await store.append_message('1', HumanMessage('订单1001退货'))
        await store.append_message('1', AIMessage('需审核[1]'))
        order = await DemoOrderProvider().get_order(user_id='demo-user', order_id='1001')
        state = {'state_version': 2, 'conversation_id': '1', 'user_message_id': '1',
            'raw_question': '订单1001退货', 'final_message_id': '2', 'final_answer': '需审核[1]',
            'intent': '退款退货', 'route': 'after_sales', 'turn_status': 'completed',
            'order_snapshot': order.model_dump(mode='json'), 'quality': {'useful': True},
            'reply_mode': 'answer', 'refund_decision': 'needs_review', 'decision_reason': '完好条件需审核',
            'evidence_payload': {'matches': [{'n': 1, 'answer': '政策完整原文', 'section_path': '退货政策'}]},
            'suggested_actions': [], 'citations': []}
        state['refund_offer'] = make_refund_offer(state)
        body = {'assistant_message_id': '2', 'offer_id': state['refund_offer']['offer_id'], 'reason': 'quality'}
        state.update(patch)
        config = await app.state.chat_service.graph.aupdate_state(checkpoint_config('1'), state, as_node='log_response')
        body['checkpoint_id'] = config['configurable']['checkpoint_id']
        service = getattr(app.state, 'refund_action_service', None)
        assert service is not None, 'refund submission service is missing'
        service.refunds = pending
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://localhost') as client:
            yield app, client, store, pending, body


async def submit(client, body, cid='1', **kwargs):
    """走同源写请求防护及严格四字段解析。"""
    return await client.post(f'/api/conversations/{cid}/actions/refund', json=body, **kwargs)


async def test_valid_server_draft_and_original_root_survive_later_turn(tmp_path):
    """旧答复仍有效，原因不覆盖模型判断，金额/政策完整取自原根。"""
    async with offered(tmp_path) as (app, client, _, pending, body):
        await app.state.chat_service.graph.aupdate_state(checkpoint_config('1'), {'turn_status': 'running', 'refund_offer': None})
        result = await submit(client, body)
        assert result.status_code == 200, result.text
        assert result.json() == {'request_no': 'R' + 'a' * 64, 'status': '待审核',
            'order_id': '1001', 'amount_cents': 19900, 'currency': 'CNY'}
        draft, reason = pending.calls[0]
        assert draft.user_id == 'demo-user' and reason == 'quality'
        assert draft.decision_snapshot == {'refund_decision': 'needs_review', 'decision_reason': '完好条件需审核'}
        assert draft.policy_snapshot['matches'][0]['answer'] == '政策完整原文'


@pytest.mark.parametrize('patch', [{'turn_status': 'running'}, {'reply_mode': 'clarification'},
    {'intent': '售后'}, {'refund_offer': None}, {'refund_decision': 'ineligible'},
    {'quality': {'useful': False}}, {'state_version': 1}, {'conversation_id': '2'}])
async def test_illegal_permission_never_writes(tmp_path, patch):
    """拒绝不完整、维修、澄清或无许可原根，不以正文猜测申请权。"""
    async with offered(tmp_path, **patch) as (_, client, _, pending, body):
        assert (await submit(client, body)).status_code in (404, 422)
        assert pending.calls == []


@pytest.mark.parametrize('fault', ['cross', 'child', 'offer', 'owner', 'sql', 'raw'])
async def test_identity_and_raw_durability_guard(tmp_path, fault):
    """跨会话、子图、伪offer、SQL不匹配及raw未完成均不能写入。"""
    async with offered(tmp_path) as (app, client, store, pending, body):
        cid = '1'
        if fault == 'cross':
            cid = '2'
        elif fault == 'offer':
            body['offer_id'] = str(uuid4())
        elif fault == 'owner':
            async def wrong_owner(_):
                """模拟 SQL owner 已不同于订单快照。"""
                return 'someone-else'
            store.get_user_id = wrong_owner
        elif fault == 'sql':
            store.rows['1'][1] = replace(store.rows['1'][1], content='非原答复')
        elif fault == 'child':
            # 官方 saver 子命名空间即使同样值也不是根许可。
            service = app.state.chat_service
            root = await service.checkpointer.aget_tuple(checkpoint_config('1', checkpoint_id=body['checkpoint_id']))
            cfg = {'configurable': {'thread_id': '1', 'checkpoint_ns': 'agent:child'}}
            await service.checkpointer.aput(cfg, root.checkpoint, root.metadata, {})
            body['checkpoint_id'] = root.checkpoint['id']
            async def child_state(_):
                """让图读边界暴露错误命名空间，服务必须拒绝。"""
                snap = await original(checkpoint_config('1', checkpoint_id=body['checkpoint_id']))
                return snap._replace(config={'configurable': cfg['configurable'] | {'checkpoint_id': body['checkpoint_id']}})
            original = service.graph.aget_state
            service.graph.aget_state = child_state
        elif fault == 'raw':
            service = app.state.chat_service
            # 单独保持图投影completed，raw检查才能独立决定拒绝；缺guard会错误写入。
            projected = await service.graph.aget_state(checkpoint_config('1', checkpoint_id=body['checkpoint_id']))
            async def projected_state(_):
                """提供已完成图投影，与实际raw状态刻意不一致。"""
                return projected
            service.graph.aget_state = projected_state
            saver = service.checkpointer
            original = saver.aget_tuple
            async def raw_running(config):
                """复现已投影completed但实际根仍running的存储返回。"""
                item = await original(config)
                cp = dict(item.checkpoint)
                cp['channel_values'] = item.checkpoint['channel_values'] | {'turn_status': 'running'}
                return item._replace(checkpoint=cp)
            saver.aget_tuple = raw_running
        assert (await submit(client, body, cid)).status_code in (404, 422)
        if fault != 'offer':
            locators = {k: body[k] for k in ('assistant_message_id', 'checkpoint_id')}
            assert (await client.get(f'/api/conversations/{cid}/refund-offer', params=locators)).status_code in (404, 422)
        assert pending.calls == []


@pytest.mark.parametrize('patch', [{'amount_cents': 1}, {'status': '已退款'}, {'reason': 'bad'}, {'reason': None}])
async def test_http_contract_rejects_forgery(tmp_path, patch):
    """HTTP 解析错误在任何仓储写入前返回固定安全错误。"""
    async with offered(tmp_path) as (_, client, _, pending, body):
        result = await submit(client, body | patch)
        assert result.status_code == 422 and result.json()['code'] == 'invalid_request'
        assert pending.calls == []


async def test_http_origin_busy_and_error_sanitization(tmp_path):
    """同源与占用保护沿用聊天动作约束，外部异常不泄露。"""
    async with offered(tmp_path) as (app, client, _, pending, body):
        assert (await submit(client, body, headers={'Origin': 'http://evil.invalid'})).status_code == 403
        lease = app.state.chat_service.locks.acquire('1')
        try:
            assert (await submit(client, body)).status_code == 409
            locators = {k: body[k] for k in ('assistant_message_id', 'checkpoint_id')}
            assert (await client.get('/api/conversations/1/refund-offer', params=locators)).status_code == 409
        finally:
            lease.release()
        async def fail(*args):
            """模拟 SQL 故障。"""
            raise RuntimeError('SECRET')
        pending.create_pending = fail
        result = await submit(client, body)
        assert result.status_code == 503 and 'SECRET' not in result.text
        assert result.json()['code'] == 'service_unavailable'
        assert pending.calls == []


async def test_refund_audit_only_after_commit_and_without_snapshots(tmp_path):
    """控制台成功审计必须晚于SQL提交，且不包含owner/原因/证据正文。"""
    import io
    import json
    import logging
    from app.workflow.logging import logger, WorkflowFormatter
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(WorkflowFormatter())
    logger.addHandler(handler)
    try:
        async with offered(tmp_path) as (_, client, _, pending, body):
            original = pending.create_pending
            async def commit(draft, reason):
                """边界返回之前不准出现成功审计。"""
                assert 'workflow_refund' not in stream.getvalue()
                return await original(draft, reason)
            pending.create_pending = commit
            assert (await submit(client, body)).status_code == 200
        records = [json.loads(line) for line in stream.getvalue().splitlines()]
        refund = next(r for r in records if r.get('event') == 'workflow_refund')
        assert refund == {'event': 'workflow_refund', 'phase': 'result', 'outcome': 'success',
            'action': 'submit_refund', 'conversation_id': '1', 'user_message_id': '1',
            'assistant_message_id': '2', 'request_no': 'R' + 'a' * 64}
        assert '政策完整原文' not in stream.getvalue() and 'demo-user' not in stream.getvalue()
    finally:
        logger.removeHandler(handler)


async def test_refresh_get_revalidates_original_offer_without_writing(tmp_path):
    """刷新仅凭结构定位重建原完成入口，无需HTTP JSON且不得创建申请。"""
    import asyncio
    from types import SimpleNamespace
    async with offered(tmp_path) as (app, client, _, pending, body):
        service = app.state.chat_service
        root = await service.graph.aget_state(checkpoint_config('1', checkpoint_id=body['checkpoint_id']))
        queue = asyncio.Queue()
        await service._completed_events(SimpleNamespace(conversation_id='1'), root.values, body['checkpoint_id'], queue)
        expected = (await queue.get()).data
        await service.graph.aupdate_state(checkpoint_config('1'), {'turn_status': 'running', 'refund_offer': None})
        before = await service.graph.aget_state(checkpoint_config('1'))
        locators = {k: body[k] for k in ('assistant_message_id', 'checkpoint_id')}
        response = await client.get('/api/conversations/1/refund-offer', params=locators)
        assert response.status_code == 200, response.text
        assert response.json() == expected
        assert set(response.json()) == {'assistant_message_id', 'checkpoint_id', 'offer_id', 'order',
            'refund_decision', 'decision_reason', 'reasons'}
        assert 'user_id' not in response.json()['order'] and 'policy_snapshot' not in response.json()
        assert pending.calls == []
        assert (await service.graph.aget_state(checkpoint_config('1'))).config == before.config


@pytest.mark.parametrize('params', [{'assistant_message_id': '2'}, {'checkpoint_id': 'bad'},
    {'assistant_message_id': '02', 'checkpoint_id': str(uuid4())},
    {'assistant_message_id': '2', 'checkpoint_id': str(uuid4()), 'offer_id': str(uuid4())},
    [('assistant_message_id', '2'), ('assistant_message_id', '3'), ('checkpoint_id', str(uuid4()))]])
async def test_refresh_get_rejects_bad_or_extra_locators(tmp_path, params):
    """只读请求仍严格禁止客户端offer/owner等自报内容。"""
    async with offered(tmp_path) as (_, client, _, pending, _):
        response = await client.get('/api/conversations/1/refund-offer', params=params)
        assert response.status_code == 422 and response.json()['code'] == 'invalid_request'
        assert pending.calls == []


async def test_refresh_rejects_malformed_server_offer_identity(tmp_path):
    """坏历史数据不能投影出非服务器UUID的表单身份。"""
    async with offered(tmp_path) as (app, client, _, pending, body):
        graph = app.state.chat_service.graph
        root = await graph.aget_state(checkpoint_config('1'))
        cfg = await graph.aupdate_state(checkpoint_config('1'),
            {'refund_offer': root.values['refund_offer'] | {'offer_id': 'corrupt'}}, as_node='log_response')
        result = await client.get('/api/conversations/1/refund-offer', params={
            'assistant_message_id': '2', 'checkpoint_id': cfg['configurable']['checkpoint_id']})
        assert result.status_code == 422 and pending.calls == []


@pytest.mark.parametrize('fault', ['cross', 'owner', 'sql', 'no_offer', 'incomplete', 'clarification', 'repair'])
async def test_refresh_get_uses_same_original_permission_guard(tmp_path, fault):
    """刷新不能凭浏览器结构定位把无权限原回复转换成可提交表单。"""
    patch = {'no_offer': {'refund_offer': None}, 'incomplete': {'turn_status': 'running'},
        'clarification': {'reply_mode': 'clarification'}, 'repair': {'intent': '售后'}}.get(fault, {})
    async with offered(tmp_path, **patch) as (_, client, store, pending, body):
        cid = '2' if fault == 'cross' else '1'
        if fault == 'owner':
            async def changed(_):
                """模拟SQL可信身份变化。"""
                return 'other-owner'
            store.get_user_id = changed
        elif fault == 'sql':
            store.rows['1'][1] = replace(store.rows['1'][1], content='已更改')
        locators = {k: body[k] for k in ('assistant_message_id', 'checkpoint_id')}
        response = await client.get(f'/api/conversations/{cid}/refund-offer', params=locators)
        assert response.status_code == (404 if fault == 'cross' else 422)
        assert pending.calls == []
