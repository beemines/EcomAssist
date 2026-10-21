"""Same-origin JSON feedback accepts locators only, never client evidence."""
from uuid import UUID
from fastapi import APIRouter, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import field_validator

from app.api.chat_actions import _guard_write
from app.core.errors import ServiceError
from app.flywheel.types import StrictModel, database_id


class FeedbackRequest(StrictModel):
    assistant_message_id: str
    checkpoint_id: str | None = None

    @field_validator('assistant_message_id')
    @classmethod
    def identifier(cls, value):
        return database_id(value)

    @field_validator('checkpoint_id')
    @classmethod
    def checkpoint(cls, value):
        if value is not None and str(UUID(value)) != value:
            raise ValueError('Invalid checkpoint identity')
        return value


class FeedbackRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()
        async def handle(request):
            try:
                _guard_write(request)
                return await original(request)
            except RequestValidationError:
                code, status = 'invalid_request', 422
            except ServiceError as exc:
                allowed = {'invalid_request': 422, 'invalid_conversation_id': 422,
                    'conversation_not_found': 404, 'feedback_conflict': 409,
                    'origin_forbidden': 403, 'json_required': 415, 'service_unavailable': 503}
                code = exc.code if exc.code in allowed else 'service_unavailable'
                status = allowed[code]
            except Exception:
                code, status = 'service_unavailable', 503
            return JSONResponse(status_code=status, content={'code': code,
                'message': {'feedback_conflict': '原轮完成记录无法核验，暂不能提交反馈。',
                    'service_unavailable': '反馈暂未保存，请稍后重试。'}.get(code, '反馈请求无法处理。')})
        return handle


router = APIRouter(route_class=FeedbackRoute)


@router.post('/api/conversations/{conversation_id}/feedback')
async def submit_feedback(conversation_id: str, payload: FeedbackRequest, request: Request):
    service = getattr(request.app.state, 'feedback_service', None)
    if service is None:
        raise ServiceError('service_unavailable', '', 503)
    receipt = await service.submit(conversation_id, user_id='demo-user', **payload.model_dump())
    return receipt.model_dump()
