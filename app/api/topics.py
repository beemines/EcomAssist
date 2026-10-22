"""Local distribution reads and explicit training-data review; never classify or train."""
import asyncio
from datetime import datetime
from typing import Literal
from fastapi import APIRouter,Request,Query
from fastapi.responses import JSONResponse
from app.api.review_queue import ReviewRoute
from app.core.errors import ServiceError
from app.topics.statistics import TopicFilters
from app.topics.taxonomy import default_taxonomy
from app.topics.review_submission import ReviewSubmission, ReviewSubmissionConflict

router=APIRouter(prefix='/api/topics',tags=['topics'],route_class=ReviewRoute)


def _filters(source,since,until):
    try:
        return TopicFilters(source=source,since=since,until=until)
    except ValueError:
        raise ServiceError('invalid_request','',422) from None


def _service(request):
    result=getattr(request.app.state,'topic_service',None)
    if result is None: raise ServiceError('service_unavailable','',503)
    return result


@router.get('/summary')
async def summary(request:Request,source:Literal['retrieval_low_conf','self_check','user_feedback']|None=None,
                  since:datetime|None=None,until:datetime|None=None):
    return await _service(request).summary(_filters(source,since,until))


@router.get('/questions')
async def questions(request:Request,label:str,source:Literal['retrieval_low_conf','self_check','user_feedback']|None=None,
                    since:datetime|None=None,until:datetime|None=None,offset:int=Query(0,ge=0),limit:int=Query(20,ge=1,le=100)):
    if label not in default_taxonomy().ordered_names:
        raise ServiceError('invalid_request','',422)
    return await _service(request).questions(label,_filters(source,since,until),offset=offset,limit=limit)


@router.post('/pilot-review')
async def submit_pilot(payload: ReviewSubmission, request: Request):
    service = getattr(request.app.state, 'topic_review_service', None)
    if service is None:
        raise ServiceError('service_unavailable', '', 503)
    try:
        result = await asyncio.to_thread(service.save, payload)
    except ReviewSubmissionConflict:
        raise ServiceError('review_conflict', '', 409) from None
    except ValueError:
        raise ServiceError('invalid_request', '', 422) from None
    return JSONResponse(result, headers={'Cache-Control': 'no-store'})
