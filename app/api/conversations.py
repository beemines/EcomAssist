# 会话创建与消息查询接口，将数据库中的会话身份和流水提供给调用方。
from fastapi import APIRouter, Query, Request

from app.schemas.conversation import ConversationPage, ConversationRequest, ConversationResponse, MessagePage
from app.core.errors import ServiceError


router = APIRouter()


@router.get('/api/conversations', response_model=ConversationPage)
async def list_conversations(request: Request, before_id: str | None = None,
                             limit: int = Query(default=50, ge=1, le=200)) -> ConversationPage:
    """演示当前身份来自服务端；浏览器不能用user_id枚举别人的会话。"""
    try:
        return await request.app.state.repository.list_for_user('demo-user', before_id=before_id, limit=limit)
    except ServiceError:
        raise
    except Exception:
        raise ServiceError('database_error', '会话暂时无法读取，请稍后重试。', 503) from None


@router.get('/api/conversations/{conversation_id}/messages', response_model=MessagePage)
async def read_messages(conversation_id: str, request: Request, after_id: str | None = None,
                        upto_id: str | None = None, limit: int = Query(default=200, ge=1, le=200)) -> MessagePage:
    """原文与原完成根元数据只读回载，不进入聊天或动作执行路径。"""
    try:
        page = await request.app.state.repository.read_page(conversation_id, user_id='demo-user',
            after_id=after_id, upto_id=upto_id, limit=limit)
        return await request.app.state.history_reader.decorate(page)
    except ServiceError:
        raise
    except Exception:
        raise ServiceError('database_error', '会话暂时无法读取，请稍后重试。', 503) from None


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
