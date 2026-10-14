"""协议拒绝保持公开契约，同时只记录有界、无内容的内部诊断。"""
import io
import json
import logging

import pytest
from langchain_core.messages import HumanMessage
from langgraph.runtime import Runtime

from app.agent.controls import parse_tool_selection
from app.core.errors import ServiceError
from app.tools.business import query_order
from app.workflow.agent import llm_call
from tests.test_workflow_agent import control, setup
from tests.workflow_fakes import workflow_call


SECRET = 'PRIVATE_BODY_key-secret_订单手机号_18000000000'


def rejected_reply(case):
    """把私密标记置于所有非白名单字段，逐项触发现有协议拒绝。"""
    if case == 'type':
        return HumanMessage(SECRET)
    reply = workflow_call(args={'order_id': SECRET}, identifier=SECRET)
    reply.content = SECRET
    reply.response_metadata.update(reasoning_content=SECRET, provider_error=SECRET,
        conversation_id=SECRET, user_message_id=SECRET)
    reply.additional_kwargs.update(reasoning_content=SECRET, api_key=SECRET)
    if case == 'invalid_decoded_count':
        reply.invalid_tool_calls = [{'name': SECRET, 'args': SECRET, 'id': SECRET, 'error': SECRET}]
    elif case == 'multiple_tools':
        reply.tool_calls *= 2
    elif case == 'finish':
        reply.response_metadata['finish_reason'] = SECRET
    elif case == 'raw_mirror':
        reply.additional_kwargs['tool_calls'][0]['function']['arguments'] = SECRET
    elif case == 'raw_type':
        reply.additional_kwargs['tool_calls'] = {SECRET: SECRET}
    elif case == 'raw_count':
        reply.additional_kwargs['tool_calls'] = []
    elif case == 'record':
        reply.tool_calls[0]['id'] = ' '
    elif case == 'name':
        reply.tool_calls[0]['name'] = SECRET
    elif case == 'args':
        reply.tool_calls[0]['args'] = SECRET
    return reply


@pytest.mark.parametrize('case,reason', [
    ('type', 'type'), ('invalid_decoded_count', 'invalid_decoded_count'),
    ('multiple_tools', 'multiple_tools'), ('finish', 'finish'),
    ('raw_mirror', 'raw_mirror'), ('raw_type', 'raw_mirror'),
    ('raw_count', 'raw_mirror'), ('record', 'record'), ('name', 'name'), ('args', 'args'),
])
def test_protocol_failure_has_fixed_private_reason_and_unchanged_public_error(case, reason):
    """丢失拒绝原因或修改公开服务错误都会失败，私密响应不进入异常正文。"""
    with pytest.raises(ServiceError) as caught:
        parse_tool_selection(rejected_reply(case), {'query_order': query_order})
    error = caught.value
    assert (error.code, error.message, error.status_code) == (
        'upstream_error', '模型返回了无效工具申请或未正常结束。', 502)
    assert getattr(error, 'reason', None) == reason
    assert SECRET not in str(error) and SECRET not in repr(error)


@pytest.mark.asyncio
@pytest.mark.parametrize('case', ['type', 'invalid_decoded_count', 'multiple_tools', 'finish',
    'raw_mirror', 'raw_type', 'raw_count', 'record', 'name', 'args'])
async def test_agent_protocol_warning_is_visible_without_custom_formatter_and_private(case, caplog):
    """默认 WARNING 门槛和纯消息格式也能定位失败，模型私密字段与身份伪造不能泄漏。"""
    reply = rejected_reply(case)
    reply.usage_metadata = {'input_tokens': 10, 'output_tokens': 5, 'total_tokens': 15}
    context, state = setup([reply])
    state['usage'] = {'actual': 7, 'estimated': 0, 'actual_calls': 1, 'estimated_calls': 0}
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    logger = logging.getLogger('app.workflow.agent')
    logger.addHandler(handler)
    try:
        with caplog.at_level(logging.WARNING):
            with pytest.raises(ServiceError) as caught:
                await llm_call(state, Runtime(context=context))
    finally:
        logger.removeHandler(handler)
    assert caught.value.code == 'upstream_error'
    records = [record for record in caplog.records if record.name == 'app.workflow.agent']
    assert len(records) == 1, 'protocol refusal must emit one production-visible warning'
    record = records[0]
    assert record.levelno == logging.WARNING and record.exc_info is None
    data = json.loads(stream.getvalue())
    assert data['event'] == 'agent_tool_protocol_failure'
    assert data['conversation_id'] == 'session' and data['user_message_id'] == '1'
    assert data['reason'] == ('raw_mirror' if case in ('raw_type', 'raw_count') else case)
    assert data['usage'] == {'actual': 22, 'estimated': 0, 'actual_calls': 2, 'estimated_calls': 0}
    assert set(data) == {'event', 'conversation_id', 'user_message_id', 'reason', 'usage',
        'tool_call_count', 'invalid_tool_call_count', 'raw_tool_call_count', 'finish',
        'raw_tool_calls_invalid_type'}
    assert data['raw_tool_calls_invalid_type'] == (case == 'raw_type')
    assert SECRET not in stream.getvalue() and SECRET not in caplog.text
    assert 'query_order' not in stream.getvalue()
    assert not context.repository.messages and context.model.streams == 0
    assert state['usage']['actual'] == 7 and state['decision_count'] == 0


@pytest.mark.asyncio
@pytest.mark.parametrize('finish,normalized', [(None, 'missing'), ([], 'invalid_type'),
    ({SECRET: SECRET}, 'invalid_type'), ('length', 'length'), ('content_filter', 'content_filter'),
    (SECRET, 'other')])
async def test_finish_diagnostic_normalizes_values_and_bounds_counts(finish, normalized, caplog):
    """任意结束字段只输出固定枚举，大列表仅保留限幅数量且不遍历私密调用。"""
    reply = rejected_reply('invalid_decoded_count')
    reply.invalid_tool_calls *= 1001
    reply.tool_calls *= 1001
    reply.additional_kwargs['tool_calls'] *= 1001
    reply.response_metadata['finish_reason'] = finish
    context, state = setup([reply])
    with caplog.at_level(logging.WARNING), pytest.raises(ServiceError):
        await llm_call(state, Runtime(context=context))
    records = [record for record in caplog.records if record.name == 'app.workflow.agent']
    assert len(records) == 1
    data = json.loads(records[0].getMessage())
    assert data['finish'] == normalized
    assert data['tool_call_count'] == data['invalid_tool_call_count'] == data['raw_tool_call_count'] == 1000
    assert data['usage']['estimated'] > 2048 and data['usage']['estimated_calls'] == 1
    assert SECRET not in caplog.text


@pytest.mark.asyncio
@pytest.mark.parametrize('case', ['valid_tool', 'valid_control', 'control_error', 'upstream_error'])
async def test_success_and_non_protocol_failures_do_not_emit_protocol_warning(case, caplog):
    """成功申请、成功控制以及其他失败不能伪造或重复记录协议诊断。"""
    reply = workflow_call() if case == 'valid_tool' else control('clarification')
    if case == 'control_error':
        reply.content = SECRET
    if case == 'upstream_error':
        reply = ServiceError('upstream_error', SECRET, 502)
    context, state = setup([reply])
    with caplog.at_level(logging.WARNING):
        if case in ('control_error', 'upstream_error'):
            with pytest.raises(ServiceError):
                await llm_call(state, Runtime(context=context))
        else:
            result = await llm_call(state, Runtime(context=context))
            assert result['decision_count'] == 1
    assert not [record for record in caplog.records if record.name == 'app.workflow.agent']
