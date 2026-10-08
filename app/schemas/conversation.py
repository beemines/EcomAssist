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
