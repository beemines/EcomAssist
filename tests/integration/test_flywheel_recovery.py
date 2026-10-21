import asyncio
import json
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy import text
from app.flywheel.repository import FlywheelRepository
from app.flywheel.types import PoolInput, RetrievalSnapshot, NormalizedDraft, SemanticMatch


class Clock:
    def __init__(self): self.now = datetime(2026, 10, 20, tzinfo=timezone.utc)
    def __call__(self): return self.now
    def advance(self, seconds): self.now += timedelta(seconds=seconds)


class TrackingRepository(FlywheelRepository):
    @asynccontextmanager
    async def processing_lease(self):
        async with super().processing_lease() as lease:
            self.active_lease = lease
            yield lease


class Prompts:
    def __init__(self, repository, *, match=None, error=None):
        self.repository, self.match, self.error = repository, match, error
        self.calls = []
    async def normalize(self, row):
        assert not self.repository.active_lease.connection.in_transaction()
        self.calls.append(('normalize', row['id']))
        if self.error: raise self.error
        return NormalizedDraft(normalized_question='运费如何计算？', ai_suggested_answer='待审核政策')
    async def deduplicate(self, draft, candidates):
        assert not self.repository.active_lease.connection.in_transaction()
        self.calls.append(('dedup', [c.id for c in candidates]))
        assert 1 <= len(candidates) <= 20
        return SemanticMatch(matched_review_id=self.match)


async def enqueue(repository, *, assistant='2'):
    return await repository.enqueue(PoolInput(conversation_id='1', user_message_id='1',
        assistant_message_id=assistant, raw_question='运费咋算', source='self_check', reason='政策不足',
        snapshot=RetrievalSnapshot(status='not_retrieved', payload=None)))


async def state(database, identifier):
    async with database.session() as session:
        row = (await session.execute(text('SELECT processing,matched_review_id FROM low_confidence_questions WHERE id=:id'),
            {'id': int(identifier)})).one()
    return json.loads(row.processing), row.matched_review_id


async def test_out_of_batch_match_does_not_mutate_queue(flywheel_database):
    from app.flywheel.processing import FlywheelProcessor
    repo = TrackingRepository(flywheel_database)
    receipt = await enqueue(repo)
    async with flywheel_database.session() as session, session.begin():
        await session.execute(text("INSERT INTO review_queue(normalized_question) VALUES('候选问题')"))
    prompts = Prompts(repo, match='9999')
    await FlywheelProcessor(repo, prompts, clock=Clock()).process(receipt.id)
    stored, matched = await state(flywheel_database, receipt.id)
    assert matched is None and stored['status'] == 'failed'
    async with flywheel_database.session() as session:
        assert await session.scalar(text('SELECT COUNT(*) FROM review_queue')) == 1
        assert await session.scalar(text('SELECT occurrence_count FROM review_queue')) == 1


async def test_entire_pending_queue_is_scanned_before_creating_gap(flywheel_database):
    from app.flywheel.processing import FlywheelProcessor
    repo, clock = TrackingRepository(flywheel_database), Clock()
    receipt = await enqueue(repo)
    async with flywheel_database.session() as session, session.begin():
        await session.execute(text('INSERT INTO review_queue(normalized_question) VALUES(:q)'),
            [{'q': f'已有候选问题{i}'} for i in range(205)])
    prompts = Prompts(repo)
    processor = FlywheelProcessor(repo, prompts, clock=clock)
    assert await processor.process(receipt.id) is None
    pending, matched = await state(flywheel_database, receipt.id)
    assert matched is None and pending['dedup_cursor'] == '100' and pending['status'] == 'retry_wait'
    assert len(prompts.calls) == 6
    clock.advance(5)
    result = await processor.process(receipt.id)
    assert result.created and len(prompts.calls) == 12
    assert sum(kind == 'normalize' for kind, _ in prompts.calls) == 1
    seen = [identifier for kind, ids in prompts.calls if kind == 'dedup' for identifier in ids]
    assert seen == [str(i) for i in range(1, 206)]
    async with flywheel_database.session() as session:
        assert await session.scalar(text('SELECT COUNT(*) FROM review_queue')) == 206


async def test_temporary_errors_reserve_at_most_three_attempts_across_restart(flywheel_database):
    from app.flywheel.processing import FlywheelProcessor
    repo, clock = TrackingRepository(flywheel_database), Clock()
    receipt = await enqueue(repo)
    prompts = Prompts(repo, error=TimeoutError())
    for attempt, wait in ((1, 5), (2, 30), (3, 0)):
        await FlywheelProcessor(repo, prompts, clock=clock).process(receipt.id)
        stored, matched = await state(flywheel_database, receipt.id)
        assert stored['attempt_count'] == attempt and matched is None
        assert stored['status'] == ('failed' if attempt == 3 else 'retry_wait')
        clock.advance(wait)
    await FlywheelProcessor(repo, prompts, clock=clock).process(receipt.id)
    assert len(prompts.calls) == 3


async def test_lost_lock_cannot_commit(flywheel_database):
    from app.flywheel.processing import FlywheelProcessor, LeaseLost
    repo, clock = TrackingRepository(flywheel_database), Clock()
    receipt = await enqueue(repo)
    entered, release = asyncio.Event(), asyncio.Event()
    class Blocked(Prompts):
        async def normalize(self, row):
            result = await super().normalize(row)
            entered.set()
            await release.wait()
            return result
    task = asyncio.create_task(FlywheelProcessor(repo, Blocked(repo), clock=clock).process(receipt.id))
    await asyncio.wait_for(entered.wait(), 3)
    # Only the connection held for this random schema's known test lease.
    owner = repo.active_lease.connection_id
    async with flywheel_database.engine.begin() as connection:
        await connection.exec_driver_sql(f'KILL CONNECTION {int(owner)}')
    release.set()
    with pytest.raises(LeaseLost):
        await task
    stored, matched = await state(flywheel_database, receipt.id)
    assert matched is None and stored['attempt_count'] == 1
    async with flywheel_database.session() as session:
        assert await session.scalar(text('SELECT COUNT(*) FROM review_queue')) == 0
    restarted = FlywheelProcessor(repo, Prompts(repo), clock=clock)
    await restarted.recover()
    clock.advance(5)
    result = await restarted.process(receipt.id)
    assert result.created and (await state(flywheel_database, receipt.id))[0]['attempt_count'] == 2


async def test_preexisting_null_processing_rows_are_never_sent_to_model(flywheel_database):
    from app.flywheel.processing import FlywheelProcessor
    repo = TrackingRepository(flywheel_database)
    async with flywheel_database.session() as session, session.begin():
        result = await session.execute(text("INSERT INTO low_confidence_questions(raw_question,source) VALUES('旧问题','self_check')"))
        identifier = str(result.lastrowid)
    prompts = Prompts(repo)
    assert await FlywheelProcessor(repo, prompts, clock=Clock()).process(identifier) is None
    assert prompts.calls == []


@pytest.mark.parametrize('failure', ['quota', 'cap'])
async def test_quota_error_pauses_worker_before_next_question(flywheel_database, failure):
    import httpx
    from openai import RateLimitError, APIConnectionError
    from app.context.acceptance import AcceptanceLimitExceeded
    from app.flywheel.processing import FlywheelProcessor
    from app.flywheel.worker import FlywheelWorker
    request = httpx.Request('POST', 'https://open.bigmodel.cn/api/paas/v4/chat/completions')
    if failure == 'quota':
        error = RateLimitError('safe-test-quota', response=httpx.Response(429, request=request), body={'code': '1113'})
    else:
        error = APIConnectionError(request=request)
        error.__cause__ = AcceptanceLimitExceeded('safe-test-cap')
    repo, clock = TrackingRepository(flywheel_database), Clock()
    first, second = await enqueue(repo), await enqueue(repo, assistant='4')
    prompts = Prompts(repo, error=error)
    worker = FlywheelWorker(FlywheelProcessor(repo, prompts, clock=clock), poll_seconds=.01)
    worker.start()
    try:
        async with asyncio.timeout(2):
            while worker.paused_reason is None:
                await asyncio.sleep(.005)
    finally:
        await worker.close(timeout_seconds=.1)
    assert len(prompts.calls) == 1
    assert worker.paused_reason == ('quota_exhausted' if failure == 'quota' else 'acceptance_budget')
    assert (await state(flywheel_database, first.id))[0]['status'] == 'failed'
    assert (await state(flywheel_database, second.id))[0]['status'] == 'pending'


async def test_approval_during_semantic_call_revalidates_before_assignment(flywheel_database):
    from app.flywheel.processing import FlywheelProcessor
    repo, clock = TrackingRepository(flywheel_database), Clock()
    receipt = await enqueue(repo)
    async with flywheel_database.session() as session, session.begin():
        result = await session.execute(text("INSERT INTO review_queue(normalized_question) VALUES('运费如何计算')"))
        target = str(result.lastrowid)
    class Approving(Prompts):
        async def deduplicate(self, draft, candidates):
            match = await super().deduplicate(draft, candidates)
            async with flywheel_database.session() as session, session.begin():
                await session.execute(text("UPDATE review_queue SET review_status='通过' WHERE id=:id"), {'id': int(target)})
            return match
    await FlywheelProcessor(repo, Approving(repo, match=target), clock=clock).process(receipt.id)
    stored, matched = await state(flywheel_database, receipt.id)
    assert matched is None and stored['status'] == 'retry_wait' and stored['dedup_cursor'] is None
    assert (await repo.get_review(target))['occurrence_count'] == 1


async def test_cancellation_recovery_and_replay_do_not_repeat_counts(flywheel_database):
    from app.flywheel.processing import FlywheelProcessor
    repo, clock = TrackingRepository(flywheel_database), Clock()
    receipt = await enqueue(repo)
    entered = asyncio.Event()
    class Blocked(Prompts):
        async def normalize(self, row):
            entered.set()
            await asyncio.Event().wait()
    running = asyncio.create_task(FlywheelProcessor(repo, Blocked(repo), clock=clock).process(receipt.id))
    await asyncio.wait_for(entered.wait(), 2)
    running.cancel()
    with pytest.raises(asyncio.CancelledError):
        await running
    restarted = FlywheelProcessor(repo, Prompts(repo), clock=clock)
    assert await restarted.recover()
    clock.advance(5)
    result = await restarted.process(receipt.id)
    assert result.created
    assert await restarted.process(receipt.id) is None
    assert (await repo.get_review(result.review_id))['occurrence_count'] == 1


async def test_explicit_management_only_initializes_selected_historical_id_and_never_resets_attempts(flywheel_database):
    repo, clock = TrackingRepository(flywheel_database), Clock()
    async with flywheel_database.session() as session, session.begin():
        await session.execute(text("INSERT INTO low_confidence_questions(id,raw_question,source) VALUES "
            "(100,'显式选中的旧问题','self_check'),(101,'未选择的旧问题','self_check')"))
    await repo.manage_processing('100', action='initialize', now=clock())
    stored, _ = await state(flywheel_database, '100')
    assert stored['status'] == 'pending' and stored['attempt_count'] == 0
    async with flywheel_database.session() as session:
        assert await session.scalar(text('SELECT processing FROM low_confidence_questions WHERE id=101')) is None
    stored.update(status='failed', attempt_count=3,
        last_error={'code': 'temporary_upstream', 'stage': 'normalize', 'message': '三次失败'})
    async with flywheel_database.session() as session, session.begin():
        await session.execute(text('UPDATE low_confidence_questions SET processing=:state WHERE id=100'),
            {'state': json.dumps(stored)})
    with pytest.raises(ValueError, match='attempt'):
        await repo.manage_processing('100', action='retry', now=clock())
    assert (await state(flywheel_database, '100'))[0]['attempt_count'] == 3
