"""Human decisions are atomic; publication reuses one immutable knowledge ID."""
import asyncio
import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import httpx
from app.flywheel.types import PublicationState, PublicationReceipt, TaskError, database_id
from app.flywheel.processing import FlywheelProcessor, PauseWorker
from app.flywheel.leases import LeaseLost
from app.flywheel.worker import FlywheelWorker
from app.observability.tracing import ExecutionIdentity, begin_execution, operation


def publication_state(row):
    value = row['publication']
    if value is None:
        raise ValueError('Publication metadata is unavailable')
    return PublicationState.model_validate_json(value if isinstance(value, str) else json.dumps(value))


def publication_receipt(row):
    return PublicationReceipt(review_id=str(row['id']),
        knowledge_chunk_id=str(row['knowledge_chunk_id']) if row['knowledge_chunk_id'] is not None else None,
        status=publication_state(row).status)


def _text(value, limit):
    if type(value) is not str or not value.strip() or len(value) > limit:
        raise ValueError('Nonblank bounded human text is required')
    return value


class ReviewService:
    def __init__(self, repository):
        self.repository = repository

    async def approve(self, review_id, *, approved_answer, normalized_question=None):
        return await self.repository.approve_review(database_id(review_id),
            approved_answer=_text(approved_answer, 16000),
            normalized_question=_text(normalized_question, 512) if normalized_question is not None else None)

    async def reject(self, review_id, *, reason):
        await self.repository.reject_review(database_id(review_id), reason=_text(reason, 512))

    async def retry_publication(self, review_id):
        return await self.repository.retry_publication(database_id(review_id))

    async def list_reviews(self, **kwargs):
        return await self.repository.list_reviews(**kwargs)

    async def details(self, review_id, **kwargs):
        return await self.repository.review_details(database_id(review_id), **kwargs)


class _PublicationPoller:
    def __init__(self, publisher):
        self.publisher, self.repository, self.clock = publisher, self, publisher.clock
    async def next_pending_id(self, now):
        return await self.publisher.repository.next_publication_id(now)
    async def recover(self):
        return await self.publisher.recover()
    async def process(self, identifier):
        return await self.publisher.publish(identifier)


class PublicationWorker:
    def __init__(self, repository, jobs, *, clock=None, observability=None):
        self.repository, self.jobs = repository, jobs
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.observability = observability
        self._worker = FlywheelWorker(_PublicationPoller(self))

    @property
    def tasks(self): return self._worker.tasks
    @property
    def paused_reason(self): return self._worker.paused_reason
    def start(self): self._worker.start()
    async def close(self, timeout_seconds=30): await self._worker.close(timeout_seconds)

    async def recover(self):
        async with self.repository.publication_lease() as lease:
            if lease is None:
                return False
            await self.repository.recover_publications(lease)
            return True

    @staticmethod
    def _error(exc):
        classified = FlywheelProcessor._error(exc)
        if classified[0] != 'processing_failed':
            return classified
        pending, seen = [exc], set()
        while pending and len(seen) < 32:
            current = pending.pop()
            if id(current) in seen: continue
            seen.add(id(current))
            pending.extend(value for value in (current.__cause__, current.__context__) if value is not None)
            if isinstance(current, httpx.HTTPStatusError):
                status = current.response.status_code
                if status in (401, 403):
                    return 'authentication_failed', False, True, '嵌入服务鉴权或权限失败，发布已暂停。'
                if status == 402:
                    return 'quota_exhausted', False, True, '上游拒绝计费请求，发布已暂停。'
                if status == 429 or status >= 500:
                    return 'temporary_upstream', True, False, '向量服务暂时不可用，等待有界重试。'
        return classified

    async def publish(self, review_id):
        review_id = database_id(review_id)
        async with self.repository.publication_lease() as lease:
            if lease is None:
                return publication_receipt(await self.repository.get_review(review_id))
            claimed = await self.repository.claim_publication(lease, review_id, self.clock())
            if claimed is None:
                return publication_receipt(await self.repository.get_review(review_id))
            row, state = claimed
            identity = ExecutionIdentity('review:' + review_id, 'publication', uuid4().hex, 'publication')
            with begin_execution(self.observability, identity) as trace:
                try:
                    async with asyncio.timeout(120):
                        with operation('knowledge.publish', input={'review_id': review_id,
                                'knowledge_chunk_id': row['knowledge_chunk_id']}, metadata={'observation_type': 'span'}):
                            await self.jobs.vectorize_ids([int(row['knowledge_chunk_id'])])
                    state.status, state.published_at = 'ready', self.clock()
                    state.next_attempt_at = state.last_error = None
                    await self.repository.save_publication(lease, review_id, state)
                    trace.finish('success')
                except (LeaseLost, asyncio.CancelledError):
                    raise
                except Exception as exc:
                    code, retry, pause, message = self._error(exc)
                    state.published_at = None
                    state.status = 'pending' if retry and state.attempt_count < 3 else 'failed'
                    state.next_attempt_at = (self.clock() + timedelta(seconds=5 if state.attempt_count == 1 else 30)
                        if state.status == 'pending' else None)
                    state.last_error = TaskError(code=code, stage='publication', message=message)
                    await self.repository.save_publication(lease, review_id, state)
                    trace.finish('error')
                    if pause:
                        raise PauseWorker(code) from None
            return PublicationReceipt(review_id=review_id, knowledge_chunk_id=row['knowledge_chunk_id'], status=state.status)
