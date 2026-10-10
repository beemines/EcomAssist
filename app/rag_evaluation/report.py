"""CaseRecord 校验、逐题宏平均与白名单公开报告；所有函数均无文件写入。

本地 CaseRecord 固定字段见 CASE_FIELDS，全部必填；未完成产物为 null。
query_plan={standard:str, expansions:list[str]}；mapped_groups 为
[{group_id:str, alternatives:list[list[positive_int64]]}]；prompt_citations
为 [{n:positive_int, chunk_id:decimal_str, section_path:str|null,
question:str, answer:str}]，ID 必须来自 final_ids。decision 沿用
{useful:bool,reason:str,response_kind:knowledge|social|clarification,
source:self_check|retrieval_low_conf|null}。两种 verdict 沿用共享契约的 JSON。
judge_snapshot={prompt_version:str,finish_reason:str,raw_response:str(可省)}；
raw_response 仅本地保存。error={code:安全标识,type:安全标识,message:str}，
投影永远以固定安全消息覆盖任意 exception 文本。metrics 为 null 或已知名的
0..1有限数/null，但汇总和公开分数始终从阶段产物重算，不能相信旧分数。

ReportV2 输入={schema_version:2,records:list[CaseRecord],可选run_id/dataset_id/
fingerprint/scope}；输出同名白名单及重算 summary。summary={rows:list[Row],
common_generation:{eval_ids:list[str],valid_n:int,rows:list[Row]}}。
Row={bucket,strategy,total,attempted,completed,errors,not_attempted,status_counts,
metrics:{metric:{value:float|null,valid_n:int,excluded:{reason:int}}}}。
生成共同集合要求四路 completed 且联合裁判合法；零断言只让 faithfulness N/A。
合法完成裁判 finish_reason 必须为 stop；库外题没有正例要点。bucket 只接受
五个登记桶（D_absent 与内部 D_unanswerable 均可），候选/最终最多50/10个
去重主键。非null的 metrics 可为已知指标子集，但每个值须与阶段产物一致。
candidate_group_coverage 截断50；召回和命中截断5/10；prompt_group_coverage
只统计实际送入生成的完整证据。answer_point_coverage 为逐题要点比例（正例
拒答为0），faithfulness 为逐题支持断言比例（零断言 N/A）。拒答两率仅使用
completed/judge_error 的合法最终 answer 与严格 bool refused，裁判失败仍留痕。
"""

from collections import Counter
from collections.abc import Mapping, Sequence
import copy
import math
import re

from app.rag_evaluation.contracts import MappedGroup
from app.rag_evaluation.metrics import RETRIEVAL_METRICS, retrieval_metrics, unique_ids, validate_groups

STRATEGIES = ("dense", "bm25", "hybrid", "hybrid_rerank")
BUCKETS = ("A_policy", "B_model", "C_colloquial", "E_multi", "D_unanswerable", "D_absent")
STATUSES = ("completed", "rewrite_error", "retrieval_error", "self_check_error", "answer_error",
            "judge_error", "cancelled", "not_attempted")
STAGES = ("rewrite", "retrieval", "self_check", "answer", "judgment", "complete")
METRIC_NAMES = RETRIEVAL_METRICS + ("answer_point_coverage", "faithfulness", "absent_refusal_rate",
                                     "answerable_false_refusal_rate")
CASE_FIELDS = (
    "eval_id", "strategy", "bucket", "difficulty", "category", "should_refuse", "refused", "status",
    "stage", "query", "query_plan", "mapped_groups", "candidate_ids", "final_ids", "prompt_citations",
    "decision", "answer", "point_verdicts", "claim_verdicts", "metrics", "error", "elapsed_ms", "judge_snapshot",
)


def _require(condition: bool, message: str) -> None:
    """字段契约失败时只报告字段级原因，不拼接任何私有值。"""
    if not condition:
        raise ValueError(message)


def _text(value: object, *, blank: bool = False) -> bool:
    """严格区分字符串和任意可转字符串对象，按字段决定是否允许空内容。"""
    return isinstance(value, str) and (blank or bool(value.strip()))


def _object(value: object, fields: tuple[str, ...]) -> dict:
    """复制嵌套白名单必填字段，额外请求体和模型元数据不会被透传。"""
    _require(isinstance(value, Mapping) and all(field in value for field in fields), "对象缺少必填字段")
    return {field: copy.deepcopy(value[field]) for field in fields}


def _mapped_groups(value: object) -> tuple[MappedGroup, ...]:
    """JSON 映射为共享不可变组并复用 AND/OR 校验，供存储与汇总共同使用。"""
    _require(isinstance(value, list), "mapped_groups 须为列表")
    result = []
    for item in value:
        group = _object(item, ("group_id", "alternatives"))
        _require(isinstance(group["alternatives"], list), "alternatives 须为列表")
        _require(all(isinstance(bundle, list) for bundle in group["alternatives"]), "证据组合须为列表")
        result.append(MappedGroup(group["group_id"], tuple(tuple(bundle) for bundle in group["alternatives"])))
    groups = tuple(result)
    validate_groups(groups)
    return groups


def _verdicts(value: object, kind: str) -> list[dict] | None:
    """只接收共享裁判契约的严格布尔 JSON，缺阶段用 null 而非空列表。"""
    if value is None:
        return None
    _require(isinstance(value, list), "verdicts 须为列表或null")
    name, flag = ("point_id", "covered") if kind == "point" else ("claim", "supported")
    result = [_object(item, (name, flag, "reason")) for item in value]
    for item in result:
        _require(_text(item[name]) and type(item[flag]) is bool and _text(item["reason"]), "verdict 字段非法")
    if kind == "point":
        _require(len({item[name] for item in result}) == len(result), "要点号重复")
    return result


def safe_error(value: object) -> dict[str, str] | None:
    """仅公开安全 code/type 和固定中文消息，不公开 SDK 原始异常文本。"""
    if value is None:
        return None
    error = _object(value, ("code", "type", "message"))
    _require(_text(error["message"], blank=True), "error.message 须为文本")
    for field in ("code", "type"):
        _require(isinstance(error[field], str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{0,63}", error[field]) is not None,
                 "error 标识非法")
    return {"code": error["code"], "type": error["type"], "message": "该阶段执行失败"}


def validate_case_record(record: Mapping[str, object]) -> dict[str, object]:
    """返回独立本地白名单副本；严格验证阶段产物、元数据和裁判，不修改输入。"""
    row = _object(record, CASE_FIELDS)
    for key in ("eval_id", "bucket", "difficulty", "query"):
        _require(_text(row[key]), f"{key} 须为非空文本")
    _require(row["bucket"] in BUCKETS, "bucket 未登记")
    _require(row["strategy"] in STRATEGIES and row["status"] in STATUSES and row["stage"] in STAGES, "策略或阶段非法")
    _require(row["category"] is None or _text(row["category"]), "category 非法")
    _require(type(row["should_refuse"]) is bool and (row["refused"] is None or type(row["refused"]) is bool), "拒答标签须为布尔")
    groups = _mapped_groups(row["mapped_groups"])
    _require(bool(groups) != row["should_refuse"], "可答题须有证据组，库外题不得有证据组")
    row["mapped_groups"] = [{"group_id": group.group_id, "alternatives": [list(bundle) for bundle in group.alternatives]} for group in groups]
    if row["query_plan"] is not None:
        plan = _object(row["query_plan"], ("standard", "expansions"))
        _require(_text(plan["standard"]) and len(plan["standard"]) <= 512, "standard 非法")
        _require(isinstance(plan["expansions"], list) and len(plan["expansions"]) <= 4 and
                 all(_text(item) and len(item) <= 64 for item in plan["expansions"]), "expansions 非法")
        row["query_plan"] = plan
    for key in ("candidate_ids", "final_ids"):
        if row[key] is not None:
            _require(isinstance(row[key], list), f"{key} 须为列表或null")
            _require(len(unique_ids(row[key])) <= (50 if key == "candidate_ids" else 10), "检索结果超过固定上限")
    if row["final_ids"] is not None:
        _require(row["candidate_ids"] is not None and set(row["final_ids"]) <= set(row["candidate_ids"]), "最终证据不在候选集合")
    if row["prompt_citations"] is not None:
        _require(isinstance(row["prompt_citations"], list) and row["final_ids"] is not None, "提示证据缺少检索来源")
        citations = [_object(item, ("n", "chunk_id", "section_path", "question", "answer")) for item in row["prompt_citations"]]
        seen_n, seen_id = set(), set()
        for item in citations:
            _require(type(item["n"]) is int and item["n"] > 0 and item["n"] not in seen_n, "引用编号非法或重复")
            identifier = item["chunk_id"]
            _require(isinstance(identifier, str) and re.fullmatch(r"[1-9][0-9]*", identifier) is not None,
                     "引用主键须为十进制文本")
            _require(int(identifier) in row["final_ids"] and identifier not in seen_id, "提示证据不在最终集合或重复")
            _require(item["section_path"] is None or _text(item["section_path"]), "section_path 非法")
            _require(_text(item["question"], blank=True) and _text(item["answer"]), "引用正文非法")
            seen_n.add(item["n"])
            seen_id.add(identifier)
        row["prompt_citations"] = citations
    if row["decision"] is not None:
        decision = _object(row["decision"], ("useful", "reason", "response_kind", "source"))
        _require(type(decision["useful"]) is bool and _text(decision["reason"]) and
                 decision["response_kind"] in ("knowledge", "social", "clarification") and
                 decision["source"] in (None, "self_check", "retrieval_low_conf"), "decision 非法")
        row["decision"] = decision
    _require(row["answer"] is None or _text(row["answer"]), "answer 须为非空文本或null")
    row["point_verdicts"] = _verdicts(row["point_verdicts"], "point")
    row["claim_verdicts"] = _verdicts(row["claim_verdicts"], "claim")
    if row["judge_snapshot"] is not None:
        snapshot = _object(row["judge_snapshot"], ("prompt_version", "finish_reason"))
        _require(all(_text(value) for value in snapshot.values()), "裁判快照元数据非法")
        if "raw_response" in row["judge_snapshot"]:
            raw = row["judge_snapshot"]["raw_response"]
            _require(_text(raw, blank=True), "裁判原文须为文本")
            snapshot["raw_response"] = raw
        row["judge_snapshot"] = snapshot
    row["error"] = safe_error(row["error"])
    elapsed = row["elapsed_ms"]
    _require(elapsed is None or (type(elapsed) in (int, float) and math.isfinite(elapsed) and elapsed >= 0), "elapsed_ms 非法")
    if row["metrics"] is not None:
        _require(isinstance(row["metrics"], Mapping) and set(row["metrics"]) <= set(METRIC_NAMES), "metrics 字段非法")
        _require(all(value is None or (type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1)
                     for value in row["metrics"].values()), "metrics 值非法")
    _validate_stages(row)
    if row["metrics"] is not None:
        expected, _ = _score(row)
        _require(all(value == expected[name] for name, value in row["metrics"].items()), "metrics 与阶段产物不一致")
    return row


def _validate_stages(row: dict) -> None:
    """每阶段只有成功产物可留存；失败后的阶段不得伪造完成数据。"""
    status, stage = row["status"], row["stage"]
    failure_stage = {"rewrite_error": "rewrite", "retrieval_error": "retrieval", "self_check_error": "self_check",
                     "answer_error": "answer", "judge_error": "judgment", "not_attempted": "rewrite", "completed": "complete"}
    _require(status == "cancelled" or stage == failure_stage[status], "status/stage 不一致")
    products = (("query_plan",), ("candidate_ids", "final_ids", "prompt_citations"), ("decision",),
                ("answer", "refused"), ("point_verdicts", "claim_verdicts", "judge_snapshot"))
    limit = STAGES.index(stage)
    for index, fields in enumerate(products):
        if index < limit:
            _require(all(row[field] is not None for field in fields), "完成阶段缺少产物")
        elif index > limit or status != "completed":
            # 失败裁判允许保留本地原文快照，判定结果必须为空。
            for field in fields:
                if field == "judge_snapshot" and index == limit:
                    continue
                _require(row[field] is None, "未完成阶段含成功产物")
    if status == "completed":
        _require(row["error"] is None and bool(row["point_verdicts"]) != row["should_refuse"], "完成题目缺少联合裁判或要点越界")
        _require(row["judge_snapshot"]["finish_reason"] == "stop", "完成裁判遭截断")
    elif status.endswith("_error"):
        _require(row["error"] is not None, "失败阶段缺少错误")


def _score(row: dict) -> tuple[dict[str, float | None], dict[str, str]]:
    """从合法产物逐题计分，并给每个 N/A 一个具体排除原因。"""
    scores, reasons = dict.fromkeys(METRIC_NAMES), {}
    status = row["status"]
    groups = _mapped_groups(row["mapped_groups"])
    if row["final_ids"] is not None:
        prompts = [int(item["chunk_id"]) for item in row["prompt_citations"]]
        scores.update(retrieval_metrics(row["final_ids"], row["candidate_ids"], prompts, groups))
    for name in RETRIEVAL_METRICS:
        if scores[name] is None:
            reasons[name] = "expected_refusal" if row["should_refuse"] else status
    if status == "completed":
        points, claims = row["point_verdicts"], row["claim_verdicts"]
        if row["should_refuse"]:
            reasons["answer_point_coverage"] = "expected_refusal"
        else:
            scores["answer_point_coverage"] = 0. if row["refused"] else sum(point["covered"] for point in points) / len(points)
        if claims:
            scores["faithfulness"] = sum(claim["supported"] for claim in claims) / len(claims)
        else:
            reasons["faithfulness"] = "zero_claims"
    else:
        reasons.update(answer_point_coverage=status, faithfulness=status)
    applicable = "absent_refusal_rate" if row["should_refuse"] else "answerable_false_refusal_rate"
    other = "answerable_false_refusal_rate" if row["should_refuse"] else "absent_refusal_rate"
    reasons[other] = "expected_refusal" if row["should_refuse"] else "answerable"
    if status in ("completed", "judge_error"):
        scores[applicable] = float(row["refused"])
    else:
        reasons[applicable] = status
    return scores, reasons


def case_metrics(record: Mapping[str, object]) -> dict[str, float | None]:
    """供 runner 写入逐题分数；合法阶段完成前相应指标保持 null。"""
    return _score(validate_case_record(record))[0]


def _summary_rows(records: list[dict]) -> list[dict]:
    """每桶及整体逐题宏平均，分母、排除原因与状态计数分别输出。"""
    scored = [(row, *_score(row)) for row in records]
    result = []
    for bucket in ["overall"] + sorted({row["bucket"] for row in records}):
        for strategy in STRATEGIES:
            selected = [(row, scores, reasons) for row, scores, reasons in scored
                        if row["strategy"] == strategy and (bucket == "overall" or row["bucket"] == bucket)]
            counts = Counter(row["status"] for row, _, _ in selected)
            metrics = {}
            for name in METRIC_NAMES:
                values = [scores[name] for _, scores, _ in selected if scores[name] is not None]
                excluded = Counter(reasons[name] for _, scores, reasons in selected if scores[name] is None)
                metrics[name] = {"value": sum(values) / len(values) if values else None,
                                 "valid_n": len(values), "excluded": dict(sorted(excluded.items()))}
            errors = sum(count for status, count in counts.items() if status.endswith("_error"))
            result.append(dict(bucket=bucket, strategy=strategy, total=len(selected),
                               attempted=len(selected) - counts["not_attempted"], completed=counts["completed"],
                               errors=errors, not_attempted=counts["not_attempted"],
                               status_counts={status: counts[status] for status in STATUSES}, metrics=metrics))
    return result


def summarize_records(records: Sequence[dict[str, object]]) -> dict[str, object]:
    """验证记录唯一性和四路题面一致性后，返回全量及共同合法生成集合统计。"""
    _require(isinstance(records, Sequence) and not isinstance(records, (str, bytes)), "records 须为序列")
    rows = [validate_case_record(record) for record in records]
    keyed, identities = {}, {}
    for row in rows:
        key = (row["eval_id"], row["strategy"])
        _require(key not in keyed, "重复题号策略记录")
        keyed[key] = row
        identity = [row[field] for field in ("bucket", "difficulty", "category", "should_refuse", "query", "mapped_groups")]
        _require(row["eval_id"] not in identities or identities[row["eval_id"]] == identity, "四路题目元数据不一致")
        identities[row["eval_id"]] = identity
    common_ids = sorted(eval_id for eval_id in identities if all(
        (eval_id, strategy) in keyed and keyed[(eval_id, strategy)]["status"] == "completed" for strategy in STRATEGIES))
    common = [row for row in rows if row["eval_id"] in common_ids]
    return {"rows": _summary_rows(rows), "common_generation": {
        "eval_ids": common_ids, "valid_n": len(common_ids), "rows": _summary_rows(common)}}


def public_report(report: Mapping[str, object]) -> dict[str, object]:
    """公开 v2 白名单和重算指标；旧版显式走只读适配器，未知版本拒绝。"""
    _require(isinstance(report, Mapping), "report 须为对象")
    if report.get("schema_version") == 1 or ("schema_version" not in report and "summary" in report):
        return adapt_legacy(report)
    _require(type(report.get("schema_version")) is int and report["schema_version"] == 2, "未知报告版本")
    _require(isinstance(report.get("records"), list), "records 须为列表")
    rows = [validate_case_record(row) for row in report["records"]]
    summary = summarize_records(rows)
    for row in rows:
        row["metrics"] = _score(row)[0]
        if row["judge_snapshot"] is not None:
            row["judge_snapshot"].pop("raw_response", None)
    result = {"schema_version": 2, "records": rows, "summary": summary}
    for key in ("run_id", "dataset_id", "fingerprint", "scope"):
        if key in report:
            _require(_text(report[key]), f"{key} 须为文本")
            if key == "scope":
                _require(report[key] in ("pilot", "full"), "scope 非法")
            result[key] = report[key]
    return result


def adapt_legacy(report: Mapping[str, object]) -> dict[str, object]:
    """只读保留 v1 已有 summary 与计数；新口径缺失用 null，不回算旧数据。"""
    _require(isinstance(report, Mapping) and isinstance(report.get("records"), list) and
             isinstance(report.get("summary"), list), "旧报告结构非法")
    # summary 历史仅由数字/桶/策略组成，逐层白名单避免扩展时夹带私有内容。
    summary_fields = ("bucket", "strategy", "total", "attempted", "completed", "errors", "not_attempted",
                      "recall_at_10", "recall_at_10_n", "recall_at_50", "recall_at_50_n", "mrr_at_10", "mrr_at_10_n",
                      "prompt_recall", "prompt_recall_n", "faithfulness", "faithfulness_n", "refusal_accuracy",
                      "refusal_n", "wrong_allow", "all_required_count")
    summaries = []
    for original in report["summary"]:
        _require(isinstance(original, Mapping), "旧summary非法")
        row = {key: copy.deepcopy(original[key]) for key in summary_fields if key in original}
        for key, value in row.items():
            _require(_text(value) if key in ("bucket", "strategy") else value is None or
                     (type(value) in (int, float) and math.isfinite(value)), "旧summary值非法")
        summaries.append(row)
    records = []
    for original in report["records"]:
        row = _object(original, ("eval_id", "strategy", "status"))
        _require(row["status"] in ("ok", "error", "not_attempted"), "旧status非法")
        _require(_text(row["eval_id"]) and row["strategy"] in STRATEGIES, "旧记录身份非法")
        for field in ("bucket", "difficulty", "query", "answer"):
            if field in original:
                _require(original[field] is None or _text(original[field], blank=True), "旧文本字段非法")
                row[field] = original[field]
        row["metrics"] = dict.fromkeys(METRIC_NAMES)
        # 同名历史检索分数口径不同，放在 legacy_metrics，不冒充 v2 完整组分数。
        row["legacy_metrics"] = {}
        for key in ("recall_at_10", "recall_at_50", "mrr_at_10", "prompt_recall", "faithfulness", "refusal_accuracy"):
            if key in original:
                value = original[key]
                _require(value is None or (type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1), "旧指标非法")
                row["legacy_metrics"][key] = value
        records.append(row)
    counts = Counter(row["status"] for row in records)
    return {"schema_version": 1, "records": records, "summary": summaries,
            "counts": {"total": len(records), "completed": counts["ok"], "errors": counts["error"],
                       "not_attempted": counts["not_attempted"]}}
