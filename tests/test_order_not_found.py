"""查无当前账号订单是正常业务结果，不是系统故障或可编造的物流事实。"""
import json

import pytest
from langchain_core.messages import ToolMessage
from langgraph.runtime import Runtime

from app.core.errors import ServiceError
from app.workflow.agent import llm_call
from app.workflow.persistence import checkpoint_config
from tests.fakes import decode_sse
from tests.test_workflow_agent import control, setup
from tests.test_workflow_api import Store, intent, request, workflow_app
from tests.workflow_fakes import ScriptedWorkflowModel, workflow_call


@pytest.mark.parametrize('name,question,tool', [
    ('物流', '我买的恒温猫窝订单9999一直没发货，什么时候到', 'query_logistics'),
    ('订单', '查询订单9999的状态', 'query_order'),
])
async def test_unknown_order_completes_business_reply_without_claiming_delivery(tmp_path, name, question, tool):
    """真实固定订单提供器、父图/API/SSE与检查点，未知9999不可随机造成功。"""
    model = ScriptedWorkflowModel([control('clarification'), control('clarification')],
                                  intent_replies=[intent(name)])
    store = Store()
    async with workflow_app(tmp_path, model=model, store=store) as app:
        frames = decode_sse((await request(app, question)).text)
        snapshot = await app.state.chat_service.graph.aget_state(checkpoint_config('1'))
    assert frames[-1][0] == 'done'
    answer = ''.join(data['delta'] for event, data in frames if event == 'delta')
    assert '未找到' in answer and '订单号' in answer
    assert not any(word in answer for word in ('已发货', '已签收', '天内', '退款', '手机号'))
    assert not any(event in ('error', 'actions', 'refund_offer') for event, _ in frames)
    state = snapshot.values
    assert snapshot.next == () and state['turn_status'] == 'completed'
    assert state['raw_question'] == question and state['final_answer'] == answer
    assert state['tool_call_count'] == 1 and state['tool_trace'][0]['name'] == tool
    results = [message for message in state['messages'] if isinstance(message, ToolMessage)]
    assert len(results) == 1 and results[0].status == 'error'
    assert json.loads(results[0].content)['error']['code'] == 'not_found'
    assert store.commits == 1 and model.decisions == 1 and model.streams == 0


@pytest.mark.parametrize('status,payload', [
    ('error', {'error': {'code': 'tool_timeout'}}),
    ('error', {'error': {'code': 'tool_connection_error'}}),
    ('error', {'error': {'code': 'tool_execution_error'}}),
    ('success', {'error': {'code': 'not_found'}}),
    ('error', {'order_id': '9999', 'status': '已签收', 'error': {'code': 'not_found'}}),
])
async def test_operational_or_conflicting_outcomes_still_fail_closed(status, payload):
    """只处理规范业务未找到；真正失败与自相矛盾结果不能变成成功答复。"""
    context, state = setup([control('clarification')], question='订单9999物流', intent='物流')
    read = workflow_call('query_logistics', {'order_id': '9999'})
    state['messages'] += [read, ToolMessage(json.dumps(payload), tool_call_id=read.tool_calls[0]['id'], status=status)]
    with pytest.raises(ServiceError) as caught:
        await llm_call(state, Runtime(context=context))
    assert caught.value.code == 'invalid_answer'
    assert context.model.streams == 0 and not context.repository.messages
