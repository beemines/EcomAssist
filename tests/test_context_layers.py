"""Context views must preserve raw users and complete native tool turns."""
import json
from dataclasses import replace

import pytest

from app.context.tokens import ESTIMATOR_VERSION
from app.context.types import ContextAnchors, ContextBudget
from app.core.errors import InputTooLong
from app.repositories.records import MessageRecord


def budget(**changes):
    values = dict(window=10000, phases={}, desired=5000, history=5000,
                  layer1=3500, layer2=1500, evidence=1000, summary=1000,
                  safety=300, estimator_version=ESTIMATOR_VERSION)
    values.update(changes)
    return ContextBudget(**values)


def turn(start=1, *, user='请查订单', answer='答' * 81, results=('x' * 160, 'x' * 161)):
    rows = [MessageRecord(start, 'user', user, None, None)]
    for index, result in enumerate(results):
        call_id = f'call-{start}-{index}'
        calls = [{'id': call_id, 'type': 'function', 'function': {
            'name': 'query_order', 'arguments': '{"order_id":"ORD-123"}'}}]
        rows.extend([MessageRecord(start + 1 + 2 * index, 'assistant', None, calls, None),
                     MessageRecord(start + 2 + 2 * index, 'tool', result, None, call_id)])
    rows.append(MessageRecord(start + len(rows), 'assistant', answer, None, None))
    return rows


def test_layer1_is_exact_and_layer2_user_is_exact():
    from app.context.layers import plan_layers

    large = json.dumps({'order_id': 'ORD-123', 'model': 'M-甲', 'mock': True,
                        'status': '已签收', 'details': '长' * 200}, ensure_ascii=False)
    old = turn(results=('x' * 160, large))
    recent = turn(7, user=' 原文\n不要改🙂 ', results=('原始结果',))
    plan = plan_layers(old + recent, ContextAnchors(None, 6), budget(), current_user_id=11)
    assert [(m.id, m.role, m.content, m.tool_call_id) for m in plan.layer1] == [
        (str(r.id), r.role, r.content, r.tool_call_id) for r in recent]
    assert json.loads(plan.layer1[1].tool_calls_json) == recent[1].tool_calls
    assert plan.layer2[0].content == '请查订单'
    assert plan.layer2[2].content == 'x' * 160
    assert plan.layer2[-1].content == '答' * 80 + '后文已截短'
    archived = json.loads(plan.layer2[4].content)
    assert archived == {'archived': True, 'tool': 'query_order', 'status': 'success',
                        'sql_id': '5', 'tool_call_id': 'call-1-1', 'order_id': 'ORD-123',
                        'model': 'M-甲', 'mock': True}
    assert '\n' not in plan.layer2[4].content
    recent[1].tool_calls[0]['function']['arguments'] = '{}'
    assert json.loads(plan.layer1[1].tool_calls_json)[0]['function']['arguments'] == '{"order_id":"ORD-123"}'


@pytest.mark.parametrize('size', [79, 80, 81])
def test_layer2_answer_unicode_boundary(size):
    from app.context.layers import plan_layers

    rows = turn(answer='🙂' * size, results=())
    plan = plan_layers(rows, ContextAnchors(None, 2), budget(), current_user_id=3)
    assert plan.layer2[-1].content == '🙂' * min(size, 80) + ('后文已截短' if size > 80 else '')


def test_trim_aligns_to_complete_tool_turns():
    from app.context.layers import plan_layers

    rows = turn(results=('旧' * 150, '旧' * 150)) + turn(7, results=())
    plan = plan_layers(rows, ContextAnchors(None, None), budget(layer1=180), current_user_id=9)
    assert [m.id for m in plan.layer1] == ['7', '8']
    assert [m.id for m in plan.layer2] == ['1', '2', '3', '4', '5', '6']
    assert plan.anchors == ContextAnchors(None, 6)
    assert plan.downgrade_ranges == ((1, 6),)
    assert [(m.role, m.tool_call_id) for m in plan.layer2[1:5]] == [
        ('assistant', None), ('tool', 'call-1-0'), ('assistant', None), ('tool', 'call-1-1')]


def test_exact_layer1_threshold_does_not_downgrade():
    from app.context.layers import plan_layers

    # user 'q': 8+2+1=11; assistant 'a': 8+3+1=12.
    rows = turn(user='q', answer='a', results=())
    plan = plan_layers(rows, ContextAnchors(None, None), budget(layer1=23), current_user_id=3)
    assert [m.id for m in plan.layer1] == ['1', '2']
    assert plan.anchors.layer1_from is None


def test_oversize_backlog_errors_without_dropping_user():
    from app.context.layers import plan_layers

    rows = turn(user='用户原话' * 100, results=())
    with pytest.raises(InputTooLong, match='history'):
        plan_layers(rows, ContextAnchors(None, None), budget(history=300, layer1=200), current_user_id=3)
    assert rows[0].content == '用户原话' * 100


def test_layer2_can_borrow_unused_layer1_without_deleting_backlog():
    from app.context.layers import plan_layers

    plan = plan_layers(turn(results=()), ContextAnchors(None, 2),
                       budget(layer2=10, history=500), current_user_id=3)
    assert [m.id for m in plan.layer2] == ['1', '2']
    assert plan.layer2_tokens > 10


def test_current_user_and_future_rows_are_not_history():
    from app.context.layers import plan_layers

    rows = turn(results=()) + [MessageRecord(3, 'user', '当前', None, None),
                              MessageRecord(4, 'assistant', '未来', None, None)]
    plan = plan_layers(rows, ContextAnchors(None, None), budget(), current_user_id=3)
    assert [m.id for m in plan.layer1] == ['1', '2']


def test_duplicate_call_id_is_not_a_completed_boundary():
    from app.repositories.context import _completed_boundaries

    rows = turn()
    rows[3] = replace(rows[3], tool_calls=rows[1].tool_calls)
    rows[4] = replace(rows[4], tool_call_id=rows[2].tool_call_id)
    assert _completed_boundaries(rows) == set()


@pytest.mark.parametrize('damage', ['missing_result', 'wrong_id', 'duplicate_id'])
def test_failed_tool_residue_cannot_be_stitched_into_success(damage):
    from app.context.layers import plan_layers
    from app.context.view import build_snapshot, compose_call
    from langchain_core.messages import HumanMessage, SystemMessage

    rows = turn()
    if damage == 'missing_result':
        del rows[2]
    elif damage == 'wrong_id':
        rows[2] = replace(rows[2], tool_call_id='wrong')
    else:
        rows[3] = replace(rows[3], tool_calls=rows[1].tool_calls)
        rows[4] = replace(rows[4], tool_call_id=rows[2].tool_call_id)
    source = rows + turn(7, results=())
    plan = plan_layers(source, ContextAnchors(None, None), budget(), current_user_id=9)
    assert [m.id for m in plan.layer1] == [str(row.id) for row in source]
    frozen = build_snapshot(plan, (), conversation_id='1', user_message_id='9', budget=budget())
    packet = compose_call(frozen, system=SystemMessage('s'), current=HumanMessage('新问题'),
                          attachment={}, pending=(), tools=(), output_tokens=512)
    assert [m.id for m in packet.messages[1:-2]] == ['1', '7', '8']
    audit = json.loads(packet.messages[-1].content)['history_audit']
    assert [item['id'] for item in audit] == [str(row.id) for row in rows[1:]]
    assert audit[0]['tool_calls_json'] == plan.layer1[1].tool_calls_json


def test_cancelled_user_remains_verbatim_and_audit_keeps_raw_fields_after_downgrade():
    from app.context.layers import plan_layers
    from app.context.view import build_snapshot, compose_call
    from langchain_core.messages import HumanMessage, SystemMessage

    rows = turn(user='已取消原话\n🙂')[:2] + turn(7, results=())
    plan = plan_layers(rows, ContextAnchors(None, None), budget(layer1=1), current_user_id=9)
    assert plan.layer2[0].content == '已取消原话\n🙂'
    assert plan.layer2[1].content is None
    frozen = build_snapshot(plan, (), conversation_id='1', user_message_id='9', budget=budget())
    packet = compose_call(frozen, system=SystemMessage('s'), current=HumanMessage('下一轮'),
                          attachment={}, pending=(), tools=(), output_tokens=512)
    assert [m.content for m in packet.messages[1:-2]] == ['已取消原话\n🙂', '请查订单', '答' * 80 + '后文已截短']
    audit = json.loads(packet.messages[-1].content)['history_audit']
    assert audit == [{'kind': 'interrupted', 'id': '2', 'role': 'assistant', 'content': None,
                      'tool_calls_json': plan.layer2[1].tool_calls_json, 'tool_call_id': None}]


def test_unmatched_tail_cannot_advance_layer1_boundary():
    from app.context.layers import plan_layers

    plan = plan_layers(turn()[:2], ContextAnchors(None, None), budget(layer1=1), current_user_id=3)
    assert plan.anchors.layer1_from is None
    assert [m.id for m in plan.layer1] == ['1', '2']


def test_malformed_record_errors_instead_of_hiding_source():
    from app.context.layers import plan_layers

    rows = turn()[:2]
    rows[1] = replace(rows[1], tool_calls=[{'broken': True}])
    with pytest.raises(ValueError):
        plan_layers(rows, ContextAnchors(None, None), budget(), current_user_id=3)


def test_audit_cost_also_advances_complete_layer1_boundary():
    from app.context.layers import plan_layers

    rows = turn(user='取消', answer='ok')[:2] + turn(7, user='q', answer='a', results=())
    rows[1].tool_calls[0]['function']['arguments'] = json.dumps({'order_id': 'x' * 1000})
    plan = plan_layers(rows, ContextAnchors(None, None), budget(layer1=100), current_user_id=9)
    assert plan.anchors.layer1_from == 8
    assert plan.layer1 == ()
    assert [m.id for m in plan.layer2] == ['1', '2', '7', '8']


@pytest.mark.parametrize('result,want', [
    ({'error': {'code': 'timeout'}, 'details': 'x' * 200}, 'error'),
    ({'status': 'error', 'details': 'x' * 200}, 'error'),
    ({'success': False, 'details': 'x' * 200}, 'error'),
    ('x' * 161, 'unknown'),
])
def test_large_failure_or_unstructured_result_never_claims_success(result, want):
    from app.context.layers import plan_layers

    content = json.dumps(result) if isinstance(result, dict) else result
    plan = plan_layers(turn(results=(content,)), ContextAnchors(None, 4), budget(), current_user_id=5)
    archived = json.loads(plan.layer2[2].content)
    assert archived['status'] == want
    assert archived['order_id'] == 'ORD-123'


def test_history_exact_hard_limit_and_one_less_errors():
    from app.context.layers import plan_layers

    rows = turn(user='q', answer='a', results=())
    assert plan_layers(rows, ContextAnchors(None, None), budget(history=23), current_user_id=3).layer1_tokens == 23
    with pytest.raises(InputTooLong):
        plan_layers(rows, ContextAnchors(None, None), budget(history=22), current_user_id=3)
