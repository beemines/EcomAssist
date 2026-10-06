import json
from collections.abc import Sequence

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage

from app.core.errors import InputTooLong
from app.core.memory import estimate_tokens
from app.repositories.records import MessageRecord, message_from_record, record_from_message


def _validate_turn(messages: Sequence[BaseMessage], *, pending: bool = False) -> None:
    if not messages or not isinstance(messages[0], HumanMessage):
        raise ValueError("A turn must start with a user message.")
    # 通过同一转换器检查字段与文本界限，避免回放和预算使用不同规则。
    for message in messages:
        message_from_record(record_from_message(message))
    if len(messages) == 2 and not pending:
        if isinstance(messages[1], AIMessage) and not messages[1].tool_calls:
            return
    expected = 3 if pending else 4
    if len(messages) == expected:
        request, result = messages[1:3]
        if (
            isinstance(request, AIMessage) and len(request.tool_calls) == 1
            and isinstance(result, ToolMessage) and result.tool_call_id == request.tool_calls[0]["id"]
            and (pending or isinstance(messages[3], AIMessage) and not messages[3].tool_calls)
        ):
            return
    raise ValueError("History must contain a complete, matched single-tool turn.")


def completed_turns(rows: Sequence[MessageRecord]) -> list[list[BaseMessage]]:
    """按主键回放；坏组停到下一 user，完整轮次后的孤立结果忽略。"""
    turns: list[list[BaseMessage]] = []
    group: list[BaseMessage] | None = None
    for row in sorted(rows, key=lambda item: item.id):
        if row.role == "user":
            group = []
        if group is None:
            continue
        try:
            message = message_from_record(row)
            group.append(message)
            if isinstance(message, AIMessage) and not message.tool_calls:
                _validate_turn(group)
                turns.append(group)
                group = None
            elif len(group) > 3:
                group = None
        except (ValueError, TypeError, KeyError, RecursionError):
            group = None
    return turns


def _serialized_size(value: object) -> int:
    return len(json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8"))


def _message_size(messages: Sequence[BaseMessage]) -> int:
    total = estimate_tokens(list(messages))
    for message in messages:
        row = record_from_message(message)
        if row.tool_calls is not None:
            total += _serialized_size(row.tool_calls)
        if row.tool_call_id is not None:
            total += _serialized_size({"tool_call_id": row.tool_call_id})
    return total


def build_tool_messages(
    system: SystemMessage,
    turns: Sequence[Sequence[BaseMessage]],
    current: HumanMessage,
    budget: int,
    *,
    tool_schema: list[dict],
    current_tool_messages: Sequence[BaseMessage] = (),
) -> list[BaseMessage]:
    """必需输入不可裁断；预算不足时只移除最旧的完整历史轮次。"""
    if not isinstance(system, SystemMessage) or not isinstance(system.content, str):
        raise ValueError("System message must contain text.")
    message_from_record(record_from_message(current))
    if not isinstance(current, HumanMessage):
        raise ValueError("Current message must be a user message.")
    pending = list(current_tool_messages)
    if pending:
        _validate_turn([current, *pending], pending=True)
    for turn in turns:
        _validate_turn(turn)
    # system 不属于数据库消息角色，单独沿用纯文本开销计数。
    schema_size = _serialized_size(tool_schema)
    required = estimate_tokens([system]) + _message_size([current, *pending]) + schema_size
    if required > budget:
        raise InputTooLong()
    kept = list(turns)
    costs = [_message_size(turn) for turn in kept]
    total = required + sum(costs)
    dropped = 0
    while total > budget and dropped < len(kept):
        total -= costs[dropped]
        dropped += 1
    return [system, *(message for turn in kept[dropped:] for message in turn), current, *pending]
