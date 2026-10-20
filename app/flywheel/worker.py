"""One managed loop; MySQL state, not this in-memory task, is the queue."""
import asyncio
import logging
from contextvars import Context
from datetime import datetime, timezone
from app.flywheel.processing import PauseWorker, LeaseLost

logger = logging.getLogger(__name__)


class FlywheelWorker:
    def __init__(self, processor, *, poll_seconds=1):
        self.processor, self.tasks, self.paused_reason = processor, set(), None
        self.poll_seconds, self._stop = poll_seconds, asyncio.Event()

    def start(self):
        if self.tasks or self.paused_reason is not None or self._stop.is_set():
            return
        task = asyncio.create_task(self._run(), name='ch09-flywheel', context=Context())
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)

    async def resume(self):
        """Only an explicit human retry may clear a stopped consumer's pause."""
        if self._stop.is_set():
            raise RuntimeError('Background worker is closing')
        if self.paused_reason is not None and self.tasks:
            await asyncio.gather(*tuple(self.tasks),return_exceptions=True)
        self.tasks.difference_update(task for task in tuple(self.tasks) if task.done())
        self.paused_reason=None
        self.start()

    async def _wait(self):
        try:
            await asyncio.wait_for(self._stop.wait(), self.poll_seconds)
        except TimeoutError:
            pass

    async def _run(self):
        while not self._stop.is_set():
            try:
                if not await self.processor.recover():
                    await self._wait()
                    continue
                clock = getattr(self.processor, 'clock', lambda: datetime.now(timezone.utc))
                identifier = await self.processor.repository.next_pending_id(clock())
                if identifier is not None:
                    await self.processor.process(identifier)
            except PauseWorker as exc:
                self.paused_reason = str(exc)
                logger.warning('flywheel status=paused reason=%s', self.paused_reason)
                return
            except LeaseLost:
                logger.warning('flywheel status=lease_lost recovery=pending')
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                # Unknown state versions/DB faults must not spin a paid loop.
                self.paused_reason = 'worker_unavailable'
                logger.warning('flywheel status=paused error_type=%s', type(exc).__name__)
                return
            await self._wait()

    async def close(self, timeout_seconds=30):
        self._stop.set()
        tasks = set(self.tasks)
        if not tasks:
            return
        _, pending = await asyncio.wait(tasks, timeout=timeout_seconds)
        for task in pending:
            task.cancel()
        if pending:
            # A faulty provider's cancellation cleanup must not turn shutdown
            # into another unbounded wait. Retain ownership on timeout.
            done, remaining = await asyncio.wait(pending, timeout=min(5, max(.05, timeout_seconds)))
            if done:
                await asyncio.gather(*done, return_exceptions=True)
            if remaining:
                self.paused_reason = 'shutdown_pending'
                raise RuntimeError('flywheel background shutdown timed out; tasks remain owned')
        self.tasks.difference_update(task for task in tasks if task.done())
