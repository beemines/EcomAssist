"""Pinned partitions preserve old train/validation and exclude exposed test IDs."""
import hashlib
import pytest
from app.topics.types import LabelledSample
from app.topics.taxonomy import default_taxonomy
from ml.topic_classifier.tests.test_data import corpus,Tokenizer
from ml.topic_classifier.data import build_splits,write_dataset

def extra(count,prefix):
    names=default_taxonomy().ordered_names
    return [LabelledSample(id=f'{prefix}-{i}',text=prefix+hashlib.sha256(f'{prefix}-{i}'.encode()).hexdigest()[:10],
        labels=[names[i%17]],origin='synthetic',group_id=f'{prefix}-family-{i}',source_question_ids=[],pilot=False) for i in range(count)]

def original(tmp_path):
    rows=corpus(120);manifest=build_splits(rows,Tokenizer());root=tmp_path/'source';write_dataset(rows,manifest,root)
    return root,manifest

def test_pinned_iteration_keeps_original_validation_hash_and_training_identity(tmp_path):
    from ml.topic_classifier.remediation import pinned_manifest
    root,old=original(tmp_path)
    new,rows=pinned_manifest(root,extra(128,'train'),extra(187,'test'),Tokenizer())
    assert new.splits['validation']==old.splits['validation']
    assert new.file_hashes['validation']==old.file_hashes['validation']
    assert set(old.splits['train'])<=set(new.splits['train'])
    assert not (set(old.splits['test'])&set(i for ids in new.splits.values() for i in ids))
    assert len(new.splits['test'])==187
    assert all(min(value['positive'],value['negative'])>=10 for value in new.label_counts['test'].values())

@pytest.mark.parametrize('bad',['family','old_test','missing_class','probe'])
def test_pinned_iteration_rejects_leakage_and_missing_coverage(tmp_path,bad):
    from ml.topic_classifier.remediation import pinned_manifest
    root,old=original(tmp_path);train=extra(128,'train');test=extra(187,'test')
    if bad=='family':test[0]=test[0].model_copy(update={'group_id':train[0].group_id})
    elif bad=='old_test':test[0]=test[0].model_copy(update={'id':old.splits['test'][0]})
    elif bad=='missing_class':test=[row.model_copy(update={'labels':('物流',)}) for row in test]
    else:train[0]=train[0].model_copy(update={'text':'买大了想退','labels':('退换货','尺码')})
    with pytest.raises(ValueError):pinned_manifest(root,train,test,Tokenizer())
