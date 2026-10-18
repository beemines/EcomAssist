"""One workflow-owned extra generation; never retries tools, streams or commits."""
import asyncio
import json
import logging
import time

from app.core.errors import ServiceError
from app.agent.controls import ToolProtocolError, ToolProtocolReason
from openai import ContentFilterFinishReasonError, LengthFinishReasonError

logger = logging.getLogger(__name__)


def _permanent_failure(error):
    """Only inspect typed markers, never provider messages/response bodies."""
    pending, seen = [error], set()
    while pending:
        item = pending.pop()
        if id(item) in seen:
            continue
        seen.add(id(item))
        status = getattr(item, 'status_code', None)
        # asyncio.timeout uses an internal CancelledError as its TimeoutError cause.
        # Caller cancellation is checked on the active task and never caught as ServiceError.
        if (isinstance(item, (ContentFilterFinishReasonError, LengthFinishReasonError))
                or type(status) is int and 400 <= status < 500 and status not in (408, 409, 429)):
            return True
        pending.extend(child for child in (item.__cause__, item.__context__) if child is not None)
        if isinstance(item, BaseExceptionGroup):
            pending.extend(item.exceptions)
    return False


def recover_generation(context, state, runtime, stage, error, usage, *, attempted, reserve):
    """Claim only after charged generation and fresh deadline/budget preflight."""
    task = asyncio.current_task()
    if (not attempted or not isinstance(error, ServiceError)
            or error.code not in ('invalid_structured_output', 'upstream_timeout', 'upstream_error')
            or getattr(error, 'finish_reason', None) in ('length', 'content_filter')
            or isinstance(error, ToolProtocolError) and error.reason == ToolProtocolReason.NAME
            or _permanent_failure(error)
            or context.model_recovery_used or context.deadline <= time.monotonic()
            or task is not None and task.cancelling()):
        return False
    try:
        reserve()
    except ServiceError:
        return False
    context.model_recovery_used = True
    fields = {'conversation_id': state['conversation_id'], 'user_message_id': state['user_message_id'],
              'stage': stage, 'attempt': 1, 'max_attempts': 1, 'code': error.code, 'usage': dict(usage)}
    logger.warning(json.dumps({'event': 'model_recovery', **fields}, ensure_ascii=True,
                              separators=(',', ':'), allow_nan=False))
    if context.context_logger is not None:
        try:
            context.context_logger.event('model_recovery', fields)
        except Exception:
            pass
    # Existing status DTO and UI accept checking; details stay in bounded metadata.
    runtime.stream_writer({'event': 'status', 'data': {'phase': 'checking', 'origin': 'workflow'}})
    return True
