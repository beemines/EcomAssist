from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, field_validator
from app.repositories.conversations import _conversation_id
from app.core.errors import ServiceError


class TicketConfirmationRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    turn_id: str
    confirmation_id: str
    checkpoint_id: str
    decision: Literal['confirm', 'cancel']

    @field_validator('turn_id')
    @classmethod
    def sql_identity(cls, value):
        try:
            _conversation_id(value)
        except ServiceError:
            raise ValueError('Invalid SQL identity') from None
        return value

    @field_validator('confirmation_id', 'checkpoint_id')
    @classmethod
    def uuid_identity(cls, value):
        if str(UUID(value)) != value:
            raise ValueError('Invalid UUID identity')
        return value
