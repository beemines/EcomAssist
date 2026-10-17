"""All DDL runs exclusively in migration_database's owned random 3308 schemas."""
import hashlib
import importlib
from pathlib import Path
import re

import pytest
import pytest_asyncio
from sqlalchemy import event, text


@pytest_asyncio.fixture
async def context_schema(migration_database):
    assert migration_database.engine.url.port == 3308
    assert migration_database.engine.url.database.startswith('ch03_migration_')
    ddl = re.sub(r'(?m)^\s*--.*$', '', Path('sql/schema.sql').read_text(encoding='utf-8'))
    async with migration_database.engine.begin() as connection:
        for statement in ddl.split(';'):
            if statement.strip().startswith(('CREATE TABLE conversations', 'CREATE TABLE messages')):
                await connection.exec_driver_sql(statement.strip())
        await connection.execute(text("INSERT INTO conversations (id,user_id) VALUES (1,'context-test'),(2,'other-test')"))
        await connection.execute(text("INSERT INTO messages (id,conversation_id,role,content) VALUES (10,1,'user','原文🙂中文')"))
    return migration_database


async def message_bytes(database):
    async with database.session() as session:
        rows = (await session.execute(text('SELECT id,conversation_id,role,HEX(content),CAST(tool_calls AS CHAR),tool_call_id,created_at FROM messages ORDER BY id'))).all()
        return hashlib.sha256(repr(rows).encode()).hexdigest()


async def test_verify_missing_is_read_only_and_repeat_migration_preserves_original(context_schema):
    migration = importlib.import_module('app.context.migration')
    before = await message_bytes(context_schema)
    statements = []

    def capture(connection, cursor, statement, parameters, context, executemany):
        statements.append(statement.lstrip().upper())

    event.listen(context_schema.engine.sync_engine, 'before_cursor_execute', capture)
    try:
        with pytest.raises(RuntimeError, match='missing'):
            await migration.verify_context(context_schema)
        assert not any(sql.startswith(('CREATE', 'ALTER', 'SET NAMES')) for sql in statements)
    finally:
        event.remove(context_schema.engine.sync_engine, 'before_cursor_execute', capture)
    await migration.migrate_context(context_schema)
    await migration.migrate_context(context_schema)
    await migration.verify_context(context_schema)
    assert await message_bytes(context_schema) == before


@pytest.mark.parametrize('partial', ['summary', 'first-step', 'anchors', 'table-only'])
async def test_partial_implicitly_committed_ddl_resumes(context_schema, partial):
    migration = importlib.import_module('app.context.migration')
    from app.quality.migration import _statements
    first = _statements(Path('sql/ch07.sql').read_text(encoding='utf-8'))
    second = _statements(Path('sql/ch07-layers.sql').read_text(encoding='utf-8'))
    async with context_schema.engine.begin() as connection:
        if partial == 'summary':
            await connection.exec_driver_sql(first[1].split(',\n')[0])
        elif partial == 'table-only':
            await connection.exec_driver_sql(second[2])
        else:
            await connection.exec_driver_sql(first[1])
            if partial == 'anchors':
                await connection.exec_driver_sql(second[1])
    await migration.migrate_context(context_schema)
    await migration.verify_context(context_schema)


@pytest.mark.parametrize('alter', [
    'ALTER TABLE conversations MODIFY summary VARCHAR(200) NULL',
    'ALTER TABLE conversations MODIFY summary_upto_msg_id BIGINT NULL',
    "ALTER TABLE conversations MODIFY layer1_from_msg_id BIGINT UNSIGNED NULL COMMENT 'drift'",
    'ALTER TABLE conversation_summaries DROP INDEX uk_conv_seq',
    'ALTER TABLE conversation_summaries DROP INDEX idx_conv_upto',
    'ALTER TABLE conversation_summaries MODIFY seq INT UNSIGNED NOT NULL',
    'ALTER TABLE conversation_summaries MODIFY content TEXT CHARACTER SET latin1 NOT NULL',
    'ALTER TABLE conversation_summaries ADD surprise INT NULL',
    "ALTER TABLE conversation_summaries COMMENT='drift'",
])
async def test_existing_schema_drift_is_refused_without_repair(context_schema, alter):
    migration = importlib.import_module('app.context.migration')
    await migration.migrate_context(context_schema)
    async with context_schema.engine.begin() as connection:
        await connection.exec_driver_sql(alter)
    for action in (migration.verify_context, migration.migrate_context):
        with pytest.raises(RuntimeError, match='schema.*mismatch'):
            await action(context_schema)


async def test_user_ddl_and_orm_mapping_match(context_schema):
    migration = importlib.import_module('app.context.migration')
    from app.db.models import Conversation, ConversationSummary
    from app.quality.migration import _statements
    from sqlalchemy.dialects.mysql import dialect
    async with context_schema.engine.begin() as connection:
        for name in ('ch07.sql', 'ch07-layers.sql'):
            for statement in _statements(Path('sql', name).read_text(encoding='utf-8')):
                await connection.exec_driver_sql(statement)
    await migration.verify_context(context_schema)
    async with context_schema.session() as session:
        for model in (Conversation, ConversationSummary):
            rows = (await session.execute(text('SELECT COLUMN_NAME,COLUMN_TYPE,IS_NULLABLE,COLUMN_COMMENT FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:name ORDER BY ORDINAL_POSITION'), {'name': model.__tablename__})).all()
            assert [row.COLUMN_NAME for row in rows] == list(model.__table__.c.keys())
            for row, column in zip(rows, model.__table__.c):
                compiled = column.type.compile(dialect=dialect())
                prefix, separator, suffix = compiled.partition('(')
                # MySQL normalizes SQLAlchemy INTEGER (the INT synonym) to int.
                assert row.COLUMN_TYPE == ('int' if compiled == 'INTEGER' else prefix.lower() + separator + suffix)
                assert row.IS_NULLABLE == ('YES' if column.nullable else 'NO')
                assert row.COLUMN_COMMENT == (column.comment or '')
        indexes = (await session.execute(text("SELECT INDEX_NAME,COLUMN_NAME,SEQ_IN_INDEX,NON_UNIQUE FROM information_schema.STATISTICS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='conversation_summaries'"))).all()
        assert set(indexes) == {('PRIMARY', 'id', 1, 0), ('uk_conv_seq', 'conversation_id', 1, 0), ('uk_conv_seq', 'seq', 2, 0), ('idx_conv_upto', 'conversation_id', 1, 1), ('idx_conv_upto', 'upto_msg_id', 2, 1)}


async def test_partial_schema_drift_is_rejected_before_any_missing_ddl(context_schema):
    migration = importlib.import_module('app.context.migration')
    async with context_schema.engine.begin() as connection:
        await connection.exec_driver_sql('ALTER TABLE conversations ADD COLUMN summary INT NULL AFTER status')
    statements = []

    def capture(connection, cursor, statement, parameters, context, executemany):
        statements.append(statement.lstrip().upper())

    event.listen(context_schema.engine.sync_engine, 'before_cursor_execute', capture)
    try:
        with pytest.raises(RuntimeError, match='schema.*mismatch'):
            await migration.migrate_context(context_schema)
    finally:
        event.remove(context_schema.engine.sync_engine, 'before_cursor_execute', capture)
    assert not any(statement.startswith(('CREATE', 'ALTER', 'SET NAMES')) for statement in statements)


async def test_resume_after_actual_ddl_interruption_preserves_committed_first_step(context_schema):
    migration = importlib.import_module('app.context.migration')

    def fail_second_step(connection, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith('ALTER TABLE CONVERSATIONS') and 'layer1_from_msg_id' in statement:
            raise RuntimeError('simulated interrupted migration')

    event.listen(context_schema.engine.sync_engine, 'before_cursor_execute', fail_second_step)
    try:
        with pytest.raises(RuntimeError, match='interrupted'):
            await migration.migrate_context(context_schema)
    finally:
        event.remove(context_schema.engine.sync_engine, 'before_cursor_execute', fail_second_step)
    async with context_schema.session() as session:
        names = set((await session.scalars(text("SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='conversations'"))).all())
        assert {'summary', 'summary_upto_msg_id'} <= names
        assert 'layer1_from_msg_id' not in names
    await migration.migrate_context(context_schema)
    await migration.verify_context(context_schema)


async def test_partial_anchor_in_wrong_position_refuses_before_adding_its_predecessor(context_schema):
    migration = importlib.import_module('app.context.migration')
    from app.quality.migration import _statements
    statement = _statements(Path('sql/ch07.sql').read_text(encoding='utf-8'))[1]
    anchor = statement.split(',\n')[1].strip().replace('AFTER summary', 'AFTER updated_at')
    async with context_schema.engine.begin() as connection:
        await connection.exec_driver_sql('ALTER TABLE conversations ' + anchor)
    with pytest.raises(RuntimeError, match='schema.*mismatch'):
        await migration.migrate_context(context_schema)
    async with context_schema.session() as session:
        names = set((await session.scalars(text("SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='conversations'"))).all())
        assert 'summary' not in names
        assert 'layer1_from_msg_id' not in names
