"""Frozen, calibrated evidence strength; this score is not a correctness probability."""
from bisect import bisect_right
import hashlib
import json
import math
from typing import Literal
from pydantic import Field, model_validator
from app.flywheel.types import StrictModel, Versioned, database_id

ALGORITHM = 'ch09-ecdf-minrank-strict-v1'


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def model_fingerprint(model):
    return canonical_hash({'model': model, 'score_kind': 'rerank'})


def evidence_budget_fingerprint(*, top_k, token_budget):
    from app.context.tokens import ESTIMATOR_VERSION
    return canonical_hash({'selector': 'prepare_workflow_evidence-v1', 'estimator': ESTIMATOR_VERSION,
        'top_k': top_k, 'evidence_token_budget': token_budget})


def load_online_rule(path, *, top_k, budget_fingerprint, rerank_model):
    from pathlib import Path
    rule = ConfidenceRule.model_validate_json(Path(path).read_text(encoding='utf-8'))
    verify_rule(rule, top_k=top_k, budget_fingerprint=budget_fingerprint,
        model_fingerprint=model_fingerprint(rerank_model), require_actual=True)
    from app.rag_evaluation.dataset import load_dataset, DATASET_ID
    dataset = load_dataset(DATASET_ID, root=Path(__file__).parents[2] / 'evals/datasets')
    verify_rule(rule, top_k=top_k, budget_fingerprint=budget_fingerprint,
        dataset_fingerprint=dataset.fingerprint, corpus_hash=dataset.corpus_hash, require_actual=True)
    return rule


class CalibrationSource(StrictModel):
    dataset_id: str = Field(min_length=1)
    dataset_fingerprint: str = Field(pattern=r'^[0-9a-f]{64}$')
    corpus_hash: str = Field(pattern=r'^[0-9a-f]{64}$')
    rerank_model: str = Field(min_length=1)
    model_fingerprint: str = Field(pattern=r'^[0-9a-f]{64}$')
    top_k: int = Field(ge=1, le=10)
    budget_fingerprint: str = Field(pattern=r'^[0-9a-f]{64}$')
    source_kind: Literal['fixture', 'actual']


class ConfidenceRule(Versioned):
    algorithm: Literal['ch09-ecdf-minrank-strict-v1']
    rule_version: str = Field(pattern=r'^[0-9a-f]{64}$')
    source: CalibrationSource
    split_fingerprint: str = Field(pattern=r'^[0-9a-f]{64}$')
    calibration_fingerprint: str = Field(pattern=r'^[0-9a-f]{64}$')
    calibration_ids: list[str] = Field(min_length=2)
    top1_distribution: list[float] = Field(min_length=1)
    gap_distribution: list[float] = Field(min_length=1)
    score_floor: float
    weights: tuple[int, int, int]
    threshold: float = Field(ge=0, le=1)

    @model_validator(mode='after')
    def valid_parameters(self):
        if any(not 0 <= weight <= 3 for weight in self.weights) or not sum(self.weights):
            raise ValueError('Confidence weights must be nonzero integer grid parameters')
        if (self.top1_distribution != sorted(self.top1_distribution)
                or self.gap_distribution != sorted(self.gap_distribution)
                or any(value < 0 for value in self.gap_distribution)):
            raise ValueError('Confidence distributions must be finite and sorted')
        return self


class EvidenceDecision(StrictModel):
    useful: bool
    evidence_confidence: float = Field(ge=0, le=1)
    features: dict
    reason: str
    rule_version: str


def selected_rankings(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get('matches'), list):
        raise ValueError('Successful retrieval payload is required')
    if payload.get('retrieval', {}).get('strategy', 'hybrid_rerank') != 'hybrid_rerank':
        raise ValueError('Confidence requires hybrid_rerank evidence')
    error = payload.get('error')
    if error and not (isinstance(error, dict) and error.get('code') == 'not_found' and not payload['matches']):
        raise ValueError('Retrieval failure cannot be a confidence refusal')
    unique = {}
    for row in payload['matches']:
        if not isinstance(row, dict):
            raise ValueError('Invalid rerank evidence row')
        identifier = row.get('id')
        if type(identifier) not in (str, int):
            raise ValueError('Invalid evidence identity')
        identifier = database_id(str(identifier))
        score = row.get('score')
        if type(score) not in (int, float) or not math.isfinite(score) or row.get('score_kind') != 'rerank':
            raise ValueError('Invalid authoritative rerank score')
        unique[identifier] = max(float(score), unique.get(identifier, float('-inf')))
    return sorted(unique.items(), key=lambda row: (-row[1], int(row[0])))


def empirical_signal(value, distribution):
    if not distribution or distribution[0] == distribution[-1]:
        return 0.
    minimum_rank = bisect_right(distribution, distribution[0])
    return max(0., min(1., (bisect_right(distribution, value) - minimum_rank) /
                       (len(distribution) - minimum_rank)))


def score_features(scores, *, score_floor, top_k, top1_distribution, gap_distribution):
    scores = sorted(scores, reverse=True)
    top1 = scores[0] if scores else None
    has_top2 = len(scores) >= 2
    gap = scores[0] - scores[1] if has_top2 else 0.
    effective = sum(score > score_floor for score in scores)
    return {'top1': top1, 'gap': gap, 'has_top2': has_top2, 'selected_count': len(scores),
        'effective_count': effective, 'count_ratio': effective / top_k,
        'top1_signal': empirical_signal(top1, top1_distribution) if top1 is not None else 0.,
        'gap_signal': empirical_signal(gap, gap_distribution) if has_top2 else 0.}


def combined_score(features, weights):
    # Identical rounding in calibration/replay prevents platform-level tiny ties.
    return round(sum(weight * value for weight, value in zip(weights,
        (features['top1_signal'], features['count_ratio'], features['gap_signal']))) / sum(weights), 12)


def verify_rule(rule, *, top_k, budget_fingerprint, model_fingerprint=None,
                dataset_fingerprint=None, corpus_hash=None, require_actual=False):
    if not isinstance(rule, ConfidenceRule):
        raise ValueError('A calibrated rule artifact is required')
    if rule.rule_version != canonical_hash(rule.model_dump(mode='json', exclude={'rule_version'})):
        raise ValueError('Confidence rule integrity mismatch')
    if rule.source.top_k != top_k or rule.source.budget_fingerprint != budget_fingerprint:
        raise ValueError('Confidence budget signature mismatch')
    if require_actual and rule.source.source_kind != 'actual':
        raise ValueError('An actual calibration source is required')
    for expected, actual in ((model_fingerprint, rule.source.model_fingerprint),
                             (dataset_fingerprint, rule.source.dataset_fingerprint),
                             (corpus_hash, rule.source.corpus_hash)):
        if expected is not None and expected != actual:
            raise ValueError('Confidence source signature mismatch')


def evaluate_evidence(payload, rule, *, top_k, budget_fingerprint):
    verify_rule(rule, top_k=top_k, budget_fingerprint=budget_fingerprint)
    ranked = selected_rankings(payload)
    if len(ranked) > top_k:
        raise ValueError('Confidence only accepts actually selected prompt evidence')
    features = score_features([score for _, score in ranked], score_floor=rule.score_floor, top_k=top_k,
        top1_distribution=rule.top1_distribution, gap_distribution=rule.gap_distribution)
    score = combined_score(features, rule.weights) if ranked else 0.
    useful = bool(ranked) and score > rule.threshold
    return EvidenceDecision(useful=useful, evidence_confidence=score, features=features,
        reason='calibrated_evidence_pass' if useful else 'calibrated_evidence_insufficient', rule_version=rule.rule_version)
