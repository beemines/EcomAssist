"""Bridge trusted forced Workflow reads into the same execution engine."""
from dataclasses import replace
from langchain_core.tools import StructuredTool
from app.tools.catalog_types import BoundCatalog, ToolRegistration
from app.tools.types import ToolContext, ExecutionContext


def execution_context(state, runtime):
    context = runtime.execution_context
    if context is None:
        context = ExecutionContext(state['conversation_id'], int(state['user_message_id']),
            state.get('intent') or '其他', state['raw_question'], deadline=runtime.deadline)
    return replace(context, intent=state.get('intent') or '其他',
        ticket_requested=bool(state.get('ticket_request')))


async def run_workflow_tool(call, registered: ToolRegistration, *, context, executor):
    catalog = BoundCatalog({registered.definition.name: registered},
        ToolContext(context.conversation_id, context.user_message_id, context.raw_question))
    return await executor.execute(call, catalog, context=context)


def forced_read_registration(definition, operation):
    async def invoke(**arguments):
        return await operation()
    return ToolRegistration(definition, lambda context: StructuredTool.from_function(
        coroutine=invoke, name=definition.name, description=definition.description,
        args_schema=definition.input_schema))
