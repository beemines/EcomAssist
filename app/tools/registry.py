# 按本轮可信上下文组装五个工具，形成供模型绑定和执行器查找的注册表。
from collections.abc import Awaitable, Callable

from langchain_core.tools import BaseTool

from app.orders.types import OrderProvider
from app.repositories.faq import FAQRepository
from app.repositories.tickets import TicketRepository
from app.tools.business import contextual_tools, query_logistics, query_order, query_product, scoped_order_tools
from app.tools.types import ToolContext


# 合并演示工具和当前请求的上下文工具，按工具名称建立查找表。
def build_registry(faq: FAQRepository, tickets: TicketRepository, context: ToolContext, *, order_provider: OrderProvider | None = None, owner_resolver: Callable[[str], Awaitable[str]] | None = None) -> dict[str, BaseTool]:
    if (order_provider is None) != (owner_resolver is None):
        raise ValueError("order_provider and owner_resolver must be provided together.")
    orders = [query_order, query_logistics] if order_provider is None else scoped_order_tools(order_provider, owner_resolver, context)
    tools = [*orders, query_product, *contextual_tools(faq, tickets, context)]
    return {tool.name: tool for tool in tools}


def build_catalog(faq, tickets, *, order_provider=None, owner_resolver=None):
    """Register context-bound factories once; MCP owns logistics in the new catalog."""
    from app.tools.catalog import ToolCatalog
    from app.tools.catalog_types import ToolDefinition, ToolRegistration
    catalog = ToolCatalog()
    def registry(context):
        return build_registry(faq, tickets, context, order_provider=order_provider,
                              owner_resolver=owner_resolver)
    for name, tool in registry(ToolContext('0', 0, '')).items():
        if name == 'query_logistics':
            continue
        schema = tool.tool_call_schema
        schema = schema if isinstance(schema, dict) else schema.model_json_schema()
        definition = ToolDefinition(name, tool.description, schema,
            operation='write' if name == 'create_ticket' else 'read')
        catalog.register(ToolRegistration(definition,
            lambda context, key=name: registry(context)[key]))
    return catalog
