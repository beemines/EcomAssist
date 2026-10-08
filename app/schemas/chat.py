from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.repositories.conversations import _conversation_id
from app.core.errors import ServiceError


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    conversation_id: str = Field(strict=True, min_length=1, max_length=20)
    message: str = Field(strict=True, min_length=1, max_length=20000)

    # 沿用仓储身份规则校验会话主键，将业务错误转换为 Schema 校验错误。
    @field_validator("conversation_id")
    @classmethod
    def canonical_identity(cls, value: str) -> str:
        try:
            _conversation_id(value)
        except ServiceError:
            raise ValueError("must be a canonical positive decimal identity") from None
        return value

    # 拒绝只有空白的聊天消息，保留合法用户原文。
    @field_validator("message")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value
