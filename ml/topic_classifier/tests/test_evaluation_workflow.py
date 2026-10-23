"""Fixture-only IO ordering: freeze validation choices before held-out truth opens."""
import json
from pathlib import Path
import numpy as np
import pytest
from app.topics.types import LabelledSample,ClassifyItem
from ml.topic_classifier.tests.test_data import corpus,Tokenizer
from ml.topic_classifier.data import build_splits,write_dataset,freeze_augmentations
from ml.topic_classifier.doctor import file_hash
from ml.topic_classifier.tests.test_export import fixtures
from ml.topic_classifier.artifacts import evaluate_run


def test_evaluation_freezes_choices_before_test_then_creates_pending_review_only(tmp_path,monkeypatch):
    import ml.topic_classifier.artifacts as module
    rows=corpus();tokenizer=Tokenizer();manifest=build_splits(rows,tokenizer)
    dataset=tmp_path/'dataset';write_dataset(rows,manifest,dataset)
    parent=LabelledSample.model_validate_json((dataset/'train.jsonl').read_text(encoding='utf-8').splitlines()[0])
    child=parent.model_copy(update={'id':parent.id+'-aug','text':parent.text+'呀'})
    freeze_augmentations(rows,manifest,[child],tokenizer,dataset)
    training,_,_=fixtures(tmp_path,dataset_hash=manifest.manifest_hash,augmentation_hash=file_hash(dataset/'train-augmentations.jsonl'))
    reports=tmp_path/'actual-fixture-reports'
    class FakeCPUClassifierForOrderingOnly:
        def __init__(self,*args,**kwargs):pass
        def predict(self,items):
            assert all(isinstance(row,ClassifyItem) and not hasattr(row,'labels') for row in items)
            result=np.full((len(items),17),-10.);result[:,0]=10.
            for i,row in enumerate(items):
                if row.id=='reserved-probe':result[i,2]=10.
            return result
        def close(self):pass
    monkeypatch.setattr(module,'CPUClassifier',FakeCPUClassifierForOrderingOnly)
    original=Path.open
    def guard(self,*args,**kwargs):
        if self==dataset/'test.jsonl':
            assert (reports/'thresholds.json').exists()
            assert (reports/'context.json').exists()
        return original(self,*args,**kwargs)
    monkeypatch.setattr(Path,'open',guard)
    result=evaluate_run(dataset,Path(training.best_checkpoint).parent,reports,pilot_receipt_hash='a'*64,
        model_output=tmp_path/'model',review_root=tmp_path/'review-packs')
    assert result['status']=='complete' and result['human_status']=='pending'
    assert result['dataset_size']==len(manifest.splits['test'])
    assert (reports/'silver.json').exists() and (reports/'metrics.html').exists()
    gold=tmp_path/'review-packs/test-review/pack.json';pack=json.loads(gold.read_text(encoding='utf-8'))
    assert len(pack['samples'])==68 and pack['purpose']=='test'
    assert not gold.with_name('review-receipt.json').exists()
    before=(reports/'thresholds.json').read_bytes()
    assert evaluate_run(dataset,Path(training.best_checkpoint).parent,reports,pilot_receipt_hash='a'*64,
        model_output=tmp_path/'model',review_root=tmp_path/'review-packs')==result
    assert (reports/'thresholds.json').read_bytes()==before
    from ml.topic_classifier.artifacts import finalize_run
    from app.topics.manifest import verify_release
    from app.topics.reviews import ReviewPack,ReviewDecision,apply_review
    from datetime import datetime,timezone
    with pytest.raises(ValueError,match='human review'):
        finalize_run(reports,tmp_path/'model',review_root=tmp_path/'review-packs')
    for name in ('test-review','error-review'):
        local=tmp_path/'review-packs'/name
        if not (local/'pack.json').exists():continue
        pack=ReviewPack.model_validate_json((local/'pack.json').read_text(encoding='utf-8'))
        decisions=[ReviewDecision(sample_id=row.id,pack_hash=pack.pack_hash,decision='accept',final_labels=row.labels,
            reviewer='unit-fixture-only',reviewed_at=datetime.now(timezone.utc).isoformat()) for row in pack.samples]
        human=apply_review(pack,decisions)
        (local/'review-receipt.json').write_text(human.model_dump_json(),encoding='utf-8')
    released=finalize_run(reports,tmp_path/'model',review_root=tmp_path/'review-packs')
    assert released['human_status']=='reviewed'
    assert verify_release(tmp_path/'model').model_version==result['model_version']
    assert finalize_run(reports,tmp_path/'model',review_root=tmp_path/'review-packs')==released
    assert (reports/'thresholds.json').read_bytes()==before
    assert json.loads((reports/'silver.json').read_text(encoding='utf-8'))['human_status']=='pending'
