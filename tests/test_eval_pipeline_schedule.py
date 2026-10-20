from datetime import datetime, timezone, timedelta
from types import SimpleNamespace
import pytest


class Manager:
    def __init__(self): self.calls = []
    async def start(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(run_key=kwargs['run_key'])


async def test_schedule_is_disabled_by_default():
    from app.eval_pipeline.schedule import EvaluationSchedule
    manager = Manager()
    assert await EvaluationSchedule(manager).tick(datetime(2026,10,20,19,tzinfo=timezone.utc)) is None
    assert not manager.calls


async def test_shanghai_three_am_boundary_runs_once_and_skips_missed_days():
    from app.eval_pipeline.schedule import EvaluationSchedule
    manager = Manager()
    schedule = EvaluationSchedule(manager, enabled=True)
    before = datetime(2026,10,20,18,59,59,tzinfo=timezone.utc)
    boundary = before + timedelta(seconds=1)
    assert schedule.next_due(before).astimezone(timezone.utc) == boundary
    assert await schedule.tick(before) is None
    assert await schedule.tick(boundary) is not None
    assert await schedule.tick(boundary) is None
    await schedule.tick(boundary + timedelta(days=4, minutes=2))
    assert len(manager.calls) == 2
    assert all(row['scope']=='full_300' and row['triggered_by']=='定时' for row in manager.calls)


async def test_busy_schedule_is_skipped_without_spinning_or_overlapping():
    from app.eval_pipeline.schedule import EvaluationSchedule
    from app.core.errors import ServiceError
    class Busy(Manager):
        async def start(self, **kwargs):
            self.calls.append(kwargs)
            raise ServiceError('eval_busy', '', 409)
    manager = Busy()
    schedule = EvaluationSchedule(manager, enabled=True)
    instant = datetime(2026,10,20,19,tzinfo=timezone.utc)
    assert await schedule.tick(instant) is None
    assert await schedule.tick(instant + timedelta(seconds=1)) is None
    assert len(manager.calls) == 1


def test_schedule_requires_aware_clock():
    from app.eval_pipeline.schedule import EvaluationSchedule
    with pytest.raises(ValueError): EvaluationSchedule(Manager()).next_due(datetime(2026,10,20))
