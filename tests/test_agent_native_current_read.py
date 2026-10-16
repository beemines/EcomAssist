"""当前必读策略必须进入原生工具请求，非必读阶段保持auto。"""
import json

import httpx
import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.runtime import Runtime

from app.core.errors import ServiceError
from app.workflow.agent import llm_call
from tests.test_workflow_agent import control, setup
from tests.workflow_fakes import workflow_call


@pytest.mark.parametrize('raw,resolved,name,order', [
    ('我的订单1001到哪了', '我的订单1001到哪了', 'query_logistics', '1001'),
    ('它的物流呢？', '订单1001的物流呢？', 'query_logistics', '1001'),
    ('不要退款，我要查订单1002物流。', '不要退款，我要查订单1002物流。', 'query_logistics', '1002'),
    ('订单1001状态', '订单1001状态', 'query_order', '1001'),
])
async def test_required_current_read_is_native_and_later_control_auto(raw, resolved, name, order):
    """把绑定退回auto会使首次必读约束缺失；成功后不能继续强迫工具。"""
    context, state = setup([workflow_call(name, {'order_id': order}), control()], question=raw,
        intent='订单' if name == 'query_order' else '物流')
    state['resolved_question'] = resolved
    state['messages'] = [HumanMessage('订单1001状态', id='old'), AIMessage('请确认订单。'), *state['messages']]
    first = await llm_call(state, Runtime(context=context))
    selected = first['selected']
    assert selected.tool_calls[0]['args'] == {'order_id': order}
    assert first['selected_origin'] == 'agent'
    current = {**state, **first, 'messages': [*state['messages'], selected,
        ToolMessage(json.dumps({'order_id': order}), tool_call_id=selected.tool_calls[0]['id'])]}
    second = await llm_call(current, Runtime(context=context))
    assert second['selected'] is None and second['reply_mode'] == 'answer'
    assert context.decision_model.bind_options == [
        {'tool_choice': name, 'parallel_tool_calls': False},
        {'tool_choice': 'auto', 'parallel_tool_calls': False}]


@pytest.mark.parametrize('question,route,intent,missing_tool', [
    ('查物流', 'business', '物流', False),
    ('查订单1001和订单1002物流', 'business', '物流', False),
    ('还没选订单，没确定查哪一单的物流。', 'business', '物流', False),
    ('订单1001物流', 'knowledge', '物流', False),
    ('订单1001物流', 'after_sales', '售后', False),
    ('订单1001商品', 'business', '商品咨询', False),
    ('订单1001物流', 'business', '物流', True),
])
async def test_non_required_or_unavailable_current_read_remains_auto(question, route, intent, missing_tool):
    """缺少唯一可信目标、业务路由或可绑定工具不能被强迫执行。"""
    reply = control('clarification')
    if route == 'after_sales':
        reply.content = json.dumps({'reply_mode': 'clarification', 'suggested_actions': [],
            'refund_decision': 'not_applicable', 'decision_reason': '需要信息'})
    context, state = setup([reply], question=question, intent=intent)
    state['route'] = route
    state['messages'] = [HumanMessage('订单1001状态', id='old'), AIMessage('请确认订单。'), *state['messages']]
    if missing_tool:
        del context.registry['query_logistics']
    await llm_call(state, Runtime(context=context))
    assert context.decision_model.bind_options == [{'tool_choice': 'auto', 'parallel_tool_calls': False}]


async def test_failed_current_read_does_not_force_or_retry():
    """已有失败配对后auto控制仍拒绝，不能隐藏故障或自动重试。"""
    context, state = setup([control('clarification')], question='订单1001物流', intent='物流')
    request = workflow_call('query_logistics', {'order_id': '1001'})
    state['messages'] += [request, ToolMessage('{"error":{"code":"tool_execution_error"}}',
        tool_call_id='call_1', status='error')]
    with pytest.raises(ServiceError) as caught:
        await llm_call(state, Runtime(context=context))
    assert caught.value.code == 'invalid_answer'
    assert context.decision_model.bind_options == [{'tool_choice': 'auto', 'parallel_tool_calls': False}]
    assert context.decision_model.decisions == 1 and not context.repository.messages


async def test_locked_chatopenai_sends_named_current_read_without_network():
    """实际SDK序列化必须保留生产必读约束及原生参数Schema。"""
    requests = []
    def respond(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, json={'id': 'fake', 'object': 'chat.completion', 'created': 0,
            'model': 'offline', 'choices': [{'index': 0, 'finish_reason': 'tool_calls',
            'message': {'role': 'assistant', 'content': None, 'tool_calls': [{'id': 'read',
                'type': 'function', 'function': {'name': 'query_logistics', 'arguments': '{"order_id":"1001"}'}}]}}],
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}})
    context, state = setup([], question='我的订单1001到哪了', intent='物流')
    context.settings.llm_token_limit_field = 'max_tokens'
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        sync_client = httpx.Client(transport=httpx.MockTransport(respond))
        model = ChatOpenAI(model='offline', api_key='offline', base_url='https://offline.invalid/v1',
            http_client=sync_client, http_async_client=client, max_retries=0, use_responses_api=False)
        context.decision_model = model
        try:
            result = await llm_call(state, Runtime(context=context))
        finally:
            model.root_client.close()
            await model.root_async_client.close()
    assert result['selected_origin'] == 'agent' and result['selected'].tool_calls[0]['args'] == {'order_id': '1001'}
    assert len(requests) == 1
    assert requests[0]['tool_choice'] == {'type': 'function', 'function': {'name': 'query_logistics'}}
    assert requests[0]['parallel_tool_calls'] is False and requests[0]['max_tokens'] == 2048
    tool = next(t for t in requests[0]['tools'] if t['function']['name'] == 'query_logistics')
    assert tool['function']['parameters']['required'] == ['order_id']
