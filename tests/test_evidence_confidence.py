import math
import pytest
from tests.flywheel_confidence_fakes import payload, rule


def test_single_evidence_has_no_infinite_gap():
    from app.quality.evidence_confidence import evaluate_evidence
    selected = rule()
    result = evaluate_evidence(payload((.9,)), selected, top_k=2, budget_fingerprint=selected.source.budget_fingerprint)
    assert result.features['gap'] == result.features['gap_signal'] == 0
    assert not result.features['has_top2']
    assert math.isfinite(result.evidence_confidence) and 0 <= result.evidence_confidence <= 1


def test_score_order_is_independent_of_sandwich_display_order():
    from app.quality.evidence_confidence import evaluate_evidence
    selected = rule(top_k=3)
    result = evaluate_evidence(payload((.9, .6, .8)), selected, top_k=3,
                               budget_fingerprint=selected.source.budget_fingerprint)
    assert result.features['top1'] == .9
    assert result.features['gap'] == pytest.approx(.1)


def test_duplicate_chunks_do_not_inflate_evidence_count():
    from app.quality.evidence_confidence import evaluate_evidence
    selected = rule(top_k=3)
    result = evaluate_evidence(payload((.9, .8, .7), ids=['1', '1', '2']), selected, top_k=3,
                               budget_fingerprint=selected.source.budget_fingerprint)
    assert result.features['selected_count'] == 2
    assert result.features['effective_count'] <= 2


def test_empty_evidence_is_always_refused():
    from app.quality.evidence_confidence import evaluate_evidence
    selected = rule()
    result = evaluate_evidence(payload(()), selected, top_k=2, budget_fingerprint=selected.source.budget_fingerprint)
    assert not result.useful and result.evidence_confidence == 0


@pytest.mark.parametrize('damage', ['nan', 'wrong_kind'])
def test_invalid_scores_are_contract_errors_not_knowledge_deficiency(damage):
    from app.quality.evidence_confidence import evaluate_evidence
    selected, data = rule(), payload()
    if damage == 'nan': data['matches'][0]['score'] = float('nan')
    else: data['matches'][0]['score_kind'] = 'rrf'
    with pytest.raises(ValueError):
        evaluate_evidence(data, selected, top_k=2, budget_fingerprint=selected.source.budget_fingerprint)


@pytest.mark.parametrize('score', [.25, .5])
def test_hand_typed_threshold_without_calibration_provenance_is_not_a_rule(score):
    from app.quality.evidence_confidence import ConfidenceRule
    with pytest.raises(ValueError):
        ConfidenceRule(threshold=score, weights=[1, 1, 1])


def test_signature_and_rule_integrity_are_verified():
    from app.quality.evidence_confidence import evaluate_evidence, verify_rule
    selected = rule()
    with pytest.raises(ValueError, match='budget'):
        evaluate_evidence(payload(), selected, top_k=2, budget_fingerprint='d' * 64)
    with pytest.raises(ValueError, match='actual'):
        verify_rule(selected, top_k=2, budget_fingerprint=selected.source.budget_fingerprint, require_actual=True)
    changed = selected.model_copy(update={'threshold': .12345})
    with pytest.raises(ValueError, match='integrity'):
        evaluate_evidence(payload(), changed, top_k=2, budget_fingerprint=selected.source.budget_fingerprint)
