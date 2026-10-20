import pytest
from tests.flywheel_confidence_fakes import rule,payload


def test_keyword_signal_checks_model_anchor_in_actual_text():
    from app.quality.reference_confidence import clause_features
    present=clause_features('XM-A17可以雨中充电吗？',[{'question':'XM-A17充电条件','answer':'机身和接口必须干燥。'}])
    absent=clause_features('XM-A18可以雨中充电吗？',[{'question':'XM-A17充电条件','answer':'机身和接口必须干燥。'}])
    assert present['anchors_complete'] is True
    assert absent['anchors_complete'] is False and absent['clause_signal']==0


def test_reference_gate_cannot_allow_high_score_for_wrong_model():
    from app.quality.reference_confidence import reference_rule
    from app.quality.evidence_confidence import evaluate_evidence
    selected=reference_rule(rule(),threshold=.5,score_floor=.4)
    data=payload((.99,.9))
    for row in data['matches']: row.update(question='XM-A17充电条件',answer='必须保持干燥。')
    result=evaluate_evidence(data,selected,question='XM-A18可以雨中充电吗？',top_k=2,
        budget_fingerprint=selected.source.budget_fingerprint)
    assert not result.useful and result.features['anchors_complete'] is False


def test_reference_calibration_prioritizes_no_false_allow_and_never_fits_heldout():
    from app.quality.reference_confidence import fit_reference_rule
    from tests.flywheel_confidence_fakes import samples_and_split
    samples,split=samples_and_split()
    texts={sample.eval_id:{'question':'配送政策', 'matches':[
        {'question':'配送政策','answer':'普通地区配送。'} for _ in sample.rankings]} for sample in samples}
    report=fit_reference_rule(samples,split,texts)
    assert report['calibration']['false_allow']==0
    changed=[sample.model_copy(update={'sufficient':not sample.sufficient})
        if sample.eval_id in split.held_out_ids else sample for sample in samples]
    assert fit_reference_rule(changed,split,texts)['rule']==report['rule']
    assert len(report['threshold_scan'])>=2
    assert report['held_out']['n']==len(split.held_out_ids)
    assert report['signal_weights']=={'top1':.5,'count':.2,'gap':.2,'clause':.1}


def test_snapshot_report_preserves_unknown_and_zero_denominators():
    from app.quality.confidence_report import distribution,rate_summary
    assert distribution([])=={'n':0,'min':None,'p25':None,'median':None,'p75':None,'max':None}
    assert distribution([.1,.3,.5])['median']==.3
    assert rate_summary({'n':0,'true_negative':0,'false_positive':0,'true_positive':0,'false_negative':0})=={
        'answerable_n':0,'unanswerable_n':0,'answerable_pass_rate':None,'false_allow_rate':None}


def test_order_number_is_not_required_in_general_policy_evidence():
    from app.quality.reference_confidence import clause_features
    result=clause_features('订单1001满99元包邮吗？',[{'question':'运费政策','answer':'满99元包邮。'}])
    assert result['anchors_complete'] is True


def test_loading_four_signal_rule_keeps_version_and_old_rule_still_works():
    from app.quality.reference_confidence import reference_rule
    from app.quality.evidence_confidence import parse_rule,verify_rule,evaluate_evidence
    old=rule(); new=reference_rule(old,threshold=.5,score_floor=.4)
    for selected in (old,new):
        loaded=parse_rule(selected.model_dump_json())
        verify_rule(loaded,top_k=2,budget_fingerprint=loaded.source.budget_fingerprint)
        assert loaded.rule_version==selected.rule_version
    assert evaluate_evidence(payload(),old,top_k=2,budget_fingerprint=old.source.budget_fingerprint).useful
