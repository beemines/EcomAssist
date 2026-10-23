"""Synthetic selection fixtures never count as real human decisions or model scores."""
from collections import Counter
from datetime import datetime,timezone
import pytest
from app.topics.reviews import ReviewDecision,apply_review,digest
from app.topics.taxonomy import default_taxonomy
from ml.topic_classifier.tests.test_data import corpus
from ml.topic_classifier.artifacts import make_test_review_packs,human_subset_report


def rows():return [row.model_copy(update={'pilot':False}) for row in corpus(10)]


def test_test_gold_selection_is_frozen_group_diverse_and_covers_each_label_twice():
    samples=rows();predictions={row.id:row.labels for row in samples}
    gold,errors,selection=make_test_review_packs(samples,predictions,dataset_hash='1'*64,model_version='2'*64)
    repeated=make_test_review_packs(list(reversed(samples)),predictions,dataset_hash='1'*64,model_version='2'*64)
    assert gold.pack_hash==repeated[0].pack_hash and selection==repeated[2]
    assert gold.purpose=='test' and len(gold.samples)==68 and errors is None
    assert len({row.group_id for row in gold.samples})==68
    coverage=Counter(label for row in gold.samples for label in row.labels)
    assert all(coverage[label]>=2 for label in default_taxonomy().ordered_names)
    assert selection['human_status']=='pending' and selection['errors_count']==0


def test_error_review_is_deduplicated_and_does_not_repeat_gold_work():
    samples=rows();predictions={row.id:() for row in samples}
    gold,errors,selection=make_test_review_packs(samples,predictions,dataset_hash='1'*64,model_version='2'*64)
    assert errors.purpose=='errors' and 1<=len(errors.samples)<=34
    assert not ({row.id for row in gold.samples}&{row.id for row in errors.samples})
    assert len({row.group_id for row in errors.samples})==len(errors.samples)
    assert selection['predictions_hash'] and selection['error_pack_hash']==errors.pack_hash


def test_error_pack_does_not_repeat_a_gold_family_through_another_paraphrase():
    samples=rows()
    samples+= [row.model_copy(update={'id':row.id+'-variant','text':row.text+'另一说法'}) for row in samples]
    prediction={row.id:() for row in samples}
    gold,errors,_=make_test_review_packs(samples,prediction,dataset_hash='1'*64,model_version='2'*64)
    assert not ({row.group_id for row in gold.samples}&{row.group_id for row in errors.samples})


def test_human_corrections_create_only_a_subset_report_against_frozen_predictions():
    samples=rows();predictions={row.id:() for row in samples}
    gold,_,selection=make_test_review_packs(samples,predictions,dataset_hash='1'*64,model_version='2'*64)
    decisions=[ReviewDecision(sample_id=row.id,pack_hash=gold.pack_hash,decision='accept',final_labels=row.labels,
        reviewer='unit-test-fixture-only',reviewed_at=datetime.now(timezone.utc).isoformat()) for row in gold.samples]
    receipt=apply_review(gold,decisions)
    result=human_subset_report(gold,receipt,predictions,selection)
    assert result['reviewed_count']==result['retained_count']==68
    assert result['metrics']['sample_count']==68 and result['metrics']['needs_review_rate']==1
    assert result['model_version']=='2'*64
    changed=predictions|{gold.samples[0].id:('其他',)}
    with pytest.raises(ValueError):human_subset_report(gold,receipt,changed,selection)


def test_review_selection_cannot_accept_training_rows_or_bad_prediction_membership():
    samples=rows();prediction={row.id:row.labels for row in samples}
    with pytest.raises(ValueError):make_test_review_packs(samples[:-1],prediction,dataset_hash='1'*64,model_version='2'*64)
    samples[0]=samples[0].model_copy(update={'pilot':True})
    with pytest.raises(ValueError):make_test_review_packs(samples,prediction,dataset_hash='1'*64,model_version='2'*64)


def test_new_68_review_includes_four_of_each_explicit_scene_before_general_class_coverage():
    samples=rows();predictions={r.id:r.labels for r in samples}
    ordered=sorted(samples,key=lambda r:digest({'scene-fixture':r.id}))
    required={'A':[r.id for r in ordered[:12]],'B':[r.id for r in ordered[12:24]]}
    gold,_,selection=make_test_review_packs(samples,predictions,dataset_hash='1'*64,model_version='2'*64,required_scenes=required)
    ids={r.id for r in gold.samples}
    assert len(gold.samples)==68 and all(len(ids&set(required[k]))>=4 for k in ('A','B'))
    assert selection['gold_scene_coverage']['A']>=4 and selection['gold_scene_coverage']['B']>=4
    with pytest.raises(ValueError):make_test_review_packs(samples,predictions,dataset_hash='1'*64,model_version='2'*64,
        required_scenes={'A':['unknown']*12,'B':required['B']})
