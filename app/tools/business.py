# 五个客服业务工具：订单、商品、物流使用模拟数据，FAQ 与工单访问仓储。
import random
from collections.abc import Awaitable, Callable
from typing import Annotated

from langchain_core.tools import BaseTool, InjectedToolCallId, tool

from app.repositories.faq import FAQRepository
from app.orders.types import OrderProvider
from app.repositories.tickets import TicketRepository
from app.tools.schemas import FAQArgs, OrderArgs, ProductArgs, TicketArgs
from app.tools.types import ToolContext


# 按给定订单号生成带 mock 标记的随机订单演示结果。
@tool(args_schema=OrderArgs)
async def query_order(order_id: str) -> dict:
    """查询订单演示信息；结果是随机模拟数据。"""
    return {"order_id": order_id, "mock": True, "status": random.choice(["待付款", "待发货", "已完成"]), "amount": random.randint(1000, 50000) / 100}


# 按给定商品号生成带 mock 标记的随机商品演示结果。
@tool(args_schema=ProductArgs)
async def query_product(product_id: str) -> dict:
    """查询商品演示信息；结果是随机模拟数据。"""
    return {"product_id": product_id, "mock": True, "name": random.choice(["便携水杯", "旅行背包", "桌面台灯"]), "price": random.randint(1000, 30000) / 100, "stock": random.randint(0, 100)}


# 按给定订单号生成带 mock 标记的随机物流演示结果。
@tool(args_schema=OrderArgs)
async def query_logistics(order_id: str) -> dict:
    """查询订单物流演示进度；结果是随机模拟数据。"""
    return {"order_id": order_id, "mock": True, "status": random.choice(["已揽收", "运输中", "派送中"]), "tracking_no": "MOCK" + str(random.randint(10000000, 99999999)), "estimated_delivery_days": random.randint(1, 5)}


# 为原订单与物流工具绑定 SQL 会话身份，保持模型只填写订单号。
def scoped_order_tools(provider: OrderProvider, owner_resolver: Callable[[str], Awaitable[str]], context: ToolContext) -> list[BaseTool]:
    # 返回统一业务错误，不为未知订单或其他身份编造订单事实。
    def not_found() -> dict:
        return {"error": {"code": "not_found", "message": "未找到当前演示身份的订单。"}}

    # 每次读取均从可信会话解析身份，与列表使用同一订单提供器。
    @tool(args_schema=OrderArgs)
    async def query_order(order_id: str) -> dict:
        """查询当前演示身份的固定订单事实，结果明确标记为 mock。"""
        order = await provider.get_order(user_id=await owner_resolver(context.conversation_id), order_id=order_id)
        return order.model_dump(mode="json") if order is not None else not_found()

    # 物流快照复用订单事实，仅为已发货演示订单提供稳定跟踪编号。
    @tool(args_schema=OrderArgs)
    async def query_logistics(order_id: str) -> dict:
        """查询当前演示订单的固定 mock 物流信息。"""
        order = await provider.get_order(user_id=await owner_resolver(context.conversation_id), order_id=order_id)
        if order is None:
            return not_found()
        return {
            **order.model_dump(mode="json"),
            "logistics_status": "已签收" if order.signed_at is not None else "未发货",
            "tracking_no": "MOCK" + order.order_id if order.signed_at is not None else None,
            "estimated_delivery_days": None,
        }

    return [query_order, query_logistics]


# 为当前请求创建 FAQ 和工单工具闭包，绑定可信会话与用户消息身份。
def contextual_tools(faq: FAQRepository, tickets: TicketRepository, context: ToolContext) -> list[BaseTool]:
    # 每个请求独立闭包，模型无法指定会话或消息主键。
    # 仅使用当前问题的连续原文片段检索 FAQ，返回命中状态和结果。
    @tool(args_schema=FAQArgs)
    async def query_faq(keyword: str) -> dict:
        """使用当前问题的连续原文片段申请 FAQ 混合检索，最多十条权威知识。"""
        if keyword not in context.user_question:
            return {"error": {"code": "invalid_keyword", "message": "关键词必须是当前用户问题中的连续原文片段。"}}
        return await faq.retrieve(keyword, raw_question=context.user_question, category=context.category)

    # 调用标识由执行器注入，模型不能指定会话身份或伪造幂等键。
    # 使用闭包身份和运行时注入的调用标识创建幂等人工工单。
    @tool(args_schema=TicketArgs)
    async def create_ticket(description: str, ticket_type: str, tool_call_id: Annotated[str, InjectedToolCallId]) -> dict:
        """为当前用户问题创建人工工单；仅支持售后、投诉、咨询。"""
        return await tickets.create(conversation_id=context.conversation_id, user_message_id=context.user_message_id, tool_call_id=tool_call_id, description=description, ticket_type=ticket_type)

    return [query_faq, create_ticket]
