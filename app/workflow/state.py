"""Workflow 可持久化状态，运行客户端另由 Runtime 管理。"""
from typing import Any, Literal, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage


class WorkflowState(TypedDict):
    conversation_id: str
    user_message_id: str
    raw_question: str
    resolved_question: str
    category: str | None
    intent: str | None
    route: str | None
    # 消息使用替换语义；调用节点负责按顺序返回完整列表，不叠加历史。
    messages: list[BaseMessage]
    evidence_payload: dict[str, Any]
    citations: list[dict[str, Any]]
    quality: dict[str, Any]
    tool_trace: list[dict[str, Any]]
    suggested_actions: list[Literal['handoff', 'create_ticket']]
    decision_count: int
    tool_call_count: int
    usage: dict[str, int]
    reply_mode: Literal['answer', 'clarification'] | None
    final_answer: str | None
    final_message_id: str | None
    turn_status: Literal['pending', 'running', 'completed', 'failed', 'cancelled']


def new_turn_state(*, conversation_id: str, user_message_id: int, raw_question: str,
                   category: str | None, messages: list[BaseMessage]) -> WorkflowState:
    """复制调用方完整消息，仅绑定当前 SQL 用户身份并清空每轮派生数据。"""
    prepared = [message.model_copy(deep=True) for message in messages]
    # 历史 SQL 身份由读取仓储的调用方准备，这里只处理本轮最后一条用户消息。
    if prepared and isinstance(prepared[-1], HumanMessage):
        prepared[-1].id = str(user_message_id)
    return {
        'conversation_id': conversation_id,
        'user_message_id': str(user_message_id),
        'raw_question': raw_question,
        'resolved_question': raw_question,
        'category': category,
        'intent': None,
        'route': None,
        'messages': prepared,
        'evidence_payload': {},
        'citations': [],
        'quality': {},
        'tool_trace': [],
        'suggested_actions': [],
        'decision_count': 0,
        'tool_call_count': 0,
        'usage': {'actual': 0, 'estimated': 0, 'actual_calls': 0, 'estimated_calls': 0},
        'reply_mode': None,
        'final_answer': None,
        'final_message_id': None,
        'turn_status': 'pending',
    }
