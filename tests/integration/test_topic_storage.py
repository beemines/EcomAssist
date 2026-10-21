"""Owned3308 schema tests; no real customer pool or model is touched."""

import json

import pytest
from sqlalchemy import event, text
from sqlalchemy.exc import IntegrityError

from app.topics.migration import contracts, migrate_topics, verify_topics


async def seed(database):
    assert database.engine.url.port == 3308
    assert database.engine.url.database.startswith('ch03_migration_')
    async with database.session() as session, session.begin():
        await session.execute(text("INSERT INTO low_confidence_questions(id,raw_question,source) VALUES(41,'合成结构测试','self_check')"))


async def test_missing_schema_preview_is_read_only_and_migration_repeats_safely(flywheel_database):
    database = flywheel_database
    await seed(database)
    statements = []
    def capture(connection, cursor, statement, parameters, context, executemany):
        statements.append(statement.lstrip().upper())
    event.listen(database.engine.sync_engine, 'before_cursor_execute', capture)
    try:
        preview = await migrate_topics(database, preview=True)
    finally:
        event.remove(database.engine.sync_engine, 'before_cursor_execute', capture)
    assert preview.stage == 'missing' and not preview.complete and preview.preview
    assert all(statement.startswith('SELECT') for statement in statements)
    assert (await migrate_topics(database, preview=False)).complete
    assert (await migrate_topics(database, preview=True)).stage == 'complete'
    assert (await migrate_topics(database, preview=False)).applied_count == 0
    await verify_topics(database)
    async with database.session() as session:
        assert await session.scalar(text('SELECT COUNT(*) FROM low_confidence_questions')) == 1


async def test_base_rows_keep_null_tracking_and_original_fk_and_unique_behavior(flywheel_database):
    database = flywheel_database
    await seed(database)
    _, _, original, _ = contracts()
    async with database.engine.begin() as connection:
        for statement in original:
            await connection.exec_driver_sql(statement)
        await connection.execute(text('INSERT INTO topic_classifications(question_id,labels) VALUES(41,:labels)'),
                                 {'labels': json.dumps(['物流', '运费'], ensure_ascii=False)})
    await migrate_topics(database, preview=False)
    async with database.session() as session:
        row = (await session.execute(text('SELECT * FROM topic_classifications'))).mappings().one()
        assert all(row[key] is None for key in ('model_version', 'taxonomy_version', 'input_hash', 'batch_id'))
        assert json.loads(row['labels']) == ['物流', '运费']
    with pytest.raises(IntegrityError):
        async with database.session() as session, session.begin():
            await session.execute(text('DELETE FROM low_confidence_questions WHERE id=41'))
    with pytest.raises(IntegrityError):
        async with database.session() as session, session.begin():
            await session.execute(text("INSERT INTO topic_classifications(question_id,labels) VALUES(41,'[\"物流\"]')"))
    async with database.session() as session:
        assert await session.scalar(text('SELECT COUNT(*) FROM topic_classifications')) == 1


async def test_unknown_partial_schema_is_not_repaired(flywheel_database):
    await migrate_topics(flywheel_database, preview=False)
    async with flywheel_database.engine.begin() as connection:
        await connection.exec_driver_sql('ALTER TABLE topic_classifications ADD COLUMN unexpected INT NULL')
    for preview in (True, False):
        with pytest.raises(RuntimeError):
            await migrate_topics(flywheel_database, preview=preview)


async def test_sqlalchemy_mapping_round_trips_multilabel_and_version(flywheel_database):
    from app.db.models import TopicClassification
    await seed(flywheel_database)
    await migrate_topics(flywheel_database, preview=False)
    async with flywheel_database.session() as session, session.begin():
        row = TopicClassification(question_id=41, labels=['物流', '运费'], model_version='fixture-v1',
            taxonomy_version='ch10-topics-v1', input_hash='a'*64, batch_id='00000000-0000-0000-0000-000000000001')
        session.add(row)
        await session.flush()
        await session.refresh(row)
        assert row.id and row.classified_at
    async with flywheel_database.session() as session:
        saved = await session.get(TopicClassification, row.id)
        assert saved.labels == ['物流', '运费'] and saved.input_hash == 'a'*64
