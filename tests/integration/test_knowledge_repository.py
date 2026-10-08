import asyncio
import hashlib

import pytest
from sqlalchemy import event, select, text


def repository(database):
    try:
        from app.repositories.knowledge import KnowledgeRepository
    except ImportError:
        pytest.fail("knowledge repository is missing")
    return KnowledgeRepository(database)


def lock():
    try:
        from app.knowledge.locking import job_lock
    except ImportError:
        pytest.fail("connection-scoped job lock is missing")
    return job_lock


async def test_committed_pending_neighbors_and_done_backfill(knowledge_rows):
    from app.knowledge.types import ChunkDraft
    repo = repository(knowledge_rows.database)
    ids = await repo.add_chunks([ChunkDraft(knowledge_rows.token, "问题一", "答案一"), ChunkDraft(knowledge_rows.token, "问题二", "答案二")], link_neighbors=True)
    rows = {r.id: r for r in await repo.pending(limit=10000)}
    assert rows[ids[0]].next_chunk_id == ids[1]
    assert rows[ids[1]].prev_chunk_id == ids[0]
    assert rows[ids[0]].prev_chunk_id is None and rows[ids[1]].next_chunk_id is None
    assert await repo.get_done(ids) == []
    await repo.mark_done(ids)
    await repo.mark_done(ids)
    done = await repo.get_done(ids[::-1])
    assert [r.id for r in done] == ids[::-1]
    assert [r.vector_id for r in done] == [str(ids[1]), str(ids[0])]
    assert not set(ids) & {r.id for r in await repo.pending(limit=10000)}


async def test_mark_done_missing_id_rolls_back_existing_chunk(knowledge_rows):
    from app.knowledge.types import ChunkDraft
    repo = repository(knowledge_rows.database)
    ids = await repo.add_chunks([ChunkDraft(knowledge_rows.token, "问", "答")])
    with pytest.raises(ValueError):
        await repo.mark_done(ids + [9223372036854775807])
    assert await repo.get_done(ids) == []


@pytest.mark.parametrize("identifier", [0, -1, 9223372036854775808, True])
async def test_vector_boundary_rejects_unsigned_overflow_before_marking(knowledge_rows, identifier):
    repo = repository(knowledge_rows.database)
    with pytest.raises(ValueError, match="INT64"):
        await repo.mark_done([identifier])
    with pytest.raises(ValueError, match="INT64"):
        await repo.get_done([identifier])


async def test_stage_promote_is_committed_atomic_and_idempotent(knowledge_rows):
    from app.db.models import QAExtractionStaging
    from app.knowledge.types import ExtractedQA
    repo = repository(knowledge_rows.database)
    token = knowledge_rows.token
    await repo.stage(token, [ExtractedQA("test", token + "问一", "答一"), ExtractedQA("test", token + "问二", "答二")])
    rows = [r for r in await repo.extracted() if r.batch_no == token]
    assert [r.question for r in rows] == [token + "问一", token + "问二"]
    with pytest.raises(ValueError):
        await repo.promote([rows[0].id], [9223372036854775807])
    assert [r.status for r in await repo.extracted() if r.batch_no == token] == ["extracted", "extracted"]
    assert (token + "问一", "答一") not in await repo.qa_pairs()
    ids = await repo.promote([rows[0].id], [rows[1].id])
    assert len(ids) == 1
    async with knowledge_rows.database.session() as session:
        promoted = (await session.execute(text("SELECT category,content_type FROM knowledge_chunks WHERE id=:id"), {"id": ids[0]})).one()
        assert tuple(promoted) == ("历史客服", "faq")
    assert (token + "问一", "答一") in await repo.qa_pairs()
    assert (token + "问二", "答二") not in await repo.qa_pairs()
    assert await repo.promote([rows[0].id], [rows[1].id]) == []
    async with knowledge_rows.database.session() as session:
        states = (await session.scalars(select(QAExtractionStaging).where(QAExtractionStaging.batch_no == token).order_by(QAExtractionStaging.id))).all()
        assert [r.status for r in states] == ["kept", "discarded"]


async def test_promote_failure_after_insert_rolls_back_status_and_chunk(knowledge_rows):
    from app.knowledge.types import ExtractedQA
    repo = repository(knowledge_rows.database)
    token = knowledge_rows.token
    await repo.stage(token, [ExtractedQA("test", token + "回滚", "答")])
    row = next(r for r in await repo.extracted() if r.batch_no == token)
    def fail_update(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("UPDATE QA_EXTRACTION_STAGING"):
            raise RuntimeError("injected staging update failure")
    event.listen(knowledge_rows.database.engine.sync_engine, "before_cursor_execute", fail_update)
    try:
        with pytest.raises(RuntimeError, match="injected"):
            await repo.promote([row.id], [])
    finally:
        event.remove(knowledge_rows.database.engine.sync_engine, "before_cursor_execute", fail_update)
    assert (token + "回滚", "答") not in await repo.qa_pairs()
    assert next(r for r in await repo.extracted() if r.id == row.id).status == "extracted"


async def test_invalid_staging_batch_and_conflicting_promotion_are_rejected(knowledge_rows):
    from app.knowledge.types import ExtractedQA
    repo = repository(knowledge_rows.database)
    with pytest.raises(ValueError, match="batch_no"):
        await repo.stage("x" * 65, [ExtractedQA("test", "问", "答")])
    with pytest.raises(ValueError):
        await repo.promote([1], [1])


async def test_job_lock_two_connections_are_exclusive_and_exception_releases(mysql_database):
    job_lock = lock()
    with pytest.raises(RuntimeError, match="body"):
        async with job_lock(mysql_database):
            async with mysql_database.session() as session:
                name = "ch03:" + hashlib.sha256(b"customer_service_test").hexdigest()[:48]
                assert await session.scalar(text("SELECT GET_LOCK(:name, 0)"), {"name": name}) == 0
            with pytest.raises(RuntimeError, match="lock"):
                async with job_lock(mysql_database):
                    pytest.fail("occupied lock allowed a second job")
            raise RuntimeError("body failure")
    async with job_lock(mysql_database):
        pass


async def test_server_acquired_lock_then_client_failure_invalidates_connection(mysql_database):
    job_lock = lock()
    name = "ch03:" + hashlib.sha256(b"customer_service_test").hexdigest()[:48]
    def fail_after_acquisition(conn, cursor, statement, parameters, context, executemany):
        if "GET_LOCK" in statement:
            raise RuntimeError("acquisition acknowledgement lost")
    engine = mysql_database.engine.sync_engine
    event.listen(engine, "after_cursor_execute", fail_after_acquisition)
    try:
        with pytest.raises(RuntimeError, match="acknowledgement"):
            async with job_lock(mysql_database):
                pytest.fail("acquisition fault entered body")
    finally:
        event.remove(engine, "after_cursor_execute", fail_after_acquisition)
    async with mysql_database.session() as session:
        assert await session.scalar(text("SELECT IS_FREE_LOCK(:name)"), {"name": name}) == 1


async def test_inserted_unsigned_id_overflow_rolls_back(migration_database):
    from app.knowledge.migration import migrate
    from app.knowledge.types import ChunkDraft
    await migrate(migration_database)
    async with migration_database.engine.begin() as connection:
        await connection.execute(text("INSERT INTO knowledge_chunks(id,category,questions,answer) VALUES(9223372036854775807,'test','existing','answer')"))
    repo = repository(migration_database)
    with pytest.raises(ValueError, match="INT64"):
        await repo.add_chunks([ChunkDraft("test", "must roll back", "answer")])
    assert await repo.qa_pairs() == [("existing", "answer")]


async def test_cancelled_job_releases_connection_lock(mysql_database):
    job_lock = lock()
    entered = asyncio.Event()
    async def job():
        async with job_lock(mysql_database):
            entered.set()
            await asyncio.Event().wait()
    task = asyncio.create_task(job())
    await asyncio.wait_for(entered.wait(), 5)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    async with job_lock(mysql_database):
        pass


@pytest.mark.parametrize("failure", ["zero", "exception"])
async def test_failed_release_invalidates_still_locked_connection(mysql_database, failure):
    job_lock = lock()
    name = "ch03:" + hashlib.sha256(b"customer_service_test").hexdigest()[:48]
    def sabotage_release(conn, cursor, statement, parameters, context, executemany):
        if "RELEASE_LOCK" in statement:
            if failure == "exception":
                raise RuntimeError("injected release exception")
            return "SELECT 0", ()
        return statement, parameters
    engine = mysql_database.engine.sync_engine
    event.listen(engine, "before_cursor_execute", sabotage_release, retval=True)
    try:
        with pytest.raises(RuntimeError, match="release"):
            async with job_lock(mysql_database):
                async with mysql_database.session() as session:
                    holder = await session.scalar(text("SELECT IS_USED_LOCK(:name)"), {"name": name})
                    assert holder is not None
    finally:
        event.remove(engine, "before_cursor_execute", sabotage_release)
    async with mysql_database.session() as session:
        assert await session.scalar(text("SELECT IS_FREE_LOCK(:name)"), {"name": name}) == 1
        assert await session.scalar(text("SELECT CONNECTION_ID()")) != holder
    async with job_lock(mysql_database):
        pass


async def test_second_cancellation_during_release_waits_for_cleanup(mysql_database, monkeypatch):
    from sqlalchemy.ext.asyncio import AsyncConnection
    job_lock = lock()
    entered = asyncio.Event()
    releasing = asyncio.Event()
    allow_release = asyncio.Event()
    original = AsyncConnection.scalar
    async def delayed_scalar(self, statement, *args, **kwargs):
        if "RELEASE_LOCK" in str(statement):
            releasing.set()
            await allow_release.wait()
        return await original(self, statement, *args, **kwargs)
    monkeypatch.setattr(AsyncConnection, "scalar", delayed_scalar)
    async def job():
        async with job_lock(mysql_database):
            entered.set()
            await asyncio.Event().wait()
    task = asyncio.create_task(job())
    await asyncio.wait_for(entered.wait(), 5)
    task.cancel()
    await asyncio.wait_for(releasing.wait(), 5)
    task.cancel()
    allow_release.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    async with job_lock(mysql_database):
        pass


async def test_stage_replay_including_decided_rows_does_not_insert_duplicates(knowledge_rows):
    from app.db.models import QAExtractionStaging
    from app.knowledge.types import ExtractedQA
    repo = repository(knowledge_rows.database)
    token = knowledge_rows.token
    qa = ExtractedQA('synthetic', token + '问一', '答一')
    other = ExtractedQA('synthetic', token + '问二', '答二')
    async with lock()(knowledge_rows.database):
        assert await repo.stage(token, [qa, qa, other]) == 2
        rows = [r for r in await repo.extracted() if r.batch_no == token]
        await repo.promote([rows[0].id], [rows[1].id])
        assert await repo.stage(token, [qa, other]) == 0
    async with knowledge_rows.database.session() as session:
        states = (await session.scalars(select(QAExtractionStaging.status).where(QAExtractionStaging.batch_no == token).order_by(QAExtractionStaging.id))).all()
    assert states == ['kept', 'discarded']


async def test_history_beijing_window_converts_utc_storage_and_pages_completed(mysql_database):
    from datetime import datetime, timezone
    from uuid import uuid4
    from app.db.models import Conversation, Message
    try:
        from app.knowledge.history import KnowledgeHistory
    except ImportError:
        pytest.fail('knowledge history missing')
    token = 'history_test_' + uuid4().hex
    owned = []
    try:
        async with mysql_database.session() as session, session.begin():
            # Real deployment uses UTC MySQL CURRENT_TIMESTAMP, not Beijing DATETIME.
            offset = await session.scalar(text('SELECT TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(), NOW())'))
            assert offset == 0, 'test fixture expects verified UTC storage'
            for when, status in [
                (datetime(2026, 10, 5, 15, 59, 59), '已结束'),
                (datetime(2026, 10, 5, 16), '已结束'),
                (datetime(2026, 10, 6, 15, 59, 59), '已结束'),
                (datetime(2026, 10, 6, 16), '已结束'),
                (datetime(2026, 10, 5, 17), '进行中'),
            ]:
                row = Conversation(user_id=token, status=status, updated_at=when)
                session.add(row)
                await session.flush()
                owned.append(row.id)
                session.add_all([Message(conversation_id=row.id, role='user', content='合成问题'), Message(conversation_id=row.id, role='assistant', content='合成答案')])
        h = KnowledgeHistory(mysql_database)
        start, end = datetime(2026, 10, 6), datetime(2026, 10, 7)
        # Restrict pagination to the fixture's own new IDs.
        first = await h.completed(start, end, owned[0], 1)
        assert [r.id for r in first] == [owned[1]]
        second = await h.completed(start, end, first[-1].id, 1)
        assert [r.id for r in second] == [owned[2]]
        assert [m.role for m in first[0].messages] == ['user', 'assistant']
        assert first[0].last_message_id == first[0].messages[-1].id
        assert await h.completed(start, end, owned[-1]) == []
        # Aware UTC boundaries refer to the same Beijing half-open day.
        same = await h.completed(datetime(2026, 10, 5, 16, tzinfo=timezone.utc), datetime(2026, 10, 6, 16, tzinfo=timezone.utc), owned[0], 2)
        assert [r.id for r in same] == [owned[1], owned[2]]
    finally:
        async with mysql_database.session() as session, session.begin():
            await session.execute(text('DELETE FROM messages WHERE conversation_id IN (SELECT id FROM conversations WHERE user_id=:token)'), {'token': token})
            await session.execute(text('DELETE FROM conversations WHERE user_id=:token'), {'token': token})


async def test_real_mining_normalized_global_dedup_conflicts_and_window_replay(migration_database):
    from app.knowledge.migration import migrate
    from app.knowledge.mining import ConversationMiningJob
    from app.knowledge.types import ChunkDraft, ExtractedQA
    from tests.test_knowledge_mining import History, START, END
    await migrate(migration_database)
    repo = repository(migration_database)
    await repo.add_chunks([ChunkDraft('synthetic', '已经入库?', '答案')])
    class Extractor:
        async def extract(self, conversations):
            choices = {1: [('　邮费多少？\n', '标准配送  8元。'), ('邮费多少?', '标准配送 8元。')],
                2: [('邮费多少？', '标准配送 8元。'), ('邮费多少？', '标准配送12元。')],
                3: [('已经入库？', '答案')]}
            return [ExtractedQA(f'conversation:{r.id}:message:{r.last_message_id}', q, a) for r in conversations for q, a in choices[r.id]]
    async with lock()(migration_database):
        job = ConversationMiningJob(History(), repo, Extractor())
        assert await job.run(START, END, 1) == {'conversations': 3, 'staged': 5, 'kept': 2, 'discarded': 3}
        async def rerun_same_window():
            return (await job.run(START, END, 1))['kept']
        assert await rerun_same_window() == 0
        assert await repo.extracted() == []
    async with migration_database.session() as session:
        assert await session.scalar(text('SELECT COUNT(*) FROM qa_extraction_staging')) == 5
        assert await session.scalar(text("SELECT COUNT(*) FROM knowledge_chunks WHERE vectorize_status='pending'")) == 3
