from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.repositories.conversations import _conversation_id
from app.core.errors import ServiceError


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    conversation_id: str = Field(strict=True, min_length=1, max_length=20)
    message: str = Field(strict=True, min_length=1, max_length=20000)

    @field_validator("conversation_id")
    @classmethod
    def canonical_identity(cls, value: str) -> str:
        try:
            _conversation_id(value)
        except ServiceError:
            raise ValueError("must be a canonical positive decimal identity") from None
        return value

    @field_validator("message")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value
