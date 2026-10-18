"""Hot-registration example; enable module and its local policy rule only."""
from langchain_core.tools import StructuredTool
from app.tools.catalog_types import ToolDefinition, ToolRegistration


def register(catalog):
    definition = ToolDefinition('query_demo_dispatch_site',
        '查询订单模拟发货站点；仅用于演示工具热注册。',
        {'type': 'object', 'properties': {'order_id': {'type': 'string', 'minLength': 1, 'maxLength': 64}},
         'required': ['order_id'], 'additionalProperties': False}, order_id_arg='order_id')
    async def query_demo_dispatch_site(order_id):
        return {'order_id': order_id, 'dispatch_site': '成都演示发货站', 'mock': True}
    catalog.register(ToolRegistration(definition, lambda context: StructuredTool.from_function(
        coroutine=query_demo_dispatch_site, name=definition.name, description=definition.description,
        args_schema=definition.input_schema)))
