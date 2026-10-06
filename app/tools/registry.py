from langchain_core.tools import BaseTool

from app.repositories.faq import FAQRepository
from app.repositories.tickets import TicketRepository
from app.tools.business import contextual_tools, query_logistics, query_order, query_product
from app.tools.types import ToolContext


def build_registry(faq: FAQRepository, tickets: TicketRepository, context: ToolContext) -> dict[str, BaseTool]:
    tools = [query_order, query_product, query_logistics, *contextual_tools(faq, tickets, context)]
    return {tool.name: tool for tool in tools}
