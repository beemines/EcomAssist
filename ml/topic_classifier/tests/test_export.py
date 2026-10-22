"""Fake file/CPU-check fixtures verify packaging, never training or quality."""
import json
import hashlib
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pytest
from app.topics.reviews import digest
from app.topics.manifest import verify_manifest,read_manifest
from ml.topic_classifier.evaluation import select_thresholds
from ml.topic_classifier.train import TrainingReceipt,CONFIG
from ml.topic_classifier.doctor import BASE_MODEL,BASE_REVISION,file_hash
from ml.topic_classifier.artifacts import export_bundle
from tests.test_topic_manifest import model_files


def fixtures(tmp_path,*,dataset_hash='1'*64,augmentation_hash='2'*64):
    root=tmp_path/'training';root.mkdir();best=root/'best';best.mkdir();model_files(best)
    identity=dict(dataset_hash=dataset_hash,augmentation_hash=augmentation_hash,base=BASE_MODEL,revision=BASE_REVISION,
        seed=20261021,config=CONFIG,lock_hash=file_hash(Path(__file__).parents[1]/'uv.lock'))
    (root/'run.json').write_text(json.dumps(identity),encoding='utf-8')
    history=dict(config_hash=digest(identity),dataset_hash=dataset_hash,parameters=102280721,trainable_parameters=102280721,
        encoder_before='3'*64,encoder_after='4'*64,epochs=[dict(epoch=1.,step=10,eval_macro_f1=.5)])
    (root/'history.json').write_text(json.dumps(history),encoding='utf-8')
    fields=dict(best_checkpoint=str(best.resolve()),history_path=str((root/'history.json').resolve()),dataset_hash=dataset_hash,
        config_hash=digest(identity),augmentation_hash=augmentation_hash,best_epoch=1.,best_macro_f1=.5,
        encoder_before='3'*64,encoder_after='4'*64,weights_hash=file_hash(best/'model.safetensors'),history_hash=file_hash(root/'history.json'))
    training=TrainingReceipt(**fields,receipt_hash=digest(fields))
    (root/'receipt.json').write_text(training.model_dump_json(),encoding='utf-8')
    thresholds=select_thresholds(np.zeros((20,17)),np.zeros((20,17)),split='validation')
    reports=tmp_path/'reports';reports.mkdir()
    context=dict(training_receipt_hash=training.receipt_hash,dataset_hash=training.dataset_hash,
        threshold_hash=thresholds.threshold_hash,pilot_receipt_hash='a'*64,
        validation_items=[dict(id='val-1',text='物流在哪里?')])
    (reports/'context.json').write_text(json.dumps(context),encoding='utf-8')
    return training,thresholds,reports


def test_export_core_has_no_report_hash_cycle_and_resumes_only_same_source(tmp_path,monkeypatch):
    import ml.topic_classifier.artifacts as module
    training,thresholds,reports=fixtures(tmp_path)
    monkeypatch.setattr(module,'_cpu_checks',lambda *args:dict(roundtrip=dict(passed=True,max_abs_difference=0.),
        probe=dict(text='买大了想退',labels=['退换货','尺码'],passed=True)))
    output=tmp_path/'candidate'
    identity=export_bundle(training,thresholds,reports,output)
    assert verify_manifest(output)==identity
    manifest=read_manifest(output)
    assert manifest.core.training_receipt_hash==training.receipt_hash
    assert manifest.core.files['model.safetensors'].sha256==training.weights_hash
    assert all('report' not in name for name in manifest.core.files)
    assert json.loads((reports/'probe.json').read_text(encoding='utf-8'))['passed']
    assert export_bundle(training,thresholds,reports,output)==identity
    (output/'model.safetensors').write_bytes(b'changed')
    with pytest.raises(ValueError):export_bundle(training,thresholds,reports,output)


def test_failed_cpu_roundtrip_never_publishes_a_candidate(tmp_path,monkeypatch):
    import ml.topic_classifier.artifacts as module
    training,thresholds,reports=fixtures(tmp_path)
    monkeypatch.setattr(module,'_cpu_checks',lambda *args:dict(roundtrip=dict(passed=False,max_abs_difference=1.),
        probe=dict(text='买大了想退',labels=[],passed=False)))
    with pytest.raises(ValueError):export_bundle(training,thresholds,reports,tmp_path/'candidate')
    assert not (tmp_path/'candidate').exists()
    assert not json.loads((reports/'cpu-roundtrip.json').read_text(encoding='utf-8'))['passed']


def test_failed_independent_multilabel_probe_is_not_published(tmp_path,monkeypatch):
    import ml.topic_classifier.artifacts as module
    training,thresholds,reports=fixtures(tmp_path)
    monkeypatch.setattr(module,'_cpu_checks',lambda *args:dict(roundtrip=dict(passed=True,max_abs_difference=0.),
        probe=dict(text='买大了想退',labels=['退换货'],passed=False)))
    with pytest.raises(ValueError):export_bundle(training,thresholds,reports,tmp_path/'candidate')
    assert not (tmp_path/'candidate').exists()
    assert json.loads((reports/'probe.json').read_text(encoding='utf-8'))['labels']==['退换货']


def test_cpu_loader_never_falls_back_to_a_random_missing_classifier_head(tmp_path,monkeypatch):
    import transformers
    from app.topics.taxonomy import default_taxonomy
    from ml.topic_classifier.artifacts import CPUClassifier
    weights=tmp_path/'model.safetensors';weights.write_bytes(b'fake unit loader bytes')
    config=SimpleNamespace(model_type='bert',hidden_size=768,num_hidden_layers=12,num_attention_heads=12,
        num_labels=17,problem_type='multi_label_classification',id2label=dict(enumerate(default_taxonomy().ordered_names)))
    class Model:
        def cpu(self):return self
        def float(self):return self
        def eval(self):return self
    def load(*args,**kwargs):
        return (Model(),dict(missing_keys=['classifier.weight'],unexpected_keys=[],mismatched_keys=[],error_msgs=[])) if kwargs.get('output_loading_info') else Model()
    monkeypatch.setattr(transformers.AutoConfig,'from_pretrained',lambda *a,**k:config)
    monkeypatch.setattr(transformers.AutoTokenizer,'from_pretrained',lambda *a,**k:object())
    monkeypatch.setattr(transformers.AutoModelForSequenceClassification,'from_pretrained',load)
    with pytest.raises(ValueError):CPUClassifier(tmp_path,weights_hash=hashlib.sha256(weights.read_bytes()).hexdigest())
