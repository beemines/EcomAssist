"""A frozen local sampling control must not change labels or evaluation draws."""
from collections import Counter
from types import SimpleNamespace

import pytest
import torch
from transformers import BertConfig, BertForSequenceClassification, TrainingArguments, default_data_collator

from app.topics.types import LabelledSample
from ml.topic_classifier.data import SEED
from ml.topic_classifier.train import EncodedSamples


def samples():
    return tuple(SimpleNamespace(id=str(i), text='短句问题' if i<8 else '这是用于本地采样对照的完整长句问题文本') for i in range(100))


def test_short_quota_is_thirty_percent_without_extra_steps_or_label_access():
    from ml.topic_classifier.sampling import ShortQuotaSampler
    source=samples()
    sampler=ShortQuotaSampler(source)
    indices=list(sampler)
    assert len(indices)==len(sampler)==100
    assert sum(i<8 for i in indices)==30
    assert len({i for i in indices if i>=8})==70
    assert set(i for i in indices if i<8)==set(range(8))
    assert set(Counter(i for i in indices if i<8).values())<={3,4}
    assert all(0<=i<100 for i in indices)
    assert [r.id for r in source]==[str(i) for i in range(100)]


def test_epoch_stream_is_reproducible_on_resume_and_different_between_epochs():
    from ml.topic_classifier.sampling import ShortQuotaSampler
    a=ShortQuotaSampler(samples());b=ShortQuotaSampler(samples())
    first=list(a)
    a.set_epoch(3);third=list(a)
    b.set_epoch(3)
    assert third==list(b) and third!=first and sum(i<8 for i in third)==30
    a.set_epoch(0)
    assert list(a)==first
    with pytest.raises(ValueError):a.set_epoch(-1)
    with pytest.raises(ValueError):ShortQuotaSampler(samples(),seed=123)
    with pytest.raises(ValueError):ShortQuotaSampler(samples()[8:])


class IndexTokenizer:
    def __init__(self,rows):self.index={row.text:i for i,row in enumerate(rows)}
    def __call__(self,text,**kwargs):return {'input_ids':[self.index[text]],'attention_mask':[1]}


def test_real_trainer_loader_resamples_only_training_and_applies_epoch(tmp_path):
    from ml.topic_classifier.sampling import ShortSamplingTrainer
    rows=tuple(LabelledSample(id=str(i),text=(f'短句{i:02d}' if i<8 else f'完整长句问题用于本地采样对照验证第{i:02d}条'),
        labels=['其他'],origin='synthetic',group_id=str(i),source_question_ids=[],pilot=False) for i in range(100))
    data=EncodedSamples(rows,IndexTokenizer(rows))
    model=BertForSequenceClassification(BertConfig(vocab_size=128,hidden_size=16,num_hidden_layers=1,
        num_attention_heads=2,intermediate_size=32,num_labels=17,problem_type='multi_label_classification'))
    args=TrainingArguments(output_dir=str(tmp_path),use_cpu=True,per_device_train_batch_size=4,
        per_device_eval_batch_size=4,seed=SEED,data_seed=SEED,report_to='none',dataloader_pin_memory=False)
    trainer=ShortSamplingTrainer(model=model,args=args,train_dataset=data,eval_dataset=data,
        data_collator=default_data_collator)
    loader=trainer.get_train_dataloader()
    loader.set_epoch(0)
    first=[int(i) for batch in loader for i in batch['input_ids'][:,0]]
    loader.set_epoch(1)
    second=[int(i) for batch in loader for i in batch['input_ids'][:,0]]
    assert len(first)==len(second)==100 and sum(i<8 for i in first)==sum(i<8 for i in second)==30
    assert first!=second
    actual=[int(i) for batch in trainer.get_eval_dataloader() for i in batch['input_ids'][:,0]]
    assert actual==list(range(100))


def test_cli_control_is_explicit_and_does_not_change_default(monkeypatch,capsys):
    from ml.topic_classifier import cli,train
    captured=[]
    def fake_training(dataset,base_dir,output,**kwargs):
        captured.append(kwargs)
        return SimpleNamespace(model_dump_json=lambda **_: '{}')
    monkeypatch.setattr(train,'train',fake_training)
    base=['topic','train','--dataset','unused','--base-dir','unused','--output','unused']
    monkeypatch.setattr('sys.argv',base+['--short-sampling-control'])
    cli.main()
    assert captured[-1].get('short_sampling') is True
    monkeypatch.setattr('sys.argv',base)
    cli.main()
    assert captured[-1].get('short_sampling',False) is False
