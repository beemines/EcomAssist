"""按完整证据组计算新口径；不修改旧物理块召回指标。"""

from collections.abc import Sequence

from app.rag_evaluation.contracts import MappedGroup

RETRIEVAL_METRICS = (
    "recall_at_5", "recall_at_10", "mrr_at_10", "all_groups_hit_at_5",
    "all_groups_hit_at_10", "candidate_group_coverage", "prompt_group_coverage",
)


def unique_ids(ids: Sequence[int]) -> list[int]:
    """保留首次出现的排名，拒绝布尔值和非正 INT64 主键。"""
    if isinstance(ids, (str, bytes)) or not isinstance(ids, Sequence):
        raise ValueError("主键须为序列")
    if any(type(value) is not int or not 1 <= value <= 9223372036854775807 for value in ids):
        raise ValueError("主键须为正 INT64")
    return list(dict.fromkeys(ids))


def validate_groups(groups: tuple[MappedGroup, ...]) -> None:
    """校验 AND/OR 组合非空且组号唯一，不允许空组合虚构完整命中。"""
    if not isinstance(groups, tuple) or any(not isinstance(group, MappedGroup) for group in groups):
        raise ValueError("证据组须为 MappedGroup 元组")
    seen = set()
    for group in groups:
        if not isinstance(group.group_id, str) or not group.group_id.strip() or group.group_id in seen:
            raise ValueError("证据组号为空或重复")
        seen.add(group.group_id)
        if not isinstance(group.alternatives, tuple) or not group.alternatives:
            raise ValueError("证据替代组合为空")
        for bundle in group.alternatives:
            if not isinstance(bundle, tuple) or not bundle or len(unique_ids(bundle)) != len(bundle):
                raise ValueError("证据组合为空或重复")


def _coverage(ids: Sequence[int], groups: tuple[MappedGroup, ...]) -> float:
    """任一完整替代组合满足即覆盖该组，各组等权。"""
    selected = set(ids)
    return sum(any(set(bundle) <= selected for bundle in group.alternatives) for group in groups) / len(groups)


def retrieval_metrics(
    ranked_ids: Sequence[int], candidate_ids: Sequence[int], prompt_ids: Sequence[int],
    groups: tuple[MappedGroup, ...],
) -> dict[str, float | None]:
    """先去重后截断：最终5/10、候选50、完整提示集；空金标全部 N/A。

    recall 为完整组比例，all_groups_hit 为所有组齐全的0/1；MRR10
    只要求命中任意相关块，不能用它代替全组命中。
    """
    ranked, candidates, prompts = unique_ids(ranked_ids), unique_ids(candidate_ids), unique_ids(prompt_ids)
    validate_groups(groups)
    if not groups:
        return dict.fromkeys(RETRIEVAL_METRICS)
    at5, at10 = _coverage(ranked[:5], groups), _coverage(ranked[:10], groups)
    relevant = {identifier for group in groups for bundle in group.alternatives for identifier in bundle}
    mrr = next((1 / rank for rank, identifier in enumerate(ranked[:10], 1) if identifier in relevant), 0.)
    return dict(recall_at_5=at5, recall_at_10=at10, mrr_at_10=mrr,
                all_groups_hit_at_5=float(at5 == 1), all_groups_hit_at_10=float(at10 == 1),
                candidate_group_coverage=_coverage(candidates[:50], groups),
                prompt_group_coverage=_coverage(prompts, groups))
