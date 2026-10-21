"""Frozen pipeline control; clients cannot choose models, budgets or file paths."""
from fastapi import APIRouter, Request, Query
from pydantic import field_validator
from app.api.review_queue import ReviewRoute
from app.flywheel.types import StrictModel
from app.eval_pipeline.types import EvalScope, run_key
from app.core.errors import ServiceError


class StartRequest(StrictModel):
    run_key: str
    scope: EvalScope
    _key=field_validator('run_key')(run_key)


router=APIRouter(route_class=ReviewRoute)


def manager(request):
    value=getattr(request.app.state,'eval_pipeline_manager',None)
    if value is None: raise ServiceError('service_unavailable','评估未启用。',503)
    return value


def checked_key(value):
    try: return run_key(value)
    except ValueError: raise ServiceError('invalid_request','',422) from None


@router.post('/api/eval-runs',status_code=202)
async def start(payload: StartRequest,request: Request):
    value=await manager(request).start(run_key=payload.run_key,scope=payload.scope,triggered_by='手动')
    return value.model_dump(mode='json')


@router.get('/api/eval-runs')
async def list_runs(request: Request,offset:int=Query(0,ge=0),limit:int=Query(20,ge=1,le=100),scope:EvalScope|None=None):
    return await manager(request).list_runs(offset=offset,limit=limit,scope=scope)


@router.get('/api/eval-runs/{key}')
async def get_run(key:str,request: Request):
    return (await manager(request).get_run(checked_key(key))).model_dump(mode='json')


@router.get('/api/eval-runs/{key}/report')
async def report(key:str,request: Request):
    return await manager(request).get_report(checked_key(key))
