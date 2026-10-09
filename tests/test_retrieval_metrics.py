import importlib
import pytest


def api():
    """加载被测评估接口，缺实现时给出明确的行为失败。"""
    try:
        return importlib.import_module('evals.retrieval_metrics')
    except ImportError:
        pytest.fail('retrieval metrics are missing')


def test_metrics_distinguish_partial_recall_and_rank():
    """验证多相关块只命中部分时Recall和首命中排名倒数不同。"""
    assert api().retrieval_metrics([20, 10], {10, 30}, k=10) == {'recall': .5, 'mrr': .5}


def test_empty_gold_is_not_perfect_and_duplicates_do_not_consume_rank():
    """验证空金标不作满分、重复主键不占排名及未命中为零。"""
    assert api().retrieval_metrics([20], set(), k=10) == {'recall': None, 'mrr': None}
    assert api().retrieval_metrics([20, 20, 10], {10}, k=2) == {'recall': 1., 'mrr': .5}
    assert api().retrieval_metrics([20], {10}, k=10) == {'recall': 0., 'mrr': 0.}


def test_top_fifty_is_not_top_ten():
    """验证候选召回五十与最终十条证据的指标阶段分离。"""
    ranked = list(range(1, 51))
    assert api().retrieval_metrics(ranked, {40}, k=10)['recall'] == 0
    assert api().retrieval_metrics(ranked, {40}, k=50)['recall'] == 1


def test_threshold_refusal_f1_tie_uses_higher_observed_threshold():
    """验证拒答正类混淆矩阵和同分优先更高观察门槛。"""
    result = api().choose_threshold([{'score': .2, 'sufficient': False}, {'score': .3, 'sufficient': False},
                                    {'score': .6, 'sufficient': True}, {'score': .9, 'sufficient': True}])
    assert result['threshold'] == .6
    assert result['refusal_f1'] == 1.
    assert result['confusion'] == {'tp': 2, 'fp': 0, 'fn': 0, 'tn': 2}


@pytest.mark.parametrize('samples', [[], [{'score': float('nan'), 'sufficient': True}],
                                    [{'score': .2, 'sufficient': 'false'}]])
def test_invalid_threshold_samples_fail(samples):
    """验证非法分数或非布尔标签不能产生校准建议。"""
    with pytest.raises(ValueError):
        api().choose_threshold(samples)
