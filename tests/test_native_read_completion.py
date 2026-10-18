import pytest
from langchain_core.messages import AIMessage, AIMessageChunk
from app.core.errors import ServiceError
from app.tools.policies import PolicySnapshot
from app.tools.registry import build_catalog
from app.tools.types import ToolContext, ExecutionContext
from tests.test_workflow_agent import setup, run
from tests.workflow_fakes import workflow_call


def native_context(replies):
    context, state = setup(replies, question='订单1001状态是什么', intent='订单',
        answer='已读取订单1001的模拟结果。', single_attempt=True)
    catalog = build_catalog(context.faq_repository, object())
    policy = PolicySnapshot.from_dict({'tools': [{'source': 'builtin', 'name': 'query_order', 'operation': 'read'}]})
    context.registry = catalog.snapshot(policy=policy).bind(ToolContext('1', 2, state['raw_question']))
    context.execution_context = ExecutionContext('1', 2, '订单', state['raw_question'])
    return context, state


async def test_native_stop_after_fresh_read_only_signals_checked_final_generation():
    # Captured GLM behavior: natural language after successful tool results.
    draft = '订单1001的查询结果如下。SECRET_UNCHECKED_DRAFT'
    context, state = native_context([workflow_call('query_order', {'order_id': '1001'}),
        AIMessage(draft, response_metadata={'finish_reason': 'stop'})])
    result, events = await run(context, state)
    assert result['final_answer'].endswith('已读取订单1001的模拟结果。')
    assert 'SECRET_UNCHECKED_DRAFT' not in str(result) and 'SECRET_UNCHECKED_DRAFT' not in str(events)
    assert context.model.streams == 1 and context.decision_model.decisions == 2


@pytest.mark.parametrize('body,with_read', [('{"name":"create_ticket","args":{}}', True), ('草稿答案', False)])
async def test_fake_json_or_missing_fresh_read_cannot_use_native_stop(body, with_read):
    replies = [workflow_call('query_order', {'order_id': '1001'})] if with_read else []
    context, state = native_context([*replies, AIMessage(body, response_metadata={'finish_reason': 'stop'})])
    with pytest.raises(ServiceError):
        await run(context, state)
    assert context.model.streams == 0


@pytest.mark.parametrize('change', ['legacy', 'after_sales', 'ticket', 'failed', 'later_failed', 'unpaired'])
async def test_native_stop_does_not_mask_other_protocols_or_failed_reads(change):
    import json
    from langchain_core.messages import HumanMessage, ToolMessage
    context, state = native_context([AIMessage('不可信草稿', response_metadata={'finish_reason': 'stop'})])
    request = workflow_call('query_order', {'order_id': '1001'})
    result = ToolMessage(json.dumps({'order_id': '1001', 'mock': True}), tool_call_id=request.tool_calls[0]['id'])
    # Seed the same persisted pair a preceding successful node would produce.
    state['messages'] = [HumanMessage(state['raw_question'], id=state['user_message_id']), request, result]
    if change == 'legacy':
        context.registry = dict(context.registry)
    elif change == 'after_sales':
        state.update(route='after_sales', intent='退款退货')
    elif change == 'ticket':
        state['ticket_request'] = {'origin_user_message_id': state['user_message_id']}
    elif change == 'failed':
        result.status = 'error'
        result.content = '{"error":{"code":"timeout"}}'
    elif change == 'later_failed':
        second = workflow_call('query_order', {'order_id': '1001'}, identifier='second')
        state['messages'].extend([second, ToolMessage('{"error":{"code":"timeout"}}',
            tool_call_id='second', status='error')])
    else:
        result.tool_call_id = 'other_call'
    with pytest.raises(ValueError if change == 'unpaired' else ServiceError):
        await run(context, state)
    assert context.model.streams == 0


async def test_native_stop_still_rejects_invalid_independent_final_stream():
    context, state = native_context([workflow_call('query_order', {'order_id': '1001'}),
        AIMessage('草稿停止', response_metadata={'finish_reason': 'stop'})])
    context.model.final_chunks = [AIMessageChunk('不完整最终正文', response_metadata={'finish_reason': 'length'})]
    with pytest.raises(ServiceError):
        await run(context, state)
    assert context.model.streams == 1
