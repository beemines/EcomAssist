from collections import Counter
import pytest
from tests.flywheel_confidence_fakes import samples_and_split


def test_held_out_labels_do_not_change_fit():
    from app.quality.calibration import fit_confidence_rule
    samples, split = samples_and_split()
    original = fit_confidence_rule(samples, split, baseline_threshold=.5)
    changed = [sample.model_copy(update={'sufficient': not sample.sufficient})
               if sample.eval_id in split.held_out_ids else sample for sample in samples]
    replay = fit_confidence_rule(changed, split, baseline_threshold=.5)
    assert replay.rule == original.rule
    assert replay.held_out != original.held_out


def test_constant_features_do_not_claim_perfect_discrimination():
    from app.quality.calibration import fit_confidence_rule
    samples, split = samples_and_split()
    constant = [row.model_copy(update={'rankings': [
        row.rankings[0].model_copy(update={'score': .4})]}) for row in samples]
    first = fit_confidence_rule(constant, split, baseline_threshold=.5)
    second = fit_confidence_rule(constant, split, baseline_threshold=.5)
    assert first.rule == second.rule
    assert first.calibration['f1'] == pytest.approx(2/3)
    assert first.calibration['false_refusal'] == 2


def test_weights_allow_zero_but_never_all_zero_and_are_frozen_by_source():
    from app.quality.calibration import fit_confidence_rule
    samples, split = samples_and_split()
    result = fit_confidence_rule(samples, split, baseline_threshold=.5)
    assert all(type(value) is int and 0 <= value <= 3 for value in result.rule.weights)
    assert sum(result.rule.weights) > 0
    assert result.calibration['n'] == result.held_out['n'] == 4
    assert result.baseline['calibration']['n'] == 4
    assert result.rule.source.source_kind == 'fixture'


def test_frozen_split_is_stratified_and_keeps_regressions_with_original_group():
    from app.rag_evaluation.dataset import load_dataset, DATASET_ID
    from app.quality.calibration import build_calibration_split
    from pathlib import Path
    dataset = load_dataset(DATASET_ID, root=Path('evals/datasets'))
    first, second = build_calibration_split(dataset), build_calibration_split(dataset)
    assert first == second
    assert len(first.calibration_ids) == 100 and len(first.held_out_ids) == 200
    assert not set(first.calibration_ids) & set(first.held_out_ids)
    cases = {case.eval_id: case for case in dataset.cases}
    assert Counter(cases[identifier].bucket for identifier in first.calibration_ids) == {
        'A_policy': 20, 'B_model': 20, 'C_colloquial': 20, 'D_unanswerable': 20, 'E_multi': 20}
    assert first.regression_sides['R3'] == first.side_for('D3')
    assert first.regression_sides['R30'] == first.side_for('D30')


def test_missing_label_class_fails_before_fitting():
    from app.quality.calibration import fit_confidence_rule
    samples, split = samples_and_split()
    with pytest.raises(ValueError, match='label'):
        fit_confidence_rule([row.model_copy(update={'sufficient': True}) for row in samples], split)


def test_calibration_cli_dry_run_reads_no_credentials_or_database(monkeypatch, capsys):
    from app.flywheel import cli
    monkeypatch.setattr(cli, 'load_settings', lambda: pytest.fail('dry-run loaded credentials'))
    cli.main(['calibrate', '--database', 'test', '--output', 'runtime/ch09-evidence/calibration',
        '--acceptance-run', 'ch09-local-20261019'])
    output = capsys.readouterr().out
    assert 'dry-run' in output and '300' in output and '100' in output and '200' in output


async def test_collected_samples_use_actual_prompt_budget_and_gold_groups():
    from pathlib import Path
    from app.rag_evaluation.dataset import load_dataset, DATASET_ID
    from app.quality.calibration import build_calibration_split, collect_calibration_samples
    from app.quality.evidence_confidence import evidence_budget_fingerprint
    from tests.flywheel_confidence_fakes import payload
    from types import SimpleNamespace
    dataset = load_dataset(DATASET_ID, root=Path('evals/datasets'))
    id_map = {chunk.chunk_key: i for i, chunk in enumerate(dataset.chunks, 1)}
    first = dataset.cases[0]
    gold = [id_map[key] for key in first.groups[0].alternatives[0]]
    seen = []
    class Retrieval:
        async def retrieve(self, question, **kwargs):
            seen.append(kwargs)
            data = payload([.9] * len(gold), ids=[str(key) for key in gold])
            return data
    source = samples_and_split()[0][0].source.model_copy(update={
        'dataset_id': dataset.dataset_id, 'dataset_fingerprint': dataset.fingerprint,
        'corpus_hash': dataset.corpus_hash, 'source_kind': 'actual', 'top_k': 10,
        'budget_fingerprint': evidence_budget_fingerprint(top_k=10, token_budget=6000)})
    split = build_calibration_split(dataset)
    result = await collect_calibration_samples(dataset, split, id_map, Retrieval(), source,
        token_budget=6000, case_ids=[first.eval_id])
    assert len(result) == 1 and result[0].sufficient
    assert seen[0]['top_k'] == 10 and seen[0]['query_plan'].standard == first.query
    assert not seen[0]['query_plan'].expansions


async def test_calibration_run_cleans_owned_resources_and_persists_report(tmp_path, monkeypatch):
    import json
    from types import SimpleNamespace
    from app.quality import calibration, calibration_resources
    from app.rag_evaluation import dataset, manager, store
    from app.rag_evaluation.contracts import CleanupResult
    from tests.fakes import fake_settings
    samples, split = samples_and_split()
    fixture = SimpleNamespace(dataset_id='fixture_ch09', fingerprint='a'*64, corpus_hash='b'*64,
        cases=[SimpleNamespace(eval_id=row.eval_id) for row in samples])
    monkeypatch.setattr(dataset, 'load_dataset', lambda *a, **k: fixture)
    monkeypatch.setattr(calibration, 'build_calibration_split', lambda data: split)
    monkeypatch.setattr(manager, 'build_run_config', lambda *a: {})
    class Store:
        def __init__(self, path): pass
        async def create(self, *args): return 'owned-test-run'
    monkeypatch.setattr(store, 'RunStore', Store)
    class Resources:
        repository = embedder = index = reranker = None
        closed = False
        def __init__(self, *args, **kwargs): pass
        async def prepare(self, dataset): return {}
        async def cleanup(self):
            Resources.closed = True
            return CleanupResult(True, (), ())
    monkeypatch.setattr(calibration_resources, 'CalibrationResources', Resources)
    async def collect(*args, **kwargs): return samples
    monkeypatch.setattr(calibration, 'collect_calibration_samples', collect)
    result = await calibration.run_calibration(fake_settings(), tmp_path, None)
    assert Resources.closed
    manifest = json.loads((tmp_path / 'manifest.json').read_text(encoding='utf-8'))
    assert manifest['state'] == 'completed' and manifest['cleanup']['ok']
    assert json.loads((tmp_path / 'rule.json').read_text(encoding='utf-8'))['rule_version'] == result.rule.rule_version
