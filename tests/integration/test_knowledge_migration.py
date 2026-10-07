from pathlib import Path
import re

import pytest
from sqlalchemy import text


def migrator():
    try:
        from app.knowledge.migration import migrate
    except ImportError:
        pytest.fail("authoritative knowledge migration is missing")
    return migrate


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


async def test_changed_current_database_is_refused_before_any_ddl(migration_database):
    migrate = migrator()
    async with migration_database.engine.begin() as connection:
        await connection.execute(text("USE mysql"))
    with pytest.raises(RuntimeError, match="target database"):
        await migrate(migration_database)
