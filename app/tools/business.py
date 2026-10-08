# 五个客服业务工具：订单、商品、物流使用模拟数据，FAQ 与工单访问仓储。
import random
from typing import Annotated

from langchain_core.tools import BaseTool, InjectedToolCallId, tool

from app.repositories.faq import FAQRepository
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


# 为当前请求创建 FAQ 和工单工具闭包，绑定可信会话与用户消息身份。
def contextual_tools(faq: FAQRepository, tickets: TicketRepository, context: ToolContext) -> list[BaseTool]:
    # 每个请求独立闭包，模型无法指定会话或消息主键。
    # 仅使用当前问题的连续原文片段检索 FAQ，返回命中状态和结果。
    @tool(args_schema=FAQArgs)
    async def query_faq(keyword: str) -> dict:
        """使用当前问题的连续原文片段语义检索 FAQ，最多三条。"""
        if keyword not in context.user_question:
            return {"error": {"code": "invalid_keyword", "message": "关键词必须是当前用户问题中的连续原文片段。"}}
        matches = await faq.search(keyword, limit=3)
        return {"found": bool(matches), "matches": matches}

    # 调用标识由执行器注入，模型不能指定会话身份或伪造幂等键。
    # 使用闭包身份和运行时注入的调用标识创建幂等人工工单。
    @tool(args_schema=TicketArgs)
    async def create_ticket(description: str, ticket_type: str, tool_call_id: Annotated[str, InjectedToolCallId]) -> dict:
        """为当前用户问题创建人工工单并转人工；仅支持售后、投诉、咨询。"""
        return await tickets.create(conversation_id=context.conversation_id, user_message_id=context.user_message_id, tool_call_id=tool_call_id, description=description, ticket_type=ticket_type)

    return [query_faq, create_ticket]
