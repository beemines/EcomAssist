"""Real MySQL reads only in migration_database's disposable 3308 schema."""
import pytest
from sqlalchemy import event, text

from tests.integration.test_context_migration import context_schema, message_bytes
from tests.test_context_conversation_api import history_client


@pytest.fixture
def repository_type():
    from app.repositories.conversations import ConversationRepository
    return ConversationRepository


async def test_mysql_owned_pages_freeze_bigint_null_and_original_bytes(context_schema, tmp_path, repository_type):
    from app.context.migration import migrate_context
    await migrate_context(context_schema)
    async with context_schema.engine.begin() as conn:
        await conn.execute(text("UPDATE conversations SET user_id='demo-user' WHERE id=1"))
        await conn.execute(text('INSERT INTO messages (id,conversation_id,role,content,tool_calls) VALUES (9007199254740993,1,\'assistant\',NULL,:calls)'),
            {'calls': '[{"id":"call","type":"function","function":{"name":"query_order","arguments":"{}"}}]'})
        await conn.execute(text("INSERT INTO messages (id,conversation_id,role,content,tool_call_id) VALUES (9007199254740994,1,'tool','原结果','call')"))
    before = await message_bytes(context_schema)
    statements = []
    def capture(conn, cursor, statement, params, context, many):
        statements.append(statement.lstrip().upper())
    event.listen(context_schema.engine.sync_engine, 'before_cursor_execute', capture)
    try:
        async with history_client(context_schema, tmp_path) as (_, client, _, _, _):
            first = (await client.get('/api/conversations/1/messages?limit=1')).json()
            assert first['upto_id'] == '9007199254740994' and first['next_after_id'] == '10'
            second = (await client.get('/api/conversations/1/messages', params={
                'after_id': '10', 'upto_id': first['upto_id'], 'limit': 1})).json()
            assert second['messages'][0]['id'] == '9007199254740993'
            assert second['messages'][0]['content'] is None
            assert second['messages'][0]['tool_calls'][0]['id'] == 'call'
            assert (await client.get('/api/conversations/2/messages')).status_code == 404
            listing = (await client.get('/api/conversations')).json()
            assert [item['id'] for item in listing['items']] == ['1']
            assert listing['items'][0]['first_question_preview'] == '原文🙂中文'
    finally:
        event.remove(context_schema.engine.sync_engine, 'before_cursor_execute', capture)
    assert all(sql.startswith('SELECT') for sql in statements)
    assert await message_bytes(context_schema) == before


async def test_mysql_new_arrival_does_not_change_frozen_read(context_schema, repository_type):
    from app.context.migration import migrate_context
    await migrate_context(context_schema)
    async with context_schema.engine.begin() as conn:
        await conn.execute(text("UPDATE conversations SET user_id='demo-user' WHERE id=1"))
        await conn.execute(text("INSERT INTO messages (id,conversation_id,role,content) VALUES (20,1,'assistant','旧答'),(30,1,'user','原新问')"))
    repository = repository_type(context_schema)
    first = await repository.read_page('1', user_id='demo-user', after_id=None, upto_id=None, limit=1)
    async with context_schema.engine.begin() as conn:
        await conn.execute(text("INSERT INTO messages (id,conversation_id,role,content) VALUES (40,1,'assistant','新到答复')"))
    second = await repository.read_page('1', user_id='demo-user', after_id=first.next_after_id, upto_id=first.upto_id, limit=200)
    assert first.upto_id == second.upto_id == '30'
    assert [row.id for row in first.messages + second.messages] == ['10', '20', '30']
    assert second.next_after_id is None
