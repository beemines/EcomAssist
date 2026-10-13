"""父图固定路由与每次调用作用域的 Agent 子图。"""
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.workflow import nodes
from app.workflow.runtime import WorkflowRuntime
from app.workflow.state import WorkflowState


def _intent_route(state: WorkflowState):
    """分类结果只映射四个固定出口，不由模型决定节点名。"""
    return state['route']


def _gate_route(state: WorkflowState):
    """内容自评与分数闸只用 useful 判定是否允许进入 Agent。"""
    return 'agent' if state['quality']['useful'] else 'knowledge_fallback'


def build_workflow_graph(agent_graph: CompiledStateGraph, *, checkpointer: BaseCheckpointSaver) -> CompiledStateGraph:
    """父图使用显式官方 saver，受控/正式 Agent 共享同一状态和 Runtime。"""
    graph = StateGraph(WorkflowState, context_schema=WorkflowRuntime)
    for name in ('resolve_reference', 'classify_intent', 'retrieve_knowledge', 'confidence_gate',
                 'knowledge_fallback', 'complaint_response', 'social_response', 'log_response'):
        graph.add_node(name, getattr(nodes, name))
    graph.add_node('agent', agent_graph)
    graph.add_edge(START, 'resolve_reference')
    graph.add_edge('resolve_reference', 'classify_intent')
    graph.add_conditional_edges('classify_intent', _intent_route, {'knowledge': 'retrieve_knowledge',
        'business': 'agent', 'complaint': 'complaint_response', 'social': 'social_response'})
    graph.add_edge('retrieve_knowledge', 'confidence_gate')
    graph.add_conditional_edges('confidence_gate', _gate_route)
    for name in ('agent', 'knowledge_fallback', 'complaint_response', 'social_response'):
        graph.add_edge(name, 'log_response')
    graph.add_edge('log_response', END)
    return graph.compile(checkpointer=checkpointer)
