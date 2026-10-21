"""父图固定路由与每次调用作用域的 Agent 子图。"""
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime
from langchain_core.runnables import RunnableConfig

from app.workflow import nodes
from app.workflow.runtime import WorkflowRuntime
from app.workflow.state import WorkflowState


def _intent_route(state: WorkflowState):
    """分类结果只映射固定出口，不由模型决定节点名。"""
    return state['route']


def _gate_route(state: WorkflowState):
    """内容自评与分数闸只用 useful 判定是否允许进入 Agent。"""
    return 'agent' if state['quality']['useful'] else 'knowledge_fallback'


def _order_route(state: WorkflowState):
    """明确订单直接查询，其余先等待用户选择。"""
    return 'load_order' if nodes.selected_order_id(state) else 'prepare_order_selection'


def _loaded_route(state: WorkflowState):
    """不存在或越权订单回到当前身份候选，不伪造成功订单。"""
    return 'expand_queries' if state['order_snapshot'] else 'prepare_order_selection'


def _selection_route(state: WorkflowState):
    """无可办订单时明确结束，避免空候选卡片形成死暂停。"""
    return 'await_order_selection' if state['order_selection']['cards'] else 'no_order_response'


def build_workflow_graph(agent_graph: CompiledStateGraph, *, checkpointer: BaseCheckpointSaver, callbacks=None) -> CompiledStateGraph:
    """父图使用显式官方 saver，受控/正式 Agent 共享同一状态和 Runtime。"""
    graph = StateGraph(WorkflowState, context_schema=WorkflowRuntime)
    for name in ('resolve_reference', 'classify_intent', 'retrieve_knowledge', 'confidence_gate',
                 'knowledge_fallback', 'complaint_response', 'social_response', 'other_response', 'log_response',
                 'resolve_order', 'prepare_order_selection', 'await_order_selection', 'load_order', 'expand_queries', 'retrieve_policies', 'no_order_response'):
        graph.add_node(name, getattr(nodes, name))
    async def call_agent(state: WorkflowState, config: RunnableConfig, runtime: Runtime[WorkflowRuntime]):
        """Preserve child runtime/stream lineage while returning only new messages."""
        from app.workflow.agent import agent_delta
        before_ids = frozenset(message.id for message in state['messages'])
        result = await agent_graph.ainvoke(state, config=config, context=runtime.context)
        return agent_delta(before_ids, result)

    graph.add_node('agent', call_agent)
    from app.workflow import ticket_confirmation
    for name in ('prepare_ticket_confirmation', 'await_ticket_confirmation', 'execute_ticket_confirmation', 'ticket_confirmation_response'):
        graph.add_node(name, getattr(ticket_confirmation, name))
    graph.add_conditional_edges('agent', lambda state: 'prepare_ticket_confirmation' if state.get('ticket_proposal') else 'log_response')
    graph.add_edge('prepare_ticket_confirmation', 'await_ticket_confirmation')
    graph.add_edge('await_ticket_confirmation', 'execute_ticket_confirmation')
    graph.add_edge('execute_ticket_confirmation', 'ticket_confirmation_response')
    graph.add_edge('ticket_confirmation_response', 'log_response')
    graph.add_edge(START, 'resolve_reference')
    graph.add_edge('resolve_reference', 'classify_intent')
    graph.add_conditional_edges('classify_intent', _intent_route, {'knowledge': 'retrieve_knowledge',
        'business': 'agent', 'after_sales': 'resolve_order', 'complaint': 'complaint_response', 'social': 'social_response', 'other': 'other_response'})
    graph.add_conditional_edges('resolve_order', _order_route)
    graph.add_conditional_edges('prepare_order_selection', _selection_route)
    graph.add_edge('await_order_selection', 'load_order')
    graph.add_conditional_edges('load_order', _loaded_route)
    graph.add_edge('expand_queries', 'retrieve_policies')
    graph.add_edge('retrieve_policies', 'confidence_gate')
    graph.add_edge('retrieve_knowledge', 'confidence_gate')
    graph.add_conditional_edges('confidence_gate', _gate_route)
    for name in ('knowledge_fallback', 'complaint_response', 'social_response', 'other_response', 'no_order_response'):
        graph.add_edge(name, 'log_response')
    graph.add_edge('log_response', END)
    compiled = graph.compile(checkpointer=checkpointer)
    return compiled.with_config(callbacks=callbacks) if callbacks else compiled
