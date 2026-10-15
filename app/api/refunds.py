"""独立于Agent工具的退款显式提交HTTP入口。"""
from fastapi import APIRouter, Request
from pydantic import ValidationError

from app.api.chat_actions import ActionRoute
from app.core.errors import ServiceError
from app.refunds.types import RefundActionRequest, RefundOfferLocator, RefundReceipt


router = APIRouter(route_class=ActionRoute)


@router.get('/api/conversations/{conversation_id}/refund-offer')
async def refund_offer(conversation_id: str, request: Request) -> dict:
    """只读重验浏览器保存的两个原定位，不从文本或DOM恢复申请权。"""
    try:
        pairs = request.query_params.multi_items()
        if len(pairs) != len(dict(pairs)):
            raise ValueError('duplicate query locator')
        locator = RefundOfferLocator.model_validate(dict(pairs))
    except (ValidationError, ValueError):
        raise ServiceError('invalid_request', '', 422) from None
    service = request.app.state.refund_action_service
    if service is None:
        raise ServiceError('service_unavailable', '', 503)
    try:
        return await service.offer(conversation_id, locator)
    except ServiceError:
        raise
    except Exception:
        raise ServiceError('service_unavailable', '', 503) from None


@router.post('/api/conversations/{conversation_id}/actions/refund', response_model=RefundReceipt)
async def submit_refund(conversation_id: str, payload: RefundActionRequest, request: Request) -> RefundReceipt:
    """严格四字段解析后交给原根权限服务，只有SQL提交成功才返回待审。"""
    service = request.app.state.refund_action_service
    if service is None:
        raise ServiceError('service_unavailable', '', 503)
    try:
        return await service.submit(conversation_id, payload)
    except ServiceError:
        raise
    except Exception:
        raise ServiceError('service_unavailable', '', 503) from None
