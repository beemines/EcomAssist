"""Local Langfuse statistics, without exposing its project credentials."""
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

from app.observability.intent_usage import IntentUsageReader
from app.api.review_queue import ReviewRoute,EmptyRequest
from app.core.errors import ServiceError

router = APIRouter(prefix='/api/observability', tags=['observability'],route_class=ReviewRoute)


@router.get('/intent-usage')
async def intent_usage(request: Request, from_time: datetime | None = None,
                       to_time: datetime | None = None,refresh:bool=False):
    end = to_time or datetime.now(timezone.utc).replace(second=0, microsecond=0)
    start = from_time or end - timedelta(days=7)
    reader = getattr(request.app.state, 'intent_usage_reader', None) or IntentUsageReader(None)
    try:
        return await reader.read(start, end,**({'force_refresh':True} if refresh else {}))
    except ValueError:
        raise ServiceError('invalid_request','Use timezone-aware dates and a positive range no longer than 90 days',422) from None


def report_root(request):
    return getattr(request.app.state,'confidence_report_root',Path(__file__).resolve().parents[2])


@router.get('/confidence')
async def confidence_report(request:Request):
    from app.quality.confidence_report import read_confidence_report
    return await asyncio.to_thread(read_confidence_report,report_root(request),
        getattr(request.app.state,'confidence_rule',None))


@router.post('/confidence/recompute')
async def recompute_confidence(payload:EmptyRequest,request:Request):
    from app.quality.confidence_report import recompute_reference_report
    lock=getattr(request.app.state,'confidence_report_lock',None)
    if lock is None:
        lock=request.app.state.confidence_report_lock=asyncio.Lock()
    if lock.locked(): raise ServiceError('eval_busy','校准报告正在重算。',409)
    async with lock:
        await asyncio.to_thread(recompute_reference_report,report_root(request))
        return await confidence_report(request)
