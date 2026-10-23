"""Append short validation without moving any prior held-out example into training."""
from pathlib import Path
import pytest
from ml.topic_classifier.tests.test_remediation_data import original,extra
from ml.topic_classifier.tests.test_data import Tokenizer


def test_new_validation_appends_to_old_membership_and_keeps_all_exposed_tests_out(tmp_path):
    from ml.topic_classifier.remediation import pinned_manifest
    source,old=original(tmp_path)
    addition=extra(64,'new-validation')
    manifest,rows=pinned_manifest(source,extra(64,'new-train'),extra(187,'fresh-test'),Tokenizer(),new_validation=addition)
    assert set(old.splits['validation'])<set(manifest.splits['validation'])
    assert set(manifest.splits['validation'])==set(old.splits['validation'])|{r.id for r in addition}
    assert set(old.splits['train'])<set(manifest.splits['train'])
    assert not (set(old.splits['test'])&set(i for values in manifest.splits.values() for i in values))
    for name in ('validation','test'):
        assert all(min(c['positive'],c['negative'])>=10 for c in manifest.label_counts[name].values())


def test_appended_validation_rejects_training_and_exposed_test_families(tmp_path):
    from ml.topic_classifier.remediation import pinned_manifest
    source,old=original(tmp_path);train=extra(64,'new-train');validation=extra(64,'new-validation')
    validation[0]=validation[0].model_copy(update={'group_id':train[0].group_id})
    with pytest.raises(ValueError):pinned_manifest(source,train,extra(187,'fresh-test'),Tokenizer(),new_validation=validation)


def test_missing_actual_training_review_stops_before_any_heldout_or_tokenizer_read(tmp_path,monkeypatch):
    from ml.topic_classifier.negation import freeze_negation
    original_open=Path.open
    def guard(path,*args,**kwargs):
        assert path.name!='test.jsonl','No held-out truth should open before the training review gate'
        return original_open(path,*args,**kwargs)
    monkeypatch.setattr(Path,'open',guard)
    with pytest.raises(ValueError,match='human'):freeze_negation(tmp_path/'source',tmp_path/'iteration',tmp_path/'base')


def test_freeze_command_keeps_real_human_gate_and_does_not_create_a_dataset(tmp_path,monkeypatch):
    from ml.topic_classifier.cli import main
    monkeypatch.setattr('sys.argv',['topic','freeze-negation','--source',str(tmp_path/'source'),
        '--iteration-root',str(tmp_path/'negation-v4'),'--base-dir',str(tmp_path/'base')])
    with pytest.raises(ValueError,match='human'):main()
    assert not (tmp_path/'negation-v4/dataset').exists()
