"""最终审查回归：真实父图公开边界、当前读取与失败调用账本。"""
import asyncio
import json
from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, ToolMessage
from langgraph.errors import NodeCancelledError

from app.core.errors import ServiceError
from app.workflow.persistence import checkpoint_config
from tests.fakes import decode_sse
from tests.test_workflow_agent import setup, run, control
from tests.test_workflow_api import workflow_app, request, intent, Store
from tests.workflow_fakes import ScriptedWorkflowModel, workflow_call


@pytest.mark.parametrize('valid', [False, True])
async def test_clarification_validated_before_any_public_delta(tmp_path, valid):
    """把验证移回流末尾即泄漏多片历史事实，实际HTTP和SQL会发现。"""
    parts = ['请提供', '订单号。'] if valid else ['台灯已经签收，', '签收日期为2026-10-13。']
    model = ScriptedWorkflowModel([control('clarification')], intent_replies=[intent('物流')],
        final_chunks=[*(AIMessageChunk(p) for p in parts), AIMessageChunk('', response_metadata={'finish_reason': 'stop'})])
    store = Store()
    async with workflow_app(tmp_path, model=model, store=store) as app:
        frames = decode_sse((await request(app, '查一下物流')).text)
        snapshot = await app.state.chat_service.graph.aget_state(checkpoint_config('1'))
        assert not app.state.chat_service._tasks
        app.state.chat_service.locks.acquire('1').release()
    assert model.closed
    if valid:
        assert ''.join(data['delta'] for name, data in frames if name == 'delta') == ''.join(parts)
        assert frames[-1][0] == 'done' and store.commits == 1
    else:
        assert not any(name in ('delta', 'done', 'actions', 'refund_offer') for name, _ in frames)
        assert frames[-1][1]['code'] == 'invalid_answer'
        assert store.commits == 0 and snapshot.values['turn_status'] != 'completed'


@pytest.mark.parametrize('raw,resolved,order', [
    ('它的物流呢？', '订单1001的物流呢？', '1001'),
    ('不要退款，我要查订单1002物流。', '不要退款，我要查订单1002物流。', '1002'),
])
async def test_parent_current_read_and_normalized_prompts(raw, resolved, order):
    """历史事实不作当前证据；规范问题进入两阶段提示且SQL原文身份不变。"""
    from langgraph.checkpoint.memory import InMemorySaver
    from app.workflow.graph import build_workflow_graph
    from app.workflow.agent import build_agent_graph
    from app.workflow.nodes import state_evidence
    from app.workflow.understanding import Resolution
    context, state = setup([control('clarification'), control('clarification')], question=raw,
        intent='物流', answer='模拟物流查询：包裹运输中。')
    prior = [HumanMessage('订单1001的状态', id='old-u'), workflow_call(args={'order_id': '1001'}),
        ToolMessage(json.dumps({'order_id': '1001', 'mock': True, 'status': '已签收'}), tool_call_id='call_1'),
        AIMessage('历史模拟结果：已签收。')]
    state['messages'] = prior + state['messages']
    original = state['messages'][-1].model_copy(deep=True)
    async def resolve(question, history):
        """只替换理解网络边界，实体验证由生产控制边界保留。"""
        return Resolution(resolved, True)
    context.understanding.resolve = resolve
    parent = build_workflow_graph(build_agent_graph(), checkpointer=InMemorySaver())
    result = await parent.ainvoke(state, context=context, config={'configurable': {'thread_id': raw}})
    assert result['turn_status'] == 'completed' and result['reply_mode'] == 'answer'
    assert result['tool_call_count'] == 1 and result['tool_trace'][0]['name'] == 'query_logistics'
    assert result['tool_trace'][0]['origin'] == 'workflow'
    assert context.repository.messages[0].tool_calls[0]['args'] == {'order_id': order}
    for messages in [*context.decision_model.tool_inputs, *context.model.stream_inputs,
                     state_evidence({**state, 'resolved_question': resolved}, context).messages]:
        current = next(m for m in messages if m.id == original.id)
        assert current.content == resolved
    assert result['messages'][len(prior)] == original and result['raw_question'] == raw


async def test_failed_matching_current_read_cannot_clarify_or_retry():
    """读取失败后不得以澄清掩盖依赖故障，也不能自动重试。"""
    context, state = setup([workflow_call('query_logistics', {'order_id': '1001'}), control('clarification')],
        question='订单1001物流', intent='物流', answer='请提供订单号。')
    from app.tools.types import ToolOutcome
    async def failed(call, registry):
        """外部读取不可用，仍走真实工具节点与审计配对。"""
        return ToolOutcome({'error': {'code': 'tool_execution_error', 'message': '不可用'}}, 'error', 1)
    context.executor.execute = failed
    with pytest.raises(ServiceError):
        await run(context, state)
    assert context.model.streams == 0 and len(context.repository.messages) == 2


@pytest.mark.parametrize('failure', ['invalid', 'partial', 'truncated', 'timeout', 'cancel', 'success'])
async def test_final_attempt_accounting_survives_every_exit(failure):
    """最终验证或取消之前漏记调用、实际usage重复累加都改变终端快照。"""
    chunks = [AIMessageChunk('请提供订单号。')]
    if failure == 'invalid':
        chunks = [AIMessageChunk('订单已经签收。')]
    if failure in ('partial', 'timeout', 'cancel'):
        chunks.append({'partial': RuntimeError('failed'), 'timeout': TimeoutError(), 'cancel': asyncio.CancelledError()}[failure])
    else:
        chunks.append(AIMessageChunk('', response_metadata={'finish_reason': 'length' if failure == 'truncated' else 'stop'},
            usage_metadata={'input_tokens': 11, 'output_tokens': 7, 'total_tokens': 18}))
    context, state = setup([control('clarification')], question='查订单', chunks=chunks)
    observations = []
    context.usage_observer = observations.append
    if failure == 'success':
        result, _ = await run(context, state)
        assert result['usage'] == observations[-1]['usage']
    else:
        with pytest.raises((ServiceError, asyncio.CancelledError, NodeCancelledError)):
            await run(context, state)
    usage = observations[-1]['usage'] if observations else state['usage']
    assert usage['actual_calls'] + usage['estimated_calls'] == 2
    if failure in ('invalid', 'truncated', 'success'):
        assert usage['actual'] == 18 and usage['actual_calls'] == 1 and usage['estimated_calls'] == 1
    assert context.model.closed


@pytest.mark.parametrize('reply', [AIMessage('not-json', response_metadata={'finish_reason': 'stop'}), TimeoutError(), asyncio.CancelledError()])
async def test_control_failed_attempt_is_observable(reply):
    """非法控制与等待故障没有图update也必须记录本次尝试。"""
    context, state = setup([reply], question='查订单')
    observations = []
    context.usage_observer = observations.append
    with pytest.raises((ServiceError, asyncio.CancelledError, NodeCancelledError)):
        await run(context, state)
    assert observations and observations[-1]['usage']['estimated_calls'] == 1


async def test_service_actual_usage_replaces_estimates_without_stale_overwrite(tmp_path):
    """实际父图custom/update排队后终端账本必须是四次调用的替换快照。"""
    reply = control('clarification')
    reply.usage_metadata = {'input_tokens': 13, 'output_tokens': 4, 'total_tokens': 17}
    model = ScriptedWorkflowModel([reply], intent_replies=[intent('订单')], final_chunks=[
        AIMessageChunk('请提供订单号。'), AIMessageChunk('', response_metadata={'finish_reason': 'stop'},
            usage_metadata={'input_tokens': 11, 'output_tokens': 7, 'total_tokens': 18})])
    async with workflow_app(tmp_path, model=model) as app:
        service = app.state.chat_service
        prepared = await service.prepare('1', '查订单')
        events = [event async for event in service.stream(prepared)]
        service.release(prepared)
        assert events[-1].event == 'done'
        assert prepared.audit['usage']['actual'] == 36  # 理解1+控制17+最终18。
        assert prepared.audit['usage']['actual_calls'] == 3
        assert prepared.audit['usage']['estimated_calls'] == 1  # 分类未回usage。


async def test_explicit_unselected_order_keeps_clarification_despite_history():
    """用户明确未选单时唯一历史订单也不能被强制读策略猜成本轮目标。"""
    raw = '还没选订单，没确定查哪一单的物流。'
    context, state = setup([control('clarification')], question=raw, intent='物流', answer='请提供订单号。')
    state['messages'] = [HumanMessage('订单1001物流'), workflow_call('query_logistics', {'order_id': '1001'}),
        ToolMessage(json.dumps({'order_id': '1001', 'mock': True, 'status': '已签收'}), tool_call_id='call_1'),
        AIMessage('历史模拟物流。'), *state['messages']]
    result, events = await run(context, state)
    assert result['reply_mode'] == 'clarification' and result['tool_call_count'] == 0
    assert result['final_answer'] == '请提供订单号。' and not context.repository.messages


async def test_received_actual_usage_survives_deadline_before_delta():
    """已收到实际usage的片段随后遇截止，必须采用actual且不能公开任何文字。"""
    from app.workflow.agent import finalize_answer
    context, state = setup([], question='查订单')
    state['reply_mode'] = 'clarification'
    observations, events = [], []
    context.usage_observer = observations.append
    class Model:
        async def astream(self, messages):
            """网络已返回片段，但此时整轮期限刚过。"""
            context.deadline = 0
            yield AIMessageChunk('请提供订单号。', response_metadata={'finish_reason': 'stop'},
                usage_metadata={'input_tokens': 11, 'output_tokens': 7, 'total_tokens': 18})
    context.model = Model()
    with pytest.raises(ServiceError) as caught:
        await finalize_answer(state, SimpleNamespace(context=context, stream_writer=events.append))
    assert caught.value.code == 'upstream_timeout'
    assert observations[-1]['usage'] == {'actual': 18, 'estimated': 0, 'actual_calls': 1, 'estimated_calls': 0}
    assert not any(event['event'] == 'delta' for event in events)
    assert context.upstream is None and not context.repository.messages


async def test_verified_factual_answer_streams_before_completion(tmp_path):
    """修复澄清缓冲不得把有当前成功读取的正常事实流也改成整段缓存。"""
    from app.workflow.agent import MOCK_DATA_NOTICE

    gate, waiting = asyncio.Event(), asyncio.Event()
    class Model(ScriptedWorkflowModel):
        async def astream(self, messages, **kwargs):
            """最终网络流在首片后阻塞，消费者必须已经收到该事实片段。"""
            try:
                yield AIMessageChunk('模拟物流查询：包裹运输中。')
                waiting.set()
                await gate.wait()
                yield AIMessageChunk('', response_metadata={'finish_reason': 'stop'})
            finally:
                self.closed = True
    model = Model([workflow_call('query_logistics', {'order_id': '1001'}), control()], intent_replies=[intent('物流')])
    store = Store()
    store.users['1'] = 'demo-user'
    async with workflow_app(tmp_path, model=model, store=store) as app:
        service = app.state.chat_service
        prepared = await service.prepare('1', '订单1001物流')
        events = service.stream(prepared)
        async def receive_factual_delta():
            async for event in events:
                if event.event == 'delta':
                    if event.data['delta'] == MOCK_DATA_NOTICE:
                        continue
                    assert '模拟物流' in event.data['delta']
                    return
                assert event.event != 'done'
            pytest.fail('Provider factual delta was not streamed.')

        await asyncio.wait_for(receive_factual_delta(), 2)
        await asyncio.wait_for(waiting.wait(), 2)
        assert not gate.is_set()
        gate.set()
        rest = [event async for event in events]
        service.release(prepared)
        assert rest[-1].event == 'done' and model.closed
