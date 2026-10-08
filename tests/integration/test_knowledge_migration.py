# 独立测试库中的知识 DDL 迁移测试，覆盖已有结构核验及字段、索引、外键漂移。
from pathlib import Path
import re

import pytest
from sqlalchemy import text


# 加载权威知识迁移入口，缺失实现时报告明确的测试失败。
def migrator():
    try:
        from app.knowledge.migration import migrate
    except ImportError:
        pytest.fail("authoritative knowledge migration is missing")
    return migrate


# 验证迁移可重复执行且真实表、字段、默认值、注释与外键符合原始 DDL。
async def test_migration_executes_original_ddl_and_checks_existing_schema(migration_database):
    migrate = migrator()
    await migrate(migration_database)
    await migrate(migration_database)
    async with migration_database.session() as session:
        tables = set((await session.scalars(text("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE()"))).all())
        assert tables == {"knowledge_chunks", "qa_extraction_staging"}
        comment = await session.scalar(text("SELECT TABLE_COMMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='knowledge_chunks'"))
        assert comment == "知识库 chunk 原文权威源"
        columns = (await session.execute(text("SELECT COLUMN_NAME,COLUMN_TYPE,IS_NULLABLE,COLUMN_DEFAULT,EXTRA FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='knowledge_chunks'"))).all()
        c = {r.COLUMN_NAME: r for r in columns}
        assert c["id"].COLUMN_TYPE == "bigint unsigned" and c["id"].EXTRA == "auto_increment"
        assert c["category"].COLUMN_TYPE == "varchar(255)" and c["section_path"].COLUMN_TYPE == "varchar(512)"
        assert c["vectorize_status"].COLUMN_TYPE == "enum('pending','done')" and c["vectorize_status"].COLUMN_DEFAULT == "pending"
        rules = (await session.execute(text("SELECT CONSTRAINT_NAME,DELETE_RULE FROM information_schema.REFERENTIAL_CONSTRAINTS WHERE CONSTRAINT_SCHEMA=DATABASE()"))).all()
        assert set(rules) == {("fk_chunks_prev", "SET NULL"), ("fk_chunks_next", "SET NULL")}


# 验证只存在部分目标表时拒绝迁移，并且不会补建第二张表。
async def test_partial_schema_refused_without_creating_second_table(migration_database):
    migrate = migrator()
    ddl = Path("sql/ch03-ddl.sql").read_text(encoding="utf-8")
    ddl = re.sub(r"(?m)^--.*$", "", ddl)
    statements = [s.strip() for s in ddl.split(";") if s.strip()]
    async with migration_database.engine.begin() as connection:
        for statement in statements[:2]:
            await connection.execute(text(statement))
    with pytest.raises(RuntimeError, match="partial"):
        await migrate(migration_database)
    async with migration_database.session() as session:
        assert set((await session.scalars(text("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE()"))).all()) == {"knowledge_chunks"}


# 验证字段长度、默认值、索引、外键、可空性或表注释漂移都会被拒绝。
@pytest.mark.parametrize("alter", [
    "ALTER TABLE knowledge_chunks MODIFY category VARCHAR(254) NOT NULL",
    "ALTER TABLE knowledge_chunks ALTER vectorize_status SET DEFAULT 'done'",
    "ALTER TABLE knowledge_chunks DROP INDEX idx_category",
    "ALTER TABLE knowledge_chunks DROP FOREIGN KEY fk_chunks_prev",
    "ALTER TABLE qa_extraction_staging MODIFY question TEXT NULL",
    "ALTER TABLE qa_extraction_staging COMMENT='wrong'",
], ids=["length", "default", "index", "foreign-key", "nullable", "comment"])
async def test_existing_schema_drift_is_rejected(migration_database, alter):
    migrate = migrator()
    await migrate(migration_database)
    async with migration_database.engine.begin() as connection:
        await connection.execute(text(alter))
    with pytest.raises(RuntimeError, match="schema"):
        await migrate(migration_database)


# 验证指向另一数据库同名表的外键不能通过现有结构校验。
async def test_foreign_key_to_another_schema_is_rejected(migration_database):
    from app.db.session import Database
    migrate = migrator()
    name = migration_database.engine.url.database + "_other"
    other = Database(migration_database.engine.url.set(database=name))
    async with migration_database.engine.begin() as connection:
        await connection.execute(text(f"CREATE DATABASE `{name}` CHARACTER SET utf8mb4"))
    try:
        await migrate(migration_database)
        await migrate(other)
        async with migration_database.engine.begin() as connection:
            await connection.execute(text("ALTER TABLE knowledge_chunks DROP FOREIGN KEY fk_chunks_prev"))
            await connection.execute(text(f"ALTER TABLE knowledge_chunks ADD CONSTRAINT fk_chunks_prev FOREIGN KEY (prev_chunk_id) REFERENCES `{name}`.knowledge_chunks(id) ON DELETE SET NULL"))
        with pytest.raises(RuntimeError, match="schema"):
            await migrate(migration_database)
    finally:
        await other.dispose()
        async with migration_database.engine.begin() as connection:
            await connection.execute(text("ALTER TABLE knowledge_chunks DROP FOREIGN KEY fk_chunks_prev"))
            await connection.execute(text(f"DROP DATABASE `{name}`"))


# 验证连接当前数据库被切换后，迁移在执行 DDL 前拒绝错误目标。
async def test_changed_current_database_is_refused_before_any_ddl(migration_database):
    migrate = migrator()
    async with migration_database.engine.begin() as connection:
        await connection.execute(text("USE mysql"))
    with pytest.raises(RuntimeError, match="target database"):
        await migrate(migration_database)


# 验证枚举成员或默认值的大小写漂移被识别，即使其他字段属性保持一致。
@pytest.mark.parametrize("enum_sql,default", [("ENUM('Extracted','kept','discarded')", "Extracted"), ("ENUM('extracted','Kept','discarded')", "extracted")], ids=["member-and-default-case", "member-case-only"])
async def test_enum_literal_case_drift_is_rejected_with_other_properties_preserved(migration_database, enum_sql, default):
    migrate = migrator()
    await migrate(migration_database)
    async with migration_database.engine.begin() as connection:
        await connection.execute(text(f"ALTER TABLE qa_extraction_staging MODIFY status {enum_sql} NOT NULL DEFAULT '{default}' COMMENT '已抽出待去重 / 去重保留 / 去重丢弃'"))
        column = (await connection.execute(text("SELECT COLUMN_TYPE,COLUMN_DEFAULT,IS_NULLABLE,COLUMN_COMMENT FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='qa_extraction_staging' AND COLUMN_NAME='status'"))).one()
        assert tuple(column) == ("enum" + enum_sql[4:], default, "NO", "已抽出待去重 / 去重保留 / 去重丢弃")
    with pytest.raises(RuntimeError, match="qa_extraction_staging.status"):
        await migrate(migration_database)
