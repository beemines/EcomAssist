# 证据预算行为测试：整块保留、稳定引用以及完整历史与工具字段计费。
import importlib
import json

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.core.errors import InputTooLong
from tests.test_tool_history import tool_turn


# 延迟加载待实现模块，使缺失实现表现为明确的 RED 断言。
def builder():
    try:
        return importlib.import_module('app.core.evidence').build_evidence
    except ImportError:
        pytest.fail('bounded evidence builder is missing')


# 使用真实 FAQ 载荷结构构造完整证据，不从被测实现生成期望值。
def payload(answers=('规则甲', '规则乙', '规则丙', '规则丁'), *, strategy='hybrid_rerank', score=0.9):
    return {'found': bool(answers), 'matches': [
        {'id': 100 + i, 'question': f'问题{i}', 'answer': answer, 'category': '售后',
         'section_path': '退货/条件', 'score': score - i * .1,
         'score_kind': {'hybrid_rerank': 'rerank', 'dense': 'cosine', 'bm25': 'bm25', 'hybrid': 'rrf'}[strategy]}
        for i, answer in enumerate(answers)
    ], 'retrieval': {'strategy': strategy, 'candidate_count': 50, 'match_count': len(answers)}}


# 保留实际工具调用，参数长度也必须影响预算。
def request(size=1):
    return AIMessage('', tool_calls=[{'id': 'call-current', 'name': 'search_faq',
                                     'args': {'keyword': 'x' * size}, 'type': 'tool_call'}])


# 默认提供充分预算，允许各用例只改变关键边界。
def build(data=None, *, budget=100000, turns=(), call=None):
    return builder()(system=SystemMessage('系统'), turns=turns, current=HumanMessage('如何退货？'),
                     request=call or request(), payload=data if data is not None else payload(), budget=budget)


# 验证最强两条位于两端、编号不变、主键字符串化且实际工具正文与引用全集一致。
def test_evidence_edges_stable_numbers_exact_prompt_and_string_ids():
    original = payload()
    packet = build(original)
    shown = json.loads(packet.messages[-1].content)
    assert [c.n for c in packet.citations] == [1, 3, 4, 2]
    assert [(c.n, c.chunk_id) for c in packet.citations] == [(1, '100'), (3, '102'), (4, '103'), (2, '101')]
    assert [(m['n'], m['id']) for m in shown['matches']] == [(1, '100'), (3, '102'), (4, '103'), (2, '101')]
    assert [c.answer for c in packet.citations] == [m['answer'] for m in shown['matches']]
    assert packet.payload == shown and packet.best_score == .9 and packet.strategy == 'hybrid_rerank'
    assert 'n' not in original['matches'][0] and original['matches'][0]['id'] == 100


@pytest.mark.parametrize('text', ['x' * 11000, '😀' * 17000], ids=['character-limit', 'utf8-byte-limit'])
# 分别触发字符/UTF-8字节上限，任何正文只能整块保留或删除。
def test_serialized_json_limits_select_only_whole_blocks(text):
    packet = build(payload((text, '可用完整规则', text)))
    serialized = packet.messages[-1].content
    assert len(serialized) <= 20000 and len(serialized.encode('utf-8')) <= 65535
    assert all(c.answer in (text, '可用完整规则') for c in packet.citations)
    assert '可用完整规则' in [c.answer for c in packet.citations]
    assert len(packet.citations) < 3
    assert sorted(c.n for c in packet.citations) == list(range(1, len(packet.citations) + 1))


# 最强正文超限时选后续完整证据，编号只在选择结束后分配。
def test_oversized_best_skipped_and_numbering_assigned_after_selection():
    packet = build(payload(('x' * 21000, '规则乙', '规则丙')))
    assert [(c.n, c.chunk_id) for c in packet.citations] == [(1, '101'), (2, '102')]
    assert packet.best_score == .8


@pytest.mark.parametrize('answers,budget', [(('x' * 21000,), 100000), (('😀' * 17000,), 100000), (('规则' * 1000,), 1000)], ids=['character-limit', 'utf8-byte-limit', 'input-budget'])
# 全部候选装不下必须报告预算错误，不能伪造无命中。
def test_all_candidates_unfittable_is_budget_error_not_empty_evidence(answers, budget):
    with pytest.raises(InputTooLong):
        build(payload(answers), budget=budget)


# 旧工具历史仅整轮删除，当前调用参数与结果关联均计费。
def test_whole_history_trimmed_and_current_tool_fields_counted():
    recent = [HumanMessage('谢谢'), AIMessage('不客气')]
    packet = build(payload(('完整规则',)), budget=1000, turns=[tool_turn(2000), recent])
    assert [m.type for m in packet.messages] == ['system', 'human', 'ai', 'human', 'ai', 'tool']
    assert packet.messages[1:3] == recent and packet.messages[-1].tool_call_id == 'call-current'
    with pytest.raises(InputTooLong):
        build(payload(('完整规则',)), budget=1000, call=request(2000))


# 空工具分支保持用户消息；其他工具结果完整保留，不伪造知识引用。
def test_no_tool_branch_and_non_faq_business_payload():
    packet = builder()(system=SystemMessage('系统'), turns=[], current=HumanMessage('你好'),
                       request=None, payload=None, budget=1000)
    assert packet.payload == {} and packet.citations == [] and packet.best_score is None
    assert [m.type for m in packet.messages] == ['system', 'human']
    business = build({'found': True, 'order_id': 'synthetic', 'status': '待发货', 'mock': True})
    assert business.citations == [] and business.payload['status'] == '待发货'


# 非法半轮历史即使可以被预算删除仍应明确拒绝。
def test_invalid_history_is_not_silently_discarded():
    with pytest.raises(ValueError):
        build(turns=[[HumanMessage('半轮')]])
