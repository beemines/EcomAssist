"""Nonblocking admission with two running jobs, eight waiting conversations, no retries."""
import asyncio
from collections import deque
from collections.abc import Callable
from dataclasses import replace
import json
import logging
import time
from uuid import uuid4

from app.context.layers import _compact_layer2, history_tokens
from app.context.summarizer import SUMMARY_OUTPUT_TOKENS, required_entities, summary_input_tokens, validate_summary
from app.context.types import ContextBudget, SummaryRequest
from app.core.tool_history import completed_boundaries
from app.repositories.context import ContextRepository
from app.repositories.records import MessageRecord


def _default_event(name, fields):
    logging.getLogger('app.context.summary').info(json.dumps({'event': name, **fields}, ensure_ascii=False))


class SummaryManager:
    def __init__(self, repository: ContextRepository, generator, *, budget_provider: Callable[[], ContextBudget],
                 event_logger: Callable[[str, dict], None] | None = None):
        self.repository, self.generator = repository, generator
        self.budget_provider = budget_provider
        self.event_logger = event_logger or _default_event
        self._running = {}
        self._waiting = deque()
        self._conversations = set()
        self._closed = False

    def _event(self, name, request, *, batch=None, target=None, started=None, reason=None):
        now = time.time()
        fields = dict(task_id=request.task_id, conversation_id=request.conversation_id,
            seq=batch.expected_seq+1 if batch else None, from_msg_id=str(batch.from_msg_id) if batch else None,
            upto_msg_id=str(batch.upto_msg_id) if batch else None,
            expected_s=str(batch.expected_summary_upto) if batch and batch.expected_summary_upto is not None else None,
            target_l=str(target) if target is not None else None, threshold=request.budget.layer2,
            layer2_tokens=request.layer2_tokens, waiting=len(self._waiting), running=len(self._running),
            created_at=request.created_at, started_at=started, ended_at=now,
            elapsed_ms=max(0, round((now-(started or request.created_at))*1000)), reason=reason)
        # Event sinks must not leak arbitrary exception/model/client representations,
        # nor turn a committed summary into a failed task if logging is unavailable.
        try:
            self.event_logger(name, fields)
        except Exception:
            logging.getLogger('app.context.summary').error('summary event sink failed')

    def notify(self, conversation_id: str, *, layer2_tokens: int, budget: ContextBudget) -> bool:
        if not isinstance(conversation_id, str) or not conversation_id.isascii() or not conversation_id.isdecimal() or int(conversation_id) <= 0:
            raise ValueError('Summary conversation id must be a positive decimal string.')
        if type(layer2_tokens) is not int or layer2_tokens < 0:
            raise ValueError('Layer2 usage must be a nonnegative integer.')
        request = SummaryRequest(uuid4().hex, str(int(conversation_id)), layer2_tokens, budget, time.time())
        reason = ('closed' if self._closed else 'below_threshold' if layer2_tokens <= budget.layer2 else
                  'duplicate' if request.conversation_id in self._conversations else
                  'busy' if len(self._running) >= 2 and len(self._waiting) >= 8 else None)
        if reason:
            self._event('summary_skipped', request, reason=reason)
            return False
        asyncio.get_running_loop()  # Fail before admission if no owning event loop exists.
        self._conversations.add(request.conversation_id)
        if len(self._running) < 2:
            self._launch(request)
        else:
            self._waiting.append(request)
        self._event('summary_notify', request)
        return True

    def _launch(self, request):
        self._running[request.conversation_id] = asyncio.create_task(self._run(request))

    async def startup(self) -> None:
        cursor = 0
        while not self._closed:
            page = await self.repository.list_downgraded(after_id=cursor, limit=100)
            if not page:
                return
            for conversation_id in page:
                if self._closed:
                    return
                budget = self.budget_provider()
                request = SummaryRequest(uuid4().hex, conversation_id, 0, budget, time.time())
                try:
                    anchors, _ = await self.repository.load(conversation_id)
                    batch = await self.repository.load_batch(conversation_id, target_upto=anchors.layer1_from)
                    if batch is not None:
                        usage = history_tokens(_compact_layer2(batch.source_rows))
                        self.notify(conversation_id, layer2_tokens=usage, budget=budget)
                except Exception:
                    self._event('summary_failed', request, reason='recovery_error')
            cursor = int(page[-1])
            if len(page) < 100:
                return

    async def _prefix(self, batch, budget):
        records = [MessageRecord(int(row.id), row.role, row.content,
                   json.loads(row.tool_calls_json) if row.tool_calls_json is not None else None, row.tool_call_id)
                   for row in batch.source_rows]
        chosen = None
        for boundary in sorted(completed_boundaries(records)):
            rows = tuple(row for row in batch.source_rows if int(row.id) <= boundary)
            candidate = replace(batch, source_rows=rows, upto_msg_id=boundary)
            # Entity lower bound prevents asking for a paragraph that cannot retain
            # all identities. No paid retry/split after a failed model response.
            if (summary_input_tokens(candidate) + SUMMARY_OUTPUT_TOKENS + budget.safety > budget.window
                    or sum(map(len, required_entities(candidate))) > 200):
                break
            chosen = candidate
        if chosen is None:
            raise ValueError('Summary window cannot hold one complete raw turn.')
        if chosen.upto_msg_id == batch.upto_msg_id:
            return batch
        # Repository creates the authoritative hash and CAS expectations in its own
        # short read session; a concurrent change causes skip, not a new target.
        actual = await self.repository.load_batch(batch.conversation_id, target_upto=chosen.upto_msg_id)
        if (actual is None or actual.source_rows != chosen.source_rows
                or actual.expected_summary_upto != batch.expected_summary_upto or actual.expected_seq != batch.expected_seq):
            return None
        return actual

    async def _run(self, request):
        started, target, batch, stage = time.time(), None, None, 'load'
        try:
            anchors, _ = await self.repository.load(request.conversation_id)
            target = anchors.layer1_from
            if target is None or target <= (anchors.summary_upto or 0):
                self._event('summary_skipped', request, target=target, started=started, reason='covered')
                return
            expected_s, expected_seq = anchors.summary_upto, None
            while True:
                whole = await self.repository.load_batch(request.conversation_id, target_upto=target)
                if (whole is None or whole.expected_summary_upto != expected_s
                        or expected_seq is not None and whole.expected_seq != expected_seq):
                    self._event('summary_skipped', request, batch=batch, target=target, started=started, reason='conflict')
                    return
                if expected_seq is None:
                    self._event('summary_trigger', request, batch=whole, target=target, started=started)
                batch = whole  # Preserve the failed source range even if no prefix can fit.
                stage = 'capacity'
                batch = await self._prefix(whole, request.budget)
                if batch is None:
                    self._event('summary_skipped', request, target=target, started=started, reason='conflict')
                    return
                self._event('summary_start', request, batch=batch, target=target, started=started)
                stage = 'generation'
                content = await self.generator.summarize(batch)
                stage = 'validation'
                content = validate_summary(content, batch)
                stage = 'commit'
                segment = await self.repository.append_segment(batch, content, summary_budget=request.budget.summary)
                if segment is None:
                    self._event('summary_skipped', request, batch=batch, target=target, started=started, reason='conflict')
                    return
                self._event('summary_done', request, batch=batch, target=target, started=started, reason='committed')
                if segment.upto_msg_id == target:
                    return
                expected_s, expected_seq = segment.upto_msg_id, segment.seq
                stage = 'load'
        except asyncio.CancelledError:
            self._event('summary_failed', request, batch=batch, target=target, started=started, reason='cancelled')
            raise
        except Exception as exc:
            self._event('summary_failed', request, batch=batch, target=target, started=started,
                        reason='timeout' if isinstance(exc, TimeoutError) else f'{stage}_error')
        finally:
            self._running.pop(request.conversation_id, None)
            self._conversations.discard(request.conversation_id)
            if self._waiting and not self._closed:
                self._launch(self._waiting.popleft())

    async def aclose(self) -> None:
        self._closed = True
        while self._waiting:
            request = self._waiting.popleft()
            self._conversations.discard(request.conversation_id)
            self._event('summary_skipped', request, reason='closed')
        running = tuple(self._running.values())
        if not running:
            return
        _, pending = await asyncio.wait(running, timeout=5)
        for task in pending:
            task.cancel()
        await asyncio.gather(*running, return_exceptions=True)
