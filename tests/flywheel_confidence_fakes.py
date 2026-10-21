"""Hand-labeled rankings only; never represent real model calibration."""
import json
from pathlib import Path


def samples_and_split(*, top_k=2, budget_fingerprint=None):
    from app.quality.calibration import CalibrationSample, CalibrationSplit
    from app.quality.evidence_confidence import CalibrationSource, model_fingerprint
    data = json.loads((Path(__file__).parent / 'fixtures/flywheel/calibration_rankings.json').read_text(encoding='utf-8'))
    source = dict(data['source'], top_k=top_k)
    if budget_fingerprint is not None:
        source['budget_fingerprint'] = budget_fingerprint
    source['model_fingerprint'] = model_fingerprint(source['rerank_model'])
    source = CalibrationSource.model_validate(source)
    samples = [CalibrationSample(eval_id=row['eval_id'], group_id=row['eval_id'], bucket=row['bucket'],
        rankings=[{'chunk_id': str(i), 'score': score, 'score_kind': 'rerank'} for i, score in enumerate(row['scores'], 1)],
        sufficient=row['sufficient'], source=source, rankings_source=f'fixture:calibration_rankings.json#{row["eval_id"]}')
        for row in data['samples']]
    split = CalibrationSplit.from_ids(data['calibration_ids'], data['held_out_ids'],
        dataset_fingerprint=source.dataset_fingerprint)
    return samples, split


def rule(*, top_k=2, budget_fingerprint=None):
    from app.quality.calibration import fit_confidence_rule
    samples, split = samples_and_split(top_k=top_k, budget_fingerprint=budget_fingerprint)
    return fit_confidence_rule(samples, split, baseline_threshold=.5).rule


def payload(scores=(.9, .2), *, ids=None):
    return {'found': bool(scores), 'matches': [
        {'id': ids[i] if ids is not None else str(i+1), 'question': f'规则{i+1}', 'answer': f'完整政策原文{i+1}',
         'section_path': '政策', 'score': score, 'score_kind': 'rerank'} for i, score in enumerate(scores)],
        'retrieval': {'strategy': 'hybrid_rerank', 'candidate_count': len(scores), 'match_count': len(scores)}}
