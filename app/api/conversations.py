from fastapi import APIRouter, Request

from app.schemas.conversation import ConversationRequest, ConversationResponse
from app.core.errors import ServiceError


router = APIRouter()


# 创建用户会话并返回字符串主键，将数据库故障转换为服务错误。
@router.post("/api/conversations", response_model=ConversationResponse)
async def create_conversation(payload: ConversationRequest, request: Request) -> ConversationResponse:
    try:
        identifier = await request.app.state.repository.create(payload.user_id)
        return ConversationResponse(conversation_id=identifier)
    except ServiceError:
        raise
    except Exception:
        raise ServiceError("database_error", "会话暂时无法创建，请稍后重试。", 503) from None
