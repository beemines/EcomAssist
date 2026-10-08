# 按本轮可信上下文组装五个工具，形成供模型绑定和执行器查找的注册表。
from langchain_core.tools import BaseTool

from app.repositories.faq import FAQRepository
from app.repositories.tickets import TicketRepository
from app.tools.business import contextual_tools, query_logistics, query_order, query_product
from app.tools.types import ToolContext


# 合并演示工具和当前请求的上下文工具，按工具名称建立查找表。
def build_registry(faq: FAQRepository, tickets: TicketRepository, context: ToolContext) -> dict[str, BaseTool]:
    tools = [query_order, query_product, query_logistics, *contextual_tools(faq, tickets, context)]
    return {tool.name: tool for tool in tools}
