import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, END, StateGraph
from langgraph.types import Command
from langchain_core.messages import HumanMessage
from app.workflow.state import WorkflowState, new_turn_state
from app.workflow.runtime import WorkflowRuntime
from app.workflow.ticket_confirmation import prepare_ticket_confirmation, await_ticket_confirmation
from app.workflow.ticket_actions import pending_ticket
from tests.test_dynamic_agent_tools import dynamic_runtime


async def test_preview_pauses_in_own_root_node_without_business_write():
    ctx, state, audit = dynamic_runtime([])
    from tests.test_workflow_api import Store
    ctx.repository = Store()
    state = new_turn_state(conversation_id='1', user_message_id=1, raw_question='饮水机漏水，帮我建工单', category=None, messages=[HumanMessage('饮水机漏水，帮我建工单')])
    state.update(ticket_request={'origin_user_message_id': '1', 'source_texts': [state['raw_question']]},
        ticket_proposal={'tool_call_id': 'ticket', 'args': {'ticket_type': '售后', 'description': '饮水机漏水'}})
    graph = StateGraph(WorkflowState, context_schema=WorkflowRuntime)
    graph.add_node('prepare_ticket_confirmation', prepare_ticket_confirmation)
    graph.add_node('await_ticket_confirmation', await_ticket_confirmation)
    graph.add_edge(START, 'prepare_ticket_confirmation')
    graph.add_edge('prepare_ticket_confirmation', 'await_ticket_confirmation')
    graph.add_edge('await_ticket_confirmation', END)
    compiled = graph.compile(checkpointer=InMemorySaver())
    await compiled.ainvoke(state, {'configurable': {'thread_id': '1'}}, context=ctx)
    snapshot = await compiled.aget_state({'configurable': {'thread_id': '1'}})
    preview = pending_ticket(snapshot, '1')
    assert snapshot.next == ('await_ticket_confirmation',)
    assert preview['description'] == '饮水机漏水' and preview['ticket_type'] == '售后'
    assert audit.records == []  # no attempted business execution while waiting
    assert pending_ticket(snapshot, '2') is None
