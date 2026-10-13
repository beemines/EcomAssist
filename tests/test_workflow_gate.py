"""知识闸和最终证据：错误放行、故障拒答、证据丢失均可被离线断言发现。"""
import json

import pytest
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from app.core.errors import InputTooLong
from tests.test_evidence import payload
from tests.test_workflow_routes import outer_graph, run_outer
from tests.workflow_fakes import workflow_call, workflow_runtime


@pytest.mark.asyncio
@pytest.mark.parametrize('data', [payload(()), payload(('低分资料',), score=.4)])
async def test_weak_knowledge_never_enters_agent(data):
    """空命中或真实重排低分在内容自评前拒绝，整条路径不进入 Agent。"""
    context = workflow_runtime(payload=data)
    trace, state = await run_outer(context)
    assert trace == ['resolve_reference','classify_intent','retrieve_knowledge','confidence_gate',
        'knowledge_fallback','log_response']
    assert len(context.sufficiency.calls) == 0
    assert context.repository.refusals[0]['source'] == 'retrieval_low_conf'
    assert state['turn_status'] == 'completed' and state['final_message_id'] == '103'


@pytest.mark.asyncio
@pytest.mark.parametrize('useful', [True, False])
async def test_sufficient_score_checks_content_before_agent(useful):
    """只有真实达标且内容自评有用的资料进入 Agent。"""
    context = workflow_runtime(payload=payload(('退货条件原文',)), useful=useful)
    trace, state = await run_outer(context)
    assert trace[:4] == ['resolve_reference','classify_intent','retrieve_knowledge','confidence_gate']
    assert trace[4] == ('agent' if useful else 'knowledge_fallback')
    assert context.sufficiency.calls[0][0] == '退货政策是什么？'
    assert context.faq_repository.calls == [('退货政策是什么？', '退货政策是什么？', '售后')]
    assert state['tool_trace'][0]['origin'] == 'workflow'
    assert state['citations'][0]['answer'] == '退货条件原文'
    stored = json.loads(context.repository.messages[1].content)
    assert 'n' not in stored['matches'][0]
    if not useful:
        assert context.repository.refusals[0]['source'] == 'self_check'


@pytest.mark.asyncio
async def test_retrieval_fault_is_error_not_low_confidence():
    """外部服务故障不执行拒答提交或 Agent。"""
    context = workflow_runtime(error=RuntimeError('离线向量故障'))
    with pytest.raises(RuntimeError, match='离线向量故障'):
        await run_outer(context)
    assert not context.repository.refusals


def agent_evidence(data, messages, *, budget=8000):
    """调用生产多结果构建器，缺失接口明确表现为 RED 断言。"""
    from app.core import evidence
    assert hasattr(evidence, 'build_agent_evidence'), 'multi-result evidence implementation missing'
    return evidence.build_agent_evidence(system=SystemMessage('系统'), turns=[], current=HumanMessage('当前问题'),
        current_tool_messages=messages, payloads=data, budget=budget)


def test_multi_result_evidence_deduplicates_ranks_and_keeps_business():
    """跨 FAQ 结果按 chunk 身份取强分、最终统一编号，业务申请结果均保留。"""
    a = payload(('旧弱原文','另一个规则'), score=.8)
    b = payload(('新强原文',), score=.95)
    business = {'found': True, 'order_id': 'A-42', 'status': '待发货', 'mock': True}
    calls = [workflow_call('query_faq', {'keyword': '当前'}, 'faq-1'),
        ToolMessage(json.dumps(a, ensure_ascii=False), tool_call_id='faq-1'),
        workflow_call('query_order', identifier='order-1'),
        ToolMessage(json.dumps(business, ensure_ascii=False), tool_call_id='order-1'),
        workflow_call('query_faq', {'keyword': '问题'}, 'faq-2'),
        ToolMessage(json.dumps(b, ensure_ascii=False), tool_call_id='faq-2')]
    packet = agent_evidence([a,business,b], calls)
    assert [(c.n, c.chunk_id, c.answer) for c in packet.citations] == [
        (1,'100','新强原文'), (2,'101','另一个规则')]
    assert [m.type for m in packet.messages][-6:] == ['ai','tool','ai','tool','ai','tool']
    assert json.loads(packet.messages[-3].content)['status'] == '待发货'
    assert 'n' not in json.loads(calls[-1].content)['matches'][0]
    final = json.loads(packet.messages[-1].content)
    assert [(item['n'], item['id'], item['answer']) for item in final['matches']] == [
        (1,'100','新强原文'), (2,'101','另一个规则')]
    earlier = json.loads(packet.messages[-5].content)
    assert earlier['evidence_merged'] and earlier['retrieval']['match_count'] == 0


def test_multi_result_evidence_counts_all_current_results():
    """不能只给 FAQ 证据计费而漏掉巨大业务结果或工具入参。"""
    business = {'found': True, 'details': '数据' * 3000}
    calls = [workflow_call(identifier='order-1'),
        ToolMessage(json.dumps(business, ensure_ascii=False), tool_call_id='order-1')]
    with pytest.raises(InputTooLong):
        agent_evidence([business], calls, budget=1000)


def test_multi_result_limits_top_ten_before_whole_block_budget_selection():
    """至多十块先按真实重排排序，过大块可跳过，最终引用是实际 Prompt 集合。"""
    data = payload(tuple(['巨大资料' * 3000, *['规则' + str(i) for i in range(1, 12)]]), score=2)
    messages = [workflow_call('query_faq', {'keyword': '当前'}, 'faq'),
        ToolMessage(json.dumps(data, ensure_ascii=False), tool_call_id='faq')]
    packet = agent_evidence([data], messages)
    assert len(packet.citations) == 9
    assert sorted(c.chunk_id for c in packet.citations) == [str(i) for i in range(101, 110)]
    assert sorted(c.n for c in packet.citations) == list(range(1, 10))
    assert [(c.n, c.answer) for c in packet.citations] == [
        (item['n'], item['answer']) for item in json.loads(packet.messages[-1].content)['matches']]


@pytest.mark.asyncio
async def test_knowledge_gate_runs_before_any_visible_delta():
    """自定义流只在闸后输出兜底 delta；分类/检索不能泄露可见正文。"""
    from app.workflow.state import new_turn_state
    context = workflow_runtime()
    state = new_turn_state(conversation_id='1', user_message_id=7, raw_question='库外政策？',
        category=None, messages=[HumanMessage('库外政策？')])
    seen, delta = [], []
    async for kind, event in outer_graph().astream(state, {'configurable': {'thread_id': '1'}},
        context=context, stream_mode=['updates', 'custom']):
        if kind == 'updates':
            seen.extend(event)
        elif event['event'] == 'delta':
            delta.append(event['data']['text'])
            assert seen == ['resolve_reference','classify_intent','retrieve_knowledge','confidence_gate']
    assert len(delta) == 1


@pytest.mark.asyncio
async def test_non_rerank_scores_cannot_bypass_online_gate():
    """BM25/RRF 的高数字不冒充真实重排分，也不落入低置信池。"""
    context = workflow_runtime(payload=payload(('文本',), strategy='bm25', score=99))
    with pytest.raises(ValueError, match='rerank'):
        await run_outer(context)
    assert not context.repository.refusals
