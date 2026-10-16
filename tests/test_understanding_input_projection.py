"""理解视图保留订单来源，不让历史FAQ正文耗尽唯一订单上下文。"""
import json
from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.agent.controls import estimate_call_input
from app.core.errors import ServiceError
from app.workflow import nodes
from app.workflow.entities import trusted_order_ids
from app.workflow.state import new_turn_state
from tests.test_query_understanding import understanding
from tests.workflow_fakes import workflow_call, workflow_runtime


def large_history(*orders):
    """完整成功物流后接含巨大FAQ的完整退款资格轮次；不依赖真实服务。"""
    messages = [HumanMessage('查物流', id='original-user')]
    for order in orders:
        messages += [workflow_call('query_logistics', {'order_id': order}, 'log-' + order),
            ToolMessage(json.dumps({'order_id': order, 'mock': True}), tool_call_id='log-' + order)]
    messages += [AIMessage('已查询模拟物流。', id='original-final'), HumanMessage('这个能退吗', id='refund-user')]
    messages += [workflow_call('query_order', {'order_id': orders[0]}, 'order-read'),
        ToolMessage(json.dumps({'order_id': orders[0], 'mock': True}), tool_call_id='order-read'),
        workflow_call('query_faq', {'keyword': '能退吗'}, 'large-faq'),
        ToolMessage(json.dumps({'matches': [{'answer': '政策' * 2000}]}, ensure_ascii=False), tool_call_id='large-faq'),
        AIMessage('可按政策申请，需核验商品完好。', id='refund-final')]
    return messages


async def test_huge_faq_cannot_remove_trusted_order_from_understanding_input():
    history = large_history('1001')
    original = [m.model_dump() for m in history]
    service, model = understanding('订单1001的包裹大概什么时候到')
    result = await service.resolve('那大概什么时候到', history)
    actual = model.intent_inputs[0]
    assert result.query == '订单1001的包裹大概什么时候到'
    assert trusted_order_ids(actual[1:-1]) == {'1001'}
    assert [m.tool_calls[0]['name'] for m in actual if isinstance(m, AIMessage) and m.tool_calls] == ['query_logistics', 'query_order']
    assert [m.tool_call_id for m in actual if isinstance(m, ToolMessage)] == ['log-1001', 'order-read']
    assert [m.content for m in actual if isinstance(m, HumanMessage)] == ['查物流', '这个能退吗', '那大概什么时候到']
    assert [m.model_dump() for m in history] == original and estimate_call_input(actual, []) <= 8000


async def test_node_reservation_matches_actual_projected_input(monkeypatch):
    history = large_history('1001')
    service, model = understanding('订单1001的包裹大概什么时候到')
    ctx = workflow_runtime()
    ctx.understanding = service
    state = new_turn_state(conversation_id='1', user_message_id=353,
        raw_question='那大概什么时候到', category=None,
        messages=[*history, HumanMessage('那大概什么时候到')])
    reserved = []
    reserve = nodes.reserve_call
    def capture(messages, *args, **kwargs):
        reserved.append(messages)
        return reserve(messages, *args, **kwargs)
    monkeypatch.setattr(nodes, 'reserve_call', capture)
    update = await nodes.resolve_reference(state, SimpleNamespace(context=ctx, stream_writer=lambda event: None))
    assert update['resolved_question'] == '订单1001的包裹大概什么时候到'
    assert len(reserved) == 1 and reserved[0] == model.intent_inputs[0]
    assert trusted_order_ids(reserved[0][1:-1]) == {'1001'}


async def test_latest_multiple_orders_remain_ambiguous_after_projection():
    history = large_history('1001', '1002')
    # 保持最新完整轮次同时有两单，不能将早前列表顺序当作用户选单。
    history[-1:-1] = [workflow_call('query_order', {'order_id': '1002'}, 'second-order'),
        ToolMessage('{"order_id":"1002","mock":true}', tool_call_id='second-order')]
    service, model = understanding('订单1001的包裹大概什么时候到')
    with pytest.raises(ServiceError):
        await service.resolve('那大概什么时候到', history)
    assert trusted_order_ids(model.intent_inputs[0][1:-1]) == {'1001', '1002'}


@pytest.mark.parametrize('kind', ['incomplete', 'orphan', 'error'])
async def test_projection_cannot_create_order_fact_from_invalid_sources(kind):
    history = large_history('1001')
    if kind == 'incomplete':
        history = history[4:-1]
    elif kind == 'orphan':
        history = [ToolMessage('{"order_id":"1001"}', tool_call_id='orphan')]
    else:
        history = [HumanMessage('查物流'), workflow_call('query_logistics', {'order_id': '1001'}, 'failed'),
            ToolMessage('{"order_id":"1001","error":{"code":"not_found"}}', tool_call_id='failed'),
            AIMessage('未找到订单。')]
    service, model = understanding('订单1001的包裹大概什么时候到')
    with pytest.raises(ServiceError):
        await service.resolve('那大概什么时候到', history)
    assert not trusted_order_ids(model.intent_inputs[0][1:-1])
    if kind == 'error':
        assert json.loads(next(m.content for m in model.intent_inputs[0] if isinstance(m, ToolMessage)))['error']['code'] == 'not_found'
