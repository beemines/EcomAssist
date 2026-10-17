# 还原可回放的完整工具轮次，并把工具 Schema、申请与结果计入输入预算。
import json
from collections.abc import Sequence

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage

from app.core.errors import InputTooLong
from app.core.memory import estimate_tokens
from app.repositories.records import MessageRecord, decode_tool_calls, message_from_record, record_from_message


# 校验完整或待回答轮次的顺序配对，并要求全轮工具调用标识唯一。
def _validate_turn(messages: Sequence[BaseMessage], *, pending: bool = False) -> None:
    if not messages or not isinstance(messages[0], HumanMessage):
        raise ValueError("A turn must start with a user message.")
    # 通过同一转换器检查字段与文本界限，避免回放和预算使用不同规则。
    for message in messages:
        message_from_record(record_from_message(message))
    exchanges = messages[1:]
    if not pending:
        if not exchanges or not isinstance(exchanges[-1], AIMessage) or exchanges[-1].tool_calls:
            raise ValueError("A complete turn must end with an assistant answer.")
        exchanges = exchanges[:-1]
    if len(exchanges) % 2 or (pending and not exchanges):
        raise ValueError("Tool requests must have adjacent matched results.")
    seen: set[str] = set()
    for index in range(0, len(exchanges), 2):
        request, result = exchanges[index:index + 2]
        if not isinstance(request, AIMessage) or len(request.tool_calls) != 1 or not isinstance(result, ToolMessage):
            raise ValueError("Each tool request must be followed by its result.")
        identifier = request.tool_calls[0]["id"]
        if identifier in seen or result.tool_call_id != identifier:
            raise ValueError("Tool call ids must be unique and match the adjacent result.")
        seen.add(identifier)


# 按消息主键恢复完整轮次，跳过损坏、未完成和孤立的消息组合。
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
        except (ValueError, TypeError, KeyError, RecursionError):
            group = None
    return turns


# 用紧凑 UTF-8 JSON 的字节数估算工具结构的输入开销。
def _serialized_size(value: object) -> int:
    return len(json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8"))


# 合计正文与工具申请、结果关联标识的开销，避免只计算可见文本。
def _message_size(messages: Sequence[BaseMessage]) -> int:
    total = estimate_tokens(list(messages))
    for message in messages:
        row = record_from_message(message)
        if row.tool_calls is not None:
            total += _serialized_size(row.tool_calls)
        if row.tool_call_id is not None:
            total += _serialized_size({"tool_call_id": row.tool_call_id})
    return total


# 检查必需输入预算，并按最旧优先移除完整历史轮次后组装模型消息。
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
    # 系统提示、当前问题、工具 Schema 和当前申请/结果是不可裁断的必需输入。
    required = estimate_tokens([system]) + _message_size([current, *pending]) + schema_size
    if required > budget:
        raise InputTooLong()
    kept = list(turns)
    costs = [_message_size(turn) for turn in kept]
    total = required + sum(costs)
    dropped = 0
    # 以整轮为单位淘汰最旧历史，避免只保留工具申请或只保留工具结果。
    while total > budget and dropped < len(kept):
        total -= costs[dropped]
        dropped += 1
    return [system, *(message for turn in kept[dropped:] for message in turn), current, *pending]


def completed_boundaries(rows: Sequence[MessageRecord]) -> set[int]:
    """只承认本会话完整轮次的末条客服；工具往返未配对不能成为边界。

    新user可结束之前取消/失败的残留，其原文仍留在待摘要批次中。
    坏角色/损坏JSON明确诊断；孤立的合法工具行保留但不伪造成完成。
    """
    completed = set()
    active, valid, pending = False, False, None
    seen: set[str] = set()
    for index, row in enumerate(rows):
        record = MessageRecord(row.id, row.role, row.content, row.tool_calls, row.tool_call_id)
        message_from_record(record)
        if row.role == 'user':
            active, valid, pending = True, True, None
            seen = set()
        elif row.role == 'tool':
            if not active or pending is None or row.tool_call_id != pending:
                valid = False
            pending = None
        elif row.tool_calls is not None:
            if not active or pending is not None:
                valid = False
            pending = decode_tool_calls(row.tool_calls)[0]['id']
            if pending in seen:
                valid = False
            seen.add(pending)
        else:
            next_is_user_or_end = index + 1 == len(rows) or rows[index + 1].role == 'user'
            if active and valid and pending is None and next_is_user_or_end:
                completed.add(row.id)
            active = False
    return completed
