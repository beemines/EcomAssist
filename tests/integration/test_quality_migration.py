# 对随机自有 schema 执行用户原样 DDL，验证幂等检查与结构漂移拒绝。
from pathlib import Path
import re
import json
from types import SimpleNamespace

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.dialects.mysql import dialect


# 为质量表外键建立原会话及消息表，不接触共享业务表。
@pytest_asyncio.fixture
async def quality_schema(migration_database):
    ddl = re.sub(r"(?m)^\s*--.*$", "", Path("sql/schema.sql").read_text(encoding="utf-8"))
    async with migration_database.engine.begin() as connection:
        await connection.exec_driver_sql("SET NAMES utf8mb4")
        for statement in [s.strip() for s in ddl.split(";") if s.strip()][:2]:
            await connection.exec_driver_sql(statement)
    return migration_database


# 加载迁移入口；缺失实现时报告行为未提供。
def migrator():
    try:
        from app.quality.migration import migrate_quality
    except ImportError:
        pytest.fail("quality migration is missing")
    return migrate_quality


# 原样 SQL 文件与用户提供文本一致，重复迁移只检查、不重建或改动已有行。
async def test_original_ddl_and_repeat_migration_preserve_rows(quality_schema):
    migrate = migrator()
    expected = Path("prompt.md").read_text(encoding="utf-8").split("```SQL")[-1].split("```")[0].strip()
    assert Path("sql/ch04-ddl.sql").read_text(encoding="utf-8").strip() == expected
    await migrate(quality_schema)
    async with quality_schema.session() as session, session.begin():
        await session.execute(text("INSERT INTO faith_cases(eval_id,bucket,query,answer,reason) VALUES('A1','A_policy','q','a','r')"))
    await migrate(quality_schema)
    async with quality_schema.session() as session:
        assert await session.scalar(text("SELECT COUNT(*) FROM faith_cases")) == 1
        assert (await session.execute(text("SELECT strategy,status,seen_count FROM faith_cases"))).one() == ("hybrid_rerank", "未解决", 1)
        columns = (await session.execute(text("SELECT COLUMN_NAME,COLUMN_TYPE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='low_confidence_questions'"))).all()
        assert "useful" not in dict(columns)
        assert dict(columns)["source"] == "enum('retrieval_low_conf','self_check','user_feedback')"


# 只有一张质量表存在时拒绝迁移，防止自动修复掩盖上次执行失败。
async def test_partial_quality_schema_is_refused(quality_schema):
    migrate = migrator()
    await migrate(quality_schema)
    async with quality_schema.engine.begin() as connection:
        await connection.exec_driver_sql("DROP TABLE faith_cases")
    with pytest.raises(RuntimeError, match="partial"):
        await migrate(quality_schema)
    async with quality_schema.session() as session:
        assert await session.scalar(text("SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='faith_cases'")) == 0


# 字段、默认值、中文注释、索引和外键都必须符合原文，额外 useful 列也被拒绝。
@pytest.mark.parametrize("alter", [
    "ALTER TABLE faith_cases MODIFY eval_id VARCHAR(17) NOT NULL COMMENT '评估集题号,如 A43;一题一行'",
    "ALTER TABLE faith_cases ALTER status SET DEFAULT '已解决'",
    "ALTER TABLE faith_cases MODIFY status ENUM('未解决','已解决','不需解决') NOT NULL DEFAULT '未解决' COMMENT '处置状态,人工点按钮改'",
    "ALTER TABLE faith_cases MODIFY reason TEXT NULL COMMENT '裁判给的理由:编在哪一句'",
    "ALTER TABLE faith_cases COMMENT='wrong'",
    "ALTER TABLE faith_cases DROP INDEX uk_eval_id",
    "ALTER TABLE low_confidence_questions DROP FOREIGN KEY fk_lcq_conversation",
    "ALTER TABLE low_confidence_questions ADD useful BOOLEAN NULL",
    "ALTER TABLE faith_cases MODIFY seen_count INT UNSIGNED NOT NULL DEFAULT 1 COMMENT 'wrong'",
    "ALTER TABLE faith_cases ADD INDEX extra_index(bucket)",
], ids=["length", "default", "enum", "nullable", "table-comment", "unique-index", "fk", "useful", "column-comment", "extra-index"])
async def test_quality_schema_drift_is_refused(quality_schema, alter):
    migrate = migrator()
    await migrate(quality_schema)
    async with quality_schema.engine.begin() as connection:
        await connection.exec_driver_sql(alter)
    with pytest.raises(RuntimeError, match="schema"):
        await migrate(quality_schema)


# 会话外键必须指向当前 schema 且维持默认删除规则。
async def test_quality_foreign_key_delete_rule_is_checked(quality_schema):
    migrate = migrator()
    await migrate(quality_schema)
    async with quality_schema.engine.begin() as connection:
        await connection.exec_driver_sql("ALTER TABLE low_confidence_questions DROP FOREIGN KEY fk_lcq_conversation")
        await connection.exec_driver_sql("ALTER TABLE low_confidence_questions ADD CONSTRAINT fk_lcq_conversation FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE")
    with pytest.raises(RuntimeError, match="schema"):
        await migrate(quality_schema)


# 当前连接被切换到别的库时，在执行质量 DDL 前拒绝。
async def test_quality_migration_checks_current_database(quality_schema):
    migrate = migrator()
    async with quality_schema.engine.begin() as connection:
        await connection.exec_driver_sql("USE mysql")
    with pytest.raises(RuntimeError, match="target database"):
        await migrate(quality_schema)


# 比较 ORM 与原 DDL 真正生成的数据库字段，防止列类型、默认值或中文注释被误改。
async def test_quality_mapping_matches_original_database_definition(quality_schema):
    from app.db.models import FaithCase, LowConfidenceQuestion

    await migrator()(quality_schema)
    async with quality_schema.session() as session:
        for model in (LowConfidenceQuestion, FaithCase):
            table = model.__table__
            columns = (await session.execute(text("SELECT COLUMN_NAME,COLUMN_TYPE,IS_NULLABLE,COLUMN_DEFAULT,COLUMN_COMMENT FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:table ORDER BY ORDINAL_POSITION"), {"table": table.name})).all()
            assert [c.COLUMN_NAME for c in columns] == list(table.c.keys())
            for actual, expected in zip(columns, table.c):
                # ENUM 值按原样比较，只统一类型名称的拼写。
                sql_type = expected.type.compile(dialect=dialect())
                prefix, separator, suffix = sql_type.partition("(")
                normalized_type = prefix.lower() + separator + suffix
                # MySQL 展示 INT；SQLAlchemy 的 INTEGER 是相同的整数类型别名。
                normalized_type = normalized_type.replace("integer unsigned", "int unsigned")
                assert actual.COLUMN_TYPE == normalized_type
                assert actual.COLUMN_COMMENT == expected.comment
                assert actual.IS_NULLABLE == ("YES" if expected.nullable else "NO")
                default = str(expected.server_default.arg).strip("'") if expected.server_default else None
                if default == "CURRENT_TIMESTAMP":
                    assert actual.COLUMN_DEFAULT.lower().replace("()", "") == "current_timestamp"
                else:
                    assert actual.COLUMN_DEFAULT == default


# 外键指向另一个自有随机数据库时必须拒绝，即使被引用表名称和字段相同。
async def test_quality_foreign_key_to_another_schema_is_refused(quality_schema):
    from app.db.session import Database

    migrate = migrator()
    name = quality_schema.engine.url.database + "_other"
    other = Database(quality_schema.engine.url.set(database=name))
    async with quality_schema.engine.begin() as connection:
        await connection.exec_driver_sql(f"CREATE DATABASE `{name}` CHARACTER SET utf8mb4")
    try:
        async with other.engine.begin() as connection:
            await connection.exec_driver_sql(f"CREATE TABLE conversations LIKE `{quality_schema.engine.url.database}`.conversations")
        await migrate(quality_schema)
        async with quality_schema.engine.begin() as connection:
            await connection.exec_driver_sql("ALTER TABLE low_confidence_questions DROP FOREIGN KEY fk_lcq_conversation")
            await connection.exec_driver_sql(f"ALTER TABLE low_confidence_questions ADD CONSTRAINT fk_lcq_conversation FOREIGN KEY(conversation_id) REFERENCES `{name}`.conversations(id)")
        with pytest.raises(RuntimeError, match="schema"):
            await migrate(quality_schema)
    finally:
        await other.dispose()
        async with quality_schema.engine.begin() as connection:
            await connection.exec_driver_sql("ALTER TABLE low_confidence_questions DROP FOREIGN KEY fk_lcq_conversation")
            await connection.exec_driver_sql(f"DROP DATABASE `{name}`")


# 命令真正执行迁移、查看和处置，输出中文 JSON 并持久化人工说明。
async def test_quality_cli_runs_migrate_cases_and_resolve(quality_schema, monkeypatch, capsys):
    from app.quality import cli
    from app.quality.repository import QualityRepository
    from app.quality.types import FaithCaseInput

    monkeypatch.setattr(cli, "load_settings", lambda: SimpleNamespace(database_url=quality_schema.engine.url))
    await cli.run(cli.parser().parse_args(["migrate"]))
    assert capsys.readouterr().out.strip() == "Quality schema ready"
    repository = QualityRepository(quality_schema)
    await repository.record_fabrication(FaithCaseInput("A1", "A_policy", "q", "hybrid_rerank", "答案", "理由", [], None))
    await cli.run(cli.parser().parse_args(["resolve", "--eval-id", "A1", "--status", "已解决", "--resolution", "补充资料"]))
    assert capsys.readouterr().out.strip() == "Case updated"
    await cli.run(cli.parser().parse_args(["cases", "--status", "已解决"]))
    rows = json.loads(capsys.readouterr().out)
    assert len(rows) == 1 and rows[0]["resolution"] == "补充资料"
    assert rows[0]["citations"] == [] and rows[0]["resolved_at"] is not None
