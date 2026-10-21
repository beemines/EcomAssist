# 在随机自有数据库内验证拒答短事务和忠实度台账，不修改共享业务表。
import asyncio
from dataclasses import replace
from pathlib import Path
import re

import pytest
import pytest_asyncio
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy import text

from app.core.errors import ServiceError
from app.repositories.conversations import ConversationRepository
from tests.schema_sources import ch04_original_ddl


# 执行用户权威 SQL 于自有 schema；先建立原会话/消息表，再建立质量表。
@pytest_asyncio.fixture
async def quality_database(migration_database):
    business = re.sub(r"(?m)^\s*--.*$", "", Path("sql/schema.sql").read_text(encoding="utf-8"))
    quality = ch04_original_ddl()
    quality = re.sub(r"(?m)^\s*--.*$", "", quality)
    async with migration_database.engine.begin() as connection:
        await connection.exec_driver_sql("SET NAMES utf8mb4")
        for statement in [s.strip() for s in business.split(";") if s.strip()][:2]:
            await connection.exec_driver_sql(statement)
        for statement in re.split(r";(?=(?:[^']*'[^']*')*[^']*$)", quality):
            if statement.strip():
                await connection.exec_driver_sql(statement.strip())
    # ConversationRepository now uses ch07 anchor columns. Exercise the old
    # quality contract against its real current conversation prerequisite.
    from app.context.migration import migrate_context
    await migrate_context(migration_database)
    return migration_database


# 加载真实质量仓储及台账输入，缺失功能时明确报告 RED。
def quality_api(database):
    try:
        from app.quality.repository import QualityRepository
        from app.quality.types import FaithCaseInput
    except ImportError:
        pytest.fail("quality repository is missing")
    case = FaithCaseInput("A1", "A_policy", "何时到账", "hybrid_rerank", "保证明天到账", "证据没有期限", [{"n": 1, "chunk_id": 5, "answer": "以银行为准"}, {"n": 2, "chunk_id": 6, "answer": "未引用原文"}], "judge-test")
    return QualityRepository(database), case


# 验证提交成功后可回放拒答且问题池保存用户原话、原因和入口。
@pytest.mark.parametrize("source", ["retrieval_low_conf", "self_check"])
async def test_refusal_commits_message_and_question(quality_database, source):
    repository, _ = quality_api(quality_database)
    conversations = ConversationRepository(quality_database)
    conversation_id = await conversations.create("quality-test")
    await conversations.append_message(conversation_id, HumanMessage("到底啥时候到钱啊？"))
    message_id = await repository.commit_refusal(conversation_id, AIMessage("现有证据不足，无法承诺到账时间。"), raw_question="到底啥时候到钱啊？", source=source, reason="资料未提供期限")
    messages = await conversations.load_messages(conversation_id)
    assert messages[-1].id == message_id and messages[-1].role == "assistant"
    assert messages[-1].content == "现有证据不足，无法承诺到账时间。" and messages[-1].tool_calls is None
    async with quality_database.session() as session:
        row = (await session.execute(text("SELECT conversation_id,raw_question,source,reason FROM low_confidence_questions"))).one()
        assert tuple(row) == (int(conversation_id), "到底啥时候到钱啊？", source, "资料未提供期限")


# 用真实数据库触发器拒绝第二次写入，证明首次 flush 后消息也随事务回滚。
async def test_refusal_transaction_rolls_back_both_writes(quality_database):
    repository, _ = quality_api(quality_database)
    conversation_id = await ConversationRepository(quality_database).create("quality-rollback")
    async with quality_database.engine.begin() as connection:
        await connection.exec_driver_sql("CREATE TRIGGER reject_pool BEFORE INSERT ON low_confidence_questions FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='owned test failure'")
    with pytest.raises(Exception, match="owned test failure"):
        await repository.commit_refusal(conversation_id, AIMessage("证据不足"), raw_question="q", source="self_check", reason="不足")
    async with quality_database.session() as session:
        assert await session.scalar(text("SELECT COUNT(*) FROM messages")) == 0
        assert await session.scalar(text("SELECT COUNT(*) FROM low_confidence_questions")) == 0


# 非法拒答参数及已结束/不存在会话都不能产生任何持久化副作用。
@pytest.mark.parametrize("invalid", ["source", "empty-answer", "tool-answer", "raw-overflow", "reason-overflow", "ended", "missing", "bad-id", "wrong-role"])
async def test_invalid_refusal_has_no_writes(quality_database, invalid):
    repository, _ = quality_api(quality_database)
    conversation_id = await ConversationRepository(quality_database).create("quality-invalid")
    answer = AIMessage("证据不足")
    kwargs = dict(raw_question="原话", source="self_check", reason="证据不足")
    if invalid == "source":
        kwargs["source"] = "user_feedback"
    elif invalid == "empty-answer":
        answer = AIMessage(" ")
    elif invalid == "tool-answer":
        answer = AIMessage("", tool_calls=[{"id": "c1", "name": "search_faq", "args": {}}])
    elif invalid == "wrong-role":
        answer = HumanMessage("证据不足")
    elif invalid == "raw-overflow":
        kwargs["raw_question"] = "中" * 21846
    elif invalid == "reason-overflow":
        kwargs["reason"] = "中" * 21846
    elif invalid == "ended":
        async with quality_database.session() as session, session.begin():
            await session.execute(text("UPDATE conversations SET status='已结束' WHERE id=:id"), {"id": int(conversation_id)})
    elif invalid == "missing":
        conversation_id = "18446744073709551615"
    else:
        conversation_id = "0"
    expected_error = ServiceError if invalid in ("ended", "missing", "bad-id") else ValueError
    with pytest.raises(expected_error):
        await repository.commit_refusal(conversation_id, answer, **kwargs)
    async with quality_database.session() as session:
        assert await session.scalar(text("SELECT COUNT(*) FROM messages")) == 0
        assert await session.scalar(text("SELECT COUNT(*) FROM low_confidence_questions")) == 0


# 同题重跑只更新最近快照并递增次数，保留第一次出现的时间。
async def test_repeated_case_updates_full_snapshot_and_count(quality_database):
    repository, case = quality_api(quality_database)
    await repository.record_fabrication(case)
    first = (await repository.list_cases())[0]
    await repository.record_fabrication(replace(case, answer="保证今天到账", reason="又承诺期限", strategy="dense"))
    rows = await repository.list_cases()
    assert len(rows) == 1
    assert rows[0]["seen_count"] == 2 and rows[0]["answer"] == "保证今天到账"
    assert rows[0]["reason"] == "又承诺期限" and rows[0]["strategy"] == "dense"
    assert rows[0]["citations"] == case.citations and rows[0]["first_seen_at"] == first["first_seen_at"]


# 已处置题目复发后重开并清空说明，同时保留此前处置时间。
@pytest.mark.parametrize("status", ["已解决", "无需解决"])
async def test_recurrent_case_reopens_without_losing_resolution_time(quality_database, status):
    repository, case = quality_api(quality_database)
    await repository.record_fabrication(case)
    await repository.resolve_case(case.eval_id, status, "补充了银行期限原文")
    previous = (await repository.list_cases(status))[0]
    assert previous["resolved_at"] is not None
    await repository.record_fabrication(case)
    row = (await repository.list_cases("未解决"))[0]
    assert row["seen_count"] == 2 and row["status"] == "未解决"
    assert row["resolution"] is None and row["resolved_at"] == previous["resolved_at"]
    assert await repository.list_cases(status) == []


# 并发 upsert 由 MySQL 唯一索引与原子表达式保证不丢累计次数。
async def test_concurrent_upserts_do_not_lose_counts(quality_database):
    repository, case = quality_api(quality_database)
    await asyncio.gather(*(repository.record_fabrication(case) for _ in range(12)))
    row = (await repository.list_cases())[0]
    assert row["seen_count"] == 12


# 处置说明必须非空且适配字段长度，非法状态或未知题号不改变现有记录。
@pytest.mark.parametrize("status,resolution", [("已解决", None), ("已解决", " "), ("无需解决", ""), ("无需解决", "x" * 301), ("bad", "reason")])
async def test_resolution_rejects_invalid_inputs(quality_database, status, resolution):
    repository, case = quality_api(quality_database)
    await repository.record_fabrication(case)
    with pytest.raises(ValueError):
        await repository.resolve_case(case.eval_id, status, resolution)
    row = (await repository.list_cases())[0]
    assert row["status"] == "未解决" and row["resolution"] is None
    with pytest.raises(ValueError):
        await repository.resolve_case("missing", "已解决", "补充资料")
    with pytest.raises(ValueError):
        await repository.list_cases("bad")


# 人工重开清空说明但保留处置时间，且 last_seen_at 由每次实际复发显式刷新。
async def test_manual_reopen_and_last_seen_refresh(quality_database):
    repository, case = quality_api(quality_database)
    await repository.record_fabrication(case)
    await repository.resolve_case(case.eval_id, "已解决", "补资料")
    previous = (await repository.list_cases())[0]
    await repository.resolve_case(case.eval_id, "未解决", "丢弃说明")
    reopened = (await repository.list_cases())[0]
    assert reopened["resolution"] is None and reopened["resolved_at"] == previous["resolved_at"]
    async with quality_database.session() as session, session.begin():
        await session.execute(text("UPDATE faith_cases SET last_seen_at='2000-01-01' WHERE eval_id=:id"), {"id": case.eval_id})
    await repository.record_fabrication(case)
    assert (await repository.list_cases())[0]["last_seen_at"].year >= 2026
