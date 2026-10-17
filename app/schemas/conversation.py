# 会话创建与返回契约，限制用户标识并使用字符串传递会话编号。
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.repositories.conversations import _conversation_id


class ConversationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: str = Field(strict=True, min_length=1, max_length=64)

    # 拒绝只有空白的用户标识，保留合法标识的原始值。
    @field_validator("user_id")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value


class ConversationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    conversation_id: str = Field(strict=True, min_length=1, max_length=20)

    # 确认返回的会话主键符合规范正十进制身份格式。
    @field_validator("conversation_id")
    @classmethod
    def canonical_identity(cls, value: str) -> str:
        _conversation_id(value)
        return value


class ConversationItem(BaseModel):
    """侧栏按创建ID排序，摘要更新时间不决定位置。"""
    id: str
    status: str
    created_at: datetime
    updated_at: datetime
    first_question_preview: str
    has_summary: bool


class ConversationPage(BaseModel):
    items: list[ConversationItem]
    next_before_id: str | None = None


class HistoryMessage(BaseModel):
    """原始SQL字段；不把NULL工具申请正文转为空字符串。"""
    id: str
    role: str
    content: str | None
    tool_calls: list[dict[str, Any]] | None
    tool_call_id: str | None
    created_at: datetime


class MessagePage(BaseModel):
    # 仅供只读装饰器绑定可信SQL会话，不额外暴露在HTTP响应中。
    conversation_id: str = Field(exclude=True)
    messages: list[HistoryMessage]
    upto_id: str | None
    next_after_id: str | None = None
    turn_metadata: dict[str, dict[str, Any]] = Field(default_factory=dict)
