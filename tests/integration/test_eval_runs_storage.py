import asyncio
import pytest
from uuid import uuid4
from sqlalchemy import text
from tests.eval_pipeline_fakes import seed_report


async def test_terminal_run_publication_is_idempotent_and_uses_question_count(flywheel_database):
    from app.eval_pipeline.store import EvalRunRepository
    report = seed_report(str(uuid4()))
    repo = EvalRunRepository(flywheel_database)
    first, second = await asyncio.gather(repo.publish(report), repo.publish(report))
    assert first == second
    async with flywheel_database.session() as session:
        row = (await session.execute(text('SELECT dataset_size,run_key,metrics FROM eval_runs'))).one()
    assert row.dataset_size == 20 and row.run_key == report.run_key


async def test_reservation_has_no_scores_and_does_not_authorize_duplicate_dispatch(flywheel_database):
    from app.eval_pipeline.store import EvalRunRepository
    report = seed_report(str(uuid4()), status='preparing')
    repo = EvalRunRepository(flywheel_database)
    assert await repo.reserve(report)
    assert not await EvalRunRepository(flywheel_database).reserve(report)
    row = await repo.get(report.run_key)
    assert row['metrics']['status'] == 'preparing'
    assert row['metrics']['scores'] is None


async def test_same_run_key_cannot_change_frozen_configuration(flywheel_database):
    from app.eval_pipeline.store import EvalRunRepository
    from app.core.errors import ServiceError
    report = seed_report(str(uuid4()))
    repo = EvalRunRepository(flywheel_database)
    await repo.publish(report)
    report.config_fingerprint = 'f' * 64
    with pytest.raises(ServiceError): await repo.publish(report)


async def test_cross_process_lease_and_orphan_receipt_never_replay(flywheel_database):
    from app.eval_pipeline.store import EvalRunRepository
    report=seed_report(str(uuid4()),status='preparing')
    first,second=EvalRunRepository(flywheel_database),EvalRunRepository(flywheel_database)
    await first.reserve(report)
    async with first.lease() as lease:
        assert lease is not None
        async with second.lease() as contender:
            assert contender is None
        await first.recover_orphans(set(),lease=lease)
    row=await second.get(report.run_key)
    assert row['metrics']['status']=='interrupted' and row['metrics']['scores'] is None
    assert not await second.reserve(report)
