"""Bounded model stages and a durable, lease-owned normalization attempt."""
import json
import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import httpx
from openai import APIConnectionError, APIStatusError
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from app.context.tokens import estimate_payload
from app.core.extraction import invalid_output, validate_structured_output
from app.core.errors import ServiceError
from app.core.provider_errors import is_bigmodel_quota_failure
from app.context.acceptance import AcceptanceLimitExceeded
from app.flywheel.types import NormalizedDraft, SemanticMatch, TaskError, ReviewChanged
from app.flywheel.prompts import NORMALIZE_SYSTEM, DEDUP_SYSTEM
from app.flywheel.leases import LeaseLost
from app.observability.tracing import begin_execution, ExecutionIdentity


class InputBudgetError(ValueError):
    pass


class PauseWorker(RuntimeError):
    pass


class DeferredScan(RuntimeError):
    pass


class PromptClient:
    def __init__(self, model, *, callbacks=None):
        self.normalizer = model.with_structured_output(NormalizedDraft, method='json_mode', include_raw=True)
        self.matcher = model.with_structured_output(SemanticMatch, method='json_mode', include_raw=True)
        if callbacks:
            self.normalizer = self.normalizer.with_config(callbacks=callbacks)
            self.matcher = self.matcher.with_config(callbacks=callbacks)

    @staticmethod
    def _messages(system, data):
        return [SystemMessage(system), HumanMessage(json.dumps(data, ensure_ascii=False, separators=(',', ':')))]

    @staticmethod
    async def _call(model, messages, schema):
        if estimate_payload(messages) > 12000:
            raise InputBudgetError('flywheel input budget exceeded')
        output = await model.ainvoke(messages)
        raw = output.get('raw') if isinstance(output, dict) else None
        if (not isinstance(raw, AIMessage) or raw.response_metadata.get('finish_reason') != 'stop'
                or raw.tool_calls or raw.invalid_tool_calls or raw.additional_kwargs.get('tool_calls')):
            raise invalid_output()
        return validate_structured_output(output, schema)

    async def normalize(self, row):
        data = {'raw_question': row['raw_question'], 'snapshot_status': row.get('snapshot_status'), 'evidence': []}
        snapshot = row.get('retrieved_chunks')
        if isinstance(snapshot, str):
            snapshot = json.loads(snapshot)
        messages = self._messages(NORMALIZE_SYSTEM, data)
        if estimate_payload(messages) > 12000:
            raise InputBudgetError('flywheel input budget exceeded')
        for chunk in snapshot.get('chunks', []) if isinstance(snapshot, dict) else []:
            trial = {**data, 'evidence': [*data['evidence'], chunk]}
            candidate = self._messages(NORMALIZE_SYSTEM, trial)
            if estimate_payload(candidate) <= 12000:
                data, messages = trial, candidate
        return await self._call(self.normalizer, messages, NormalizedDraft)

    @classmethod
    def dedup_messages(cls, draft, candidates):
        return cls._messages(DEDUP_SYSTEM, {'normalized_question': draft.normalized_question,
            'candidates': [candidate.model_dump() for candidate in candidates]})

    async def deduplicate(self, draft, candidates):
        if not 1 <= len(candidates) <= 20:
            raise ValueError('Candidate batch must be in 1..20')
        result = await self._call(self.matcher, self.dedup_messages(draft, candidates), SemanticMatch)
        if result.matched_review_id is not None and result.matched_review_id not in {row.id for row in candidates}:
            raise invalid_output()
        return result


class FlywheelProcessor:
    def __init__(self, repository, prompts, *, clock=None, observability=None):
        self.repository, self.prompts = repository, prompts
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.observability = observability

    async def recover(self):
        async with self.repository.processing_lease() as lease:
            if lease is None:
                return False
            await self.repository.recover_processing(lease, self.clock())
            return True

    @staticmethod
    def _error(exc):
        pending, seen = [exc], set()
        while pending and len(seen) < 32:
            error = pending.pop()
            if id(error) in seen:
                continue
            seen.add(id(error))
            if isinstance(error, AcceptanceLimitExceeded):
                return 'acceptance_budget', False, True, '验收物理调用额度已用尽，后台已暂停。'
            pending.extend(item for item in (error.__cause__, error.__context__) if item is not None)
            if isinstance(error, BaseExceptionGroup):
                pending.extend(error.exceptions)
        if is_bigmodel_quota_failure(exc) or (isinstance(exc, APIStatusError)
                and exc.code in ('insufficient_quota', 'billing_hard_limit_reached')):
            return 'quota_exhausted', False, True, '模型可用额度不足，后台已暂停。'
        if isinstance(exc, APIStatusError) and exc.status_code in (401, 403):
            return 'authentication_failed', False, True, '模型鉴权失败，后台已暂停。'
        if isinstance(exc, DeferredScan):
            return 'scan_budget', True, False, '本次扫描达到调用上限，保留游标继续。'
        if isinstance(exc, ReviewChanged):
            return 'review_changed', True, False, '待审候选有变化，等待重新核验。'
        if (isinstance(exc, (TimeoutError, httpx.TransportError, APIConnectionError))
                or isinstance(exc, APIStatusError) and (exc.status_code >= 500 or exc.status_code == 429)
                or isinstance(exc, ServiceError) and exc.code in ('upstream_timeout', 'upstream_error')):
            return 'temporary_upstream', True, False, '模型暂时不可用，等待有界重试。'
        if isinstance(exc, ServiceError) and exc.code == 'invalid_structured_output':
            return 'invalid_output', False, False, '模型结构或归并目标无效，未改变待审队列。'
        if isinstance(exc, InputBudgetError):
            return 'input_budget', False, False, '原始问题或单条候选超过输入预算，需人工处理。'
        return 'processing_failed', False, False, '处理失败，请检查安全诊断后决定是否重试。'

    async def process(self, pool_id):
        async with self.repository.processing_lease() as lease:
            if lease is None:
                return None
            claimed = await self.repository.claim_processing(lease, pool_id, self.clock())
            if claimed is None:
                return None
            row, current = claimed
            identity = ExecutionIdentity(row['conversation_id'] or 'unbound',
                row['user_message_id'] or f'pool:{pool_id}', uuid4().hex, 'flywheel')
            with begin_execution(self.observability, identity) as trace:
                try:
                    async with asyncio.timeout(120):
                        result = await self._process(lease, pool_id, row, current)
                    trace.finish('success')
                    return result
                except (LeaseLost, asyncio.CancelledError):
                    raise
                except Exception as exc:
                    code, retry, pause, message = self._error(exc)
                    if isinstance(exc, ReviewChanged):
                        current.dedup_cursor = current.candidate_fingerprint = None
                    current.last_error = TaskError(code=code,
                        stage='normalize' if current.normalized_draft is None else 'dedup', message=message)
                    current.status = 'retry_wait' if retry and current.attempt_count < 3 else 'failed'
                    current.next_attempt_at = (self.clock() + timedelta(seconds=5 if current.attempt_count == 1 else 30)
                                               if current.status == 'retry_wait' else None)
                    await self.repository.save_processing(lease, pool_id, current)
                    trace.finish('deferred' if isinstance(exc, DeferredScan) else 'error')
                    if pause:
                        raise PauseWorker(code) from None
                    return None

    async def _process(self, lease, pool_id, row, current):
        calls = 0
        if current.normalized_draft is None:
            calls += 1
            draft = await self.prompts.normalize(row)
            if not isinstance(draft, NormalizedDraft):
                raise invalid_output()
            current.normalized_draft = draft
            await self.repository.save_processing(lease, pool_id, current)
        candidates, fingerprint = await self.repository.candidate_snapshot(lease)
        if current.candidate_fingerprint != fingerprint:
            current.candidate_fingerprint, current.dedup_cursor = fingerprint, None
            await self.repository.save_processing(lease, pool_id, current)
        remaining = [row for row in candidates if current.dedup_cursor is None or int(row.id) > int(current.dedup_cursor)]
        while remaining:
            if calls >= 6:
                raise DeferredScan()
            batch = []
            for candidate in remaining[:20]:
                trial = [*batch, candidate]
                if estimate_payload(PromptClient.dedup_messages(current.normalized_draft, trial)) > 12000:
                    break
                batch = trial
            if not batch:
                raise InputBudgetError('Candidate input budget exceeded')
            calls += 1
            match = await self.prompts.deduplicate(current.normalized_draft, batch)
            if (not isinstance(match, SemanticMatch) or match.matched_review_id is not None
                    and match.matched_review_id not in {row.id for row in batch}):
                raise invalid_output()
            if match.matched_review_id is not None:
                return await self.repository.finish_processing(lease, pool_id, current=current,
                    matched_review_id=match.matched_review_id, fingerprint=fingerprint)
            current.dedup_cursor = batch[-1].id
            await self.repository.save_processing(lease, pool_id, current)
            remaining = remaining[len(batch):]
        return await self.repository.finish_processing(lease, pool_id, current=current,
            matched_review_id=None, fingerprint=fingerprint)
