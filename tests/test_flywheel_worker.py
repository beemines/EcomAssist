import asyncio
import pytest


async def test_quota_pause_does_not_take_next_task_and_close_reaps_owned_task():
    from app.flywheel.worker import FlywheelWorker
    from app.flywheel.processing import PauseWorker
    class Repo:
        async def next_pending_id(self, now): return '1'
    class Processor:
        repository = Repo()
        calls = 0
        async def recover(self): return True
        async def process(self, identifier):
            self.calls += 1
            raise PauseWorker('quota_exhausted')
    processor = Processor()
    worker = FlywheelWorker(processor, poll_seconds=.01)
    worker.start()
    async with asyncio.timeout(1):
        while worker.paused_reason is None:
            await asyncio.sleep(.005)
    await worker.close(timeout_seconds=.1)
    assert worker.paused_reason == 'quota_exhausted' and processor.calls == 1
    assert not worker.tasks


async def test_close_cancels_inflight_background_instead_of_abandoning_reference():
    from app.flywheel.worker import FlywheelWorker
    started, cancelled = asyncio.Event(), asyncio.Event()
    class Repo:
        async def next_pending_id(self, now): return '1'
    class Processor:
        repository = Repo()
        async def recover(self): return True
        async def process(self, identifier):
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()
    worker = FlywheelWorker(Processor(), poll_seconds=.01)
    worker.start()
    await asyncio.wait_for(started.wait(), 1)
    await worker.close(timeout_seconds=.02)
    assert cancelled.is_set() and not worker.tasks


async def test_slow_cancellation_cleanup_has_bounded_close_and_keeps_task_owned():
    from app.flywheel.worker import FlywheelWorker
    started, release = asyncio.Event(), asyncio.Event()
    class Repo:
        async def next_pending_id(self, now): return '1'
    class Processor:
        repository = Repo()
        async def recover(self): return True
        async def process(self, identifier):
            started.set()
            try: await asyncio.Event().wait()
            finally: await release.wait()
    worker = FlywheelWorker(Processor(), poll_seconds=.01)
    worker.start()
    await asyncio.wait_for(started.wait(), 1)
    owned = set(worker.tasks)
    try:
        async with asyncio.timeout(.3):
            with pytest.raises(RuntimeError, match='shutdown'):
                await worker.close(timeout_seconds=.01)
        assert worker.tasks == owned
    finally:
        release.set()
        await asyncio.gather(*owned, return_exceptions=True)
        await worker.close(timeout_seconds=.01)
