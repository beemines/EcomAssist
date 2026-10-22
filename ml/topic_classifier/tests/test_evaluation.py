"""Fixed labelled matrices verify metric arithmetic, not classifier quality."""
import json
import numpy as np
import pytest
from app.topics.taxonomy import default_taxonomy
from ml.topic_classifier.evaluation import evaluate_multilabel,select_thresholds,decode_logits


def test_fixed_matrix_reports_all_seventeen_one_vs_rest_confusions():
    truth=np.zeros((3,17),dtype=int);prediction=truth.copy()
    truth[:,:2]=[[1,1],[1,0],[0,1]];prediction[:,:2]=[[1,0],[0,1],[0,1]]
    report=evaluate_multilabel(truth,prediction,taxonomy=default_taxonomy())
    assert report.sample_count==3 and len(report.per_class)==17
    assert report.per_class[0].confusion==((1,0),(1,1))
    assert report.per_class[1].confusion==((0,1),(1,1))
    assert report.per_class[0].f1==pytest.approx(2/3) and report.per_class[1].f1==.5
    assert report.macro_f1==pytest.approx((2/3+.5)/17)
    assert report.micro_f1==pytest.approx(4/7) and report.exact_match==pytest.approx(1/3)
    assert report.hamming_loss==pytest.approx(3/51)
    assert report.per_class[16].support==0 and report.per_class[16].undefined_denominators
    assert 'NaN' not in report.model_dump_json() and json.loads(report.model_dump_json())['sample_count']==3


def test_empty_predictions_are_counted_as_false_negatives():
    truth=np.zeros((2,17),dtype=int);truth[:,0]=1
    report=evaluate_multilabel(truth,np.zeros_like(truth),taxonomy=default_taxonomy())
    assert report.sample_count==2 and report.needs_review_rate==1 and report.exact_match==0
    assert report.per_class[0].confusion==((0,0),(2,0)) and report.micro_f1==0


def test_thresholds_use_validation_only_and_ties_prefer_point_five():
    truth=np.zeros((20,17),dtype=int);truth[:10,0]=1
    logits=np.full((20,17),-10.);logits[:10,0]=10.
    selected=select_thresholds(logits,truth,split='validation')
    assert selected.thresholds[0]==.5 and selected.per_class[0].calibrated
    assert selected.thresholds[1]==.5 and not selected.per_class[1].calibrated
    assert selected.per_class[1].reason=='正例或负例少于10条'
    with pytest.raises(ValueError):select_thresholds(logits,truth,split='test')


def test_scan_selects_observed_validation_threshold_without_argmax_fallback():
    truth=np.zeros((20,17),dtype=int);truth[:10,0]=1
    logits=np.full((20,17),-10.)
    logits[:10,0]=np.log(.35/.65);logits[10:,0]=np.log(.2/.8)
    selected=select_thresholds(logits,truth,split='validation')
    assert selected.thresholds[0]==.35
    decoded=decode_logits(logits,selected.thresholds)
    assert decoded[:10,0].all() and not decoded[10:].any()
    other=np.full((2,17),-10000.);other[0,[0,16]]=10000.;other[1,16]=10000.
    decision=decode_logits(other,[.5]*17)
    assert decision[0,0] and not decision[0,16] and decision[1,16]
    assert not decode_logits(np.full((1,17),-1e308),[.5]*17).any()


@pytest.mark.parametrize('kind',['nan','wrong_shape','non_binary','empty'])
def test_invalid_evaluation_arrays_fail_closed(kind):
    truth=np.zeros((2,17));logits=np.zeros((2,17))
    if kind=='nan':logits[0,0]=np.nan
    elif kind=='wrong_shape':logits=logits[:,:16]
    elif kind=='non_binary':truth[0,0]=.5
    else:truth=truth[:0];logits=logits[:0]
    with pytest.raises(ValueError):select_thresholds(logits,truth,split='validation')
