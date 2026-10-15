"""只读待选和同源JSON选单恢复HTTP。"""
from fastapi import APIRouter, Request

from app.api.chat_actions import ActionRoute
from app.api.streaming import ManagedChatResponse
from app.core.errors import ServiceError
from app.schemas.order_actions import OrderSelectionRequest


router = APIRouter(route_class=ActionRoute)


@router.get('/api/conversations/{conversation_id}/pending-order')
async def pending_order(conversation_id: str, request: Request):
    """读取当前暂停快照，未知服务不泄露内部异常。"""
    service = request.app.state.order_action_service
    if service is None:
        raise ServiceError('service_unavailable', '', 503)
    return await service.pending(conversation_id)


@router.post('/api/conversations/{conversation_id}/actions/select-order')
async def select_order(conversation_id: str, payload: OrderSelectionRequest, request: Request):
    """HTTP预检成功才返回托管SSE，流内故障继续用error终止。"""
    service = request.app.state.order_action_service
    if service is None:
        raise ServiceError('service_unavailable', '', 503)
    prepared = await service.select(conversation_id, payload)
    return ManagedChatResponse(service.service, prepared)
