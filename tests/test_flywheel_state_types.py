from datetime import datetime, timezone
import json

import pytest
from pydantic import ValidationError


def test_processing_state_has_fixed_version_and_bounded_attempts():
    from app.flywheel.types import ProcessingState
    state = ProcessingState()
    assert state.status == 'pending' and state.attempt_count == 0
    for changes in ({'schema_version': 2}, {'attempt_count': 4}, {'attempt_count': True},
                    {'status': 'surprise'}, {'untrusted_state': 'model input'},
                    {'status': 'running', 'attempt_count': 0}):
        with pytest.raises(ValidationError):
            ProcessingState.model_validate(changes)


def test_json_time_is_aware_and_publication_ready_requires_timestamp():
    from app.flywheel.types import ProcessingState, PublicationState
    with pytest.raises(ValidationError):
        PublicationState(status='ready')
    with pytest.raises(ValidationError):
        ProcessingState.model_validate_json(json.dumps({'status': 'retry_wait',
            'attempt_count': 1, 'next_attempt_at': '2026-10-19T01:00:00'}))
    state = ProcessingState.model_validate_json(json.dumps({'status': 'retry_wait',
        'attempt_count': 1, 'next_attempt_at': '2026-10-19T01:00:00+00:00'}))
    assert state.next_attempt_at.utcoffset().total_seconds() == 0
    ready = PublicationState(status='ready', published_at=datetime.now(timezone.utc), attempt_count=1)
    assert ready.published_at.tzinfo is not None


@pytest.mark.parametrize('value', [1, 1.0, True, '0', '-1', str(2**64), '１２３'])
def test_semantic_match_does_not_coerce_invalid_database_ids(value):
    from app.flywheel.types import SemanticMatch
    with pytest.raises(ValidationError):
        SemanticMatch(matched_review_id=value)


def test_bigint_keeps_exact_decimal_string_and_draft_has_faq_limit():
    from app.flywheel.types import SemanticMatch, NormalizedDraft
    identifier = '9007199254740993'
    match = SemanticMatch(matched_review_id=identifier)
    assert match.model_dump(mode='json') == {'matched_review_id': identifier}
    with pytest.raises(ValidationError):
        NormalizedDraft(normalized_question='字' * 513, ai_suggested_answer='待核实')


def test_snapshot_distinguishes_not_retrieved_zero_recall_and_unavailable():
    from app.flywheel.types import RetrievalSnapshot
    assert RetrievalSnapshot(status='not_retrieved', payload=None).payload is None
    empty = {'schema_version': 1, 'strategy': 'hybrid_rerank',
             'retrieved_at': datetime.now(timezone.utc), 'versions': {}, 'chunks': []}
    assert RetrievalSnapshot(status='captured', payload=empty).payload.chunks == []
    missing = {**empty, 'reason': 'legacy_payload_missing'}
    assert RetrievalSnapshot(status='unavailable', payload=missing).status == 'unavailable'
    with pytest.raises(ValidationError):
        RetrievalSnapshot(status='not_retrieved', payload=empty)
    with pytest.raises(ValidationError):
        RetrievalSnapshot(status='captured', payload=None)
