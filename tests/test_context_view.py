"""Freeze each turn's history and account for the actual outgoing attachment."""
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
import json

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from app.context.types import ContextAnchors, SummarySegment
from app.core.errors import InputTooLong
from tests.test_context_layers import budget, turn


def snapshot(*, rows=(), anchors=None, segments=(), limits=None):
    from app.context.layers import plan_layers
    from app.context.view import build_snapshot

    limits = limits or budget()
    plan = plan_layers(rows, anchors or ContextAnchors(None, None), limits, current_user_id=99)
    return build_snapshot(plan, segments, conversation_id='42', user_message_id='99', budget=limits)


def segment(seq, body='摘要'):
    return SummarySegment(seq, seq * 10 - 9, seq * 10, body, datetime(2026, 10, 17, tzinfo=timezone.utc))


def test_summary_race_cannot_change_snapshot():
    source = [segment(1)]
    before = snapshot(anchors=ContextAnchors(10, 10), segments=source)
    expected = snapshot(anchors=ContextAnchors(10, 10), segments=(segment(1),))
    source.append(segment(2))
    assert before.summaries == (segment(1),)
    assert before.anchors == ContextAnchors(10, 10)
    assert before == expected
    with pytest.raises(FrozenInstanceError):
        before.anchors = ContextAnchors(20, 20)


def test_summary_selects_latest_complete_suffix_with_metadata_budgeted():
    source = [segment(1, '旧' * 20), segment(2, '新' * 20)]
    result = snapshot(anchors=ContextAnchors(20, 20), segments=source, limits=budget(summary=115))
    assert result.summaries == (source[1],)
    assert result.omitted_summary_seqs == (1,)


def test_summary_whole_segment_too_large_is_omitted_not_truncated():
    result = snapshot(anchors=ContextAnchors(10, 10), segments=[segment(1, '长' * 300)],
                      limits=budget(summary=100))
    assert result.summaries == ()
    assert result.omitted_summary_seqs == (1,)


def test_compose_order_and_defensive_copies_and_stable_prefix():
    from app.context.view import compose_call

    frozen = snapshot(rows=turn(11, results=()), anchors=ContextAnchors(10, 10), segments=[segment(1)])
    system, current = SystemMessage('固定系统'), HumanMessage('当前原话', id='99')
    pending = [AIMessage('', tool_calls=[{'id': 'now', 'name': 'query_order', 'args': {'order_id': 'O1'}}]),
               ToolMessage('{"mock":true}', tool_call_id='now')]
    attachment = {'resolved_question': '当前原话', 'evidence': [{'text': '政策'}]}
    tools = [{'type': 'function', 'function': {'name': 'query_order', 'parameters': {'type': 'object'}}}]
    packet = compose_call(frozen, system=system, current=current, attachment=attachment,
                          pending=pending, tools=tools, output_tokens=512)
    messages = packet.messages
    assert [m.type for m in messages] == ['system', 'human', 'ai', 'human', 'human', 'ai', 'tool']
    assert [m.id for m in messages[1:4]] == ['11', '12', '99']
    assert sum(m.id == '99' for m in messages) == 1
    data = json.loads(messages[4].content)
    assert data['summaries'] == [{'seq': 1, 'from_msg_id': '1', 'upto_msg_id': '10', 'content': '摘要'}]
    assert data['data'] == attachment
    assert data['kind'] == 'context_data'
    attachment['evidence'][0]['text'] = '改'
    tools[0]['function']['name'] = '改'
    pending[0].tool_calls[0]['args']['order_id'] = '改'
    current.content = '改'
    system.content = '改'
    messages[1].content = '改'
    packet.tools[0]['function']['parameters']['type'] = '改'
    assert packet.messages[0].content == '固定系统'
    assert packet.messages[1].content == '请查订单'
    assert packet.messages[3].content == '当前原话'
    assert packet.messages[-2].tool_calls[0]['args']['order_id'] == 'O1'
    assert packet.tools[0]['function']['parameters']['type'] == 'object'
    other = compose_call(frozen, system=SystemMessage('固定系统'), current=HumanMessage('另一个问题'),
                         attachment={}, pending=(), tools=packet.tools, output_tokens=512)
    assert other.prefix_hash == packet.prefix_hash
    assert other.snapshot_id == frozen.snapshot_id


def test_packet_exact_window_boundary_and_full_attachment_accounting():
    from app.context.view import compose_call

    data = dict(system=SystemMessage('s'), current=HumanMessage('q'), attachment={'control': '原话' * 10},
                pending=(), tools=(), output_tokens=100)
    initial = compose_call(snapshot(), **data)
    required = initial.estimated_tokens + 100 + 300
    assert compose_call(snapshot(limits=budget(window=required)), **data).estimated_tokens == initial.estimated_tokens
    with pytest.raises(InputTooLong, match='window'):
        compose_call(snapshot(limits=budget(window=required - 1)), **data)


@pytest.mark.parametrize('where', ['current', 'attachment', 'pending', 'tools'])
def test_oversize_required_input_errors_without_truncation(where):
    from app.context.view import compose_call

    arguments = dict(system=SystemMessage('s'), current=HumanMessage('q'), attachment={},
                     pending=(), tools=(), output_tokens=512)
    if where == 'current':
        arguments['current'] = HumanMessage('中' * 500)
    elif where == 'attachment':
        arguments['attachment'] = {'evidence': '中' * 500}
    elif where == 'tools':
        arguments['tools'] = [{'description': '中' * 500}]
    else:
        arguments['pending'] = [AIMessage('', tool_calls=[{'id': 'a', 'name': 'q', 'args': {}}]),
                                ToolMessage('中' * 500, tool_call_id='a')]
    with pytest.raises(InputTooLong):
        compose_call(snapshot(limits=budget(window=1100)), **arguments)


def test_pending_rejects_orphans_and_duplicate_call_ids():
    from app.context.view import compose_call

    pair = [AIMessage('', tool_calls=[{'id': 'a', 'name': 'q', 'args': {}}]), ToolMessage('ok', tool_call_id='a')]
    for pending in ([pair[1]], pair * 2):
        with pytest.raises(ValueError):
            compose_call(snapshot(), system=SystemMessage('s'), current=HumanMessage('q'), attachment={},
                         pending=pending, tools=(), output_tokens=512)


def test_compose_rechecks_history_hard_cap():
    from app.context.view import compose_call

    frozen = snapshot(rows=turn(results=()))
    damaged = replace(frozen, budget=budget(history=1))
    with pytest.raises(InputTooLong, match='history'):
        compose_call(damaged, system=SystemMessage('s'), current=HumanMessage('q'), attachment={},
                     pending=(), tools=(), output_tokens=512)


def test_snapshot_accepts_frozen_nested_budget_without_deepcopy():
    limits = budget(phases={'final': {'F': 10, 'U': 100}})
    frozen = snapshot(limits=limits)
    assert frozen.budget.phases['final']['F'] == 10
    with pytest.raises(TypeError):
        frozen.budget.phases['final']['F'] = 1


def test_current_missing_id_uses_frozen_sql_id_without_mutating_input():
    from app.context.view import compose_call

    current = HumanMessage('q')
    packet = compose_call(snapshot(), system=SystemMessage('s'), current=current, attachment={},
                          pending=(), tools=(), output_tokens=512)
    assert packet.messages[-2].id == '99'
    assert current.id is None


def test_prefix_hash_includes_actual_system_name():
    from app.context.view import compose_call

    args = dict(current=HumanMessage('q'), attachment={}, pending=(), tools=(), output_tokens=512)
    first = compose_call(snapshot(), system=SystemMessage('same', name='one'), **args)
    second = compose_call(snapshot(), system=SystemMessage('same', name='two'), **args)
    assert first.prefix_hash != second.prefix_hash
