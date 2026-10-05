from fastapi import APIRouter, Request

from app.api.streaming import ManagedChatResponse
from app.schemas.chat import ChatRequest


router = APIRouter()


@router.post("/api/chat")
async def chat(payload: ChatRequest, request: Request) -> ManagedChatResponse:
    service = request.app.state.chat_service
    prepared = service.prepare(payload.session_id, payload.message)
    return ManagedChatResponse(service, prepared)
