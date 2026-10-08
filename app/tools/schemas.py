# 定义模型可填写的工具参数和服务注入字段，统一限制类型、长度与额外参数。
from typing import Annotated, Literal

from langchain_core.tools import InjectedToolCallId
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ToolArgs(BaseModel):
    # 严格类型且禁止额外字段，避免隐式转换或模型夹带未定义的业务参数。
    model_config = ConfigDict(extra="forbid", strict=True)

    # 统一拒绝全空白业务参数，保留合法标识和检索片段的原文。
    @field_validator("order_id", "product_id", "keyword", "description", check_fields=False)
    @classmethod
    def require_nonblank_business_text(cls, value: str) -> str:
        # 仅拒绝全空白；合法参数保留原文，避免改变标识符或 FAQ 连续片段。
        if not value.strip():
            raise ValueError("Business text must not be blank.")
        return value


# 查询订单和物流共享订单号参数，业务工具内部再生成各自返回数据。
class OrderArgs(ToolArgs):
    order_id: str = Field(min_length=1, max_length=64, description="用户提供的订单号")


# 商品查询按用户提供的商品标识进行，不由模型填入额外系统参数。
class ProductArgs(ToolArgs):
    product_id: str = Field(min_length=1, max_length=64, description="用户提供的商品号")


# 保留既有工具参数契约，即使内部升级向量检索，也继续接收用户问题原文片段。
class FAQArgs(ToolArgs):
    keyword: str = Field(min_length=1, max_length=128, description="当前用户问题中的连续原文片段，不改写或扩展同义词")


# 工单业务字段由模型提供，真实调用标识由执行器注入以支撑幂等创建。
class TicketArgs(ToolArgs):
    description: str = Field(min_length=1, max_length=2000, description="需要人工处理的问题描述")
    ticket_type: Literal["售后", "投诉", "咨询"] = Field(description="人工工单类型")
    # 隐藏注入字段不暴露给模型，由执行器使用真实调用标识补入。
    tool_call_id: Annotated[str, InjectedToolCallId]
