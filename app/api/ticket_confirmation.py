from fastapi import APIRouter, Request
from app.api.chat_actions import ActionRoute
from app.api.streaming import ManagedChatResponse
from app.schemas.ticket_confirmation import TicketConfirmationRequest
from app.core.errors import ServiceError

router = APIRouter(route_class=ActionRoute)


@router.get('/api/conversations/{conversation_id}/pending-ticket')
async def pending_ticket(conversation_id: str, request: Request):
    service = request.app.state.ticket_confirmation_service
    if service is None:
        raise ServiceError('service_unavailable', '', 503)
    return await service.pending(conversation_id)


@router.post('/api/conversations/{conversation_id}/actions/confirm-ticket')
async def confirm_ticket(conversation_id: str, payload: TicketConfirmationRequest, request: Request):
    service = request.app.state.ticket_confirmation_service
    if service is None:
        raise ServiceError('service_unavailable', '', 503)
    prepared = await service.confirm(conversation_id, payload)
    return ManagedChatResponse(service.service, prepared)
