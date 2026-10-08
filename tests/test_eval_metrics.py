import importlib

import pytest


GOOD = {"order_id": "A-1", "request_type": "refund", "expected_solution": "退款"}
MISSING = {"order_id": None, "request_type": "unknown", "expected_solution": None}


# 加载真实样本评分入口，缺失评测实现时报告断言失败。
def scorer():
    try:
        module = importlib.import_module("evals.evaluate")
    except ModuleNotFoundError:
        pytest.fail("evaluation implementation is missing")
    return module.score_cases


# 构造包含原文、标准答案、HTTP 状态和可选错误的评分记录。
def record(response=GOOD, *, expected=GOOD, text="订单 A-1 请退款", status=200, error=None):
    return dict(id="case", text=text, expected=expected, status_code=status,
                response=response, error_code=error)


# 验证 HTTP、结构和超时失败仍计入每个字段准确率分母。
def test_failed_cases_stay_in_all_accuracy_denominators():
    scores = scorer()([record(), record(status=502), record(response={}), record(error="timeout")])
    assert scores["total"] == 4
    assert scores["valid_count"] == 1
    assert scores["valid_rate"] == .25
    for field in GOOD:
        assert scores[f"{field}_accuracy"] == .25
    assert len(scores["failures"]) == 3


# 验证缺失字段与 unknown 类别位置都计入统计，包括失败样本。
def test_missing_positions_include_failed_cases_and_unknown():
    scores = scorer()([record(MISSING, expected=MISSING), record(None, expected=MISSING, status=None, error="timeout"),
                       record({**MISSING, "request_type": "other"}, expected=MISSING)])
    assert scores["missing_value_total"] == 9
    assert scores["missing_value_correct"] == 5
    assert scores["missing_value_accuracy"] == 5 / 9


# 验证原文约束要求合法响应且字段字面存在于原文，失败样本也留在分母。
def test_source_constraints_require_valid_output_and_literal_source_phrases():
    scores = scorer()([record(), record({**GOOD, "expected_solution": "退钱"}),
                       record({**GOOD, "order_id": "invented"}), record(status=500)])
    assert scores["source_constraint_total"] == 4
    assert scores["source_constraint_correct"] == 1
    assert scores["source_constraint_rate"] == .25
    assert scores["request_type_accuracy"] == .75


# 验证额外字段、错误枚举或类型、空白值和非对象响应不算有效输出。
@pytest.mark.parametrize("response", [
    {**GOOD, "extra": True}, {**GOOD, "request_type": "bad"},
    {**GOOD, "order_id": 1}, {**GOOD, "expected_solution": " "}, [],
])
def test_schema_invalid_response_is_never_valid(response):
    scores = scorer()([record(response)])
    assert scores["valid_count"] == 0
    assert scores["order_id_accuracy"] == 0


# 验证无样本或无缺失值位置时相关比率返回空值，避免虚构零分母准确率。
def test_zero_denominators_are_null():
    scores = scorer()([])
    assert scores["total"] == scores["missing_value_total"] == 0
    assert all(scores[key] is None for key in ["valid_rate", "order_id_accuracy", "request_type_accuracy",
                                             "expected_solution_accuracy", "missing_value_accuracy", "source_constraint_rate"])
    assert scorer()([record()])["missing_value_accuracy"] is None
