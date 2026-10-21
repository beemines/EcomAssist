"""Concrete final-review reproductions; every upstream boundary stays offline."""
import json
from pathlib import Path
import pytest


async def test_legacy_eval_row_does_not_require_a_native_run_key(tmp_path):
    from tests.test_eval_pipeline_manager import Repository,manager
    repository=Repository()
    repository.rows['legacy']={'id':'7','run_key':None,'metrics':{'faithfulness':.9}}
    value=manager(tmp_path,repository)
    result=await value.list_runs()
    assert result['items'][0]['metrics']=={'faithfulness':.9}
    assert result['comparison']['latest_id'] is None
    await value.close()


@pytest.mark.parametrize('unit', ['kg','L','公斤','升','ml','克','W','厘米'])
def test_numeric_unit_mismatch_blocks_even_high_scoring_model_evidence(unit):
    from tests.flywheel_confidence_fakes import rule,payload
    from app.quality.reference_confidence import reference_rule
    from app.quality.evidence_confidence import evaluate_evidence
    selected=reference_rule(rule(),threshold=.27,score_floor=0.)
    data=payload((.99,.9))
    for item in data['matches']: item.update(question='MH-LP100 使用范围',answer=f'适用于8{unit}，容量9{unit}。')
    result=evaluate_evidence(data,selected,question=f'MH-LP100适用20{unit}吗？',top_k=2,
        budget_fingerprint=selected.source.budget_fingerprint)
    assert result.features['anchors_complete'] is False
    assert not result.useful


def test_equivalent_unit_spellings_and_numeric_boundaries():
    from app.quality.reference_confidence import clause_features
    content=[{'answer':'MH-LP100适用于8公斤猫咪，容量9升。'}]
    assert clause_features('MH-LP100适用8kg猫咪，容量9L？',content)['anchors_complete']
    assert not clause_features('MH-LP100适用8kg猫咪，容量19L？',content)['anchors_complete']


def test_unit_comparison_never_rounds_distinct_large_values():
    from app.quality.reference_confidence import clause_features
    result=clause_features('MH-LP100容量123456789012345678901234567890L？',
        [{'answer':'MH-LP100容量123456789012345678901234567891L。'}])
    assert result['anchors_complete'] is False


def test_historical_v2_rule_retains_its_recorded_feature_semantics():
    from tests.flywheel_confidence_fakes import rule,payload
    from app.quality.reference_confidence import reference_rule
    from app.quality.evidence_confidence import canonical_hash,parse_rule,evaluate_evidence
    raw=reference_rule(rule(),threshold=.27,score_floor=0.).model_dump(mode='json',exclude={'rule_version'})
    raw['algorithm']='ch09-four-signal-zero-allow-v2';raw['rule_version']=canonical_hash(raw)
    historical=parse_rule(raw);data=payload((.99,.9))
    for item in data['matches']: item.update(question='MH-LP100 使用范围',answer='适用于8kg。')
    decision=evaluate_evidence(data,historical,question='MH-LP100适用20kg吗？',top_k=2,
        budget_fingerprint=historical.source.budget_fingerprint)
    assert decision.features['anchor_count']==1
    assert decision.rule_version==historical.rule_version


@pytest.mark.parametrize('kind',['overlap','fingerprint','cross_group'])
def test_deserialized_split_cannot_leak_labels_or_forge_its_hash(kind):
    from tests.flywheel_confidence_fakes import samples_and_split
    from app.quality.calibration import CalibrationSplit
    from app.quality.evidence_confidence import canonical_hash
    _,split=samples_and_split(); raw=split.model_dump(mode='json')
    if kind=='overlap': raw['calibration_ids'].append(raw['held_out_ids'][0])
    elif kind=='fingerprint': raw['fingerprint']='f'*64
    else:
        raw['case_groups'][raw['held_out_ids'][0]]=raw['case_groups'][raw['calibration_ids'][0]]
        raw['fingerprint']=canonical_hash({k:v for k,v in raw.items() if k!='fingerprint'})
    with pytest.raises(ValueError): CalibrationSplit.model_validate_json(json.dumps(raw))


def test_recompute_rejects_a_valid_but_different_frozen_partition(tmp_path,monkeypatch):
    from app.quality.calibration import build_calibration_split,CalibrationSplit
    from app.quality.confidence_report import recompute_reference_report
    import app.rag_evaluation.dataset as module
    dataset=module.load_dataset(module.DATASET_ID,root=Path('evals/datasets'))
    split=build_calibration_split(dataset)
    changed=CalibrationSplit.from_ids(split.held_out_ids,split.calibration_ids,
        dataset_fingerprint=split.dataset_fingerprint,case_groups=split.case_groups,
        group_buckets=split.group_buckets,
        regression_sides={key:'held_out' if side=='calibration' else 'calibration'
            for key,side in split.regression_sides.items()})
    folder=tmp_path/'runtime/ch09-evidence/calibration';folder.mkdir(parents=True)
    (folder/'split.json').write_text(changed.model_dump_json(),encoding='utf-8')
    monkeypatch.setattr(module,'load_dataset',lambda *a,**kw:dataset)
    with pytest.raises(ValueError,match='Frozen split'): recompute_reference_report(tmp_path)


async def test_atomic_snapshot_retries_only_transient_windows_replace_errors(tmp_path,monkeypatch):
    import app.rag_evaluation.store as module
    from tests.test_rag_store import config
    original=module.os.replace; attempts=[]
    def sharing(src,dst):
        attempts.append(1)
        if len(attempts)<=2:
            error=PermissionError('controlled Windows sharing denial');error.winerror=5
            raise error
        return original(src,dst)
    monkeypatch.setattr(module.os,'replace',sharing)
    store=module.RunStore(tmp_path)
    key=await store.create(config(),[('E1','dense')])
    assert (await store.get(key))['run_id']==key
    assert len(attempts)==3


async def test_atomic_snapshot_permanent_denial_is_bounded_and_not_published(tmp_path,monkeypatch):
    import app.rag_evaluation.store as module
    from tests.test_rag_store import config
    attempts=[]
    def deny(src,dst):
        attempts.append(1);error=PermissionError('controlled persistent Windows denial');error.winerror=5
        raise error
    monkeypatch.setattr(module.os,'replace',deny)
    with pytest.raises(module.StoreError): await module.RunStore(tmp_path).create(config(),[('E1','dense')])
    assert len(attempts)==4
    assert not list(tmp_path.rglob('manifest.json'))


def test_missing_usage_does_not_dilute_per_request_average_or_share():
    from tests.test_intent_usage import root,generation
    from app.observability.intent_usage import summarize_intent_usage
    rows=summarize_intent_usage([root(),root('t2')],[generation('known',{'total':100}),generation('unknown',None,trace_id='t2')])
    [row]=rows
    assert row['actual_tokens']==100 and row['unknown_calls']==1
    assert row['average_tokens'] is None and row['token_share'] is None


async def test_owned_mcp_test_child_binds_an_os_port_without_a_probe(tmp_path,monkeypatch):
    import tests.mcp_processes as module
    def forbidden_probe(): raise AssertionError('probe then release races before the child binds')
    monkeypatch.setattr(module,'free_port',forbidden_probe)
    async with module.server_process('business_mcp.logistics',tmp_path) as (child,connection):
        assert child.args[-2:]==['--port','0']
        assert connection['url'].startswith('http://127.0.0.1:')
        assert connection['url'].endswith('/mcp') and ':0/' not in connection['url']
