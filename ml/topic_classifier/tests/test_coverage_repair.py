"""The new data contract is required by the training entry point, not only a script."""
import hashlib
import json
from pathlib import Path
import pytest
from app.topics.reviews import make_review_pack,digest
from app.topics.review_submission import TopicReviewService,ReviewSubmission
from tests.test_topic_review_submission import payload
from app.topics.types import LabelledSample


def sample(i,text,labels):
    return LabelledSample(id=i,text=text,labels=labels,origin='synthetic',group_id=i,source_question_ids=[],pilot=False)


def scene_rows(prefix,n):
    a=[sample(prefix+'a'+str(i),'挤脚'+str(i)+'换宽点',['退换货','尺码']) for i in range(n)]
    b=[sample(prefix+'b'+str(i),'不退问长'+str(i),['尺码']) for i in range(n)]
    return a+b


def contract_fixture(tmp_path):
    iteration=tmp_path/'coverage-v5';dataset=iteration/'dataset';dataset.mkdir(parents=True)
    train=scene_rows('tr',32);val=scene_rows('va',16)
    pack=make_review_pack(train,snapshot_hash='1'*64,teacher_receipts=(),purpose='pilot')
    local=iteration/'train-review';local.mkdir();(local/'pack.json').write_text(pack.model_dump_json(),encoding='utf-8')
    service=TopicReviewService(local);service.save(ReviewSubmission.model_validate(payload(pack)))
    fields=dict(version='ch10-coverage-v5',manifest_hash='a'*64,training_status_hash='1'*64,
        review_receipt_hash=service.state().receipt_hash,new_train_ids=sorted(r.id for r in train),
        new_validation_ids=sorted(r.id for r in val),test_scene_hash='b'*64)
    (dataset/'coverage.json').write_text(json.dumps(fields|{'contract_hash':digest(fields)}),encoding='utf-8')
    return dataset,train,val


def test_missing_actual_human_review_prevents_freeze_before_tokenizer_or_test(tmp_path,monkeypatch):
    from ml.topic_classifier.coverage_repair import freeze_coverage
    original=Path.open
    def guard(path,*args,**kwargs):
        assert path.name!='test.jsonl'
        return original(path,*args,**kwargs)
    monkeypatch.setattr(Path,'open',guard)
    with pytest.raises(ValueError,match='human'):freeze_coverage(tmp_path/'source',tmp_path/'coverage-v5',tmp_path/'base')


def test_coverage_cli_freeze_requires_human_before_creating_dataset(tmp_path,monkeypatch):
    from ml.topic_classifier.cli import main
    monkeypatch.setattr('sys.argv',['topic','freeze-coverage','--source',str(tmp_path/'source'),
        '--iteration-root',str(tmp_path/'coverage-v5'),'--base-dir',str(tmp_path/'base')])
    with pytest.raises(ValueError,match='human'):main()
    assert not (tmp_path/'coverage-v5/dataset').exists()


def test_training_contract_binds_real_receipt_and_checks_new_scenes_without_opening_test(tmp_path,monkeypatch):
    from ml.topic_classifier.coverage_repair import validate_training_contract
    dataset,train,val=contract_fixture(tmp_path);original=Path.open
    def guard(path,*args,**kwargs):
        assert path.name not in ('test.jsonl','test-scenes.json')
        return original(path,*args,**kwargs)
    monkeypatch.setattr(Path,'open',guard)
    assert validate_training_contract(dataset,'a'*64,train,val)==hashlib.sha256((dataset/'coverage.json').read_bytes()).hexdigest()
    changed=[train[0].model_copy(update={'labels':('尺码',)})]+train[1:]
    with pytest.raises(ValueError):validate_training_contract(dataset,'a'*64,changed,val)
    with pytest.raises(ValueError):validate_training_contract(dataset,'c'*64,train,val)


def test_training_entry_refuses_a_coverage_dataset_with_its_contract_removed(tmp_path):
    from ml.topic_classifier.train import read_training_data
    from ml.topic_classifier.tests.test_data import corpus,Tokenizer
    from ml.topic_classifier.data import build_splits,write_dataset,freeze_augmentations
    dataset=tmp_path/'coverage-v5/dataset';rows=corpus();tokenizer=Tokenizer()
    manifest=build_splits(rows,tokenizer);write_dataset(rows,manifest,dataset)
    parent=LabelledSample.model_validate_json((dataset/'train.jsonl').read_text(encoding='utf-8').splitlines()[0])
    freeze_augmentations(rows,manifest,[parent.model_copy(update={'id':parent.id+'-aug','text':parent.text+'呀'})],tokenizer,dataset)
    with pytest.raises(ValueError,match='coverage'):read_training_data(dataset)
