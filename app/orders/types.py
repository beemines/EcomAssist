# 同一业务时间下的不可变演示订单事实及异步读取协议。
from datetime import date
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OrderSnapshot(BaseModel):
    """订单事实只读快照；金额始终使用整数分。"""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    user_id: str
    order_id: str
    product_id: str
    product_name: str
    model: str
    category: str
    status: str
    amount_cents: int = Field(ge=0)
    currency: Literal["CNY"] = "CNY"
    signed_at: date | None
    as_of: date = date(2026, 10, 15)
    mock: Literal[True] = True
    fixture_version: str

    # 拒绝注入事实改变固定业务日期，保持卡片与后续政策判断的时间口径一致。
    @field_validator("as_of")
    @classmethod
    def require_fixed_business_date(cls, value: date) -> date:
        if value != date(2026, 10, 15):
            raise ValueError("Demo business date must be 2026-10-15.")
        return value

    # 只返回卡片展示所需信息，避免把演示身份暴露给客户端。
    def to_card(self) -> dict:
        return self.model_dump(mode="json", exclude={"user_id"})


class OrderProvider(Protocol):
    # 列出当前可信身份可读取的订单。
    async def list_orders(self, *, user_id: str) -> list[OrderSnapshot]: ...

    # 在当前可信身份范围查询订单，未知或其他身份订单返回空。
    async def get_order(self, *, user_id: str, order_id: str) -> OrderSnapshot | None: ...
