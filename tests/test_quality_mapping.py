# 质量映射和命令边界测试，防止字段漂移及非法处置输入进入数据库。
from dataclasses import replace

import pytest


# 按测试需要加载质量功能；缺失实现时给出功能性失败。
def quality_models():
    try:
        from app.db.models import FaithCase, LowConfidenceQuestion
    except ImportError:
        pytest.fail("quality ORM mappings are missing")
    return LowConfidenceQuestion, FaithCase


# 验证问题池仅保存原话和来源，不引入未授权的 useful 列。
def test_pool_mapping_has_no_useful_column():
    pool, _ = quality_models()
    assert list(pool.__table__.c.keys()) == ["id", "conversation_id", "raw_question", "source", "reason", "created_at"]
    assert "useful" not in pool.__table__.c
    assert pool.__table__.c.source.type.enums == ["retrieval_low_conf", "self_check", "user_feedback"]
    assert pool.__table__.c.conversation_id.nullable
    assert {(fk.name, fk.target_fullname) for fk in pool.__table__.foreign_keys} == {("fk_lcq_conversation", "conversations.id")}


# 验证处置台账映射原始中文状态、计数默认值及题号唯一性。
def test_case_mapping_preserves_chinese_status_and_defaults():
    _, case = quality_models()
    columns = case.__table__.c
    assert columns.status.type.enums == ["未解决", "已解决", "无需解决"]
    assert str(columns.status.server_default.arg) == "'未解决'"
    assert str(columns.seen_count.server_default.arg) == "1" and columns.seen_count.type.unsigned
    assert str(columns.strategy.server_default.arg) == "'hybrid_rerank'"
    assert columns.eval_id.type.length == 16 and columns.resolution.type.length == 300
    assert {i.name for i in case.__table__.indexes} == {"uk_eval_id", "idx_status", "idx_last_seen_at"}
    assert next(i for i in case.__table__.indexes if i.name == "uk_eval_id").unique


# 验证台账输入拒绝数据库存不下的字段和不可 JSON 化的证据。
@pytest.mark.parametrize("field,value", [("eval_id", ""), ("eval_id", "a" * 17), ("bucket", "b" * 25), ("query", "q" * 513), ("strategy", "s" * 25), ("answer", "中" * 21846), ("reason", "中" * 21846), ("judge_model", "m" * 65), ("citations", [{"score": float("nan")}]), ("citations", ["not a dict"])], ids=["empty-id", "long-id", "long-bucket", "long-query", "long-strategy", "answer-bytes", "reason-bytes", "long-model", "nonfinite-json", "wrong-citation"])
def test_case_input_rejects_invalid_storage_values(field, value):
    try:
        from app.quality.types import FaithCaseInput
    except ImportError:
        pytest.fail("faith case input is missing")
    valid = FaithCaseInput("A1", "A_policy", "退货", "hybrid_rerank", "保证秒到账", "没有证据", [{"n": 1, "answer": "原文"}], None)
    with pytest.raises(ValueError):
        replace(valid, **{field: value})


# 验证命令行状态限制和有结论处置必须附说明，错误内容不会泄露敏感字符串。
def test_cli_restricts_resolution_and_prints_only_error_type(monkeypatch, capsys):
    try:
        from app.quality import cli
    except ImportError:
        pytest.fail("quality CLI is missing")
    with pytest.raises(SystemExit):
        cli.parser().parse_args(["cases", "--status", "bad"])
    with pytest.raises(SystemExit):
        cli.parser().parse_args(["resolve", "--eval-id", "A1", "--status", "已解决"])

    # 模拟配置加载故障，仅替换外部边界，观察实际入口的退出码与公开输出。
    def fail_settings():
        raise RuntimeError("mysql://user:secret@private-host")

    monkeypatch.setattr(cli, "load_settings", fail_settings)
    assert cli.main(["cases"]) == 1
    output = capsys.readouterr().err
    assert "RuntimeError" in output and "secret" not in output and "private-host" not in output
