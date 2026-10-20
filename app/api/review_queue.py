"""Loopback administration uses explicit human text and same-origin JSON writes."""
from typing import Literal
from fastapi import APIRouter, Request, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import Field, field_validator
from urllib.parse import urlsplit
from app.api.chat_actions import _guard_write
from app.core.errors import ServiceError
from app.flywheel.types import StrictModel, ReviewChanged, database_id


class ApproveRequest(StrictModel):
    approved_answer: str = Field(min_length=1, max_length=16000)
    normalized_question: str | None = Field(default=None, min_length=1, max_length=512)
    @field_validator('approved_answer', 'normalized_question')
    @classmethod
    def nonblank(cls, value):
        if value is not None and not value.strip(): raise ValueError('Human text cannot be blank')
        return value


class RejectRequest(StrictModel):
    reason: str = Field(min_length=1, max_length=512)
    @field_validator('reason')
    @classmethod
    def nonblank(cls, value):
        if not value.strip(): raise ValueError('Reason cannot be blank')
        return value


class EmptyRequest(StrictModel): pass


class ReviewRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()
        async def handle(request):
            try:
                if request.method != 'GET': _guard_write(request)
                else: guard_read(request)
                return await original(request)
            except RequestValidationError: code, status = 'invalid_request', 422
            except ReviewChanged: code, status = 'review_not_found', 404
            except ServiceError as exc:
                allowed = {'review_conflict': 409, 'service_unavailable': 503,
                    'origin_forbidden': 403, 'json_required': 415, 'invalid_request': 422,
                    'eval_busy':409,'eval_conflict':409,'eval_not_found':404}
                code = exc.code if exc.code in allowed else 'service_unavailable'
                status = allowed[code]
            except Exception: code, status = 'service_unavailable', 503
            return JSONResponse(status_code=status, content={'code': code,
                'message': {'review_conflict': '审核或发布状态已改变，请刷新核对。',
                    'review_not_found': '待审记录不存在。', 'service_unavailable': '审核服务暂时不可用，请稍后重试。'
                    }.get(code, '审核请求无法处理。')})
        return handle


router = APIRouter(route_class=ReviewRoute)


def guard_read(request):
    hosts,origins=request.headers.getlist('host'),request.headers.getlist('origin')
    if len(hosts)!=1 or len(origins)>1: raise ServiceError('origin_forbidden','',403)
    origin=f'{request.url.scheme}://{hosts[0]}'
    try:
        parsed=urlsplit(origin)
        canonical=(parsed.scheme in ('http','https') and parsed.netloc==hosts[0] and
            parsed.username is None and parsed.password is None and not parsed.path and not parsed.query
            and not parsed.fragment and (parsed.port is None or 1<=parsed.port<=65535))
        local=parsed.hostname in ('localhost','127.0.0.1','::1')
    except ValueError: canonical=local=False
    allowed=getattr(request.app.state,'chat_action_allowed_origins',[])
    if (not canonical or not(local or origin in allowed) or (origins and origins[0]!=origin)
            or (not origins and not local)):
        raise ServiceError('origin_forbidden','',403)


def service(request):
    result = getattr(request.app.state, 'review_service', None)
    if result is None: raise ServiceError('service_unavailable', '', 503)
    return result


def identifier(value):
    try:
        return database_id(value)
    except ValueError:
        raise ServiceError('invalid_request', '', 422) from None


@router.get('/api/review-queue')
async def list_reviews(request: Request, status: Literal['待审','通过','驳回']='待审',
        offset: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100)):
    return await service(request).list_reviews(status=status, offset=offset, limit=limit)


@router.get('/api/review-queue/{review_id}')
async def details(review_id: str, request: Request, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100)):
    return await service(request).details(identifier(review_id), offset=offset, limit=limit)


@router.post('/api/review-queue/{review_id}/approve')
async def approve(review_id: str, payload: ApproveRequest, request: Request):
    return (await service(request).approve(identifier(review_id), **payload.model_dump())).model_dump()


@router.post('/api/review-queue/{review_id}/reject')
async def reject(review_id: str, payload: RejectRequest, request: Request):
    await service(request).reject(identifier(review_id), reason=payload.reason)
    return {'review_id': review_id, 'review_status': '驳回'}


@router.post('/api/review-queue/{review_id}/retry-publication')
async def retry(review_id: str, payload: EmptyRequest, request: Request):
    return (await service(request).retry_publication(identifier(review_id))).model_dump()


@router.post('/api/low-confidence-questions/{pool_id}/retry')
async def retry_processing(pool_id: str, payload: EmptyRequest, request: Request):
    from datetime import datetime, timezone
    repository = getattr(request.app.state, 'flywheel_repository', None)
    if repository is None: raise ServiceError('service_unavailable', '', 503)
    pool_id = identifier(pool_id)
    try:
        return await repository.manage_processing(pool_id, action='retry', now=datetime.now(timezone.utc))
    except ValueError:
        raise ServiceError('review_conflict', '当前原话任务不能重试，请核对状态和次数。', 409) from None
