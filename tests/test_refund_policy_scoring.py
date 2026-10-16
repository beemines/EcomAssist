"""订单退款评分问题仅去除可信前缀，真实检索和闸保留原有边界。"""
from types import SimpleNamespace

import pytest
from langchain_core.messages import HumanMessage

from app.knowledge.types import ChunkRecord, VectorHit
from app.retrieval.types import RerankHit
from app.workflow import nodes
from app.workflow.state import new_turn_state
from tests.test_after_sales_workflow import context
from tests.test_multi_query_retrieval import workflow


QUESTION = '订单1001的MH-LP200能退货吗'
SCORING = '电子商品于2026-10-13签收，能退货吗？退货期限与适用条件是什么？'
QUERIES = (QUESTION,
    '智能猫砂盆 Max（MH-LP200）电子商品于2026-10-13签收的退货期限与适用条件是什么？',
    'MH-LP200已签收订单申请退货需满足的条件、完好状态要求及所需材料是什么？')
ORDER = {'user_id': 'demo-user', 'order_id': '1001', 'product_id': 'MH-LP200',
    'product_name': '智能猫砂盆 Max', 'model': 'MH-LP200', 'category': '电子商品',
    'status': '已签收', 'amount_cents': 19900, 'currency': 'CNY', 'signed_at': '2026-10-13',
    'as_of': '2026-10-15', 'mock': True, 'fixture_version': '2026-10-15-v2'}


async def run_retrieval(question=QUESTION, *, intent='退款退货', route='after_sales',
                        owner='demo-user', selected='1001', score=.04612918943166733,
                        signed_at='2026-10-13'):
    """外部索引/仓储/模型用边界替身，执行真实节点、多路检索、证据闸。"""
    rows = [ChunkRecord('售后', '适用范围',
        '自签收之日起7天内，商品完好、不影响二次销售支持无理由退货。定制类、生鲜类除外。',
        id=119, vectorize_status='done')]
    retriever, service, _, embedder, index, planner, reranker = workflow(
        [[VectorHit(119, .9)]] * 3, rows, [RerankHit(index=0, score=score)])
    plans = []
    original = service.finalize_candidates
    async def capture(**kwargs):
        plans.append(kwargs['plan'])
        return await original(**kwargs)
    service.finalize_candidates = capture
    ctx = context()
    ctx.workflow_retriever = retriever
    ctx.user_id = owner
    state = new_turn_state(conversation_id='1', user_message_id=305,
        raw_question='这个能退吗', category='售后', messages=[HumanMessage('这个能退吗', id='305')])
    state.update(resolved_question=question, intent=intent, route=route,
        retrieval_queries=[question, *QUERIES[1:]], order_snapshot={**ORDER, 'signed_at': signed_at},
        order_selection={'selected_order_id': selected})
    runtime = SimpleNamespace(context=ctx, stream_writer=lambda event: None)
    update = await nodes.retrieve_policies(state, runtime)
    quality = await nodes.confidence_gate({**state, **update}, runtime)
    return state, update, quality, ctx, embedder, index, planner, reranker, plans


async def test_exact305_changes_only_scoring_and_low_score_still_blocks():
    """错误使用原评分问句、改召回或放过低分都会破坏这条回归。"""
    state, update, quality, ctx, embedder, index, planner, reranker, plans = await run_retrieval()
    assert reranker.calls[0][0] == SCORING
    assert len(reranker.calls) == 1 and reranker.calls[0][2] == 10
    assert embedder.texts == list(QUERIES) and len(index.calls) == 3
    assert all(call[3] == '售后' for call in index.calls) and not planner.calls
    assert plans[0].standard == state['resolved_question'] == QUESTION
    assert update['retrieval_queries'] == list(QUERIES)
    assert update['retrieval_audit']['rerank_question'] == SCORING
    assert quality['quality']['source'] == 'retrieval_low_conf' and not ctx.sufficiency.calls


async def test_sufficient_score_content_check_still_uses_complete_question():
    """即使分数达标，政策充分性仍对原问与订单事实判断。"""
    _, _, quality, ctx, *rest = await run_retrieval(score=.8)
    assert ctx.sufficiency.calls[0][0] == QUESTION
    assert quality['quality']['useful']


@pytest.mark.parametrize('question,expected', [
    ('订单1001的MH-LP200不是质量问题，2026-10-13签收、199元，能退货吗？',
     '电子商品于2026-10-13签收，不是质量问题，2026-10-13签收、199元，能退货吗？退货期限与适用条件是什么？'),
    ('订单1001的智能猫砂盆 Max能退货吗', SCORING),
    ('订单10010的MH-LP200能退货吗', '订单10010的MH-LP200能退货吗'),
    ('订单1001的MH-LP200X能退货吗', '订单1001的MH-LP200X能退货吗'),
    ('订单1001的MH-LP2001能退货吗', '订单1001的MH-LP2001能退货吗'),
    ('订单1001的MH-LP200-新版能退货吗', '订单1001的MH-LP200-新版能退货吗'),
    ('订单1001的MH-LP200二代能退货吗', '订单1001的MH-LP200二代能退货吗'),
    ('订单1001的智能猫砂盆 Max升级版能退货吗', '订单1001的智能猫砂盆 Max升级版能退货吗'),
    ('订单1001的MH-LP200和MH-LP100哪个能退货', '订单1001的MH-LP200和MH-LP100哪个能退货'),
    ('订单1001的MH-LP200与其他商品相比能退货吗', '订单1001的MH-LP200与其他商品相比能退货吗'),
    ('订单1001的MH-LP200，订单1002也能退吗', '订单1001的MH-LP200，订单1002也能退吗'),
    ('MH-LP200能退货吗', 'MH-LP200能退货吗'),
    ('订单1001能退货吗', SCORING),
    ('订单1001的MH-LP200', '订单1001的MH-LP200'),
])
async def test_trusted_prefix_preserves_suffix_or_falls_back(question, expected):
    *_, reranker, plans = await run_retrieval(question)
    assert reranker.calls[0][0] == expected


async def test_exact358_bare_bound_order_uses_policy_scoring_without_changing_recalls():
    question = '订单1001能退吗'
    state, update, quality, ctx, embedder, index, planner, reranker, plans = await run_retrieval(question)
    expected = '电子商品于2026-10-13签收，能退吗？退货期限与适用条件是什么？'
    assert reranker.calls[0][0] == update['retrieval_audit']['rerank_question'] == expected
    assert len(reranker.calls) == 1 and len(index.calls) == 3
    assert embedder.texts == [question, *QUERIES[1:]]
    assert plans[0].standard == state['resolved_question'] == question
    assert quality['quality']['source'] == 'retrieval_low_conf' and not ctx.sufficiency.calls


@pytest.mark.parametrize('question', [
    '订单10010能退吗', '订单1001A能退吗', '订单1001-2能退吗',
    '订单1001的未知型号能退吗', '订单1001的MH-UNKNOWN能退吗',
    '订单1001二代能退吗', '订单1001能退吗，跟猫窝一样吗',
    '订单1001能退吗，订单1002也能退吗',
])
async def test_bare_order_extension_keeps_unknown_or_comparative_suffix(question):
    *_, reranker, plans = await run_retrieval(question)
    assert reranker.calls[0][0] == question


@pytest.mark.parametrize('question', [
    '订单1001的MH-LP200能退货吗，跟猫窝的规则一样吗',
    '订单1001的MH-LP200能退货吗，跟猫窝的规则不同吗',
    '订单1001的MH-LP200能退货吗，同猫窝的规则一致吗',
    '订单1001的MH-LP200能退货吗，猫窝的规则有何区别',
])
async def test_other_product_comparisons_retain_complete_scoring_question(question):
    """泛化焦点商品会丢失比较适用性，常见中文比较必须保持原评分问句。"""
    *_, reranker, plans = await run_retrieval(question)
    assert reranker.calls[0][0] == question


@pytest.mark.parametrize('overrides', [
    {'intent': '售后'}, {'intent': '商品咨询', 'route': 'knowledge'},
    {'owner': 'different-user'}, {'selected': '1002'},
    {'signed_at': None},
])
async def test_scoring_override_requires_refund_route_and_current_bound_order(overrides):
    *_, reranker, plans = await run_retrieval(**overrides)
    assert reranker.calls[0][0] == QUESTION


@pytest.mark.parametrize('scoring', ['', ' ', 'x' * 513, 42])
async def test_invalid_internal_scoring_question_rejected_before_dependencies(scoring):
    retriever, _, repo, embedder, index, planner, reranker = workflow([[], [], []])
    with pytest.raises(ValueError):
        await retriever.retrieve(question=QUESTION, queries=QUERIES, category=None,
                                 rerank_question=scoring)
    assert not repo.calls and not embedder.texts and not index.calls and not reranker.calls
