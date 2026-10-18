from langchain_core.tools import StructuredTool
from app.tools.catalog_types import ToolDefinition, ToolRegistration
from app.tools.policies import PolicySnapshot


def make_registration(name, *, source='builtin', operation='read', handler=None):
    async def default_handler(**kwargs):
        return {'answer': '中文', **kwargs}
    definition = ToolDefinition(name=name, description='测试读取能力',
        input_schema={'type': 'object', 'properties': {}, 'additionalProperties': False},
        source=source, operation=operation)
    return ToolRegistration(definition, lambda context: StructuredTool.from_function(
        coroutine=handler or default_handler, name=name, description=definition.description,
        args_schema=definition.input_schema))


def allow_policy(*registrations):
    return PolicySnapshot.from_dict({'tools': [dict(source=r.definition.source,
        name=r.definition.name, operation=r.definition.operation) for r in registrations]})
