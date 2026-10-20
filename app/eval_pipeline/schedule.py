"""Managed local daily schedule; paid execution is disabled by default."""
import asyncio
import logging
from contextvars import Context
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from uuid import uuid4
from app.core.errors import ServiceError

logger=logging.getLogger(__name__)


class EvaluationSchedule:
    def __init__(self, manager, *, enabled=False, clock=None):
        self.manager,self.enabled=manager,enabled
        self.clock=clock or (lambda:datetime.now(timezone.utc))
        self.due=None
        self.tasks=set()
        self._stop=asyncio.Event()

    def next_due(self, now):
        if now.utcoffset() is None: raise ValueError('Schedule requires aware time')
        local=now.astimezone(ZoneInfo('Asia/Shanghai'))
        candidate=local.replace(hour=3,minute=0,second=0,microsecond=0)
        return candidate if candidate>=local else candidate+timedelta(days=1)

    async def tick(self, now):
        if not self.enabled: return None
        if self.due is None: self.due=self.next_due(now)
        if now<self.due: return None
        self.due=self.next_due(now+timedelta(microseconds=1))
        try:
            view=await self.manager.start(run_key=str(uuid4()),scope='full_300',triggered_by='定时')
            return view.run_key
        except ServiceError as exc:
            if exc.code!='eval_busy': raise
            logger.info('eval_schedule status=skipped reason=busy')
            return None

    def start(self):
        if not self.enabled or self.tasks or self._stop.is_set(): return
        task=asyncio.create_task(self._run(),name='ch09-evaluation-schedule',context=Context())
        self.tasks.add(task); task.add_done_callback(self.tasks.discard)

    async def _run(self):
        while not self._stop.is_set():
            try:
                await self.tick(self.clock())
            except Exception as exc:
                logger.warning('eval_schedule status=failed type=%s',type(exc).__name__)
            try: await asyncio.wait_for(self._stop.wait(),30)
            except TimeoutError: pass

    async def close(self):
        self._stop.set()
        if self.tasks: await asyncio.gather(*self.tasks,return_exceptions=True)
