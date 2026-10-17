"""Task7: stable model-visible phase contracts, independent of business permissions."""
import importlib
import json

import pytest
from langchain_core.messages import AIMessage
from app.core.errors import ServiceError
from app.workflow.prompts import agent_decision_system, agent_final_system


def controls():
    try:
        return importlib.import_module('app.workflow.controls')
    except ImportError:
        pytest.fail('Unified workflow controls not implemented')


def test_same_phase_system_never_contains_turn_decisions():
    assert agent_decision_system('物流') == agent_decision_system('退款退货', after_sales=True)
    assert agent_final_system('物流', 'answer') == agent_final_system('退款退货', 'clarification',
        after_sales=True, refund_decision='ineligible', decision_reason='PRIVATE_DYNAMIC_REASON')


def test_nullable_control_fields_are_required_in_actual_tool_schema():
    from tests.test_workflow_agent import setup
    context, _ = setup([])
    schemas = controls().stable_read_schema(context.registry)
    assert [s['function']['name'] for s in schemas] == [
        'query_order', 'query_logistics', 'query_product', 'query_faq', 'internal_response_control']
    assert set(schemas[-1]['function']['parameters']['required']) == {
        'reply_mode', 'suggested_actions', 'refund_decision', 'decision_reason'}


@pytest.mark.parametrize('route,intent,decision,reason,valid', [
    ('business', '订单', None, None, True), ('knowledge', '商品咨询', 'eligible', '可退', False),
    ('business', '订单', None, '解释', False), ('after_sales', '退款退货', None, None, False),
    ('after_sales', '退款退货', 'needs_review', '完好状态待核验', True),
    ('after_sales', '售后', 'eligible', '故障', False),
    ('after_sales', '售后', 'not_applicable', '维修核验', True)])
def test_control_route_semantics(route, intent, decision, reason, valid):
    reply = AIMessage(json.dumps(dict(reply_mode='answer', suggested_actions=[],
        refund_decision=decision, decision_reason=reason)), response_metadata={'finish_reason': 'stop'})
    parser = controls().parse_control
    if valid:
        assert parser(reply, route=route, intent=intent).refund_decision == decision
    else:
        with pytest.raises(ServiceError):
            parser(reply, route=route, intent=intent)


@pytest.mark.parametrize('reason,valid', [
    ('已提供订单号，需查询实际物流轨迹核实包裹状态。', False), (None, True)])
def test_real_logistics_control_reason_is_not_general_reasoning(reason, valid):
    """Real Task11 negative and annotated counterpart; guard was already correct."""
    reply = AIMessage(json.dumps({'decision_reason': reason, 'refund_decision': None,
        'reply_mode': 'answer', 'suggested_actions': []}, ensure_ascii=False),
        response_metadata={'finish_reason': 'stop'})
    if valid:
        assert controls().parse_control(reply, route='business', intent='物流').decision_reason is None
    else:
        with pytest.raises(ServiceError) as caught:
            controls().parse_control(reply, route='business', intent='物流')
        assert caught.value.code == 'invalid_structured_output'


def test_missing_nullable_fields_and_length_finish_are_not_success():
    parser = controls().parse_control
    for body, finish in [('{"reply_mode":"answer","suggested_actions":[]}', 'stop'),
            ('{"reply_mode":"answer","suggested_actions":[],"refund_decision":null,"decision_reason":null}', 'length')]:
        with pytest.raises(ServiceError):
            parser(AIMessage(body, response_metadata={'finish_reason': finish}), route='business', intent='订单')


@pytest.mark.parametrize('finish', [None, 'content_filter', 'tool_calls'])
def test_control_requires_normal_stop(finish):
    reply = AIMessage('{"reply_mode":"answer","suggested_actions":[],"refund_decision":null,"decision_reason":null}',
                      response_metadata={'finish_reason': finish})
    with pytest.raises(ServiceError):
        controls().parse_control(reply, route='business', intent='订单')


def test_actual_packets_share_prefix_and_tools_across_routes():
    from tests.test_workflow_agent import setup
    from tests.test_context_agent import production_registry
    from app.workflow.context_budget import workflow_packet
    context, state = setup([], question='需要查询')
    context.registry = production_registry()
    schema = controls().stable_read_schema(context.registry)
    packets = []
    for route, intent in [('business','订单'), ('knowledge','商品咨询'), ('after_sales','退款退货')]:
        state.update(route=route, intent=intent)
        packet, _ = workflow_packet(state, context, phase='decision', tools=schema)
        packets.append(packet)
        assert len([m for m in packet.messages if m.type == 'system']) == 1
    assert len({p.prefix_hash for p in packets}) == 1
    assert len({json.dumps(p.tools,ensure_ascii=False) for p in packets}) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize('route', ['knowledge','after_sales'])
async def test_visible_faq_remains_forbidden_before_executor_or_sql(route):
    from langgraph.runtime import Runtime
    from app.workflow.agent import llm_call
    from tests.test_workflow_agent import setup
    from tests.workflow_fakes import workflow_call
    context, state = setup([workflow_call('query_faq', {'keyword':'需要'}, 'forbidden')], question='需要查询')
    state['route'] = route
    with pytest.raises(ServiceError):
        await llm_call(state, Runtime(context=context))
    assert context.repository.messages == [] and context.faq_repository.calls == []
