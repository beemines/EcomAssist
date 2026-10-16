"""模拟说明由服务器展示，原始最终流仍独立决定能否完成。"""
import asyncio
import json
from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessage, AIMessageChunk, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver

from app.core.errors import ServiceError
from app.workflow.agent import build_agent_graph, finalize_answer
from app.workflow.graph import build_workflow_graph
from tests.test_after_sales_workflow import context as after_sales_context
from tests.test_evidence import payload
from tests.test_workflow_agent import control, setup
from tests.workflow_fakes import workflow_call


NOTICE = '本轮订单、物流等业务信息为模拟演示数据，仅供参考。\n\n'


def final_context(*, mock=True, clarification=False, faq=False, chunks=None):
    """保留真实最终节点和配对证据，仅模型/仓储为现有离线替身。"""
    answer = '请提供订单号。' if clarification else '规则内容[1]。' if faq else '订单已签收。'
    ctx, state = setup([], answer=answer, chunks=chunks)
    state['reply_mode'] = 'clarification' if clarification else 'answer'
    data = payload(('规则内容',)) if faq else {'order_id': 'A-42', 'status': '已签收', 'mock': mock}
    name = 'query_faq' if faq else 'query_order'
    state['messages'] += [workflow_call(name), ToolMessage(json.dumps(data), tool_call_id='call_1')]
    events = []
    runtime = SimpleNamespace(context=ctx, stream_writer=events.append)
    return ctx, state, runtime, events


async def test_missing_model_notice_completes_refund_and_persists_exact_stream():
    """实际338缺说明的失败不能靠重试或放宽验证解决，SSE/SQL/checkpoint必须一致。"""
    decision = AIMessage(json.dumps({'reply_mode': 'answer', 'suggested_actions': [],
        'refund_decision': 'needs_review', 'decision_reason': '商品完好条件待核验'}),
        response_metadata={'finish_reason': 'stop'})
    answer = '订单1001可申请退货，商品完好条件需要核验[1]。'
    ctx, initial = setup([decision], question='订单1001能退吗', intent='退款退货', answer=answer)
    provided = after_sales_context(data=payload(('七天内商品完好支持退货。',)))
    ctx.order_provider, ctx.user_id = provided.order_provider, provided.user_id
    ctx.expander, ctx.workflow_retriever = provided.expander, provided.workflow_retriever
    parent = build_workflow_graph(build_agent_graph(), checkpointer=InMemorySaver())
    config = {'configurable': {'thread_id': 'mock-notice'}}
    events = []
    async for _, event in parent.astream(initial, config, context=ctx, stream_mode='custom', subgraphs=True):
        events.append(event)
    result = (await parent.aget_state(config)).values
    assert result['turn_status'] == 'completed' and result['refund_offer']
    assert result['final_answer'] == NOTICE + answer == ctx.repository.messages[-1].content
    assert ''.join(e['data']['text'] for e in events if e['event'] == 'delta') == result['final_answer']
    assert ctx.model.streams == 1 and ctx.decision_model.decisions == 1


@pytest.mark.parametrize('mock,clarification,faq', [(False, False, False), (True, True, False), (True, False, True)])
async def test_real_clarification_and_pure_faq_receive_no_notice(mock, clarification, faq):
    ctx, state, runtime, events = final_context(mock=mock, clarification=clarification, faq=faq)
    result = await finalize_answer(state, runtime)
    expected = '请提供订单号。' if clarification else '规则内容[1]。' if faq else '订单已签收。'
    assert result['final_answer'] == expected
    assert ''.join(e['data']['text'] for e in events if e['event'] == 'delta') == expected


async def test_notice_does_not_charge_model_usage():
    chunks = [AIMessageChunk('订单已签收。'), AIMessageChunk('', response_metadata={'finish_reason': 'stop'},
        usage_metadata={'input_tokens': 10, 'output_tokens': 7, 'total_tokens': 17})]
    ctx, state, runtime, events = final_context(chunks=chunks)
    result = await finalize_answer(state, runtime)
    assert result['final_answer'] == NOTICE + '订单已签收。'
    assert result['usage'] == {'actual': 17, 'estimated': 0, 'actual_calls': 1, 'estimated_calls': 0}


@pytest.mark.parametrize('chunks', [
    [AIMessageChunk('', response_metadata={'finish_reason': 'stop'})],
    [AIMessageChunk('   ', response_metadata={'finish_reason': 'stop'})],
    [AIMessageChunk('订单已签收。', response_metadata={'finish_reason': 'length'})],
    [AIMessageChunk('订单已签收。')],
    [AIMessageChunk('订单已签收。', additional_kwargs={'tool_calls': [{'id': 'bad'}]})],
    [AIMessageChunk('模拟' + 'x' * 19997, response_metadata={'finish_reason': 'stop'})],
    [AIMessageChunk('模拟' + '😀' * 16380, response_metadata={'finish_reason': 'stop'})],
])
async def test_notice_cannot_make_invalid_or_combined_oversized_raw_stream_successful(chunks):
    ctx, state, runtime, events = final_context(chunks=chunks)
    with pytest.raises(ServiceError):
        await finalize_answer(state, runtime)
    assert state['final_answer'] is None and not ctx.repository.messages and ctx.upstream is None


@pytest.mark.parametrize('failure', ['cancel', 'error', 'deadline'])
async def test_mock_notice_keeps_stream_cancellation_error_and_deadline_failure(failure):
    ctx, state, runtime, events = final_context()
    started = asyncio.Event()
    async def stream(messages):
        yield AIMessageChunk('订单')
        started.set()
        if failure == 'error':
            raise RuntimeError('offline stream failure')
        if failure == 'deadline':
            ctx.deadline = asyncio.get_running_loop().time() - 1
            yield AIMessageChunk('已签收', response_metadata={'finish_reason': 'stop'})
        else:
            await asyncio.Event().wait()
    ctx.model.astream = stream
    task = asyncio.create_task(finalize_answer(state, runtime))
    await started.wait()
    if failure == 'cancel':
        task.cancel()
    with pytest.raises(asyncio.CancelledError if failure == 'cancel' else ServiceError):
        await task
    assert state['final_answer'] is None and not ctx.repository.messages and ctx.upstream is None
