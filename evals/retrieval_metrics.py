# 指标遵循物理 chunk ID；空金标不进入正例检索分母。
import math


def retrieval_metrics(ranked_ids: list[int], gold_ids: set[int], *, k: int) -> dict:
    """按去重后的物理主键排名计算Recall与MRR；空金标返回不适用。"""
    if type(k) is not int or k < 1:
        raise ValueError('k must be positive')
    ranked = list(dict.fromkeys(ranked_ids))[:k]
    if not gold_ids:
        return {'recall': None, 'mrr': None}
    return {'recall': len(set(ranked) & gold_ids) / len(gold_ids),
            'mrr': next((1 / rank for rank, identifier in enumerate(ranked, 1) if identifier in gold_ids), 0.)}


# 拒答为正类；门槛等值放行，候选只来自独立校准实际有限分数。
def choose_threshold(samples: list[dict]) -> dict:
    """枚举实际观察分数，用拒答F1选门槛，同分选择较高值。"""
    if not samples or any(type(s.get('score')) not in (int, float) or not math.isfinite(s['score'])
                          or type(s.get('sufficient')) is not bool for s in samples):
        raise ValueError('finite scores and boolean sufficiency labels are required')
    results = []
    for threshold in sorted({s['score'] for s in samples}):
        confusion = dict(tp=0, fp=0, fn=0, tn=0)
        for sample in samples:
            refused, expected = sample['score'] < threshold, not sample['sufficient']
            confusion['tp' if refused and expected else 'fp' if refused else 'fn' if expected else 'tn'] += 1
        denominator = 2 * confusion['tp'] + confusion['fp'] + confusion['fn']
        results.append(dict(threshold=threshold, refusal_f1=2 * confusion['tp'] / denominator if denominator else 0.,
                            confusion=confusion))
    best = max(results, key=lambda r: (r['refusal_f1'], r['threshold']))
    return {**best, 'samples': len(samples), 'candidates': results,
            'method': 'observed scores; refusal positive; score < threshold; ties choose higher threshold'}
