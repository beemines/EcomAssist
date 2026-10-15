"""同轮选单只接收不可替换的四个身份。"""
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from app.core.errors import ServiceError
from app.repositories.conversations import _conversation_id


class OrderSelectionRequest(BaseModel):
    """禁止客户端替换 owner、金额、分类或任意运行输入。"""
    model_config = ConfigDict(extra='forbid', strict=True)
    turn_id: str
    selection_id: str
    checkpoint_id: str
    order_id: str

    @field_validator('turn_id', 'order_id')
    @classmethod
    def decimal_identity(cls, value):
        """仅接受规范 SQL 十进制字符串。"""
        try:
            _conversation_id(value)
        except ServiceError:
            raise ValueError('invalid decimal identity') from None
        return value

    @field_validator('selection_id', 'checkpoint_id')
    @classmethod
    def uuid_identity(cls, value):
        """拒绝非规范 UUID，不能提供历史执行配置。"""
        if str(UUID(value)) != value:
            raise ValueError('invalid UUID identity')
        return value
