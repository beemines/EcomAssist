from pathlib import Path
import re

from sqlalchemy import text
from sqlalchemy.dialects import mysql

from app.db.models import KnowledgeChunk, QAExtractionStaging
from app.db.session import Database


_TABLES = (KnowledgeChunk.__table__, QAExtractionStaging.__table__)
_DDL = Path(__file__).resolve().parents[2] / "sql" / "ch03-ddl.sql"


def _normalize(value: str) -> str:
    """Normalize SQL syntax while preserving quoted ENUM literals verbatim."""
    parts = re.split(r"('(?:[^'\\]|\\.|'')*')", value)
    return "".join(part if index % 2 else re.sub(r"\s+", " ", part.lower().replace("()", "")) for index, part in enumerate(parts)).strip()


async def _check(connection) -> None:
    for table in _TABLES:
        params = {"table": table.name}
        row = (await connection.execute(text("SELECT ENGINE,TABLE_COLLATION,TABLE_COMMENT,TABLE_TYPE FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:table"), params)).one()
        if row.ENGINE != "InnoDB" or not row.TABLE_COLLATION.startswith("utf8mb4_") or row.TABLE_COMMENT != table.comment or row.TABLE_TYPE != "BASE TABLE":
            raise RuntimeError(f"knowledge schema mismatch: {table.name} table options")
        columns = (await connection.execute(text("SELECT COLUMN_NAME,COLUMN_TYPE,IS_NULLABLE,COLUMN_DEFAULT,EXTRA,COLUMN_COMMENT,CHARACTER_SET_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:table ORDER BY ORDINAL_POSITION"), params)).all()
        if [row.COLUMN_NAME for row in columns] != list(table.c.keys()):
            raise RuntimeError(f"knowledge schema mismatch: {table.name} columns")
        for actual, expected in zip(columns, table.c):
            default = str(expected.server_default.arg) if expected.server_default else None
            on_update = False
            if default and " ON UPDATE " in default:
                default = default.split(" ON UPDATE ")[0]
                on_update = True
            if default and default.startswith("'"):
                default = default[1:-1]
            actual_default = str(actual.COLUMN_DEFAULT) if actual.COLUMN_DEFAULT is not None else None
            normalized_default = default
            if isinstance(expected.type, mysql.DATETIME):
                normalized_default = _normalize(default) if default is not None else None
                actual_default = _normalize(actual_default) if actual_default is not None else None
            extra = _normalize(actual.EXTRA).replace("default_generated", "").strip()
            expected_extra = "auto_increment" if expected.primary_key else "on update current_timestamp" if on_update else ""
            expected_type = _normalize(expected.type.compile(dialect=mysql.dialect()))
            if (_normalize(actual.COLUMN_TYPE) != expected_type
                    or actual.IS_NULLABLE != ("YES" if expected.nullable else "NO")
                    or actual_default != normalized_default or extra != expected_extra
                    or actual.COLUMN_COMMENT != expected.comment
                    or (isinstance(expected.type, (mysql.VARCHAR, mysql.TEXT, mysql.ENUM)) and actual.CHARACTER_SET_NAME != "utf8mb4")):
                raise RuntimeError(f"knowledge schema mismatch: {table.name}.{expected.name}")
        indexes = (await connection.execute(text("SELECT INDEX_NAME,COLUMN_NAME,SEQ_IN_INDEX,NON_UNIQUE,SUB_PART,INDEX_TYPE FROM information_schema.STATISTICS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:table"), params)).all()
        expected_indexes = {("PRIMARY", "id", 1, 0, None, "BTREE")}
        expected_indexes.update((index.name, list(index.columns)[0].name, 1, 1, None, "BTREE") for index in table.indexes)
        expected_indexes.update((fk.name, fk.parent.name, 1, 1, None, "BTREE") for fk in table.foreign_keys)
        if set(indexes) != expected_indexes:
            raise RuntimeError(f"knowledge schema mismatch: {table.name} indexes")
        foreign_keys = (await connection.execute(text("SELECT k.CONSTRAINT_NAME,k.COLUMN_NAME,k.REFERENCED_TABLE_SCHEMA,k.REFERENCED_TABLE_NAME,k.REFERENCED_COLUMN_NAME,r.DELETE_RULE,r.UPDATE_RULE FROM information_schema.KEY_COLUMN_USAGE k JOIN information_schema.REFERENTIAL_CONSTRAINTS r ON r.CONSTRAINT_SCHEMA=k.CONSTRAINT_SCHEMA AND r.TABLE_NAME=k.TABLE_NAME AND r.CONSTRAINT_NAME=k.CONSTRAINT_NAME WHERE k.TABLE_SCHEMA=DATABASE() AND k.TABLE_NAME=:table AND k.REFERENCED_TABLE_NAME IS NOT NULL"), params)).all()
        expected_fks = {(fk.name, fk.parent.name, connection.engine.url.database, "knowledge_chunks", "id", "SET NULL", "NO ACTION") for fk in table.foreign_keys}
        if set(foreign_keys) != expected_fks:
            raise RuntimeError(f"knowledge schema mismatch: {table.name} foreign keys")


async def migrate(database: Database) -> None:
    """Execute the supplied client DDL once; refuse partial or divergent schemas."""
    async with database.engine.begin() as connection:
        target = await connection.scalar(text("SELECT DATABASE()"))
        if not target or target != database.engine.url.database:
            raise RuntimeError("knowledge migration target database mismatch")
        existing = set((await connection.scalars(text("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME IN ('knowledge_chunks','qa_extraction_staging')"))).all())
        if existing and existing != {table.name for table in _TABLES}:
            raise RuntimeError("partial knowledge schema; explicit repair required")
        if not existing:
            # This fixed user script has no delimiters or semicolons inside literals.
            ddl = re.sub(r"(?m)^--.*$", "", _DDL.read_text(encoding="utf-8"))
            for statement in ddl.split(";"):
                if statement.strip():
                    await connection.exec_driver_sql(statement.strip())
        await _check(connection)
