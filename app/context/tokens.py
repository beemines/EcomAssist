"""统一估算文本、JSON及协议开销；不把启发式称为供应商 tokenizer。"""
import json
from collections.abc import Mapping, Sequence

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage


# 独立版本化：这些初始参数来自字符/协议启发式，尚无真实 usage 校准。
# 非 ASCII 每字符1.5、ASCII 每3字符1、每消息8协议单位；不按滑窗目标反推。
ESTIMATOR_VERSION = 'cjk-ascii-protocol-v1'
ASCII_CHARS_PER_TOKEN = 3
UNICODE_TOKEN_NUMERATOR = 3
UNICODE_TOKEN_DENOMINATOR = 2
MESSAGE_PROTOCOL_TOKENS = 8


def _text_tokens(text: str) -> int:
    ascii_count = sum(ord(character) < 128 for character in text)
    unicode_count = len(text) - ascii_count
    return ((ascii_count + ASCII_CHARS_PER_TOKEN - 1) // ASCII_CHARS_PER_TOKEN
            + (unicode_count * UNICODE_TOKEN_NUMERATOR + UNICODE_TOKEN_DENOMINATOR - 1)
            // UNICODE_TOKEN_DENOMINATOR)


def _plain_json(value):
    """将冻结 schema 转为出站副本，不改调用方对象。"""
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise ValueError('JSON schema keys must be strings.')
        return {key: _plain_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain_json(item) for item in value]
    return value


def _json_text(value) -> str:
    return json.dumps(_plain_json(value), ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def estimate_payload(messages: Sequence[BaseMessage], tools: Sequence[dict] = ()) -> int:
    """计实际文本形状；SQL消息ID/实测usage及重复raw镜像不在出站载荷中。

    当前应用只有文本消息；不接受未知多模态块后悄悄漏算。工具参数采用
    Chat Completions 的字符串 JSON 形状，工具关联 ID 和 name 均计费。
    """
    total = 0
    for message in messages:
        if not isinstance(message.content, str):
            raise ValueError('Context estimator supports text messages only.')
        if isinstance(message, SystemMessage):
            role = 'system'
        elif isinstance(message, HumanMessage):
            role = 'user'
        elif isinstance(message, AIMessage):
            role = 'assistant'
        elif isinstance(message, ToolMessage):
            role = 'tool'
        else:
            raise ValueError('Unsupported context message role.')
        total += MESSAGE_PROTOCOL_TOKENS + _text_tokens(role) + _text_tokens(message.content)
        if message.name is not None:
            total += _text_tokens(_json_text({'name': message.name}))
        if isinstance(message, AIMessage):
            if message.invalid_tool_calls:
                raise ValueError('Cannot estimate invalid tool calls as a valid request.')
            if message.tool_calls:
                calls = [{'id': call['id'], 'type': 'function', 'function': {
                    # langchain-openai1.6.7保留参数JSON默认分隔空格。
                    'name': call['name'], 'arguments': json.dumps(
                        _plain_json(call['args']), ensure_ascii=False, allow_nan=False)}}
                    for call in message.tool_calls]
                total += _text_tokens(_json_text({'tool_calls': calls}))
            elif message.additional_kwargs.get('tool_calls'):
                total += _text_tokens(_json_text({'tool_calls': message.additional_kwargs['tool_calls']}))
        elif isinstance(message, ToolMessage):
            total += _text_tokens(_json_text({'tool_call_id': message.tool_call_id}))
    if tools:
        total += _text_tokens(_json_text({'tools': tools}))
    return total
