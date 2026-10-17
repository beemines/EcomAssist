"""Real row-lock/CAS and append-only behavior on owned 3308 schemas."""
import asyncio
from dataclasses import replace
import importlib
import json

import pytest
import pytest_asyncio
from sqlalchemy import event, text

from tests.integration.test_context_migration import context_schema, message_bytes


@pytest_asyncio.fixture
async def history(context_schema):
    migration = importlib.import_module('app.context.migration')
    await migration.migrate_context(context_schema)
    calls = json.dumps([{'id': 'call-1', 'type': 'function', 'function': {'name': 'query_order', 'arguments': '{"order_id":"O-1"}'}}])
    async with context_schema.engine.begin() as connection:
        await connection.execute(text("INSERT INTO messages (id,conversation_id,role,content,tool_calls,tool_call_id) VALUES (13,1,'assistant',NULL,:calls,NULL),(15,2,'user','别的会话',NULL,NULL),(17,2,'assistant','另一个会话的合法最终答复',NULL,NULL),(19,1,'tool','模拟：订单已发货',NULL,'call-1'),(22,1,'assistant','当时模拟订单已发货',NULL,NULL),(25,1,'user','下一问',NULL,NULL),(30,1,'assistant','第二答',NULL,NULL),(40,1,'user','当前用户',NULL,NULL),(41,1,'assistant',NULL,:calls,NULL),(42,1,'tool','仍在处理中',NULL,'call-1')"), {'calls': calls})
    repository = importlib.import_module('app.repositories.context').ContextRepository(context_schema)
    return context_schema, repository


async def test_layer1_advances_only_to_complete_owned_final_assistant_and_never_back(history):
    database, repository = history
    from app.context.types import ContextAnchors
    anchors, segments = await repository.load('1')
    assert anchors == ContextAnchors(None, None) and segments == ()
    for invalid in (10, 13, 15, 17, 19, 23, 40, 41, 42, 100):
        assert not await repository.advance_layer1('1', expected=anchors, upto_msg_id=invalid)
    assert await repository.advance_layer1('1', expected=anchors, upto_msg_id=22)
    assert not await repository.advance_layer1('1', expected=anchors, upto_msg_id=30)
    assert not await repository.advance_layer1('1', expected=ContextAnchors(None, 22), upto_msg_id=22)
    assert await repository.advance_layer1('1', expected=ContextAnchors(None, 22), upto_msg_id=30)
    assert not await repository.advance_layer1('1', expected=ContextAnchors(None, 30), upto_msg_id=22)


async def test_batch_frozen_original_rows_handle_global_gaps_and_empty_summary(history):
    database, repository = history
    from app.context.types import ContextAnchors
    before = await message_bytes(database)
    assert await repository.load_batch('1', target_upto=22) is None
    assert await repository.advance_layer1('1', expected=ContextAnchors(None, None), upto_msg_id=30)
    for invalid in (15, 17, 19, 40, 42):
        assert await repository.load_batch('1', target_upto=invalid) is None
    batch = await repository.load_batch('1', target_upto=22)
    assert (batch.conversation_id, batch.expected_summary_upto, batch.expected_seq, batch.from_msg_id, batch.upto_msg_id) == ('1', None, 0, 10, 22)
    assert tuple(row.id for row in batch.source_rows) == ('10', '13', '19', '22')
    assert batch.source_rows[1].content is None
    assert 'query_order' in batch.source_rows[1].tool_calls_json
    segment = await repository.append_segment(batch, '', summary_budget=100)
    assert segment.seq == 1 and segment.content == ''
    anchors, segments = await repository.load('1')
    assert anchors == ContextAnchors(22, 30) and segments == (segment,)
    later = await repository.load_batch('1', target_upto=30)
    assert later.from_msg_id == 25 and later.expected_seq == 1
    assert await message_bytes(database) == before


async def test_concurrent_appends_commit_exactly_one_and_leave_prior_segments_unchanged(history):
    database, repository = history
    from app.context.types import ContextAnchors
    before = await message_bytes(database)
    await repository.advance_layer1('1', expected=ContextAnchors(None, None), upto_msg_id=22)
    first_batch = await repository.load_batch('1', target_upto=22)
    first = await repository.append_segment(first_batch, '订单O-1当时模拟已发货', summary_budget=200)
    await repository.advance_layer1('1', expected=ContextAnchors(22, 22), upto_msg_id=30)
    batch = await repository.load_batch('1', target_upto=30)
    results = await asyncio.gather(*(repository.append_segment(batch, '第二段'+str(index), summary_budget=200) for index in range(5)))
    assert sum(result is not None for result in results) == 1
    anchors, segments = await repository.load('1')
    assert anchors.summary_upto == segments[-1].upto_msg_id == 30
    assert segments[0] == first and len(segments) == 2
    assert await repository.append_segment(first_batch, '旧批次', summary_budget=200) is None
    assert await message_bytes(database) == before


@pytest.mark.parametrize('change', ['conversation', 'hash', 'from', 'upto', 'rows', 'seq', 'expected'])
async def test_forged_or_stale_batch_cannot_advance_summary(history, change):
    database, repository = history
    from app.context.types import ContextAnchors
    await repository.advance_layer1('1', expected=ContextAnchors(None, None), upto_msg_id=30)
    batch = await repository.load_batch('1', target_upto=22)
    changes = {'conversation': {'conversation_id': '2'}, 'hash': {'source_hash': '0'*64}, 'from': {'from_msg_id': 11}, 'upto': {'upto_msg_id': 19}, 'rows': {'source_rows': batch.source_rows[1:]}, 'seq': {'expected_seq': 7}, 'expected': {'expected_summary_upto': 10}}
    assert await repository.append_segment(replace(batch, **changes[change]), '错误批次', summary_budget=200) is None
    assert await repository.load('1') == (ContextAnchors(None, 30), ())


async def test_frozen_target_remains_valid_when_layer1_moves_during_generation(history):
    database, repository = history
    from app.context.types import ContextAnchors
    await repository.advance_layer1('1', expected=ContextAnchors(None, None), upto_msg_id=22)
    batch = await repository.load_batch('1', target_upto=22)
    await repository.advance_layer1('1', expected=ContextAnchors(None, 22), upto_msg_id=30)
    assert await repository.append_segment(batch, '当时结果', summary_budget=100) is not None
    assert (await repository.load('1'))[0] == ContextAnchors(22, 30)


async def test_failed_transaction_rolls_back_segment_anchor_and_projection(history):
    database, repository = history
    from app.context.types import ContextAnchors
    await repository.advance_layer1('1', expected=ContextAnchors(None, None), upto_msg_id=22)
    batch = await repository.load_batch('1', target_upto=22)

    def fail_update(connection, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith('UPDATE CONVERSATIONS'):
            raise RuntimeError('injected write failure')

    event.listen(database.engine.sync_engine, 'before_cursor_execute', fail_update)
    try:
        with pytest.raises(RuntimeError, match='injected'):
            await repository.append_segment(batch, '未提交', summary_budget=200)
    finally:
        event.remove(database.engine.sync_engine, 'before_cursor_execute', fail_update)
    assert await repository.load('1') == (ContextAnchors(None, 22), ())
    async with database.session() as session:
        assert await session.scalar(text('SELECT summary FROM conversations WHERE id=1')) is None


async def test_projection_keeps_recent_whole_segments_inside_budget(history):
    database, repository = history
    from app.context.types import ContextAnchors
    await repository.advance_layer1('1', expected=ContextAnchors(None, None), upto_msg_id=30)
    first = await repository.load_batch('1', target_upto=22)
    await repository.append_segment(first, '甲'*20, summary_budget=100)
    second = await repository.load_batch('1', target_upto=30)
    await repository.append_segment(second, '乙'*10, summary_budget=20)
    async with database.session() as session:
        assert await session.scalar(text('SELECT summary FROM conversations WHERE id=1')) == '乙'*10
    assert [segment.content for segment in (await repository.load('1'))[1]] == ['甲'*20, '乙'*10]


async def test_real_duplicate_key_rolls_back_without_anchor_or_projection_change(history):
    database, repository = history
    from app.context.types import ContextAnchors
    await repository.advance_layer1('1', expected=ContextAnchors(None, None), upto_msg_id=30)
    first = await repository.append_segment(await repository.load_batch('1', target_upto=22), '已有段', summary_budget=200)
    batch = await repository.load_batch('1', target_upto=30)
    # 只在本次自有schema注入存储故障，真实唯一键冲突必须回滚整个事务。
    async with database.engine.begin() as connection:
        await connection.exec_driver_sql('CREATE TRIGGER force_duplicate_context_seq BEFORE INSERT ON conversation_summaries FOR EACH ROW SET NEW.seq=1')
    assert await repository.append_segment(batch, '重复段', summary_budget=200) is None
    assert await repository.load('1') == (ContextAnchors(22, 30), (first,))
    async with database.session() as session:
        assert await session.scalar(text('SELECT summary FROM conversations WHERE id=1')) == '已有段'


async def test_changed_original_batch_is_refused(history):
    database, repository = history
    from app.context.types import ContextAnchors
    await repository.advance_layer1('1', expected=ContextAnchors(None, None), upto_msg_id=22)
    batch = await repository.load_batch('1', target_upto=22)
    async with database.engine.begin() as connection:
        await connection.execute(text("UPDATE messages SET content='外部改变原文' WHERE id=10"))
    assert await repository.append_segment(batch, '旧源摘要', summary_budget=200) is None
    assert await repository.load('1') == (ContextAnchors(None, 22), ())


@pytest.mark.parametrize('fault', ['orphan-tool', 'missing-result', 'wrong-result', 'middle-assistant'])
async def test_incomplete_tool_protocol_never_creates_final_boundary(history, fault):
    database, repository = history
    from app.context.types import ContextAnchors
    async with database.engine.begin() as connection:
        if fault == 'orphan-tool':
            await connection.execute(text('DELETE FROM messages WHERE id=13'))
        elif fault == 'missing-result':
            await connection.execute(text('DELETE FROM messages WHERE id=19'))
        elif fault == 'wrong-result':
            await connection.execute(text("UPDATE messages SET tool_call_id='unpaired' WHERE id=19"))
        else:
            await connection.execute(text("INSERT INTO messages (id,conversation_id,role,content) VALUES (23,1,'assistant','尚不是最终答复')"))
    assert not await repository.advance_layer1('1', expected=ContextAnchors(None, None), upto_msg_id=22)


async def test_cancelled_residue_is_retained_and_later_complete_round_can_advance(history):
    database, repository = history
    from app.context.types import ContextAnchors
    async with database.engine.begin() as connection:
        await connection.execute(text('DELETE FROM messages WHERE id=22'))
    assert await repository.advance_layer1('1', expected=ContextAnchors(None, None), upto_msg_id=30)
    batch = await repository.load_batch('1', target_upto=30)
    assert tuple(row.id for row in batch.source_rows) == ('10', '13', '19', '25', '30')


async def test_damaged_tool_json_is_diagnosed(history):
    database, repository = history
    from app.context.types import ContextAnchors
    async with database.engine.begin() as connection:
        await connection.execute(text("UPDATE messages SET tool_calls=JSON_OBJECT('damaged',1) WHERE id=13"))
    with pytest.raises(ValueError, match='Exactly one tool call'):
        await repository.advance_layer1('1', expected=ContextAnchors(None, None), upto_msg_id=22)
