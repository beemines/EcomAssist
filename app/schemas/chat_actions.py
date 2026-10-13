"""浏览器确认只提供已完成回复和官方根检查点的定位字段。"""
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.errors import ServiceError
from app.repositories.conversations import _conversation_id


class TicketActionRequest(BaseModel):
    """禁止客户端提供工单业务字段及工具调用身份。"""
    model_config = ConfigDict(extra='forbid', strict=True)
    assistant_message_id: str = Field(min_length=1, max_length=20)
    checkpoint_id: str = Field(min_length=1, max_length=128)

    @field_validator('assistant_message_id')
    @classmethod
    def valid_message_id(cls, value: str) -> str:
        """复用规范无符号 BIGINT 字符串规则，拒绝数字与前导零。"""
        try:
            _conversation_id(value)
        except ServiceError:
            raise ValueError('invalid assistant identity') from None
        return value

    @field_validator('checkpoint_id')
    @classmethod
    def valid_checkpoint_id(cls, value: str) -> str:
        """只接受官方 UUID 的规范表示，禁止其他命名空间定位文本。"""
        if str(UUID(value)) != value:
            raise ValueError('invalid checkpoint identity')
        return value
