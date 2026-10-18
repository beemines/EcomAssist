"""裸循环与 Workflow 共用的单工具协议、重复签名和累计预算。"""
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from langchain_core.tools import BaseTool

from app.core.errors import ServiceError
from app.core.memory import estimate_tokens
from app.repositories.records import decode_tool_calls, record_from_message
from app.tools.types import ToolCall

if TYPE_CHECKING:
    from app.config import Settings
    from app.context.types import ContextBudget


def resolve_turn_token_limit(settings: 'Settings', budget: 'ContextBudget', *,
                            call_limits: Mapping[str, int]) -> int:
    """新Workflow接线用：显式费用上限原样生效，缺省才采用图派生额度。"""
    from app.context.budget import derive_turn_token_limit

    derived = derive_turn_token_limit(budget, call_limits=call_limits)
    return settings.agent_total_token_budget if settings.agent_total_token_budget_explicit else derived


@dataclass(frozen=True)
class AgentLimits:
    max_tool_calls: int = 4
    total_token_budget: int = 32000
    max_decisions: int = 5
    final_output_tokens: int = 512
    decision_output_tokens: int = 2048
    input_token_budget: int = 8000

    def __post_init__(self):
        """直接调用与环境配置同样拒绝非法数字和扩大硬上限。"""
        values = (self.max_tool_calls, self.total_token_budget, self.max_decisions,
                  self.final_output_tokens, self.decision_output_tokens, self.input_token_budget)
        if any(type(value) is not int or value <= 0 for value in values):
            raise ValueError('Agent limits must be positive integers.')
        if self.max_tool_calls > 4 or self.max_decisions > 5:
            raise ValueError('Agent allows at most four tools and five decisions.')


@dataclass
class UsageLedger:
    budget: int = 32000
    actual: int = 0
    estimated: int = 0
    actual_calls: int = 0
    estimated_calls: int = 0

    def __post_init__(self):
        """账本只使用非负整数和正预算，恢复也不能注入非法余额。"""
        if type(self.budget) is not int or self.budget <= 0:
            raise ValueError('Usage budget must be a positive integer.')
        if any(type(value) is not int or value < 0 for value in
               (self.actual, self.estimated, self.actual_calls, self.estimated_calls)):
            raise ValueError('Usage costs must be nonnegative integers.')

    @property
    def spent(self) -> int:
        """合计实测与估算成本，不把保留额度当作已消耗。"""
        return self.actual + self.estimated

    @property
    def remaining(self) -> int:
        """已发生超额也保留实际成本，但可申请余额最低为零。"""
        return max(0, self.budget - self.spent)

    @property
    def source(self) -> str:
        """即使合法 usage 为零，也按调用来源区分账本类型。"""
        if self.actual_calls and self.estimated_calls:
            return 'mixed'
        if self.actual_calls:
            return 'actual'
        return 'estimated' if self.estimated_calls else 'none'


class ToolProtocolReason(StrEnum):
    """固定内部原因码，不接受上游提供的自由文本。"""
    TYPE = 'type'
    INVALID_DECODED_COUNT = 'invalid_decoded_count'
    MULTIPLE_TOOLS = 'multiple_tools'
    FINISH = 'finish'
    RAW_MIRROR = 'raw_mirror'
    RECORD = 'record'
    NAME = 'name'
    ARGS = 'args'


class ToolProtocolError(ServiceError):
    """内部携带拒绝类别，公开错误三元组和异常正文保持原契约。"""

    def __init__(self, reason: ToolProtocolReason):
        """只保存固定枚举，不附带响应对象、参数或底层异常。"""
        super().__init__('upstream_error', '模型返回了无效工具申请或未正常结束。', 502)
        self.reason = ToolProtocolReason(reason)


def call_signature(call: ToolCall) -> str:
    """用工具名和排序紧凑 JSON 识别重复，忽略调用 ID 和键顺序。"""
    return call.name + ':' + json.dumps(call.args, ensure_ascii=False, sort_keys=True,
                                      separators=(',', ':'), allow_nan=False)


def parse_tool_selection(reply: AIMessage, registry: Mapping[str, BaseTool], *, allow_unknown: bool = False) -> ToolCall | None:
    """严格校验原单工具协议并标注固定失败原因；Schema 仍交执行器校验。"""
    if not isinstance(reply, AIMessage):
        raise ToolProtocolError(ToolProtocolReason.TYPE)
    if reply.invalid_tool_calls:
        raise ToolProtocolError(ToolProtocolReason.INVALID_DECODED_COUNT)
    if len(reply.tool_calls) > 1:
        raise ToolProtocolError(ToolProtocolReason.MULTIPLE_TOOLS)
    reason = reply.response_metadata.get('finish_reason')
    if not isinstance(reason, str) or reason not in ({'stop', 'tool_calls'} if reply.tool_calls else {'stop'}):
        raise ToolProtocolError(ToolProtocolReason.FINISH)
    raw = reply.additional_kwargs.get('tool_calls')
    if raw is not None and (not isinstance(raw, list) or len(raw) != len(reply.tool_calls)):
        raise ToolProtocolError(ToolProtocolReason.RAW_MIRROR)
    if reply.tool_calls:
        call = reply.tool_calls[0]
        if not isinstance(call.get('name'), str) or not call['name'].strip() or (call['name'] not in registry and not allow_unknown):
            raise ToolProtocolError(ToolProtocolReason.NAME)
        if not isinstance(call.get('args'), dict):
            raise ToolProtocolError(ToolProtocolReason.ARGS)
    try:
        record_from_message(reply)
    except (ValueError, TypeError, KeyError, RecursionError):
        raise ToolProtocolError(ToolProtocolReason.RECORD) from None
    if not reply.tool_calls:
        return None
    if raw is not None:
        try:
            mirrored = decode_tool_calls(raw)[0]
            if (mirrored['id'] != call['id'] or mirrored['name'] != call['name']
                    or call_signature(ToolCall(mirrored['id'], mirrored['name'], mirrored['args']))
                    != call_signature(ToolCall(call['id'], call['name'], call['args']))):
                raise ValueError('Raw tool request differs from parsed request.')
        except (ValueError, TypeError, KeyError, RecursionError):
            raise ToolProtocolError(ToolProtocolReason.RAW_MIRROR) from None
    return ToolCall(call['id'], call['name'], call['args'])


def tool_protocol_diagnostic(reply) -> dict:
    """只投影有界数量、类型标记及白名单结束值，不读取正文或调用内容。"""
    if isinstance(reply, AIMessage):
        calls, invalid = reply.tool_calls, reply.invalid_tool_calls
        raw = reply.additional_kwargs.get('tool_calls')
        finish = reply.response_metadata.get('finish_reason')
    else:
        calls = invalid = raw = finish = None
    if finish is None:
        normalized_finish = 'missing'
    elif not isinstance(finish, str):
        normalized_finish = 'invalid_type'
    elif finish in ('stop', 'tool_calls', 'length', 'content_filter'):
        normalized_finish = finish
    else:
        normalized_finish = 'other'
    return {
        'tool_call_count': min(len(calls), 1000) if isinstance(calls, list) else None,
        'invalid_tool_call_count': min(len(invalid), 1000) if isinstance(invalid, list) else None,
        'raw_tool_call_count': min(len(raw), 1000) if isinstance(raw, list) else None,
        'raw_tool_calls_invalid_type': raw is not None and not isinstance(raw, list),
        'finish': normalized_finish,
    }


def estimate_call_input(messages: Sequence[BaseMessage], tool_schema: list[dict]) -> int:
    """沿用消息估算规则，计入 Schema、参数和结果关联 ID。"""
    total = estimate_tokens(list(messages))
    structures = [tool_schema]
    for message in messages:
        if isinstance(message, SystemMessage):
            continue
        row = record_from_message(message)
        if row.tool_calls is not None:
            structures.append(row.tool_calls)
        if row.tool_call_id is not None:
            structures.append({'tool_call_id': row.tool_call_id})
    return total + sum(len(json.dumps(value, ensure_ascii=False, separators=(',', ':'),
                                     allow_nan=False).encode('utf-8')) for value in structures)


def reserve_call(messages, tool_schema, ledger: UsageLedger, *, output_limit: int, final_reserve: int) -> None:
    """调用前核验输入、最大输出和最终保留；拒绝不改账本。"""
    if type(output_limit) is not int or output_limit <= 0 or type(final_reserve) is not int or final_reserve < 0:
        raise ValueError('Output limit must be positive and final reserve nonnegative.')
    if estimate_call_input(messages, tool_schema) + output_limit + final_reserve > ledger.remaining:
        raise ServiceError('token_budget', '本轮模型预算不足，无法继续查询。', 422)


def record_usage(reply, ledger: UsageLedger, *, estimated_input: int, output_limit: int) -> None:
    """合法非负且一致 usage 记实测，否则计入输入和完整输出上限。"""
    if type(estimated_input) is not int or estimated_input < 0 or type(output_limit) is not int or output_limit <= 0:
        raise ValueError('Usage estimate must be nonnegative with a positive output limit.')
    usage = getattr(reply, 'usage_metadata', None)
    values = [usage.get(key) for key in ('input_tokens', 'output_tokens', 'total_tokens')] if isinstance(usage, dict) else []
    if not values:
        raw = getattr(reply, 'response_metadata', {}).get('token_usage')
        values = [raw.get(key) for key in ('prompt_tokens', 'completion_tokens', 'total_tokens')] if isinstance(raw, dict) else []
    if (len(values) == 3 and all(type(value) is int and value >= 0 for value in values)
            and values[0] + values[1] == values[2]):
        ledger.actual += values[2]
        ledger.actual_calls += 1
    else:
        ledger.estimated += estimated_input + output_limit
        ledger.estimated_calls += 1
