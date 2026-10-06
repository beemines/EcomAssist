from typing import Annotated, Literal

from langchain_core.tools import InjectedToolCallId
from pydantic import BaseModel, ConfigDict, Field


class ToolArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class OrderArgs(ToolArgs):
    order_id: str = Field(min_length=1, max_length=64, description="用户提供的订单号")


class ProductArgs(ToolArgs):
    product_id: str = Field(min_length=1, max_length=64, description="用户提供的商品号")


class FAQArgs(ToolArgs):
    keyword: str = Field(min_length=1, max_length=128, description="当前用户问题中的连续原文片段，不改写或扩展同义词")


class TicketArgs(ToolArgs):
    description: str = Field(min_length=1, max_length=2000, description="需要人工处理的问题描述")
    ticket_type: Literal["售后", "投诉", "咨询"] = Field(description="人工工单类型")
    tool_call_id: Annotated[str, InjectedToolCallId]
