"""Local Langfuse statistics, without exposing its project credentials."""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Request

from app.observability.intent_usage import IntentUsageReader
from app.api.review_queue import guard_read
from app.core.errors import ServiceError

router = APIRouter(prefix='/api/observability', tags=['observability'])


@router.get('/intent-usage')
async def intent_usage(request: Request, from_time: datetime | None = None,
                       to_time: datetime | None = None):
    try: guard_read(request)
    except ServiceError: raise HTTPException(403,'Local administration origin required') from None
    end = to_time or datetime.now(timezone.utc).replace(second=0, microsecond=0)
    start = from_time or end - timedelta(days=7)
    reader = getattr(request.app.state, 'intent_usage_reader', None) or IntentUsageReader(None)
    try:
        return await reader.read(start, end)
    except ValueError:
        raise HTTPException(422, 'Use timezone-aware dates and a positive range no longer than 90 days') from None
