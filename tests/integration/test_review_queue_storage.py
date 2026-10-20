"""Real isolated MySQL review decisions, idempotency and transaction rollback."""
import asyncio
import json
from datetime import datetime, timezone
import pytest
from sqlalchemy import text


async def pending_review(database):
    from app.flywheel.repository import FlywheelRepository
    from tests.integration.test_flywheel_repository import item, draft
    repo = FlywheelRepository(database)
    pool = await repo.enqueue(item())
    receipt = await repo.assign(pool.id, matched_review_id=None, draft=draft())
    return repo, receipt.review_id


@pytest.fixture
async def publication_db(flywheel_database):
    from app.knowledge.migration import migrate
    await migrate(flywheel_database)
    return flywheel_database


async def test_duplicate_approval_keeps_one_knowledge_id(publication_db):
    from app.flywheel.publication import ReviewService
    repo, review_id = await pending_review(publication_db)
    service = ReviewService(repo)
    first, second = await asyncio.gather(*[
        service.approve(review_id, approved_answer='【模拟政策】满99元包邮。') for _ in range(2)])
    assert first.knowledge_chunk_id == second.knowledge_chunk_id
    async with publication_db.session() as session:
        assert await session.scalar(text('SELECT COUNT(*) FROM knowledge_chunks')) == 1
    row = await repo.get_review(review_id)
    assert row['review_status'] == '通过' and row['publication']['status'] == 'pending'
    assert row['publication']['attempt_count'] == 0


async def test_changed_approval_or_reject_after_approval_conflicts(publication_db):
    from app.flywheel.publication import ReviewService
    from app.core.errors import ServiceError
    repo, review_id = await pending_review(publication_db)
    service = ReviewService(repo)
    with pytest.raises(ValueError): await service.approve(review_id, approved_answer=' ')
    first = await service.approve(review_id, approved_answer='人工确认的答案')
    with pytest.raises(ServiceError) as err:
        await service.approve(review_id, approved_answer='事后悄悄修改')
    assert err.value.status_code == 409
    with pytest.raises(ServiceError): await service.reject(review_id, reason='已通过后驳回')
    assert (await repo.get_review(review_id))['knowledge_chunk_id'] == first.knowledge_chunk_id


async def test_approval_failure_rolls_back_knowledge_and_review(publication_db):
    from app.flywheel.publication import ReviewService
    from sqlalchemy.exc import DBAPIError
    repo, review_id = await pending_review(publication_db)
    async with publication_db.engine.begin() as connection:
        await connection.exec_driver_sql("CREATE TRIGGER fail_approval BEFORE UPDATE ON review_queue FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='controlled-test'")
    with pytest.raises(DBAPIError): await ReviewService(repo).approve(review_id, approved_answer='人工答案')
    async with publication_db.session() as session:
        assert await session.scalar(text('SELECT COUNT(*) FROM knowledge_chunks')) == 0
    assert (await repo.get_review(review_id))['review_status'] == '待审'


async def test_reject_preserves_raw_rows_without_knowledge(publication_db):
    from app.flywheel.publication import ReviewService
    repo, review_id = await pending_review(publication_db)
    service = ReviewService(repo)
    await service.reject(review_id, reason='现有知识已覆盖，应修检索')
    details = await repo.review_details(review_id)
    assert details['review']['review_status'] == '驳回' and details['total'] == 1
    assert details['review']['publication']['last_error']['message'] == '现有知识已覆盖，应修检索'
    async with publication_db.session() as session:
        assert await session.scalar(text('SELECT COUNT(*) FROM knowledge_chunks')) == 0

