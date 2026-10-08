import json
from dataclasses import dataclass
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage


@dataclass(frozen=True)
class MessageRecord:
    id: int
    role: str
    content: str | None
    tool_calls: list[dict] | None
    tool_call_id: str | None


# 校验消息文本类型和保存长度，并按需要拒绝全空白正文。
def _text(value: Any, *, nonempty: bool = False) -> str:
    if not isinstance(value, str) or len(value) > 20000 or (nonempty and not value.strip()):
        raise ValueError("Message content must be text within 20000 characters.")
    return value


# 校验工具调用标识为非空且不超过数据库字段长度的字符串。
def _call_id(value: Any) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 64:
        raise ValueError("Tool call id must be nonempty and within 64 characters.")
    return value


# 拒绝 JSON 解析中的 NaN 和无穷大常量，保证参数为有限值。
def _invalid_constant(value: str) -> None:
    raise ValueError("Tool arguments must use finite JSON values.")


# 校验单个持久化工具申请，并还原 LangChain 使用的调用字典。
def decode_tool_calls(value: Any) -> list[dict]:
    """持久化采用 Chat Completions 格式，回放时还原 LangChain 格式。"""
    if not isinstance(value, list) or len(value) != 1:
        raise ValueError("Exactly one tool call is allowed per turn.")
    call = value[0]
    if not isinstance(call, dict) or call.get("type") != "function":
        raise ValueError("Invalid Chat Completions tool call.")
    identifier = _call_id(call.get("id"))
    function = call.get("function")
    if not isinstance(function, dict) or not isinstance(function.get("name"), str) or not function["name"].strip():
        raise ValueError("Tool function must have a name.")
    arguments = function.get("arguments")
    if not isinstance(arguments, str):
        raise ValueError("Tool arguments must be a JSON string.")
    args = json.loads(arguments, parse_constant=_invalid_constant)
    if not isinstance(args, dict):
        raise ValueError("Tool arguments must be an object.")
    return [{"id": identifier, "name": function["name"], "args": args, "type": "tool_call"}]


# 把支持的文本消息转为记录，工具申请采用可审计的标准 JSON 格式。
def record_from_message(message: BaseMessage, *, identifier: int = 0) -> MessageRecord:
    """只接收本应用的文本消息，工具申请保存为可审计的标准 JSON。"""
    if isinstance(message, HumanMessage):
        return MessageRecord(identifier, "user", _text(message.content, nonempty=True), None, None)
    if isinstance(message, ToolMessage):
        return MessageRecord(identifier, "tool", _text(message.content), None, _call_id(message.tool_call_id))
    if isinstance(message, AIMessage):
        content = _text(message.content)
        if message.invalid_tool_calls:
            raise ValueError("Invalid tool calls cannot be persisted as valid requests.")
        if not message.tool_calls:
            return MessageRecord(identifier, "assistant", content, None, None)
        if len(message.tool_calls) != 1:
            raise ValueError("Exactly one tool call is allowed per turn.")
        call = message.tool_calls[0]
        serialized = [{"id": call.get("id"), "type": "function", "function": {
            "name": call.get("name"),
            "arguments": json.dumps(call.get("args"), ensure_ascii=False, separators=(",", ":"), allow_nan=False),
        }}]
        decode_tool_calls(serialized)
        return MessageRecord(identifier, "assistant", content or None, serialized, None)
    raise ValueError("Unsupported conversation message role.")


# 校验记录角色与字段组合，再还原对应的用户、助手或工具消息。
def message_from_record(row: MessageRecord) -> BaseMessage:
    if row.role == "user" and row.tool_calls is None and row.tool_call_id is None:
        return HumanMessage(_text(row.content, nonempty=True))
    if row.role == "tool" and row.tool_calls is None:
        return ToolMessage(_text(row.content), tool_call_id=_call_id(row.tool_call_id))
    if row.role == "assistant" and row.tool_call_id is None:
        if row.tool_calls is not None:
            return AIMessage("" if row.content is None else _text(row.content), tool_calls=decode_tool_calls(row.tool_calls))
        return AIMessage(_text(row.content, nonempty=True))
    raise ValueError("Invalid persisted message role or fields.")
