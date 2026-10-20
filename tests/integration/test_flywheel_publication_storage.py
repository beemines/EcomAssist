import asyncio
import json
import pytest
from sqlalchemy import text
from tests.integration.test_review_queue_storage import publication_db, pending_review
from tests.integration.test_flywheel_recovery import Clock


async def approved(database):
    from app.flywheel.publication import ReviewService
    repo, identifier = await pending_review(database)
    receipt = await ReviewService(repo).approve(identifier, approved_answer='【模拟政策】人工核准答案。')
    return repo, identifier, receipt


async def test_publication_timeout_attempts_persist_and_never_ready(publication_db):
    from app.flywheel.publication import PublicationWorker
    repo, identifier, receipt = await approved(publication_db)
    class Jobs:
        calls = []
        async def vectorize_ids(self, ids): self.calls.append(ids); raise TimeoutError()
    jobs, clock = Jobs(), Clock()
    for attempt, seconds in ((1, 5), (2, 30), (3, 0)):
        result = await PublicationWorker(repo, jobs, clock=clock).publish(identifier)
        row = await repo.get_review(identifier)
        assert row['publication']['attempt_count'] == attempt
        assert result.knowledge_chunk_id == receipt.knowledge_chunk_id
        assert result.status == ('pending' if attempt < 3 else 'failed')
        clock.advance(seconds)
    assert len(jobs.calls) == 3
    await PublicationWorker(repo, jobs, clock=clock).publish(identifier)
    assert len(jobs.calls) == 3
    async with publication_db.session() as session:
        assert await session.scalar(text('SELECT vectorize_status FROM knowledge_chunks')) == 'pending'


async def test_publication_cancel_restart_reuses_knowledge_and_repairs_running(publication_db):
    from app.flywheel.publication import PublicationWorker
    repo, identifier, receipt = await approved(publication_db)
    started = asyncio.Event()
    class BlockedJobs:
        async def vectorize_ids(self, ids): started.set(); await asyncio.Event().wait()
    worker = PublicationWorker(repo, BlockedJobs())
    task = asyncio.create_task(worker.publish(identifier))
    await asyncio.wait_for(started.wait(), 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError): await task
    assert (await repo.get_review(identifier))['publication']['status'] == 'running'
    assert await PublicationWorker(repo, BlockedJobs()).recover()
    row = await repo.get_review(identifier)
    assert row['publication']['status'] == 'pending' and row['publication']['attempt_count'] == 1
    assert row['knowledge_chunk_id'] == receipt.knowledge_chunk_id


async def test_real_local_vector_publication_is_ready_only_after_ack_readback(publication_db, milvus_collection):
    from app.flywheel.publication import PublicationWorker
    from app.repositories.knowledge import KnowledgeRepository
    from app.knowledge.hybrid_jobs import HybridKnowledgeJobs
    from app.knowledge.types import ChunkDraft
    from app.retrieval.milvus import HybridMilvusIndex
    from tests.test_hybrid_jobs import Embedder
    repo, identifier, receipt = await approved(publication_db)
    knowledge = KnowledgeRepository(publication_db)
    unrelated = await knowledge.add_chunks([ChunkDraft('模拟', '别的待处理问题', '不属于本次发布')])
    service = milvus_collection
    index = HybridMilvusIndex(service.uri, collection=service.name, client=service.client)
    await index.ensure_collection()
    embedder = Embedder()
    worker = PublicationWorker(repo, HybridKnowledgeJobs(knowledge, embedder, index))
    result = await worker.publish(identifier)
    assert result.status == 'ready' and result.knowledge_chunk_id == receipt.knowledge_chunk_id
    assert await index.all_ids() == {int(receipt.knowledge_chunk_id)}
    assert len(embedder.texts) == 1 and '别的待处理' not in embedder.texts[0]
    assert [row.id for row in await knowledge.pending_by_ids(unrelated)] == unrelated
    assert (await worker.publish(identifier)).status == 'ready'
    assert len(embedder.texts) == 1


@pytest.mark.parametrize('status,expected', [(401, 'authentication_failed'), (403, 'authentication_failed'),
    (402, 'quota_exhausted'), (429, None), (503, None)])
async def test_publication_http_auth_quota_pause_but_temporary_errors_retry(publication_db, status, expected):
    import httpx
    from app.flywheel.publication import PublicationWorker
    from app.flywheel.processing import PauseWorker
    repo, identifier, receipt = await approved(publication_db)
    response = httpx.Response(status, request=httpx.Request('POST', 'https://api.siliconflow.cn/v1/embeddings'))
    class Jobs:
        async def vectorize_ids(self, ids):
            response.raise_for_status()
    worker = PublicationWorker(repo, Jobs(), clock=Clock())
    if expected:
        with pytest.raises(PauseWorker, match=expected): await worker.publish(identifier)
    else:
        assert (await worker.publish(identifier)).status == 'pending'
    row = await repo.get_review(identifier)
    assert row['publication']['attempt_count'] == 1
    assert row['publication']['status'] == ('failed' if expected else 'pending')


async def test_explicit_manual_retry_keeps_id_and_monotonic_total_after_auto_ceiling(publication_db):
    from app.flywheel.publication import ReviewService, PublicationWorker
    repo, identifier, receipt = await approved(publication_db)
    class Jobs:
        async def vectorize_ids(self, ids): raise ValueError('ACK mismatch')
    for attempt in range(1, 4):
        result = await PublicationWorker(repo, Jobs(), clock=Clock()).publish(identifier)
        assert result.status == 'failed' and result.knowledge_chunk_id == receipt.knowledge_chunk_id
        if attempt < 3:
            retried = await ReviewService(repo).retry_publication(identifier)
            assert retried.knowledge_chunk_id == receipt.knowledge_chunk_id
    assert (await repo.get_review(identifier))['publication']['attempt_count'] == 3
    # The spec permits an explicit human retry after fixing a failed publication.
    # It authorizes one more attempt, never a counter reset or new knowledge row.
    retried = await ReviewService(repo).retry_publication(identifier)
    assert retried.knowledge_chunk_id == receipt.knowledge_chunk_id
    await PublicationWorker(repo, Jobs(), clock=Clock()).publish(identifier)
    row = await repo.get_review(identifier)
    assert row['publication']['attempt_count'] == 4 and row['publication']['status'] == 'failed'
    await PublicationWorker(repo, Jobs(), clock=Clock()).publish(identifier)
    assert (await repo.get_review(identifier))['publication']['attempt_count'] == 4


async def test_publication_holds_the_original_knowledge_job_lock(publication_db):
    from app.flywheel.publication import PublicationWorker
    from app.knowledge.locking import job_lock
    repo, identifier, receipt = await approved(publication_db)
    class Jobs:
        calls = 0
        async def vectorize_ids(self, ids): self.calls += 1
    jobs = Jobs()
    async with job_lock(publication_db):
        result = await PublicationWorker(repo, jobs).publish(identifier)
    assert jobs.calls == 0 and result.status == 'pending'


async def test_lost_publication_lease_cannot_mark_ready(publication_db):
    from app.flywheel.publication import PublicationWorker
    from app.flywheel.leases import LeaseLost
    repo, identifier, receipt = await approved(publication_db)
    class Jobs:
        async def vectorize_ids(self, ids):
            import hashlib
            name = 'ch03:' + hashlib.sha256(publication_db.engine.url.database.encode()).hexdigest()[:48]
            async with publication_db.engine.connect() as connection:
                owner = await connection.scalar(text('SELECT IS_USED_LOCK(:name)'), {'name': name})
                await connection.exec_driver_sql(f'KILL CONNECTION {int(owner)}')
    with pytest.raises(LeaseLost): await PublicationWorker(repo, Jobs()).publish(identifier)
    assert (await repo.get_review(identifier))['publication']['status'] == 'running'


async def test_publication_cannot_be_ready_while_knowledge_is_still_pending(publication_db):
    from app.flywheel.publication import PublicationWorker
    repo, identifier, _ = await approved(publication_db)
    class IncompleteJobs:
        async def vectorize_ids(self, ids): return 0
    result = await PublicationWorker(repo, IncompleteJobs()).publish(identifier)
    assert result.status == 'failed'
    assert (await repo.get_review(identifier))['publication']['published_at'] is None
