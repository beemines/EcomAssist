"""Workflow 可持久化状态，运行客户端另由 Runtime 管理。"""
from typing import Annotated, Any, Literal, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages


class OrderSelection(TypedDict):
    """仅保存服务器候选与选择回执；实际暂停根身份在公开恢复边界核验。"""
    selection_id: str
    turn_id: str
    cards: list[dict[str, Any]]
    selected_order_id: str | None
    pause_checkpoint_id: str | None


class WorkflowState(TypedDict):
    tool_catalog_version: str | None
    tool_manifest: dict[str, Any] | None
    ticket_request: dict[str, Any] | None
    ticket_proposal: dict[str, Any] | None
    ticket_confirmation: dict[str, Any] | None
    state_version: int
    context_version: int
    context_bootstrap: bool
    context_snapshot_id: str | None
    context_anchors: dict[str, str | None]
    context_budget: dict[str, Any]
    context_snapshot: dict[str, Any] | None
    conversation_id: str
    user_message_id: str
    raw_question: str
    resolved_question: str
    category: str | None
    intent: str | None
    raw_intent: str | None
    confidence: float | None
    route: str | None
    order_selection: OrderSelection | None
    order_snapshot: dict[str, Any] | None
    retrieval_queries: list[str]
    retrieval_audit: dict[str, Any]
    refund_decision: Literal['eligible', 'needs_review', 'ineligible', 'not_applicable'] | None
    decision_reason: str | None
    refund_offer: dict[str, Any] | None
    stage_usage: dict[str, dict[str, Any]]
    active_elapsed_seconds: float
    supersedes_turn_id: str | None
    # SQL 原文完整保留；普通节点只提交带稳定 SQL ID 的新消息。
    messages: Annotated[list[BaseMessage], add_messages]
    evidence_payload: dict[str, Any]
    citations: list[dict[str, Any]]
    quality: dict[str, Any]
    tool_trace: list[dict[str, Any]]
    suggested_actions: list[Literal['handoff', 'create_ticket']]
    decision_count: int
    tool_call_count: int
    usage: dict[str, int]
    model_recovery_used: bool
    reply_mode: Literal['answer', 'clarification'] | None
    final_answer: str | None
    final_message_id: str | None
    turn_status: Literal['pending', 'running', 'awaiting_order', 'superseded', 'completed', 'failed', 'cancelled']


def new_turn_state(*, conversation_id: str, user_message_id: int, raw_question: str,
                   category: str | None, messages: list[BaseMessage]) -> WorkflowState:
    """复制调用方完整消息，仅绑定当前 SQL 用户身份并清空每轮派生数据。"""
    prepared = [message.model_copy(deep=True) for message in messages]
    # 历史 SQL 身份由读取仓储的调用方准备，这里只处理本轮最后一条用户消息。
    if prepared and isinstance(prepared[-1], HumanMessage):
        prepared[-1].id = str(user_message_id)
    return {
        'tool_catalog_version': None,
        'tool_manifest': None,
        'ticket_request': None,
        'ticket_proposal': None,
        'ticket_confirmation': None,
        'state_version': 2,
        'context_version': 1,
        'context_bootstrap': False,
        'context_snapshot_id': None,
        'context_anchors': {'summary_upto': None, 'layer1_from': None},
        'context_budget': {},
        'context_snapshot': None,
        'conversation_id': conversation_id,
        'user_message_id': str(user_message_id),
        'raw_question': raw_question,
        'resolved_question': raw_question,
        'category': category,
        'intent': None,
        'raw_intent': None,
        'confidence': None,
        'route': None,
        'order_selection': None,
        'order_snapshot': None,
        'retrieval_queries': [],
        'retrieval_audit': {},
        'refund_decision': None,
        'decision_reason': None,
        'refund_offer': None,
        'stage_usage': {},
        'active_elapsed_seconds': 0.0,
        'supersedes_turn_id': None,
        'messages': prepared,
        'evidence_payload': {},
        'citations': [],
        'quality': {},
        'tool_trace': [],
        'suggested_actions': [],
        'decision_count': 0,
        'tool_call_count': 0,
        'usage': {'actual': 0, 'estimated': 0, 'actual_calls': 0, 'estimated_calls': 0},
        'model_recovery_used': False,
        'reply_mode': None,
        'final_answer': None,
        'final_message_id': None,
        'turn_status': 'pending',
    }
