from pathlib import Path
from collections import Counter
import pytest
from tests.test_rag_metrics import record


def test_no_claims_is_not_perfect_faithfulness():
    from app.eval_pipeline.runner import aggregate_metrics
    metrics = aggregate_metrics([record(strategy='hybrid_rerank', claim_verdicts=[])])
    assert metrics['faithfulness'] == {'value': None, 'valid_n': 0, 'excluded': {'zero_claims': 1}}


def test_pipeline_metrics_reuse_ch04_group_recall_and_mrr():
    from app.eval_pipeline.runner import aggregate_metrics
    from app.rag_evaluation.report import case_metrics
    row = record(strategy='hybrid_rerank', candidate_ids=[9,1,2,4], final_ids=[9, 1, 4],
        prompt_citations=[{'n': 1, 'chunk_id': '1', 'section_path': None, 'question': '退货', 'answer': '7天'}])
    expected = case_metrics(row)
    actual = aggregate_metrics([row])
    assert actual['recall_at_10']['value'] == expected['recall_at_10'] == .5
    assert actual['mrr_at_10']['value'] == expected['mrr_at_10'] == .5


def test_error_and_unattempted_are_excluded_not_scored_zero():
    from app.eval_pipeline.runner import aggregate_metrics
    row = record(strategy='hybrid_rerank', status='judge_error', stage='judgment',
        point_verdicts=None, claim_verdicts=None, error={'code':'judge_error','type':'JudgeError','message':'failed'})
    metrics = aggregate_metrics([row])
    assert metrics['faithfulness']['value'] is None and metrics['faithfulness']['valid_n'] == 0
    assert metrics['recall_at_10']['valid_n'] == 1


def test_smoke_scope_is_twenty_fixed_heldout_questions():
    from app.rag_evaluation.dataset import load_dataset, DATASET_ID
    from app.quality.calibration import build_calibration_split
    from app.eval_pipeline.runner import select_case_ids
    dataset = load_dataset(DATASET_ID, root=Path('evals/datasets'))
    selected = select_case_ids(dataset, 'smoke_20')
    assert selected == select_case_ids(dataset, 'smoke_20') and len(selected) == 20
    assert set(selected) <= set(build_calibration_split(dataset).held_out_ids)
    by_id = {case.eval_id: case for case in dataset.cases}
    assert set(Counter(by_id[key].bucket for key in selected).values()) == {4}
    assert len(select_case_ids(dataset, 'full_300')) == 300
    with pytest.raises(ValueError): select_case_ids(dataset, 'unknown')
