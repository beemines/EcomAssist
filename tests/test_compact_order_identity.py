"""Compact order commands must keep the same anchor throughout native reads."""
from dataclasses import replace

import pytest
from langchain_core.messages import AIMessage
from langchain_core.tools import StructuredTool

from app.tools.catalog import ToolCatalog
from app.tools.executor import ToolExecutor
from app.tools.types import ExecutionContext, ToolContext
from app.workflow.entities import explicit_order_ids
from tests.test_workflow_agent import setup, run
from tests.tool_system_fakes import make_registration, allow_policy
from tests.workflow_fakes import workflow_call


@pytest.mark.parametrize('question', [
    '2002物流信息异常', '2002的物流到哪了', '查2002物流', '请查询2002物流状态',
    '帮我查2002物流', '1001退款', '1001退货进度',
])
def test_compact_order_topic_is_explicit_user_identity(question):
    expected = '2002' if '2002' in question else '1001'
    assert explicit_order_ids(question) == {expected}


@pytest.mark.parametrize('question', [
    '2002', '2002元退款', '2002年物流怎么样', '2026-10-19物流', '13900139000物流',
    'MH-2002物流异常', '2002型号物流异常', '我买的恒温猫窝2002一直没发货，什么时候到',
])
def test_product_numbers_dates_prices_and_phones_are_not_compact_orders(question):
    assert explicit_order_ids(question) == set()


def test_compact_current_order_cannot_be_replaced_by_an_old_order():
    from types import SimpleNamespace
    from app.core.errors import ServiceError
    from app.workflow.entities import IdentitySource, validate_snapshot_entities
    snapshot = SimpleNamespace(summaries=(), omitted_summary_seqs=())
    sources = (IdentitySource(1, None, frozenset({'1001'}), ()),)
    validate_snapshot_entities('2002物流信息异常', '2002物流信息异常', snapshot, sources)
    with pytest.raises(ServiceError):
        validate_snapshot_entities('2002物流信息异常', '订单1001物流信息异常', snapshot, sources)


def test_followup_can_resolve_to_a_proven_compact_order():
    from types import SimpleNamespace
    from app.workflow.entities import IdentitySource, validate_snapshot_entities
    snapshot = SimpleNamespace(summaries=(), omitted_summary_seqs=())
    sources = (IdentitySource(1, None, frozenset({'2002'}), ()),)
    validate_snapshot_entities('物流信息异常', '2002物流信息异常', snapshot, sources)


async def test_captured_plain_completion_after_compact_logistics_read_reaches_checked_final():
    # The user's ordinary8005 failure: MCP succeeded, then GLM stopped in prose.
    draft = AIMessage('本轮订单、物流等业务信息为模拟演示数据，仅供参考。订单2002当前状态为运输中。UNTRUSTED_DRAFT',
                      response_metadata={'finish_reason': 'stop'})
    context, state = setup([workflow_call('query_logistics', {'order_id': '2002'}), draft],
        question='2002物流信息异常', intent='物流', answer='订单2002的模拟物流查询已完成。', single_attempt=True)
    async def handler(order_id):
        return {'order_id': order_id, 'mock': True, 'status': '运输中'}
    item = make_registration('query_logistics', source='mcp:logistics', handler=handler)
    definition = replace(item.definition, order_id_arg='order_id', allowed_intents=('物流',),
        input_schema={'type': 'object', 'properties': {'order_id': {'type': 'string'}},
                      'required': ['order_id'], 'additionalProperties': False})
    item = replace(item, definition=definition, factory=lambda ctx: StructuredTool.from_function(
        coroutine=handler, name=definition.name, description=definition.description, args_schema=definition.input_schema))
    catalog = ToolCatalog()
    policy = allow_policy(item)
    context.registry = catalog.snapshot(policy=policy, discovered=(item,)).bind(ToolContext('1', 1, state['raw_question']))
    async def owner(order_id):
        return order_id == '2002'
    context.execution_context = ExecutionContext('1', 1, '物流', state['raw_question'], policy=policy, order_authorizer=owner)
    context.executor = ToolExecutor()
    result, events = await run(context, state)
    assert result['tool_call_count'] == 1 and result['final_answer'].endswith('订单2002的模拟物流查询已完成。')
    assert context.model.streams == 1 and context.decision_model.decisions == 2
    assert 'UNTRUSTED_DRAFT' not in str(result) + str(events) + str(context.model.stream_inputs)
