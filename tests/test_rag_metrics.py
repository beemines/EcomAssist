"""组指标和公开 DTO 的行为测试；期望值由证据组合手工推导。"""

import hashlib
import importlib
import json
from pathlib import Path

import pytest

from app.rag_evaluation.contracts import MappedGroup

ROOT = Path(__file__).resolve().parents[1]
STRATEGIES = ("dense", "bm25", "hybrid", "hybrid_rerank")


def api(name):
    """缺失模块产生明确的功能断言，使 RED 指向尚未实现的行为。"""
    assert importlib.util.find_spec(f"app.rag_evaluation.{name}"), f"尚未实现 {name}"
    return importlib.import_module(f"app.rag_evaluation.{name}")


def record(eval_id="E2", strategy="dense", **changes):
    """创建完整合法题目记录，阶段失败通过显式空字段表达。"""
    value = dict(
        eval_id=eval_id, strategy=strategy, bucket="E_multi", difficulty="multi",
        category=None, should_refuse=False, refused=False, status="completed", stage="complete",
        query="退货和运费规则", query_plan={"standard": "退货和运费规则", "expansions": []},
        mapped_groups=[{"group_id": "g1", "alternatives": [[1, 2], [3]]},
                       {"group_id": "g2", "alternatives": [[4]]}],
        candidate_ids=[1, 2, 4], final_ids=[1, 2, 4],
        prompt_citations=[{"n": 1, "chunk_id": "1", "section_path": None,
                           "question": "退货", "answer": "7天"},
                          {"n": 2, "chunk_id": "4", "section_path": None,
                           "question": "运费", "answer": "买家承担"}],
        decision={"useful": True, "reason": "证据充分", "response_kind": "knowledge", "source": "self_check"},
        answer="7天内退货，买家承担运费", point_verdicts=[{"point_id": "p1", "covered": True, "reason": "已覆盖"},
                                                    {"point_id": "p2", "covered": False, "reason": "遗漏"}],
        claim_verdicts=[{"claim": "7天", "supported": True, "reason": "证据1"}],
        metrics=None, error=None, elapsed_ms=10,
        judge_snapshot={"raw_response": "PRIVATE-JUDGE", "finish_reason": "stop", "prompt_version": "v2"},
    )
    value.update(changes)
    return value


def test_duplicate_rank_and_multi_chunk_group_metrics():
    """取消去重或把 AND 组合打平将破坏首命中、最终和提示覆盖的区别。"""
    groups = (MappedGroup("g1", ((1, 2), (3,))), MappedGroup("g2", ((4,),)))
    result = api("metrics").retrieval_metrics([1, 1, 4, 2], [1, 4], [1, 4], groups)
    assert result == dict(recall_at_5=1., recall_at_10=1., mrr_at_10=1.,
                          all_groups_hit_at_5=1., all_groups_hit_at_10=1., candidate_group_coverage=.5, prompt_group_coverage=.5)


def test_first_hit_not_all_groups():
    """只命中首组不可冒充所有证据齐全，候选第十一位仍可补齐候选覆盖。"""
    groups = (MappedGroup("g1", ((1,),)), MappedGroup("g2", ((2,),)))
    result = api("metrics").retrieval_metrics([99, 1] + list(range(10, 19)) + [2], [1, 2], [1], groups)
    assert result["mrr_at_10"] == .5
    assert result["recall_at_10"] == .5
    assert result["all_groups_hit_at_10"] == 0.
    assert result["candidate_group_coverage"] == 1.
    assert all(value is None for value in api("metrics").retrieval_metrics([], [], [], ()).values())


def test_metric_valid_n_and_common_subset():
    """裁判失败保留检索分数；零断言只排除忠实度，不排除共同有效生成集合。"""
    rows = [record(strategy=s, claim_verdicts=[]) for s in STRATEGIES]
    rows += [record("E19", s) for s in STRATEGIES[:-1]]
    rows += [record("E19", "hybrid_rerank", status="judge_error", stage="judgment",
                    point_verdicts=None, claim_verdicts=None,
                    error={"code": "judge_failed", "type": "TimeoutError", "message": "PRIVATE-EXCEPTION"})]
    result = api("report").summarize_records(rows)
    assert result["common_generation"]["eval_ids"] == ["E2"]
    assert result["common_generation"]["valid_n"] == 1
    row = next(row for row in result["rows"] if row["strategy"] == "hybrid_rerank" and row["bucket"] == "overall")
    assert row["metrics"]["recall_at_10"] == {"value": 1., "valid_n": 2, "excluded": {}}
    assert row["metrics"]["answer_point_coverage"]["valid_n"] == 1
    assert row["metrics"]["faithfulness"] == {"value": None, "valid_n": 0, "excluded": {"zero_claims": 1, "judge_error": 1}}
    assert row["status_counts"]["judge_error"] == 1
    assert row["completed"] == 1 and row["errors"] == 1
    common = next(row for row in result["common_generation"]["rows"] if row["strategy"] == "dense" and row["bucket"] == "overall")
    assert common["metrics"]["faithfulness"]["valid_n"] == 0


def test_refusal_and_macro_average_have_distinct_denominators():
    """正例拒答覆盖为零、库外检索为 N/A，逐题宏平均不按断言数量加权。"""
    mod = api("report")
    rows = [record(refused=True), record("E19", point_verdicts=[{"point_id": "p1", "covered": True, "reason": "命中"}],
                   claim_verdicts=[{"claim": str(i), "supported": False, "reason": "无支持"} for i in range(3)]),
            record("D1", bucket="D_unanswerable", difficulty="absent", should_refuse=True,
                   refused=True, mapped_groups=[], point_verdicts=[], claim_verdicts=[])]
    summary = mod.summarize_records(rows)
    row = next(row for row in summary["rows"] if row["strategy"] == "dense" and row["bucket"] == "overall")
    assert row["metrics"]["answer_point_coverage"] == {"value": .5, "valid_n": 2, "excluded": {"expected_refusal": 1}}
    assert row["metrics"]["faithfulness"]["value"] == .5
    assert row["metrics"]["recall_at_10"]["excluded"] == {"expected_refusal": 1}
    assert row["metrics"]["absent_refusal_rate"]["value"] == 1.
    assert row["metrics"]["answerable_false_refusal_rate"]["value"] == .5


def test_public_projection_uses_nested_whitelist_and_safe_errors():
    """扩展字段、裁判原文、任意异常消息都不得进入浏览器可见 DTO。"""
    mod = api("report")
    value = record(status="judge_error", stage="judgment", point_verdicts=None, claim_verdicts=None,
                   error={"code": "judge_failed", "type": "TimeoutError", "message": "SECRET-EXCEPTION", "body": "SECRET-BODY"})
    value["generation_input"] = "SECRET-GENERATION"
    value["query_plan"]["model_requests"] = "SECRET-REQUEST"
    output = mod.public_report({"schema_version": 2, "records": [value], "model_requests": "SECRET-TOP"})
    encoded = json.dumps(output)
    assert "SECRET" not in encoded and "PRIVATE-JUDGE" not in encoded
    assert output["records"][0]["judge_snapshot"] == {"finish_reason": "stop", "prompt_version": "v2"}
    assert output["records"][0]["error"] == {"code": "judge_failed", "type": "TimeoutError", "message": "该阶段执行失败"}
    assert value["judge_snapshot"]["raw_response"] == "PRIVATE-JUDGE"


@pytest.mark.parametrize("changes", [
    {"refused": None}, {"should_refuse": "false"}, {"final_ids": [True]},
    {"point_verdicts": [{"point_id": "p1", "covered": "true", "reason": "错类型"}]},
    {"elapsed_ms": float("nan")}, {"mapped_groups": [{"group_id": "g", "alternatives": [[]]}]},
    {"prompt_citations": [{"n": 1, "chunk_id": "999", "section_path": None, "question": "问", "answer": "答"}]},
])
def test_case_record_rejects_invalid_public_data(changes):
    """缺字段、伪布尔和无出处提示证据必须在公共与本地记录边界被拒绝。"""
    with pytest.raises(ValueError):
        api("report").validate_case_record(record(**changes))


def test_not_attempted_stages_are_na_and_duplicate_routes_are_rejected():
    """未执行不可填零分，重复策略记录不可悄悄覆盖共同题号。"""
    mod = api("report")
    row = record(status="not_attempted", stage="rewrite", refused=None, query_plan=None,
                 candidate_ids=None, final_ids=None, prompt_citations=None, decision=None,
                 answer=None, point_verdicts=None, claim_verdicts=None, judge_snapshot=None, elapsed_ms=None)
    summary = mod.summarize_records([row])
    dense = next(r for r in summary["rows"] if r["strategy"] == "dense" and r["bucket"] == "overall")
    assert dense["not_attempted"] == 1 and dense["attempted"] == 0
    assert dense["metrics"]["recall_at_5"] == {"value": None, "valid_n": 0, "excluded": {"not_attempted": 1}}
    with pytest.raises(ValueError):
        mod.summarize_records([record(), record()])


@pytest.mark.parametrize("changes", [
    {"bucket": "overall"},
    {"candidate_ids": list(range(1, 52))},
    {"candidate_ids": list(range(1, 12)), "final_ids": list(range(1, 12))},
    {"judge_snapshot": {"prompt_version": "v2", "finish_reason": "length", "raw_response": "截断"}},
    {"metrics": {"answer_point_coverage": 1.}},
])
def test_record_rejects_oversized_routes_truncated_judgment_and_stale_scores(changes):
    """越界路数、截断裁判和虚增旧分数不得成为合法完成记录。"""
    with pytest.raises(ValueError):
        api("report").validate_case_record(record(**changes))


def test_absent_judgment_cannot_invent_positive_answer_points():
    """空金标库外题若凭裁判注入正例要点，必须拒绝这份联合判定。"""
    with pytest.raises(ValueError):
        api("report").validate_case_record(record("D1", bucket="D_unanswerable", should_refuse=True,
                                                   mapped_groups=[], refused=True))


def test_candidate_50_and_final_5_have_separate_limits():
    """候选第51块和最终第6块分别越过各自截断边界，不能提升相应分数。"""
    groups = (MappedGroup("g1", ((1,),)), MappedGroup("g2", ((2,),)))
    result = api("metrics").retrieval_metrics([1, 10, 11, 12, 13, 2], [1] + list(range(100, 149)) + [2], [1, 2], groups)
    assert result["all_groups_hit_at_5"] == 0.
    assert result["all_groups_hit_at_10"] == 1.
    assert result["candidate_group_coverage"] == .5


def test_v1_missing_metrics_are_na_and_source_unchanged():
    """读取适配器不能写旧报告或以零补齐新指标，也不能公开旧请求体。"""
    path = ROOT / "docs/validation/hybrid-retrieval-comparison.json"
    before = path.read_bytes()
    assert hashlib.sha256(before).hexdigest() == "63aa7041d7e05cb6865d44318b0191498ed5c3a5d459221d5c3408ae8d1babb3"
    original = json.loads(before)
    result = api("report").adapt_legacy(original)
    assert result["schema_version"] == 1
    assert result["counts"] == {"total": 120, "completed": 101, "errors": 19, "not_attempted": 0}
    assert result["summary"] == original["summary"]
    assert all(row["metrics"]["recall_at_5"] is None and row["metrics"]["answer_point_coverage"] is None for row in result["records"])
    assert "model_requests" not in json.dumps(result) and "generation_input" not in json.dumps(result)
    assert path.read_bytes() == before


@pytest.mark.parametrize("eval_id,expected", [("E2", 1 / 3), ("E19", .5)])
def test_audited_e2_e19_evidence_subset(eval_id, expected):
    """真实多证据题仅给首组时全组命中为零，防止以合成小例掩盖审标错误。"""
    from app.rag_evaluation.dataset import load_dataset, map_groups
    data = load_dataset("merchant-rag-300-v1", root=ROOT / "evals/datasets")
    case = next(case for case in data.cases if case.eval_id == eval_id)
    groups = map_groups(case, {chunk.chunk_key: i for i, chunk in enumerate(data.chunks, 1)})
    first = groups[0].alternatives[0]
    result = api("metrics").retrieval_metrics(first, first, first, groups)
    assert result["mrr_at_10"] == 1.
    assert result["prompt_group_coverage"] == pytest.approx(expected)
    assert result["all_groups_hit_at_10"] == 0.
    row = record(eval_id, query=case.query, bucket=case.bucket, difficulty=case.difficulty,
                 category=case.category, mapped_groups=[{"group_id": group.group_id,
                     "alternatives": [list(bundle) for bundle in group.alternatives]} for group in groups],
                 candidate_ids=list(first), final_ids=list(first),
                 prompt_citations=[{"n": index, "chunk_id": str(identifier), "section_path": None,
                                   "question": case.query, "answer": case.points[0].text}
                                  for index, identifier in enumerate(first, 1)],
                 answer=case.points[0].text,
                 point_verdicts=[{"point_id": point.point_id, "covered": index == 0,
                                  "reason": "只提供首组的完整来源"} for index, point in enumerate(case.points)],
                 claim_verdicts=[{"claim": case.points[0].text, "supported": True, "reason": "首组证据直接支持"}])
    generated = api("report").case_metrics(row)
    assert generated["answer_point_coverage"] == pytest.approx(expected)
    assert generated["faithfulness"] == 1.
