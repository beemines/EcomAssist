"""Durable per-input failures prevent repeated bad batches across restarts."""
from pathlib import Path
import pytest

from app.topics.receipts import ReceiptError, ReceiptStore, FailureKey


def key(**changes):
    return FailureKey.model_validate(dict(question_id='9007199254740993', input_hash='a'*64,
        model_version='model-v1') | changes)


def store(tmp_path):
    path = tmp_path/'runtime/receipts.sqlite3'
    ReceiptStore.initialize(path, database_identity='b'*64)
    return ReceiptStore(path, database_identity='b'*64)


def test_transient_rounds_backoff_and_pause_survive_restarts(tmp_path):
    records = store(tmp_path)
    assert records.eligible(key(), now=100)
    first = records.record_failure(key(), 'temporary_failure', now=100)
    assert first.failures == 1 and first.next_attempt_at == 160 and not first.paused
    reopened = ReceiptStore(records.path, database_identity='b'*64)
    assert not reopened.eligible(key(), now=159)
    assert reopened.eligible(key(), now=160)
    assert reopened.record_failure(key(), 'temporary_failure', now=160).next_attempt_at == 280
    third = reopened.record_failure(key(), 'temporary_failure', now=280)
    assert third.failures == 3 and third.paused and third.next_attempt_at is None
    assert not reopened.eligible(key(), now=10000)
    reopened.retry(key(), now=10000)
    assert reopened.eligible(key(), now=10000)
    assert reopened.record_failure(key(), 'temporary_failure', now=10000).failures == 1


@pytest.mark.parametrize('status', ['needs_review', 'input_too_long', 'invalid_input', 'cleaning_failed', 'permanent_failure'])
def test_data_failures_require_explicit_retry_and_new_input_or_model_is_separate(tmp_path, status):
    records = store(tmp_path)
    state = records.record_failure(key(), status, now=100)
    assert state.paused and state.status == status
    assert not records.eligible(key(), now=100000)
    assert records.eligible(key(input_hash='c'*64), now=101)
    assert records.eligible(key(model_version='model-v2'), now=101)
    assert records.states([key()])[0] == state
    records.record_success(key(), now=102)
    assert records.states([key()]) == ()


def test_deleted_corrupt_wrong_database_or_unknown_receipts_fail_closed(tmp_path):
    records = store(tmp_path)
    with pytest.raises(ReceiptError):
        ReceiptStore(records.path, database_identity='c'*64).states([key()])
    with pytest.raises(ReceiptError):
        ReceiptStore.initialize(records.path, database_identity='b'*64)
    records.path.unlink()
    with pytest.raises(ReceiptError):
        records.states([key()])
    with pytest.raises(ReceiptError):
        ReceiptStore.initialize(records.path, database_identity='b'*64)
    records.path.write_bytes(b'corrupt')
    with pytest.raises(ReceiptError):
        records.states([key()])


def test_receipts_reject_invalid_state_keys_and_unbounded_summaries(tmp_path):
    records = store(tmp_path)
    with pytest.raises(ValueError):
        records.record_failure(key(), 'random upstream error text', now=100)
    with pytest.raises(ValueError):
        key(question_id=9007199254740993)
    with pytest.raises(ValueError):
        key(input_hash='secret raw text')
    with pytest.raises(ValueError):
        records.states([key()]*10001)
    assert records.states([]) == ()
