"""共享控制的预算、usage 与单工具协议边界。"""
import pytest
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import ValidationError

from app.agent.controls import AgentLimits, UsageLedger, call_signature, parse_tool_selection, record_usage, reserve_call
from app.config import Settings
from app.core.errors import ServiceError
from app.tools.business import query_order
from tests.workflow_fakes import workflow_call, workflow_stop
from app.tools.types import ToolCall


def test_missing_usage_is_estimated():
    """usage 缺失不能记录零成本，要保守计入输入和完整输出上限。"""
    ledger = UsageLedger(10000)
    record_usage(workflow_stop(), ledger, estimated_input=100, output_limit=2048)
    assert ledger.source == 'estimated' and ledger.spent == 2148
    assert ledger.remaining == 7852


def test_actual_usage_and_malformed_usage():
    """合法非负 usage 用实测，负值/布尔或不一致总数改用估算。"""
    ledger = UsageLedger(10000)
    reply = AIMessage('', usage_metadata={'input_tokens': 10, 'output_tokens': 5, 'total_tokens': 15})
    record_usage(reply, ledger, estimated_input=100, output_limit=512)
    assert ledger.actual == 15 and ledger.spent == 15
    reply.usage_metadata = {'input_tokens': -10, 'output_tokens': 5, 'total_tokens': -5}
    record_usage(reply, ledger, estimated_input=100, output_limit=512)
    assert ledger.estimated == 612 and ledger.source == 'mixed'


def test_reserves_final_budget():
    """剩余预算不足输入加决策上限加最终保留时拒绝，申请本身不扣账。"""
    ledger = UsageLedger(600)
    with pytest.raises(ServiceError) as error:
        reserve_call([HumanMessage('x')], [], ledger, output_limit=100, final_reserve=512)
    assert error.value.code == 'token_budget'
    assert ledger.spent == 0
    reserve_call([HumanMessage('x')], [], UsageLedger(1000), output_limit=100, final_reserve=512)


def test_schema_and_tool_request_are_counted():
    """不能只计算正文而遗漏 Schema 和空正文工具参数。"""
    with pytest.raises(ServiceError):
        reserve_call([workflow_call(args={'order_id': 'x' * 400})], [{'description': 'x' * 400}],
            UsageLedger(500), output_limit=1, final_reserve=1)


def test_raw_tool_mirror_must_match():
    """raw 申请名称、ID 或参数与 SDK 解析不一致时先拒绝协议。"""
    reply = workflow_call()
    reply.additional_kwargs['tool_calls'][0]['function']['arguments'] = '{"order_id":"OTHER"}'
    with pytest.raises(ServiceError):
        parse_tool_selection(reply, {'query_order': query_order})
    assert parse_tool_selection(workflow_stop(), {'query_order': query_order}) is None


@pytest.mark.parametrize('mutation', ['id', 'unknown', 'finish', 'raw', 'invalid'])
def test_invalid_protocol_is_rejected(mutation):
    """无效标识、工具名、结束或原始申请不得进入执行。"""
    reply = workflow_call()
    if mutation == 'id':
        reply.tool_calls[0]['id'] = ' '
    elif mutation == 'unknown':
        reply.tool_calls[0]['name'] = 'create_ticket'
    elif mutation == 'finish':
        reply.response_metadata['finish_reason'] = 'length'
    elif mutation == 'raw':
        reply.additional_kwargs['tool_calls'] = {'bad': True}
    else:
        reply.invalid_tool_calls = [{'name': 'query_order', 'args': 'bad', 'id': 'bad', 'error': 'bad'}]
    with pytest.raises(ServiceError):
        parse_tool_selection(reply, {'query_order': query_order})


def test_argument_schema_is_executor_responsibility():
    """对象参数仅经协议校验，完整 Schema 错误仍交给执行器产生结果。"""
    call = parse_tool_selection(workflow_call(args={'order_id': 42}), {'query_order': query_order})
    assert call.args == {'order_id': 42}
    assert call_signature(call) == call_signature(parse_tool_selection(
        workflow_call(args={'order_id': 42}, identifier='other'), {'query_order': query_order}))


@pytest.mark.parametrize('field', ['agent_max_tool_calls', 'agent_total_token_budget', 'agent_decision_max_output_tokens', 'intent_max_output_tokens'])
@pytest.mark.parametrize('value', [True, 0, -1, float('inf'), float('nan')])
def test_agent_settings_reject_invalid_limits(field, value):
    """新配置不能把布尔值或非法数字当作模型和工具预算。"""
    with pytest.raises(ValidationError):
        Settings(_env_file=None, llm_base_url='https://example.test/', llm_model='test', llm_api_key='test', **{field: value})


def test_agent_tool_limit_cannot_exceed_four():
    """环境配置不能扩大获批的最大工具执行次数。"""
    with pytest.raises(ValidationError):
        Settings(_env_file=None, llm_base_url='https://example.test/', llm_model='test', llm_api_key='test', agent_max_tool_calls=5)


def test_valid_agent_settings_remain_independent():
    """合法环境别名可加载且不覆盖原最终输出上限。"""
    settings = Settings(_env_file=None, LLM_BASE_URL='https://example.test/', LLM_MODEL='test', LLM_API_KEY='test',
        AGENT_MAX_TOOL_CALLS=3, AGENT_TOTAL_TOKEN_BUDGET=10000,
        AGENT_DECISION_MAX_OUTPUT_TOKENS=1024, INTENT_MAX_OUTPUT_TOKENS=1024)
    assert settings.agent_max_tool_calls == 3 and settings.agent_total_token_budget == 10000
    assert settings.agent_decision_max_output_tokens == settings.intent_max_output_tokens == 1024
    assert settings.max_output_tokens == 512


@pytest.mark.parametrize('kwargs', [{'max_tool_calls': 5}, {'max_decisions': 6}, {'total_token_budget': True}, {'final_output_tokens': 0}])
def test_limits_reject_unsafe_constructor_values(kwargs):
    """直接调用也不能绕过配置层扩大硬上限。"""
    with pytest.raises(ValueError):
        AgentLimits(**kwargs)


def test_sorted_signature_ignores_argument_key_order():
    """重排对象键不能绕过同一工具参数的重复检查。"""
    assert call_signature(ToolCall('first', 'query_order', {'a': 1, 'b': 2})) == call_signature(
        ToolCall('second', 'query_order', {'b': 2, 'a': 1}))
    assert call_signature(ToolCall('first', 'query_order', {'a': 1})) != call_signature(
        ToolCall('second', 'query_logistics', {'a': 1}))


@pytest.mark.parametrize('usage', [
    {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15},
    {'prompt_tokens': True, 'completion_tokens': 5, 'total_tokens': 6},
    {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 12},
])
def test_raw_usage_validation(usage):
    """提供商原始计量也要检查类型与总数，非法计量保守估算。"""
    ledger = UsageLedger(10000)
    reply = AIMessage('', response_metadata={'token_usage': usage})
    record_usage(reply, ledger, estimated_input=100, output_limit=512)
    assert ledger.spent == (15 if usage['total_tokens'] == 15 else 612)


def test_raw_mirror_cannot_coerce_boolean_into_integer():
    """JSON 布尔与整数不能因 Python 相等规则被误认同一申请。"""
    reply = workflow_call(args={'order_id': 1})
    reply.additional_kwargs['tool_calls'][0]['function']['arguments'] = '{"order_id":true}'
    with pytest.raises(ServiceError):
        parse_tool_selection(reply, {'query_order': query_order})
