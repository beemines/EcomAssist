import asyncio
from sqlalchemy import text
import pytest


def item(source='self_check', *, user='9007199254740993', assistant='9007199254740994'):
    from app.flywheel.types import PoolInput, RetrievalSnapshot
    return PoolInput(conversation_id='1', user_message_id=user, assistant_message_id=assistant,
        raw_question='用户原话：包邮怎么计算', source=source, reason='evidence missing',
        snapshot=RetrievalSnapshot(status='not_retrieved', payload=None))


def draft():
    from app.flywheel.types import NormalizedDraft
    return NormalizedDraft(normalized_question='商品订单的包邮条件是什么？', ai_suggested_answer='待人工核实包邮政策。')


async def test_two_sources_share_one_occurrence(flywheel_database):
    from app.flywheel.repository import FlywheelRepository
    repo = FlywheelRepository(flywheel_database)
    first = await repo.enqueue(item())
    assigned = await repo.assign(first.id, matched_review_id=None, draft=draft())
    feedback = await repo.enqueue(item('user_feedback'))
    await repo.assign(feedback.id, matched_review_id=assigned.review_id, draft=draft())
    details = await repo.review_details(assigned.review_id)
    raw_rows = details['raw_questions']
    review = details['review']
    assert len(raw_rows) == 2 and review['occurrence_count'] == 1
    assert raw_rows[0]['user_message_id'] == '9007199254740993'
    assert {row['source'] for row in raw_rows} == {'self_check', 'user_feedback'}


async def test_concurrent_duplicate_delivery_returns_one_receipt(flywheel_database):
    from app.flywheel.repository import FlywheelRepository
    repo = FlywheelRepository(flywheel_database)
    receipts = await asyncio.gather(repo.enqueue(item()), repo.enqueue(item()))
    assert len({receipt.id for receipt in receipts}) == 1
    assert sum(receipt.created for receipt in receipts) == 1


async def test_different_turn_increments_and_replay_does_not(flywheel_database):
    from app.flywheel.repository import FlywheelRepository
    repo = FlywheelRepository(flywheel_database)
    first = await repo.enqueue(item())
    target = await repo.assign(first.id, matched_review_id=None, draft=draft())
    second = await repo.enqueue(item(user='3', assistant='4'))
    await repo.assign(second.id, matched_review_id=target.review_id, draft=draft())
    await repo.assign(second.id, matched_review_id=target.review_id, draft=draft())
    assert (await repo.get_review(target.review_id))['occurrence_count'] == 2


async def test_review_changed_rolls_back_assignment(flywheel_database):
    from app.flywheel.repository import FlywheelRepository
    from app.flywheel.types import ReviewChanged
    repo = FlywheelRepository(flywheel_database)
    first = await repo.enqueue(item())
    target = await repo.assign(first.id, matched_review_id=None, draft=draft())
    second = await repo.enqueue(item(user='3', assistant='4'))
    async with flywheel_database.session() as session, session.begin():
        await session.execute(text("UPDATE review_queue SET review_status='通过' WHERE id=:id"), {'id': int(target.review_id)})
    with pytest.raises(ReviewChanged):
        await repo.assign(second.id, matched_review_id=target.review_id, draft=draft())
    async with flywheel_database.session() as session:
        assert await session.scalar(text('SELECT matched_review_id FROM low_confidence_questions WHERE id=:id'), {'id': int(second.id)}) is None


async def test_rejected_recurrence_matches_original_gap_and_stays_rejected(flywheel_database):
    from app.flywheel.repository import FlywheelRepository
    repo=FlywheelRepository(flywheel_database)
    first=await repo.enqueue(item())
    target=await repo.assign(first.id,matched_review_id=None,draft=draft())
    await repo.reject_review(target.review_id,reason='低频临时问题')
    async with flywheel_database.session() as session:
        candidates,_=await repo._candidate_snapshot(session)
    assert [candidate.id for candidate in candidates]==[target.review_id]
    second=await repo.enqueue(item(user='3',assistant='4'))
    await repo.assign(second.id,matched_review_id=target.review_id,draft=draft())
    feedback=await repo.enqueue(item('user_feedback',user='3',assistant='4'))
    await repo.assign(feedback.id,matched_review_id=target.review_id,draft=draft())
    review=await repo.get_review(target.review_id)
    assert review['review_status']=='驳回' and review['occurrence_count']==2
    all_rows=await repo.list_reviews(status='全部')
    assert all_rows['total']==1
    assert (await repo.list_reviews(status='待审'))['total']==0


async def test_enqueue_in_session_does_not_commit_on_behalf_of_caller(flywheel_database):
    from app.flywheel.repository import FlywheelRepository
    repo = FlywheelRepository(flywheel_database)
    with pytest.raises(RuntimeError, match='rollback sentinel'):
        async with flywheel_database.session() as session, session.begin():
            await repo.enqueue_in_session(session, item())
            raise RuntimeError('rollback sentinel')
    async with flywheel_database.session() as session:
        assert await session.scalar(text('SELECT COUNT(*) FROM low_confidence_questions')) == 0


async def test_assignment_failure_does_not_leave_an_orphan_review(flywheel_database):
    from app.flywheel.repository import FlywheelRepository
    from sqlalchemy.exc import DBAPIError
    repo = FlywheelRepository(flywheel_database)
    receipt = await repo.enqueue(item())
    async with flywheel_database.engine.begin() as connection:
        await connection.exec_driver_sql("CREATE TRIGGER reject_assignment BEFORE UPDATE ON low_confidence_questions FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='assignment-test-sentinel'")
    with pytest.raises(DBAPIError):
        await repo.assign(receipt.id, matched_review_id=None, draft=draft())
    async with flywheel_database.session() as session:
        assert await session.scalar(text('SELECT COUNT(*) FROM review_queue')) == 0
        assert await session.scalar(text('SELECT matched_review_id FROM low_confidence_questions')) is None


async def test_new_table_mappings_round_trip_original_defaults(flywheel_database):
    from app.db.models import ReviewQueue, EvalRun
    from app.flywheel.repository import FlywheelRepository
    async with flywheel_database.session() as session, session.begin():
        review = ReviewQueue(normalized_question='中文待审问题', ai_suggested_answer='待人工核准')
        run = EvalRun(dataset_size=1, metrics={'schema_probe': '临时结构测试'})
        session.add_all([review, run])
        await session.flush()
        review_id, run_id = review.id, run.id
    assert (await FlywheelRepository(flywheel_database).get_review(str(review_id)))['review_status'] == '待审'
    async with flywheel_database.session() as session:
        assert await session.scalar(text('SELECT triggered_by FROM eval_runs WHERE id=:id'), {'id': run_id}) == '定时'


async def test_history_preview_only_returns_uninitialized_rows_in_selected_range(flywheel_database):
    from app.flywheel.repository import FlywheelRepository
    repo=FlywheelRepository(flywheel_database)
    async with flywheel_database.session() as session,session.begin():
        for key in range(1,4):
            await session.execute(text("INSERT INTO low_confidence_questions(id,raw_question,source,reason) "
                "VALUES(:id,'历史模拟问题','self_check','旧数据')"),{'id':key})
    result=await repo.preview_legacy_batch('1','2',limit=1)
    assert [row['id'] for row in result['items']]==['1']
    assert result['has_more'] is True
    async with flywheel_database.session() as session:
        assert await session.scalar(text('SELECT COUNT(*) FROM low_confidence_questions WHERE processing IS NULL'))==3
