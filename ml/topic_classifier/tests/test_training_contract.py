"""Labelled fixtures and a tiny random model test contracts, never model quality."""
import json
from pathlib import Path
import numpy as np
import pytest
import torch
from transformers import BertConfig,BertForSequenceClassification
from ml.topic_classifier.train import training_arguments,EncodedSamples,read_training_data,compute_metrics,encoder_hash,assert_full_trainable,best_validation_epoch
from ml.topic_classifier.tests.test_data import corpus,Tokenizer
from ml.topic_classifier.data import build_splits,write_dataset,freeze_augmentations


@pytest.fixture(scope='module')
def frozen(tmp_path_factory):
    root=tmp_path_factory.mktemp('train-contract')
    rows=corpus();tokenizer=Tokenizer();manifest=build_splits(rows,tokenizer)
    write_dataset(rows,manifest,root)
    from app.topics.types import LabelledSample
    parent=LabelledSample.model_validate_json((root/'train.jsonl').read_text(encoding='utf-8').splitlines()[0])
    child=parent.model_copy(update={'id':parent.id+'-aug','text':parent.text+'呀'})
    freeze_augmentations(rows,manifest,[child],tokenizer,root)
    return root,manifest


def test_training_configuration_is_full_local_eight_epoch_with_early_stop_contract(tmp_path):
    args=training_arguments(tmp_path,4)
    assert args.num_train_epochs==8 and args.per_device_train_batch_size==4 and args.gradient_accumulation_steps==4
    assert args.fp16 and args.gradient_checkpointing and args.learning_rate==2e-5 and args.weight_decay==.01
    assert args.warmup_steps==.1 and args.max_grad_norm==1 and args.save_total_limit==2
    assert args.eval_strategy.value=='epoch' and args.save_strategy.value=='epoch'
    assert args.load_best_model_at_end and args.metric_for_best_model=='macro_f1' and args.greater_is_better
    assert args.optim.value=='adamw_torch' and args.report_to==[] and args.dataloader_num_workers==0
    assert args.seed==args.data_seed==20261021
    for micro in (1,2):assert training_arguments(tmp_path,micro).gradient_accumulation_steps*micro==16
    with pytest.raises(ValueError):training_arguments(tmp_path,3)


def test_training_reads_only_train_and_validation_truth(frozen,monkeypatch):
    root,manifest=frozen;opened=[]
    original=Path.open
    def guard(self,*args,**kwargs):
        opened.append(self.name)
        assert self.name!='test.jsonl','Training must never open held-out truth'
        return original(self,*args,**kwargs)
    monkeypatch.setattr(Path,'open',guard)
    data=read_training_data(root)
    assert len(data.train)==len(manifest.splits['train'])+1 and len(data.validation)==len(manifest.splits['validation'])
    assert 'test.jsonl' not in opened
    assert not ({row.id for row in data.train}&{row.id for row in data.validation})


def test_float_multihot_targets_use_bce_and_all_parameters_have_gradients():
    from app.topics.types import LabelledSample
    row=LabelledSample(id='sample',text='尺码不合适想换货',labels=['退换货','尺码'],origin='synthetic',group_id='family',source_question_ids=[],pilot=False)
    encoded=EncodedSamples([row],Tokenizer())[0]
    assert encoded['labels'].dtype==torch.float32 and encoded['labels'].shape==(17,)
    assert encoded['labels'].sum()==2 and encoded['labels'][0]==encoded['labels'][2]==1
    model=BertForSequenceClassification(BertConfig(vocab_size=128,hidden_size=16,num_hidden_layers=1,num_attention_heads=2,
        intermediate_size=32,num_labels=17,problem_type='multi_label_classification',hidden_dropout_prob=0,attention_probs_dropout_prob=0))
    assert_full_trainable(model);before=encoder_hash(model)
    batch={key:torch.as_tensor(value).unsqueeze(0) for key,value in encoded.items()}
    output=model(**batch)
    assert torch.allclose(output.loss,torch.nn.functional.binary_cross_entropy_with_logits(output.logits,batch['labels']))
    output.loss.backward()
    assert all(parameter.grad is not None for parameter in model.parameters())
    torch.optim.AdamW(model.parameters(),lr=2e-5).step()
    assert encoder_hash(model)!=before
    next(model.base_model.parameters()).requires_grad_(False)
    with pytest.raises(ValueError):assert_full_trainable(model)


def test_dataset_rejects_unfinished_augmentation_and_corrupt_overlay(frozen,tmp_path):
    import shutil
    original,_=frozen;root=tmp_path/'copy';shutil.copytree(original,root)
    audit=json.loads((root/'data-audit.json').read_text(encoding='utf-8'))
    (root/'data-audit.json').write_text(json.dumps(audit|{'augmentation':'pending'}),encoding='utf-8')
    with pytest.raises(ValueError):read_training_data(root)
    (root/'data-audit.json').write_text(json.dumps(audit),encoding='utf-8')
    with (root/'train-augmentations.jsonl').open('a',encoding='utf-8') as out:out.write('tampered')
    with pytest.raises(ValueError):read_training_data(root)


def test_metrics_keep_all_17_columns_and_other_exclusive_without_argmax():
    truth=np.zeros((3,17));truth[0,[0,2]]=1;truth[1,16]=1;truth[2,1]=1
    logits=np.full((3,17),-10.);logits[0,[0,2,16]]=10.;logits[1,16]=10.
    metrics=compute_metrics((logits,truth))
    assert metrics['macro_f1']==pytest.approx(3/17) and metrics['micro_f1']==pytest.approx(6/7)
    assert metrics['needs_review_rate']==pytest.approx(1/3)
    logits[0,0]=np.nan
    with pytest.raises(ValueError):compute_metrics((logits,truth))


def test_best_validation_epoch_keeps_earlier_tie_and_never_reads_test_metrics():
    history=[{'epoch':1.,'eval_macro_f1':.3,'step':10},{'epoch':2.,'eval_macro_f1':.4,'step':20},
        {'epoch':3.,'eval_macro_f1':.4,'step':30},{'epoch':4.,'test_macro_f1':.99,'step':40}]
    assert best_validation_epoch(history)['epoch']==2
    with pytest.raises(ValueError):best_validation_epoch([{'epoch':1,'test_macro_f1':1}])


def test_training_lease_reuses_stale_file_and_never_replaces_live_inode(tmp_path):
    from ml.topic_classifier.train import training_lease
    marker=tmp_path/'.train.lock';marker.write_bytes(b'old stale crash file')
    with training_lease(tmp_path):
        with pytest.raises(RuntimeError):
            with training_lease(tmp_path):pass
        assert marker.stat().st_size==len(b'old stale crash file')
    assert marker.read_bytes()==b'old stale crash file'
    with training_lease(tmp_path):assert marker.exists()
