"""Deterministic grouped holdout and refusal-positive finite-grid calibration."""
import hashlib
from itertools import product
from fractions import Fraction
from typing import Literal
from pydantic import Field, field_validator, model_validator
from app.flywheel.types import StrictModel, database_id
from app.quality.evidence_confidence import (
    ALGORITHM, CalibrationSource, ConfidenceRule, canonical_hash, score_features, combined_score,
)

BUCKETS = {'A': 'A_policy', 'B': 'B_model', 'C': 'C_colloquial',
           'D': 'D_unanswerable', 'E': 'E_multi'}


class RankedEvidence(StrictModel):
    chunk_id: str
    score: float
    score_kind: Literal['rerank']

    @field_validator('chunk_id')
    @classmethod
    def identifier(cls, value): return database_id(value)


class CalibrationSample(StrictModel):
    eval_id: str = Field(min_length=1)
    group_id: str = Field(min_length=1)
    bucket: str
    rankings: list[RankedEvidence]
    sufficient: bool
    source: CalibrationSource
    rankings_source: str = Field(min_length=1)

    @model_validator(mode='after')
    def evidence_contract(self):
        if self.bucket not in BUCKETS.values() or len(self.rankings) > self.source.top_k:
            raise ValueError('Invalid calibration bucket or prompt evidence count')
        if len({row.chunk_id for row in self.rankings}) != len(self.rankings):
            raise ValueError('Calibration prompt IDs must be unique')
        if self.sufficient and not self.rankings:
            raise ValueError('Sufficient label cannot have empty prompt evidence')
        return self


class CalibrationSplit(StrictModel):
    calibration_ids: tuple[str, ...]
    held_out_ids: tuple[str, ...]
    dataset_fingerprint: str = Field(pattern=r'^[0-9a-f]{64}$')
    case_groups: dict[str, str]
    group_buckets: dict[str, str]
    regression_sides: dict[str, Literal['calibration', 'held_out']]
    fingerprint: str = Field(pattern=r'^[0-9a-f]{64}$')

    @model_validator(mode='after')
    def valid_integrity(self):
        ids=(*self.calibration_ids,*self.held_out_ids)
        if (len(set(ids))!=len(ids) or self.calibration_ids!=tuple(sorted(self.calibration_ids))
                or self.held_out_ids!=tuple(sorted(self.held_out_ids))):
            raise ValueError('Calibration split sides must be sorted, unique and disjoint')
        if (set(self.case_groups)!=set(ids)|set(self.regression_sides)
                or set(self.case_groups.values())!=set(self.group_buckets)
                or not set(self.group_buckets.values())<=set(BUCKETS.values())):
            raise ValueError('Calibration split group identities mismatch')
        training={self.case_groups[key] for key in self.calibration_ids}
        held={self.case_groups[key] for key in self.held_out_ids}
        if training & held:
            raise ValueError('Calibration groups cross held-out boundary')
        for key,side in self.regression_sides.items():
            if self.case_groups[key] not in (training if side=='calibration' else held):
                raise ValueError('Regression split side mismatch')
        if self.fingerprint!=canonical_hash(self.model_dump(mode='json',exclude={'fingerprint'})):
            raise ValueError('Calibration split fingerprint mismatch')
        return self

    @classmethod
    def from_ids(cls, calibration_ids, held_out_ids, *, dataset_fingerprint,
                 case_groups=None, group_buckets=None, regression_sides=None):
        calibration_ids, held_out_ids = tuple(sorted(calibration_ids)), tuple(sorted(held_out_ids))
        ids = [*calibration_ids, *held_out_ids]
        if len(set(ids)) != len(ids):
            raise ValueError('Calibration and heldout IDs must be disjoint and unique')
        groups = case_groups if case_groups is not None else {identifier: identifier for identifier in ids}
        buckets = group_buckets if group_buckets is not None else {identifier: BUCKETS[identifier[0]] for identifier in ids}
        data = dict(calibration_ids=calibration_ids, held_out_ids=held_out_ids,
            dataset_fingerprint=dataset_fingerprint, case_groups=groups,
            group_buckets=buckets, regression_sides=regression_sides or {})
        return cls(**data, fingerprint=canonical_hash(data))

    def side_for(self, identifier):
        group = self.case_groups[identifier]
        if any(self.case_groups[key] == group for key in self.calibration_ids):
            return 'calibration'
        if any(self.case_groups[key] == group for key in self.held_out_ids):
            return 'held_out'
        raise ValueError('Unknown calibration group')


class CalibrationResult(StrictModel):
    rule: ConfidenceRule
    calibration: dict
    held_out: dict
    baseline: dict
    samples: list[dict]
    source: dict


def build_calibration_split(dataset):
    cases = {case.eval_id: case for case in dataset.cases}
    if len(cases) != len(dataset.cases):
        raise ValueError('Duplicate calibration case identity')
    case_groups = {identifier: identifier for identifier in cases}
    group_buckets = {identifier: case.bucket for identifier, case in cases.items()}
    for regression, original in dataset.regression_links:
        if regression in case_groups or original not in cases:
            raise ValueError('Invalid verified regression link')
        case_groups[regression] = original
    calibration_groups = set()
    for bucket in sorted(set(group_buckets.values())):
        if bucket not in BUCKETS.values():
            raise ValueError('Unknown calibration bucket')
        groups = [group for group, value in group_buckets.items() if value == bucket]
        groups.sort(key=lambda group: (hashlib.sha256((dataset.fingerprint + group).encode()).hexdigest(), group))
        n = len(groups)
        take = min(n-1, max(1, n//3)) if n >= 2 else 0
        calibration_groups.update(groups[:take])
    calibration = [identifier for identifier in cases if case_groups[identifier] in calibration_groups]
    heldout = [identifier for identifier in cases if identifier not in calibration]
    for ids in (calibration, heldout):
        if {cases[identifier].should_refuse for identifier in ids} != {False, True}:
            raise ValueError('Both label classes are required on each split side')
    return CalibrationSplit.from_ids(calibration, heldout, dataset_fingerprint=dataset.fingerprint,
        case_groups=case_groups, group_buckets=group_buckets,
        regression_sides={regression: 'calibration' if original in calibration_groups else 'held_out'
                          for regression, original in dataset.regression_links})


def _matrix(labels, predictions):
    # Positive means evidence insufficient; predicted positive means refusal.
    tp = sum(not label and not prediction for label, prediction in zip(labels, predictions))
    fp = sum(label and not prediction for label, prediction in zip(labels, predictions))
    fn = sum(not label and prediction for label, prediction in zip(labels, predictions))
    tn = sum(label and prediction for label, prediction in zip(labels, predictions))
    denominator = 2*tp + fp + fn
    f1 = Fraction(2*tp, denominator) if denominator else Fraction(0)
    return {'n': len(labels), 'true_positive': tp, 'false_positive': fp, 'false_negative': fn,
        'true_negative': tn, 'false_allow': fn, 'false_refusal': fp, 'f1': float(f1)}, f1


def fit_confidence_rule(samples, split, *, baseline_threshold=None):
    samples = sorted(samples, key=lambda row: row.eval_id)
    by_id = {sample.eval_id: sample for sample in samples}
    if len(by_id) != len(samples) or set(by_id) != set(split.calibration_ids) | set(split.held_out_ids):
        raise ValueError('Calibration sample identity set does not match split')
    if not samples:
        raise ValueError('Calibration label samples missing')
    source = samples[0].source
    if source.dataset_fingerprint != split.dataset_fingerprint:
        raise ValueError('Calibration dataset signature mismatch')
    for sample in samples:
        if (sample.source != source or split.case_groups[sample.eval_id] != sample.group_id
                or split.group_buckets[sample.group_id] != sample.bucket):
            raise ValueError('Calibration sample group/source mismatch')
    training = [by_id[identifier] for identifier in split.calibration_ids]
    heldout = [by_id[identifier] for identifier in split.held_out_ids]
    for rows in (training, heldout):
        if {sample.sufficient for sample in rows} != {False, True}:
            raise ValueError('Both sufficient/insufficient label classes are required')
    scores = lambda row: sorted([value.score for value in row.rankings], reverse=True)
    observed = sorted(score for sample in training for score in scores(sample))
    if not observed:
        raise ValueError('Calibration rankings missing')
    floors = sorted({observed[((len(observed)-1)*percentile)//100] for percentile in (0, 25, 50, 75, 100)})
    top1 = sorted(scores(row)[0] for row in training if row.rankings)
    gaps = sorted(scores(row)[0]-scores(row)[1] if len(row.rankings) >= 2 else 0. for row in training)
    labels = [row.sufficient for row in training]
    best, best_order = None, None
    for floor in floors:
        features = [score_features(scores(row), score_floor=floor, top_k=source.top_k,
            top1_distribution=top1, gap_distribution=gaps) for row in training]
        for weights in product(range(4), repeat=3):
            if not sum(weights):
                continue
            values = [combined_score(row, weights) for row in features]
            for threshold in sorted(set(values)):
                predictions = [bool(row.rankings) and value > threshold for row, value in zip(training, values)]
                matrix, f1 = _matrix(labels, predictions)
                order = (-f1, matrix['false_allow'], -threshold, floor, *weights)
                if best_order is None or order < best_order:
                    best_order, best = order, (floor, weights, threshold)
    floor, weights, threshold = best
    data = dict(schema_version=1, algorithm=ALGORITHM, source=source.model_dump(mode='json'),
        split_fingerprint=split.fingerprint,
        calibration_fingerprint=canonical_hash([row.model_dump(mode='json') for row in training]),
        calibration_ids=list(split.calibration_ids), top1_distribution=top1, gap_distribution=gaps,
        score_floor=floor, weights=weights, threshold=threshold)
    rule = ConfidenceRule(**data, rule_version=canonical_hash(data))
    def evaluate(rows):
        features = [score_features(scores(row), score_floor=floor, top_k=source.top_k,
            top1_distribution=top1, gap_distribution=gaps) for row in rows]
        predicted = [bool(row.rankings) and combined_score(feature, weights) > threshold for row, feature in zip(rows, features)]
        return _matrix([row.sufficient for row in rows], predicted)[0]
    baseline = {'excluded_reason': 'baseline_not_requested'}
    if baseline_threshold is not None:
        import math
        if type(baseline_threshold) not in (float, int) or not math.isfinite(baseline_threshold):
            raise ValueError('Baseline threshold must be configured and finite')
        baseline = {name: _matrix([row.sufficient for row in rows],
            [bool(row.rankings) and max(scores(row)) >= baseline_threshold for row in rows])[0]
            for name, rows in (('calibration', training), ('held_out', heldout))}
    records = [dict(row.model_dump(mode='json'), features=score_features(scores(row), score_floor=floor,
        top_k=source.top_k, top1_distribution=top1, gap_distribution=gaps)) for row in samples]
    return CalibrationResult(rule=rule, calibration=evaluate(training), held_out=evaluate(heldout),
        baseline=baseline, samples=records, source={'regression_sides': split.regression_sides,
        'excluded': [], 'zero_weight_features': [name for name, weight in zip(('top1', 'count', 'gap'), weights) if weight == 0],
        'confidence_is_probability': False})


async def collect_calibration_samples(dataset, split, id_map, retrieval, source, *, token_budget,
                                      case_ids=None, on_sample=None):
    """Gold labels are complete-group coverage of the exact prompt selection; no answer model."""
    from app.core.evidence import prepare_workflow_evidence
    from app.rag_evaluation.contracts import MappedGroup
    from app.rag_evaluation.metrics import retrieval_metrics
    from app.retrieval.service import faq_payload
    from app.retrieval.types import QueryPlan
    from app.quality.evidence_confidence import evidence_budget_fingerprint
    if source.budget_fingerprint != evidence_budget_fingerprint(top_k=source.top_k, token_budget=token_budget):
        raise ValueError('Calibration prompt budget signature mismatch')
    rows = []
    selected_ids = set(case_ids) if case_ids is not None else {case.eval_id for case in dataset.cases}
    if not selected_ids <= {case.eval_id for case in dataset.cases}:
        raise ValueError('Unknown calibration case ID')
    for case in dataset.cases:
        if case.eval_id not in selected_ids:
            continue
        bundle = await retrieval.retrieve(case.query, category=case.category,
            strategy='hybrid_rerank', query_plan=QueryPlan(standard=case.query, expansions=[]), top_k=source.top_k)
        payload = bundle if isinstance(bundle, dict) else faq_payload(bundle)
        packet = prepare_workflow_evidence([payload], top_k=source.top_k, token_budget=token_budget)
        prompt_ids = [int(item['id']) for item in packet.payload['matches']]
        groups = tuple(MappedGroup(group.group_id, tuple(tuple(id_map[key] for key in alternative)
            for alternative in group.alternatives)) for group in case.groups)
        metrics = retrieval_metrics(prompt_ids, prompt_ids, prompt_ids, groups)
        sample = CalibrationSample(eval_id=case.eval_id, group_id=split.case_groups[case.eval_id],
            bucket=case.bucket, rankings=[RankedEvidence(chunk_id=str(item['id']), score=item['score'],
                score_kind=item['score_kind']) for item in packet.payload['matches']],
            sufficient=not case.should_refuse and metrics['prompt_group_coverage'] == 1,
            source=source, rankings_source='actual:hybrid_rerank:prepare_workflow_evidence')
        if on_sample is not None:
            await on_sample(sample)
        rows.append(sample)
    return rows


async def run_calibration(settings, output, cap):
    """One explicit paid retrieval run, with owned resources and durable raw samples."""
    import json
    from pathlib import Path
    from app.quality.evidence_confidence import CalibrationSource, model_fingerprint, evidence_budget_fingerprint
    from app.rag_evaluation.dataset import DATASET_ID, load_dataset
    from app.rag_evaluation.store import RunStore
    from app.rag_evaluation.manager import build_run_config
    from app.quality.calibration_resources import CalibrationResources
    from app.retrieval.service import RetrievalService
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    if any((output / name).exists() for name in ('manifest.json', 'rule.json', 'samples.jsonl')):
        raise ValueError('Calibration output already exists; inspect/recover ownership, never silently replay paid run')
    dataset = load_dataset(DATASET_ID, root=Path(__file__).parents[2] / 'evals/datasets')
    split = build_calibration_split(dataset)
    budget = min(6000, (settings.model_context_window+7)//8)
    source = CalibrationSource(dataset_id=dataset.dataset_id, dataset_fingerprint=dataset.fingerprint,
        corpus_hash=dataset.corpus_hash, rerank_model=settings.rerank_model,
        model_fingerprint=model_fingerprint(settings.rerank_model), top_k=settings.rerank_top_k,
        budget_fingerprint=evidence_budget_fingerprint(top_k=settings.rerank_top_k, token_budget=budget), source_kind='actual')
    # Reuse step04's strict ownership manifest and hash-checked cleanup; its config is
    # resource-only here. Actual step09 selection is frozen separately above.
    store = RunStore(output / 'resources')
    resource_settings = settings.model_copy(update={'max_output_tokens': 512,
        'query_max_output_tokens': 2048, 'sufficiency_max_output_tokens': 2048,
        'faith_judge_max_output_tokens': 2048, 'faith_judge_input_token_budget': 16000})
    run_id = await store.create(build_run_config(dataset, resource_settings, 'full'),
        [(case.eval_id, 'hybrid_rerank') for case in dataset.cases])
    manifest = {'run_id': run_id, 'state': 'running', 'source': source.model_dump(mode='json')}
    def save(name, value):
        path = output / name
        temporary = path.with_suffix(path.suffix + '.tmp')
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
        temporary.replace(path)
    save('manifest.json', manifest)
    save('split.json', split.model_dump(mode='json'))
    resources = CalibrationResources(resource_settings, store, run_id, cap=cap)
    try:
        id_map = await resources.prepare(dataset)
        retrieval = RetrievalService(resources.repository, resources.embedder, resources.index, None, resources.reranker)
        async def checkpoint(sample):
            with (output / 'samples.jsonl').open('a', encoding='utf-8') as stream:
                stream.write(sample.model_dump_json() + '\n')
                stream.flush()
        samples = await collect_calibration_samples(dataset, split, id_map, retrieval, source,
            token_budget=budget, on_sample=checkpoint)
        result = fit_confidence_rule(samples, split, baseline_threshold=settings.rerank_min_score)
        save('rule.json', result.rule.model_dump(mode='json'))
        save('report.json', result.model_dump(mode='json'))
        manifest['state'] = 'completed'
        return result
    except BaseException as exc:
        manifest.update(state='failed', error_type=type(exc).__name__)
        raise
    finally:
        from dataclasses import asdict
        cleanup = await resources.cleanup()
        manifest['cleanup'] = asdict(cleanup)
        save('manifest.json', manifest)
        if not cleanup.ok:
            raise RuntimeError('Calibration resource cleanup incomplete; inspect manifest before any next run')
