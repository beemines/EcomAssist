from fastapi import APIRouter, Request

from app.api.streaming import ManagedChatResponse
from app.schemas.chat import ChatRequest
from app.core.errors import ServiceError


router = APIRouter()


@router.post("/api/chat")
async def chat(payload: ChatRequest, request: Request) -> ManagedChatResponse:
    service = request.app.state.chat_service
    try:
        prepared = await service.prepare(payload.conversation_id, payload.message)
    except ServiceError:
        raise
    except Exception:
        raise ServiceError("database_error", "会话暂时无法读取，请稍后重试。", 503) from None
    return ManagedChatResponse(service, prepared)
