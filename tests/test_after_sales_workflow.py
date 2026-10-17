"""订单优先图的实际分支、证据与暂停，不调用真实上游。"""
import asyncio
import json
from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from app.orders.demo import DemoOrderProvider
from app.retrieval.multi import WorkflowRetrieval
from app.workflow.graph import build_workflow_graph
from app.workflow.state import new_turn_state
from tests.test_evidence import payload
from tests.test_workflow_routes import outer_graph
from tests.workflow_fakes import apply_workflow_update, workflow_runtime


def context(intent='退款退货', *, data=None):
    """真实只读订单与边界替身提供确定政策，显式注入新增依赖。"""
    ctx = workflow_runtime(intent=intent, payload=data or payload(('七天内退货需完好；质量问题可申请保修。',)))
    ctx.order_provider, ctx.user_id = DemoOrderProvider(), 'demo-user'
    class Expand:
        usage = {'actual': 10, 'estimated': 0, 'actual_calls': 1, 'estimated_calls': 0}
        async def expand(self, question, order):
            """只在已选订单后给出独立检索角度。"""
            assert order.order_id in ('1001', '1002')
            return (question, order.model + '退货及保修政策')
    class Retrieve:
        async def retrieve(self, *, question, queries, category, rerank_question=None):
            """将原过滤条件和查询保存供真实图行为断言。"""
            ctx.retrieved = (question, queries, category)
            ctx.rerank_question = rerank_question
            return WorkflowRetrieval(data if data is not None else payload(('七天内退货需完好；质量问题可申请保修。',)), {'query_count': len(queries)})
    ctx.expander, ctx.workflow_retriever = Expand(), Retrieve()
    return ctx


async def invoke(ctx, question, *, graph=None, history=()):
    """采集生产父图实际节点更新。"""
    graph = graph or outer_graph()
    initial = new_turn_state(conversation_id='1', user_message_id=7, raw_question=question,
        category='售后', messages=[*history, HumanMessage(question)])
    trace, result = [], dict(initial)
    async for event in graph.astream(initial, {'configurable': {'thread_id': '1'}}, context=ctx, stream_mode='updates'):
        for name, update in event.items():
            trace.append(name)
            if name != '__interrupt__':
                apply_workflow_update(result, update)
    return trace, result


async def test_faq_no_order_no_expansion():
    """FAQ错误走选单或扩写时，节点轨迹或可信单查询参数会改变。"""
    ctx = context('商品咨询')
    trace, result = await invoke(ctx, '一般退货政策是什么？')
    assert trace == ['resolve_reference', 'classify_intent', 'retrieve_knowledge', 'confidence_gate', 'agent', 'log_response']
    assert ctx.retrieved == ('一般退货政策是什么？', ('一般退货政策是什么？',), '售后')
    assert result['tool_call_count'] == 1


async def test_refund_loads_order_before_expand_and_policy():
    """漏查单、顺序颠倒、丢过滤或工具配对都会破坏实际结果。"""
    ctx = context()
    trace, result = await invoke(ctx, '订单1001能退吗？')
    assert trace == ['resolve_reference', 'classify_intent', 'resolve_order', 'load_order', 'expand_queries', 'retrieve_policies', 'confidence_gate', 'agent', 'log_response']
    assert result['order_snapshot']['order_id'] == '1001'
    assert result['tool_call_count'] == 2 and result['retrieval_audit'] == {'query_count': 2}
    assert ctx.retrieved[2] == '售后'
    assert ctx.rerank_question == '电子商品于2026-10-13签收，能退吗？退货期限与适用条件是什么？'
    current = result['messages'][1:-1]
    assert [m.type for m in current] == ['ai', 'tool', 'ai', 'tool']
    assert current[1].tool_call_id == current[0].tool_calls[0]['id']
    assert json.loads(current[1].content)['order_id'] == '1001'
    assert current[3].tool_call_id == current[2].tool_calls[0]['id']


async def test_missing_order_interrupts_before_agent():
    """缺单必须暂停，唯一候选也不能自动选单。"""
    ctx = context()
    trace, result = await invoke(ctx, '它能退吗？')
    assert trace == ['resolve_reference', 'classify_intent', 'resolve_order', 'prepare_order_selection', '__interrupt__']
    assert result['turn_status'] == 'awaiting_order' and result['final_message_id'] is None
    assert not ctx.repository.messages and not hasattr(ctx, 'retrieved')


async def test_repair_is_not_refund():
    """维修也必须有政策闸，但不能获得退款许可。"""
    ctx = context('售后')
    trace, result = await invoke(ctx, '订单1002需要寄修')
    assert 'retrieve_policies' in trace and trace.index('confidence_gate') < trace.index('agent')
    assert result['refund_offer'] is None


async def test_weak_policy_keeps_raw_question_and_skips_agent():
    """规范化问题检索，低分池仍存原话；弱证据不得进入Agent。"""
    ctx = context(data=payload(('低分',), score=.1))
    trace, result = await invoke(ctx, '订单1001能退吗？')
    assert 'agent' not in trace and result['quality']['source'] == 'retrieval_low_conf'
    assert ctx.repository.refusals[0]['raw_question'] == '订单1001能退吗？'


async def test_resume_does_not_repeat_understanding_or_classification():
    """同一暂停根恢复只查所选订单，消费预算和用户身份延续。"""
    ctx = context()
    graph = outer_graph()
    _, paused = await invoke(ctx, '这个能退吗？', graph=graph)
    before = ctx.model.intents
    result = await graph.ainvoke(Command(resume={'order_id': '1001'}),
        {'configurable': {'thread_id': '1'}}, context=ctx)
    assert ctx.model.intents == before
    assert result['user_message_id'] == '7' and result['tool_call_count'] == 2
    assert result['usage']['actual'] >= paused['usage']['actual']


@pytest.mark.parametrize('stage', ['understanding', 'classification', 'expansion'])
@pytest.mark.parametrize('failure', ['invalid', 'timeout'])
async def test_attempted_model_stages_record_consumption(stage, failure):
    """坏JSON和超时均已发生调用，不能在阶段usage上变成免费成功。"""
    from app.workflow.understanding import QueryUnderstanding
    from app.workflow.intent import IntentClassifier
    from app.workflow.expansion import QueryExpander
    from app.core.errors import ServiceError
    from tests.workflow_fakes import ScriptedWorkflowModel
    reply = TimeoutError() if failure == 'timeout' else AIMessage('{"invalid":true}',
        response_metadata={'finish_reason': 'stop'},
        usage_metadata={'input_tokens': 12, 'output_tokens': 8, 'total_tokens': 20})
    model = ScriptedWorkflowModel(intent_replies=[reply])
    cls = {'understanding': QueryUnderstanding, 'classification': IntentClassifier, 'expansion': QueryExpander}[stage]
    service = cls(model, input_budget=8000, timeout_seconds=1)
    with pytest.raises(ServiceError):
        if stage == 'understanding':
            await service.resolve('订单1001能退吗？', [])
        elif stage == 'classification':
            await service.classify('订单1001能退吗？')
        else:
            await service.expand('订单1001能退吗？', await DemoOrderProvider().get_order(user_id='demo-user', order_id='1001'))
    if failure == 'invalid':
        assert service.usage == {'actual': 20, 'estimated': 0, 'actual_calls': 1, 'estimated_calls': 0}
    else:
        assert service.usage['estimated_calls'] == 1 and service.usage['estimated'] > 2048


async def test_real_agent_conditional_answer_freezes_offer_after_sql():
    """实际Agent四字段控制、当前引用及SQL提交共同产生待审入口。"""
    from app.workflow.agent import build_agent_graph
    from tests.workflow_fakes import ScriptedWorkflowModel
    ctx = context()
    ctx.decision_model = ScriptedWorkflowModel([AIMessage(json.dumps({
        'reply_mode': 'answer', 'suggested_actions': [], 'refund_decision': 'needs_review',
        'decision_reason': '商品完好及二次销售条件需审核'}), response_metadata={'finish_reason': 'stop'})])
    ctx.model = ScriptedWorkflowModel(final_chunks=[AIMessageChunk('模拟订单可按政策申请，商品完好条件仍需审核[1]。'),
        AIMessageChunk('', response_metadata={'finish_reason': 'stop'})])
    graph = build_workflow_graph(build_agent_graph(), checkpointer=InMemorySaver())
    _, result = await invoke(ctx, '订单1001能退吗？', graph=graph)
    assert result['refund_decision'] == 'needs_review'
    assert result['refund_offer']['assistant_message_id'] == result['final_message_id']
    assert result['refund_offer']['policy_snapshot'] == result['evidence_payload']
    assert ctx.repository.messages[-1].content == result['final_answer']
    assert [c['n'] for c in result['citations']] == [1]
    assert 'query_faq' not in {(t['function']['name'] if isinstance(t, dict) else t.name) for t in ctx.decision_model.bound_tools[0]}


async def test_all_policy_lanes_share_one_timeout_and_faults_never_pool():
    """整段FAQ只有一次期限，部分召回不能成为弱证据或退款许可。"""
    from app.core.errors import ServiceError
    ctx = context()
    ctx.settings.faq_timeout_seconds = .01
    class Slow:
        async def retrieve(self, **kwargs):
            """外部聚合检索尚未完成，真实asyncio期限应取消它。"""
            await asyncio.sleep(.2)
            return WorkflowRetrieval(payload(('规则',)), {})
    ctx.workflow_retriever = Slow()
    with pytest.raises(ServiceError) as caught:
        await invoke(ctx, '订单1001能退吗？')
    assert caught.value.code == 'upstream_timeout'
    assert not ctx.repository.refusals and ctx.model.decisions == 0


async def test_understanding_consumes_complete_history_and_classifies_resolved():
    """不是只接通服务名称：规范问题进入分类/检索，SQL原话及身份不改。"""
    from app.workflow.understanding import Resolution
    ctx = context()
    class Understanding:
        usage = {'actual': 20, 'estimated': 0, 'actual_calls': 1, 'estimated_calls': 0}
        async def resolve(self, raw, history):
            """唯一可追溯订单来自已完成SQL轮次。"""
            assert raw == '它能退吗？' and [m.content for m in history] == ['订单1001是什么', '此前答复']
            return Resolution('订单1001能退吗？', True)
    ctx.understanding = Understanding()
    _, result = await invoke(ctx, '它能退吗？', history=[HumanMessage('订单1001是什么'), AIMessage('此前答复')])
    assert ctx.intent_model.intent_inputs[0][-1].content == '订单1001能退吗？'
    assert ctx.retrieved[0] == '订单1001能退吗？'
    assert result['messages'][2].content == '它能退吗？' and result['messages'][2].id == '7'
    assert result['stage_usage']['understanding']['actual'] == 20


async def test_sufficiency_usage_is_separate_from_32000_ledger():
    """内部充分性调用独立列账，不能宣称仅总账本覆盖全部模型调用。"""
    from app.core.sufficiency import SufficiencyService
    from tests.workflow_fakes import ScriptedWorkflowModel
    ctx = context()
    model = ScriptedWorkflowModel(intent_replies=[AIMessage(
        '{"useful":true,"reason":"政策足够给出条件答复","response_kind":"knowledge"}',
        response_metadata={'finish_reason': 'stop'}, usage_metadata={'input_tokens': 30, 'output_tokens': 10, 'total_tokens': 40})])
    ctx.sufficiency = SufficiencyService(model, input_budget=8000, timeout=1, minimum_rerank_score=.5)
    _, result = await invoke(ctx, '订单1001能退吗？')
    assert result['stage_usage']['sufficiency']['actual'] == 40
    sent = json.loads(model.intent_inputs[0][-1].content)
    assert sent['order_context']['order_id'] == '1001'
    assert not any(key in sent['order_context'] for key in ('resale_condition', 'refund_reason'))
    assert result['usage']['actual'] == 11


async def test_empty_owned_orders_finishes_without_policy_or_pause():
    """当前身份没有候选时给明确提示，不能生成无卡片的死暂停。"""
    ctx = context()
    ctx.user_id = 'unknown-user'
    trace, result = await invoke(ctx, '它能退吗？')
    assert '__interrupt__' not in trace and 'retrieve_policies' not in trace and 'agent' not in trace
    assert result['turn_status'] == 'completed' and '未找到可办理订单' in result['final_answer']
    assert not ctx.repository.refusals and result['refund_offer'] is None


@pytest.mark.parametrize('ending', ['timeout', 'cancel'])
async def test_concurrent_failed_assessment_emits_own_estimate(ending):
    """真实服务共享时，节点失败usage事件不能串入另一会话的actual40。"""
    from app.core.sufficiency import SufficiencyService
    from app.core.errors import ServiceError
    from app.workflow.nodes import assess_sufficiency
    from tests.test_evidence import build
    from tests.test_sufficiency import ConcurrentAssessmentModel
    model = ConcurrentAssessmentModel(ending)
    shared = SufficiencyService(model, input_budget=8000, minimum_rerank_score=.5)
    a, b = context(), context()
    a.sufficiency = b.sufficiency = shared
    state_a = new_turn_state(conversation_id='1', user_message_id=7, raw_question='A请求的退货规则',
        category=None, messages=[HumanMessage('A请求的退货规则')])
    state_b = {**state_a, 'conversation_id': '2', 'resolved_question': 'B请求的退货规则'}
    state_a['route'] = state_b['route'] = 'knowledge'
    events = []
    task = asyncio.create_task(assess_sufficiency(state_a, SimpleNamespace(context=a, stream_writer=events.append), build()))
    try:
        await asyncio.wait_for(model.started.wait(), 1)
        decision, stages = await assess_sufficiency(state_b,
            SimpleNamespace(context=b, stream_writer=lambda event: None), build())
        assert decision.useful and stages['sufficiency']['actual'] == 40
        if ending == 'cancel':
            task.cancel()
        else:
            model.release.set()
        with pytest.raises(asyncio.CancelledError if ending == 'cancel' else ServiceError):
            await task
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
    failure = events[0]['data']['stage_usage']['sufficiency']
    assert failure['actual'] == failure['actual_calls'] == 0
    assert failure['estimated_calls'] == 1 and failure['estimated'] > 2048
    assert events[0]['data']['usage'] == state_a['usage']
