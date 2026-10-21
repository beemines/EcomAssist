"""Only explicit, complete human decisions can become a training review receipt."""

from datetime import datetime, timezone
import json
from types import SimpleNamespace

import pytest

from app.topics.reviews import ReviewDecision, apply_review, make_review_pack
from app.topics.types import LabelledSample


def pack():
    samples = [LabelledSample(id='a', text='能开电子发票吗?', labels=['发票'], origin='synthetic',
        group_id='g-a', source_question_ids=[], pilot=True),
        LabelledSample(id='b', text='运费多少钱,包裹在哪?', labels=['物流', '运费'], origin='unverified',
        group_id='g-b', source_question_ids=['9007199254740993'], pilot=True)]
    return make_review_pack(samples, snapshot_hash='a' * 64, teacher_receipts=[])


def decision(pack, identifier, **changes):
    original = next(sample for sample in pack.samples if sample.id == identifier)
    return ReviewDecision.model_validate(dict(sample_id=identifier, pack_hash=pack.pack_hash,
        decision='accept', final_labels=list(original.labels), reviewer='Human test fixture reviewer',
        reviewed_at=datetime.now(timezone.utc).isoformat(), notes='') | changes)


def test_complete_explicit_review_binds_labels_families_and_hashes():
    original = pack()
    result = apply_review(original, [decision(original, 'a'), decision(original, 'b',
        decision='correct', final_labels=['运费'])])
    assert result.pack_hash == original.pack_hash
    assert result.taxonomy_hash == original.taxonomy_hash
    assert result.samples[1].labels == ('运费',)
    assert result.samples[1].group_id == 'g-b'
    assert result.samples[1].origin == 'unverified'
    assert all(sample.pilot for sample in result.samples)
    assert len(result.receipt_hash) == 64


@pytest.mark.parametrize('failure', ['missing', 'duplicate', 'wrong_pack', 'silent_correction', 'pack_changed'])
def test_incomplete_or_mismatched_review_cannot_pass(failure):
    original = pack()
    rows = [decision(original, 'a'), decision(original, 'b')]
    if failure == 'missing':
        rows.pop()
    elif failure == 'duplicate':
        rows[1] = rows[0]
    elif failure == 'wrong_pack':
        rows[0] = rows[0].model_copy(update={'pack_hash': '0' * 64})
    elif failure == 'silent_correction':
        rows[0] = rows[0].model_copy(update={'final_labels': ('物流',)})
    else:
        original = original.model_copy(update={'snapshot_hash': '0' * 64})
    with pytest.raises(ValueError):
        apply_review(original, rows)


@pytest.mark.parametrize('changes', [{'reviewer': ''}, {'reviewer': ' '}, {'decision': None},
    {'reviewed_at': '2026-10-21T20:00:00'}, {'final_labels': ['其他', '物流']},
    {'final_labels': []}, {'decision': 'exclude', 'final_labels': ['发票']}])
def test_default_or_invalid_decisions_are_not_human_acceptance(changes):
    original = pack()
    with pytest.raises(ValueError):
        decision(original, 'a', **changes)


def test_explicit_exclusion_is_kept_in_receipt_without_becoming_training_data():
    original = pack()
    result = apply_review(original, [decision(original, 'a', decision='exclude', final_labels=[]), decision(original, 'b')])
    assert result.excluded_ids == ('a',)
    assert [sample.id for sample in result.samples] == ['b']
    assert len(result.decisions) == 2


async def test_paid_stage_resume_reuses_completed_data_and_refuses_interrupted_or_changed_scope(tmp_path):
    from app.topics.data_cli import _checkpoint
    teacher = SimpleNamespace(last_receipt={'attempt_id': 'test-fixture-only'})
    calls = 0
    sample = pack().samples[0]
    async def controlled():
        nonlocal calls
        calls += 1
        return (sample,)
    result, receipt = await _checkpoint('example', {'scope': 1}, controlled, teacher, tmp_path, LabelledSample)
    assert result == (sample,)
    again, _ = await _checkpoint('example', {'scope': 1}, controlled, teacher, tmp_path, LabelledSample)
    assert again == result and calls == 1
    with pytest.raises(ValueError):
        await _checkpoint('example', {'scope': 2}, controlled, teacher, tmp_path, LabelledSample)
    (tmp_path/'incomplete.json').write_text(json.dumps({'state': 'in_flight'}), encoding='utf-8')
    with pytest.raises(ValueError):
        await _checkpoint('incomplete', {'scope': 1}, controlled, teacher, tmp_path, LabelledSample)
    assert calls == 1
