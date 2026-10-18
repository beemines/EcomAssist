"""内部控制与业务读取共用原生协议，保持公开/执行/持久化边界。"""
import json
import logging

import httpx
import pytest
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_openai import ChatOpenAI
from langgraph.runtime import Runtime

from app.core.errors import ServiceError
from app.config import Settings
from app.core.llm import create_model, model_with_output_budget
from app.core.memory import estimate_tokens
from app.context.tokens import estimate_payload as estimate_call_input
from app.workflow.agent import llm_call
from app.workflow.logging import safe_fields
from tests.test_workflow_agent import setup, run, control
from tests.workflow_fakes import workflow_call


def native(args=None):
    return workflow_call('internal_response_control', args if args is not None else
        {'reply_mode': 'answer', 'suggested_actions': ['handoff'],
         'refund_decision': None, 'decision_reason': None}, identifier='control_1')


@pytest.mark.parametrize('transport', ['json_control', 'native_control'])
async def test_post_logistics_sdk_uses_supported_json_mode_without_network(transport):
    """必须发送提供方支持的auto+JSON模式；原生内部控制仍可选。"""
    requests = []
    def respond(request):
        payload = json.loads(request.content)
        requests.append(payload)
        assert payload['tool_choice'] == 'auto'
        schema = next(t['function'] for t in payload['tools'] if t['function']['name'] == 'internal_response_control')
        assert set(schema['parameters']['required']) == {'reply_mode', 'suggested_actions', 'refund_decision', 'decision_reason'}
        assert schema['parameters']['additionalProperties'] is False
        assert schema['parameters']['properties']['suggested_actions']['maxItems'] == 2
        assert payload['parallel_tool_calls'] is False and payload['max_tokens'] == 2048
        assert payload['response_format'] == {'type': 'json_object'}
        assert all('strict' not in tool['function'] for tool in payload['tools'])
        message = {'role': 'assistant', 'content': '{"reply_mode":"answer","suggested_actions":["handoff"],"refund_decision":null,"decision_reason":null}'}
        if transport == 'native_control':
            message.update(content=None, tool_calls=[{'id': 'control_1', 'type': 'function',
                'function': {'name': 'internal_response_control',
                    'arguments': '{"reply_mode":"answer","suggested_actions":["handoff"],"refund_decision":null,"decision_reason":null}'}}])
        return httpx.Response(200, json={'id': 'fake', 'object': 'chat.completion', 'created': 0,
            'model': 'offline', 'choices': [{'index': 0,
                'finish_reason': 'tool_calls' if transport == 'native_control' else 'stop', 'message': message}],
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}})
    context, state = setup([], question='订单1001的物流到哪了', intent='物流')
    state['messages'] += [workflow_call('query_logistics', {'order_id': '1001'}),
        ToolMessage('{"order_id":"1001","mock":true}', tool_call_id='call_1')]
    state.update(decision_count=1, tool_call_count=1)
    context.settings.llm_token_limit_field = 'max_tokens'
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        with httpx.Client(transport=httpx.MockTransport(respond)) as sync:
            model = ChatOpenAI(model='offline', api_key='offline', base_url='https://offline.invalid/v1',
                http_client=sync, http_async_client=client, max_retries=0, use_responses_api=False)
            context.decision_model = model
            try:
                result = await llm_call(state, Runtime(context=context))
            finally:
                model.root_client.close()
                await model.root_async_client.close()
    assert len(requests) == 1
    assert result['selected'] is None and result['reply_mode'] == 'answer'
    assert result['suggested_actions'] == ['handoff'] and result['decision_count'] == 2
    assert result['usage']['actual'] == 15 and not context.repository.messages


async def test_native_control_is_not_business_execution_or_sql_or_badge(caplog):
    context, state = setup([workflow_call('query_logistics', {'order_id': '1001'}), native()],
        question='订单1001物流', intent='物流')
    with caplog.at_level(logging.INFO, logger='app.workflow.audit'):
        result, events = await run(context, state)
    assert result['tool_call_count'] == 1 and result['decision_count'] == 2
    assert result['suggested_actions'] == ['handoff']
    assert [m.type for m in context.repository.messages] == ['ai', 'tool']
    assert all(e['data']['tool'] == 'query_logistics' for e in events if e['event'] == 'status')
    decisions = [r.workflow for r in caplog.records if hasattr(r, 'workflow') and r.workflow.get('node') == 'llm_call']
    assert [r['decision_transport'] for r in decisions] == ['business_tool', 'native_control']
    assert safe_fields({'decision_transport': 'SECRET'}) == {}


@pytest.mark.parametrize('args', [{}, {'reply_mode': 'answer'}, {'reply_mode': 'answer', 'suggested_actions': [], 'extra': 1},
    {'reply_mode': True, 'suggested_actions': []}, {'reply_mode': 'answer', 'suggested_actions': 'handoff'},
    {'reply_mode': 'answer', 'suggested_actions': ['refund']}, {'reply_mode': 'answer', 'suggested_actions': ['handoff'] * 3}])
async def test_native_control_schema_failure_never_executes_or_streams(args):
    if 'suggested_actions' in args:
        args = {'refund_decision': None, 'decision_reason': None, **args}
    context, state = setup([native(args)], question='查物流', intent='物流', single_attempt=True)
    with pytest.raises(ServiceError) as caught:
        await run(context, state)
    assert caught.value.code == 'invalid_structured_output'
    assert not context.repository.messages and context.model.streams == 0


@pytest.mark.parametrize('defect', ['multiple', 'body', 'finish', 'mirror', 'mirror_args', 'id', 'unknown'])
async def test_native_control_uses_whole_selection_guards(defect):
    reply = native()
    if defect == 'multiple': reply.tool_calls.append(workflow_call().tool_calls[0])
    if defect == 'body': reply.content = '不能流出的事实'
    if defect == 'finish': reply.response_metadata['finish_reason'] = 'length'
    if defect == 'mirror': reply.additional_kwargs['tool_calls'] = []
    if defect == 'mirror_args': reply.additional_kwargs['tool_calls'] = [{'id': 'control_1', 'type': 'function',
        'function': {'name': 'internal_response_control', 'arguments': '{"reply_mode":"clarification","suggested_actions":[]}'}}]
    if defect == 'id': reply.tool_calls[0]['id'] = ''
    if defect == 'unknown': reply.tool_calls[0]['name'] = 'internal_refund'
    context, state = setup([reply], question='查物流', intent='物流')
    with pytest.raises(ServiceError):
        await run(context, state)
    assert not context.repository.messages and context.model.streams == 0


@pytest.mark.parametrize('route,intent', [('business', '物流'), ('knowledge', '商品咨询'), ('after_sales', '退款退货')])
async def test_actual_internal_schema_is_charged_and_can_block_call(route, intent):
    """漏算控制schema会让刚好只容业务schema的输入错误越过收费边界。"""
    args = {'reply_mode': 'clarification', 'suggested_actions': [], 'refund_decision': None, 'decision_reason': None}
    if route == 'after_sales':
        args.update(refund_decision='ineligible', decision_reason='需要更多信息')
    context, state = setup([native(args)], question='请帮我', intent=intent)
    state['route'] = route
    result = await llm_call(state, Runtime(context=context))
    schemas = [convert_to_openai_tool(tool) for tool in context.decision_model.bound_tools[0]]
    messages = context.decision_model.tool_inputs[0]
    internal = [s for s in schemas if s['function']['name'] == 'internal_response_control']
    assert len(internal) == 1
    if route == 'after_sales':
        params = internal[0]['function']['parameters']
        assert set(params['required']) == {'reply_mode', 'suggested_actions', 'refund_decision', 'decision_reason'}
        assert params['properties']['decision_reason']['anyOf'][0]['maxLength'] == 256
    assert result['usage']['estimated'] == estimate_call_input(messages, schemas) + 2048
    from dataclasses import replace
    from app.workflow.context_budget import runtime_snapshot
    frozen = runtime_snapshot(state, context)
    context.context_snapshot = replace(frozen, budget=replace(frozen.budget,
        window=estimate_call_input(messages, schemas) + 2048 + frozen.budget.safety - 1))
    with pytest.raises(ServiceError) as caught:
        await llm_call(state, Runtime(context=context))
    assert caught.value.code == 'input_too_long' and context.decision_model.decisions == 1


async def test_native_control_can_finalize_after_four_business_calls():
    context, state = setup([native({'reply_mode': 'clarification', 'suggested_actions': [],
                                  'refund_decision': None, 'decision_reason': None})],
        question='查物流', intent='物流', answer='请提供订单号。')
    state.update(tool_call_count=4, decision_count=4)
    result, events = await run(context, state)
    assert result['tool_call_count'] == 4 and result['decision_count'] == 5
    assert result['final_answer'] == '请提供订单号。' and context.model.streams == 1
    assert not context.repository.messages and not any(e['event'] == 'status' for e in events)


async def test_internal_name_collision_fails_before_model_or_business_execution():
    context, state = setup([native()], question='查物流', intent='物流')
    context.registry['internal_response_control'] = context.registry['query_logistics']
    with pytest.raises(ValueError, match='conflicts'):
        await llm_call(state, Runtime(context=context))
    assert context.decision_model.decisions == 0 and not context.repository.messages


@pytest.mark.parametrize('changes', [{'decision_reason': ''}, {'decision_reason': ' '},
    {'decision_reason': 'x' * 257}, {'refund_decision': True}, {'decision_reason': 2}, {'extra': 1}])
async def test_native_after_sales_strict_schema_rejects_invalid_values(changes):
    args = {'reply_mode': 'answer', 'suggested_actions': [], 'refund_decision': 'needs_review', 'decision_reason': '待核验'}
    args.update(changes)
    context, state = setup([native(args)], question='订单1001能退吗', intent='退款退货', single_attempt=True)
    state['route'] = 'after_sales'
    with pytest.raises(ServiceError) as caught:
        await llm_call(state, Runtime(context=context))
    assert caught.value.code == 'invalid_structured_output'
    assert not context.repository.messages and context.model.streams == 0


@pytest.mark.parametrize('intent,mode,decision,valid', [
    ('售后', 'answer', 'not_applicable', True), ('售后', 'answer', 'eligible', False),
    ('退款退货', 'answer', 'needs_review', True), ('退款退货', 'answer', 'eligible', True),
    ('退款退货', 'answer', 'ineligible', True), ('退款退货', 'answer', 'not_applicable', False),
    ('退款退货', 'clarification', 'needs_review', False), ('退款退货', 'clarification', 'eligible', False),
    ('退款退货', 'clarification', 'ineligible', True)])
@pytest.mark.parametrize('transport', ['json_control', 'native_control'])
async def test_after_sales_keeps_semantic_control_checks(intent, mode, decision, valid, transport):
    args = {'reply_mode': mode, 'suggested_actions': ['create_ticket'],
        'refund_decision': decision, 'decision_reason': '条件待核验'}
    reply = native(args) if transport == 'native_control' else AIMessage(json.dumps(args), response_metadata={'finish_reason': 'stop'})
    context, state = setup([reply], question='订单1001售后', intent=intent, single_attempt=True)
    state['route'] = 'after_sales'
    if valid:
        result = await llm_call(state, Runtime(context=context))
        assert result['refund_decision'] == decision and result['reply_mode'] == mode
        assert result['suggested_actions'] == ['create_ticket'] and result['selected'] is None
        assert 'refund_offer' not in result
    else:
        with pytest.raises(ServiceError) as caught:
            await llm_call(state, Runtime(context=context))
        assert caught.value.code == 'invalid_structured_output'
    system = context.decision_model.tool_inputs[0][0].text
    assert '本轮正文JSON或internal_response_control参数必须恰有reply_mode、suggested_actions、refund_decision、decision_reason四字段' in system
    assert '必须恰有reply_mode、suggested_actions两字段' not in system
    assert '例如 {"reply_mode":"answer","suggested_actions":[]}' not in system
    assert not context.repository.messages and context.model.streams == 0


@pytest.mark.parametrize('reply,valid', [(control('clarification'), True),
    (AIMessage('普通回答正文', response_metadata={'finish_reason': 'stop'}), False)])
async def test_primary_json_control_remains_strict(reply, valid, caplog):
    context, state = setup([reply], question='查物流', intent='物流', single_attempt=True)
    with caplog.at_level(logging.INFO, logger='app.workflow.audit'):
        if valid:
            result = await llm_call(state, Runtime(context=context))
            assert result['reply_mode'] == 'clarification'
            assert any(getattr(r, 'workflow', {}).get('decision_transport') == 'json_control' for r in caplog.records)
        else:
            with pytest.raises(ServiceError) as caught:
                await llm_call(state, Runtime(context=context))
            assert caught.value.code == 'invalid_structured_output'
    assert not context.repository.messages and context.model.streams == 0


@pytest.mark.parametrize('token_field', ['max_tokens', 'max_completion_tokens'])
@pytest.mark.parametrize('final_output', [512, 2000])
async def test_actual_factory_json_format_is_decision_only_and_preserves_model(token_field, final_output, tmp_path):
    """决策副本泄漏JSON格式到最终流或改写共享factory参数会破坏真实HTTP契约。"""
    settings = Settings(_env_file=None, llm_base_url='https://offline.invalid/v1', llm_model='offline',
        llm_api_key='offline', llm_token_limit_field=token_field, max_output_tokens=final_output)
    requests = []
    from app.context.logging import ContextLogger
    path = tmp_path / 'app.log'
    logger = ContextLogger(path)
    def respond(request):
        payload = json.loads(request.content)
        requests.append(payload)
        records = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
        sent = [row for row in records if row['event'] == 'model_ctx'][-1]
        assert sent['messages'] == payload['messages']
        assert sent['tools'] == payload.get('tools', [])
        assert payload['reasoning_effort'] == 'low'
        if not payload.get('stream'):
            assert payload[token_field] == 2048 and payload['tool_choice'] == 'auto'
            assert payload['response_format'] == {'type': 'json_object'}
            assert all('strict' not in tool['function'] for tool in payload['tools'])
            return httpx.Response(200, json={'id': 'control', 'object': 'chat.completion', 'created': 0,
                'model': 'offline', 'choices': [{'index': 0, 'finish_reason': 'stop', 'message': {
                    'role': 'assistant', 'content': '{"reply_mode":"clarification","suggested_actions":[],"refund_decision":null,"decision_reason":null}'}}]})
        assert payload[token_field] == final_output and 'response_format' not in payload
        assert 'tools' not in payload and 'tool_choice' not in payload
        pieces = [{'role': 'assistant', 'content': '请提供型号。'}, {}]
        data = ''.join('data: ' + json.dumps({'id': 'final', 'object': 'chat.completion.chunk',
            'created': 0, 'model': 'offline', 'choices': [{'index': 0, 'delta': piece,
                'finish_reason': None if index == 0 else 'stop'}]}) + '\n\n' for index, piece in enumerate(pieces))
        return httpx.Response(200, text=data + 'data: [DONE]\n\n', headers={'content-type': 'text/event-stream'})
    context, state = setup([], question='这个商品怎么使用', intent='商品咨询')
    state['route'] = 'knowledge'
    context.settings = settings
    context.context_logger = logger
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        model = create_model(settings, http_async_client=client, reasoning_effort='low')
        initial_extra = dict(model.extra_body)
        context.model = model_with_output_budget(model, settings, 512)
        context.decision_model = model_with_output_budget(model, settings, 2048)
        try:
            result, _ = await run(context, state)
            assert result['final_answer'] == '请提供型号。' and result['tool_call_count'] == 0
            assert model.extra_body == initial_extra == {token_field: final_output}
            assert context.decision_model.extra_body == {token_field: 2048}
            assert context.model.extra_body == {token_field: 512}
            assert model.max_retries == 0 and context.decision_model.root_async_client is model.root_async_client
            assert len(requests) == 2
        finally:
            logger.close()
            model.root_client.close()
            await model.root_async_client.close()


@pytest.mark.parametrize('body', ['{}', '{"reply_mode":"answer"}',
    '{"reply_mode":true,"suggested_actions":[]}', '{"reply_mode":"answer","suggested_actions":"handoff"}',
    '{"reply_mode":"answer","suggested_actions":[],"answer":"secret"}',
    '```json\n{"reply_mode":"answer","suggested_actions":[]}\n```',
    '{"reply_mode":"answer","suggested_actions":[]}解释', '普通正文'])
async def test_json_mode_does_not_relax_strict_control_validation(body):
    try:
        parsed = json.loads(body)
        if 'suggested_actions' in parsed:
            body = json.dumps({'refund_decision': None, 'decision_reason': None, **parsed})
    except json.JSONDecodeError:
        pass
    context, state = setup([AIMessage(body, response_metadata={'finish_reason': 'stop'})],
        question='查物流', intent='物流', single_attempt=True)
    with pytest.raises(ServiceError) as caught:
        await run(context, state)
    assert caught.value.code == 'invalid_structured_output'
    assert not context.repository.messages and context.model.streams == 0
