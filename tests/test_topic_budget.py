"""Physical teacher attempts share one crash-safe, cross-process CNY10 ledger."""

import multiprocessing
from pathlib import Path

import pytest

from app.topics.budget import BudgetError, BudgetLedger, Usage, initialize_budget


APPROVAL = 'ch10-topic-20261021'


def competing_reservations(path, queue):
    ledger = BudgetLedger(Path(path), APPROVAL)
    granted = 0
    for _ in range(5):
        try:
            ledger.reserve('generate', 'a' * 64)
            granted += 1
        except BudgetError:
            pass
    queue.put(granted)


def test_budget_survives_crash_and_competing_processes(tmp_path):
    path = tmp_path / 'budget.sqlite3'
    initialize_budget(path, APPROVAL)
    context = multiprocessing.get_context('spawn')
    queue = context.Queue()
    children = [context.Process(target=competing_reservations, args=(str(path), queue)) for _ in range(2)]
    for child in children:
        child.start()
    for child in children:
        child.join(30)
        assert child.exitcode == 0
    assert sum(queue.get(timeout=5) for _ in children) == 8
    summary = BudgetLedger(path, APPROVAL).summary()
    assert summary.used_micro == 8 * 1_205_863
    assert summary.attempts == 8 and summary.limit_micro == 10_000_000
    with pytest.raises(BudgetError):
        BudgetLedger(path, APPROVAL).reserve('label', 'b' * 64)


def test_settlement_is_integer_idempotent_and_reasoning_is_not_double_counted(tmp_path):
    path = tmp_path / 'budget.sqlite3'
    initialize_budget(path, APPROVAL)
    ledger = BudgetLedger(path, APPROVAL)
    attempt = ledger.reserve('label', 'a' * 64)
    usage = Usage(prompt_tokens=1000, completion_tokens=200, total_tokens=1200,
                  reasoning_tokens=50, reasoning_included=True)
    ledger.settle(attempt.attempt_id, usage)
    ledger.settle(attempt.attempt_id, usage)
    assert ledger.summary().used_micro == 1360
    with pytest.raises(BudgetError):
        ledger.settle(attempt.attempt_id, Usage(prompt_tokens=2, completion_tokens=1, total_tokens=3))
    assert ledger.summary().used_micro == 1360
    second = ledger.reserve('augment', 'b' * 64)
    ledger.settle(second.attempt_id, Usage(prompt_tokens=1000, completion_tokens=150, total_tokens=1200,
        reasoning_tokens=50, reasoning_included=False))
    assert ledger.summary().used_micro == 2720


def test_unknown_usage_never_releases_reserved_money(tmp_path):
    path = tmp_path / 'budget.sqlite3'
    initialize_budget(path, APPROVAL)
    ledger = BudgetLedger(path, APPROVAL)
    attempt = ledger.reserve('generate', 'a' * 64)
    ledger.mark_unknown(attempt.attempt_id, 'timeout')
    assert ledger.summary().used_micro == 1_205_863
    assert BudgetLedger(path, APPROVAL).summary().unknown_attempts == 1


def test_missing_reasoning_breakdown_is_unknown_not_a_fabricated_zero():
    usage = Usage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
    assert usage.reasoning_tokens is None
    assert usage.billable_completion == 20
    with pytest.raises(ValueError):
        Usage(prompt_tokens=10, completion_tokens=20, total_tokens=30, reasoning_included=False)


@pytest.mark.parametrize('failure', ['missing', 'corrupt', 'identity', 'deleted'])
def test_missing_corrupt_wrong_approval_or_deleted_ledger_refuses(tmp_path, failure):
    path = tmp_path / 'budget.sqlite3'
    if failure != 'missing':
        initialize_budget(path, APPROVAL)
    if failure == 'corrupt':
        path.write_bytes(b'corrupt')
    elif failure == 'deleted':
        path.unlink()
    with pytest.raises(BudgetError):
        BudgetLedger(path, 'wrong' if failure == 'identity' else APPROVAL)
    if failure == 'deleted':
        with pytest.raises(BudgetError):
            initialize_budget(path, APPROVAL)


def test_three_failures_pause_and_outcome_is_idempotent(tmp_path):
    path = tmp_path / 'budget.sqlite3'
    initialize_budget(path, APPROVAL)
    ledger = BudgetLedger(path, APPROVAL)
    for _ in range(3):
        attempt = ledger.reserve('label', 'a' * 64)
        ledger.mark_unknown(attempt.attempt_id, 'timeout')
        ledger.record_outcome(attempt.attempt_id, success=False)
        ledger.record_outcome(attempt.attempt_id, success=False)
    assert ledger.summary().consecutive_failures == 3
    with pytest.raises(BudgetError):
        ledger.reserve('label', 'a' * 64)


def test_physical_attempt_ceiling_cannot_be_reset_by_zero_usage(tmp_path):
    path = tmp_path / 'budget.sqlite3'
    initialize_budget(path, APPROVAL)
    ledger = BudgetLedger(path, APPROVAL)
    for _ in range(300):
        attempt = ledger.reserve('label', 'a' * 64)
        ledger.settle(attempt.attempt_id, Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0))
        ledger.record_outcome(attempt.attempt_id, success=True)
    assert ledger.summary().attempts == 300
    with pytest.raises(BudgetError):
        ledger.reserve('generate', 'a' * 64)


@pytest.mark.parametrize('changes', [{'prompt_tokens': True}, {'total_tokens': 4},
    {'completion_tokens': -1}, {'reasoning_tokens': 3}, {'prompt_tokens': 1048577}])
def test_invalid_usage_cannot_unlock_money(changes):
    with pytest.raises(ValueError):
        Usage(**(dict(prompt_tokens=1, completion_tokens=1, total_tokens=2) | changes))
