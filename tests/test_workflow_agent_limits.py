"""有界停止、协议故障与原始配对完整性。"""
import asyncio
import pytest
from langchain_core.messages import AIMessageChunk, HumanMessage, ToolMessage

from app.core.errors import ServiceError
from tests.test_workflow_agent import control, run, setup
from tests.workflow_fakes import workflow_call


@pytest.mark.asyncio
async def test_invalid_arguments_can_be_corrected_without_exceeding_four_calls():
    """非法参数作为匹配错误回灌，修正仍受逻辑调用上限约束。"""
    context, state = setup([workflow_call(args={}), workflow_call(identifier='fix'), control()])
    result, _ = await run(context, state)
    assert result['tool_call_count'] == 2
    assert result['messages'][2].status == 'error'
    assert result['messages'][2].tool_call_id == 'call_1'
    assert context.decision_model.tool_inputs[1][-1].status == 'error'


@pytest.mark.asyncio
async def test_step_limit_preserves_all_complete_pairs():
    """第五次工具不会入库或执行，四组历史仍完整且停止不生成假成功。"""
    context, state = setup([workflow_call(args={'order_id': f'A-{i}'}, identifier=f'c{i}') for i in range(5)])
    result, events = await run(context, state)
    assert result['tool_call_count'] == 4 and result['decision_count'] <= 5
    assert [m.type for m in result['messages'][1:]] == ['ai', 'tool'] * 4
    assert len(context.repository.messages) == 8 and context.model.streams == 0
    assert result['suggested_actions'] == ['handoff'] and '尚未完成' in result['final_answer']
    assert ''.join(e['data']['text'] for e in events if e['event'] == 'delta') == result['final_answer']


@pytest.mark.asyncio
async def test_repeat_signature_stops_without_second_execution():
    """新调用 ID 不能规避同名同参数的停止条件。"""
    context, state = setup([workflow_call(), workflow_call(identifier='another')])
    result, _ = await run(context, state)
    assert result['tool_call_count'] == 1 and len(context.repository.messages) == 2
    assert context.model.streams == 0 and result['suggested_actions'] == ['handoff']


@pytest.mark.asyncio
async def test_negative_usage_falls_back_to_estimate():
    """非法上游 usage 不减少预算，最终流缺 usage 也明确记估算。"""
    reply = control('clarification')
    reply.usage_metadata = {'input_tokens': -1, 'output_tokens': 1, 'total_tokens': 0}
    context, state = setup([reply], answer='请提供订单号。')
    result, _ = await run(context, state)
    assert result['usage']['actual'] == 0 and result['usage']['estimated'] > 2560
    assert result['usage']['estimated_calls'] == 2


@pytest.mark.asyncio
@pytest.mark.parametrize('ending', [None, 'length', RuntimeError('offline upstream fault')])
async def test_incomplete_or_faulty_final_never_commits(ending):
    """无 stop、length 和流异常都不能形成 final 状态或 SQL 最终提交。"""
    chunks = [AIMessageChunk('请提供订单号。')]
    if isinstance(ending, Exception):
        chunks.append(ending)
    elif ending:
        chunks.append(AIMessageChunk('', response_metadata={'finish_reason': ending}))
    context, state = setup([control('clarification')], chunks=chunks)
    with pytest.raises((ServiceError, RuntimeError)):
        await run(context, state)
    assert not context.repository.messages and context.model.closed and context.upstream is None


@pytest.mark.asyncio
@pytest.mark.parametrize('reason', [[], {}])
async def test_malformed_finish_reason_is_service_error(reason):
    """不可哈希结束元数据也必须使用统一协议 ServiceError。"""
    reply = control('clarification')
    reply.response_metadata['finish_reason'] = reason
    context, state = setup([reply], answer='请提供订单号。')
    with pytest.raises(ServiceError):
        await run(context, state)
    assert context.model.streams == 0 and not context.repository.messages


@pytest.mark.parametrize('reason', [[], {}])
def test_shared_parser_handles_unhashable_finish_reason(reason):
    """共享解析器不能在协议错误转换前抛出 TypeError。"""
    from app.agent.controls import parse_tool_selection
    reply = control()
    reply.response_metadata['finish_reason'] = reason
    with pytest.raises(ServiceError):
        parse_tool_selection(reply, {})


@pytest.mark.asyncio
async def test_full_final_input_reserved_before_decision():
    """只保留512输出而遗漏最终完整输入时，收费决策会错误开始。"""
    context, state = setup([control('clarification')], question='查订单' * 800, answer='请提供订单号。')
    context.settings.agent_total_token_budget = 11000
    result, _ = await run(context, state)
    assert context.decision_model.decisions == 0 and context.model.streams == 0
    assert result['suggested_actions'] == ['handoff']


@pytest.mark.asyncio
async def test_final_cancellation_closes_upstream_without_committing():
    """最终模型等待期间取消会主动关闭流，父图不能提交未完成正文。"""
    context, state = setup([control('clarification')], answer='请提供订单号。')
    context.model.block = asyncio.Event()
    task = asyncio.create_task(run(context, state))
    for _ in range(100):
        if context.model.streams:
            break
        await asyncio.sleep(.001)
    assert context.model.streams == 1
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert context.model.closed and context.upstream is None and not context.repository.messages
