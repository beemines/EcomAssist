"""A numeric reply fills only a visible, immediately preceding order-ID prompt."""
from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from app.core.errors import ServiceError
from app.repositories.records import MessageRecord
from app.workflow.entities import validate_resolved_entities, validate_snapshot_entities


def validate(raw, resolved, last_answer, snapshot_mode):
    if snapshot_mode:
        frozen = SimpleNamespace(summaries=(), omitted_summary_seqs=(), layer2=(), layer1=(
            MessageRecord(1, 'user', '物流信息异常', None, None),
            MessageRecord(2, 'assistant', last_answer, None, None)))
        validate_snapshot_entities(raw, resolved, frozen, ())
    else:
        validate_resolved_entities(raw, resolved,
            [HumanMessage('物流信息异常'), AIMessage(last_answer)])


@pytest.mark.parametrize('snapshot_mode', [False, True])
def test_current_number_supplies_order_id_after_exact_server_prompt(snapshot_mode):
    validate('1001', '订单1001物流信息异常', '请提供订单号。', snapshot_mode)


@pytest.mark.parametrize('snapshot_mode', [False, True])
@pytest.mark.parametrize('raw,resolved,last_answer', [
    ('1001', '订单1001物流信息异常', '请描述商品问题。'),
    ('1001', '订单2002物流信息异常', '请提供订单号。'),
    ('13900139000', '订单13900139000物流信息异常', '请提供订单号。'),
    ('1001元', '订单1001物流信息异常', '请提供订单号。'),
])
def test_numeric_order_reply_needs_the_prompt_and_exact_nonphone_identity(raw, resolved, last_answer, snapshot_mode):
    with pytest.raises(ServiceError):
        validate(raw, resolved, last_answer, snapshot_mode)


@pytest.mark.parametrize('trailing', [('1001',), ('1001', '1001')])
def test_repeating_a_failed_number_reply_keeps_its_visible_order_prompt(trailing):
    rows = [MessageRecord(1, 'user', '物流信息异常', None, None),
            MessageRecord(2, 'assistant', '请提供订单号。', None, None)]
    rows.extend(MessageRecord(i, 'user', value, None, None) for i, value in enumerate(trailing, 3))
    frozen = SimpleNamespace(summaries=(), omitted_summary_seqs=(), layer2=(), layer1=tuple(rows))
    validate_snapshot_entities('1001', '订单1001物流信息异常', frozen, ())


def test_an_intervening_changed_user_topic_cannot_reuse_old_order_prompt():
    rows = [MessageRecord(1, 'user', '物流信息异常', None, None),
            MessageRecord(2, 'assistant', '请提供订单号。', None, None),
            MessageRecord(3, 'user', '先不查订单了，聊点别的', None, None)]
    frozen = SimpleNamespace(summaries=(), omitted_summary_seqs=(), layer2=(), layer1=tuple(rows))
    with pytest.raises(ServiceError):
        validate_snapshot_entities('1001', '订单1001物流信息异常', frozen, ())


@pytest.mark.parametrize('snapshot_mode', [False, True])
@pytest.mark.parametrize('intervening', ['2002', '先不查订单了，聊点别的'])
def test_unbound_number_cannot_fall_back_to_an_older_proven_order(snapshot_mode, intervening):
    from app.workflow.entities import IdentitySource
    history = [HumanMessage('订单2002物流'), AIMessage('此前查过订单2002。'),
               HumanMessage('物流信息异常'), AIMessage('请提供订单号。'), HumanMessage(intervening)]
    if snapshot_mode:
        frozen = SimpleNamespace(summaries=(), omitted_summary_seqs=(), layer2=(), layer1=tuple(
            MessageRecord(i, 'user' if message.type == 'human' else 'assistant', message.content, None, None)
            for i, message in enumerate(history, 1)))
        provenance = (IdentitySource(1, None, frozenset({'2002'}), ('订单2002物流',)),)
        validate_current = lambda resolved: validate_snapshot_entities('1001', resolved, frozen, provenance)
    else:
        validate_current = lambda resolved: validate_resolved_entities('1001', resolved, history)
    validate_current('1001')  # Ambiguous numeric text can still pass through unchanged.
    with pytest.raises(ServiceError):
        validate_current('订单2002物流信息异常')
