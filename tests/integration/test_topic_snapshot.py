"""Read-only snapshot behavior on owned, disposable 3308 fixtures."""

import pytest
from sqlalchemy import event, text

from app.topics.snapshot import PoolSnapshot, export_pool, preview_pool


async def seed(database):
    assert database.engine.url.port == 3308
    assert database.engine.url.database.startswith('ch03_migration_')
    async with database.session() as session, session.begin():
        await session.execute(text("INSERT INTO low_confidence_questions "
            "(id,conversation_id,user_message_id,assistant_message_id,raw_question,source) VALUES "
            "(11,1,31,32,'验收运费怎么算','retrieval_low_conf'),"
            "(12,1,31,32,'验收运费怎么算','user_feedback'),"
            "(13,1,33,34,'XL太大只想换，手机号13800138000','self_check')"))


async def test_snapshot_is_bounded_read_only_and_keeps_same_turn_provenance(flywheel_database, tmp_path):
    database = flywheel_database
    await seed(database)
    statements = []
    def capture(connection, cursor, statement, parameters, context, executemany):
        statements.append(statement.lstrip().upper())
    event.listen(database.engine.sync_engine, 'before_cursor_execute', capture)
    try:
        preview = await preview_pool(database, from_id=11, to_id=None, limit=2)
        assert preview.ids == ('11', '12') and preview.high_water == '13'
        snapshot = await export_pool(database, preview, tmp_path / 'pool.json')
    finally:
        event.remove(database.engine.sync_engine, 'before_cursor_execute', capture)
    assert all(sql.startswith(('SELECT', 'SHOW')) for sql in statements)
    assert len(snapshot.rows) == 2
    assert [row.source for row in snapshot.rows] == ['retrieval_low_conf', 'user_feedback']
    assert {row.origin for row in snapshot.rows} == {'unverified'}
    assert all(row.user_message_id == '31' for row in snapshot.rows)
    assert snapshot.rows[0].cleaned.text == '验收运费怎么算'
    assert snapshot.rows[0].cleaned.input_hash == snapshot.rows[1].cleaned.input_hash
    assert PoolSnapshot.model_validate_json((tmp_path / 'pool.json').read_text(encoding='utf-8')) == snapshot


async def test_new_high_id_does_not_expand_frozen_scope(flywheel_database, tmp_path):
    await seed(flywheel_database)
    preview = await preview_pool(flywheel_database, from_id=11, to_id=None, limit=100)
    async with flywheel_database.session() as session, session.begin():
        await session.execute(text("INSERT INTO low_confidence_questions(id,raw_question,source) "
                                   "VALUES(14,'新问题','self_check')"))
    snapshot = await export_pool(flywheel_database, preview, tmp_path / 'pool.json')
    assert [row.id for row in snapshot.rows] == ['11', '12', '13']


@pytest.mark.parametrize('change', ['text', 'range', 'identity', 'deleted'])
async def test_changed_scope_refuses_export(flywheel_database, tmp_path, change):
    await seed(flywheel_database)
    preview = await preview_pool(flywheel_database, from_id=11, to_id=None, limit=100)
    if change == 'text':
        async with flywheel_database.session() as session, session.begin():
            await session.execute(text("UPDATE low_confidence_questions SET raw_question='changed' WHERE id=11"))
    elif change == 'deleted':
        async with flywheel_database.session() as session, session.begin():
            await session.execute(text('DELETE FROM low_confidence_questions WHERE id=11'))
    elif change == 'range':
        preview = preview.model_copy(update={'from_id': 12})
    else:
        preview = preview.model_copy(update={'database_identity': '0' * 64})
    with pytest.raises(ValueError):
        await export_pool(flywheel_database, preview, tmp_path / 'refused.json')
    assert not (tmp_path / 'refused.json').exists()
