"""不依赖图框架的有界选择、执行、完整回灌和直接收敛示例。"""
import asyncio
import json
from collections.abc import Mapping
from dataclasses import dataclass

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool

from app.agent.controls import AgentLimits, UsageLedger, call_signature, estimate_call_input, parse_tool_selection, record_usage, reserve_call
from app.core.answer_validation import ensure_answer_active
from app.core.errors import InputTooLong, ServiceError
from app.core.tool_history import build_tool_messages
from app.tools.executor import ToolExecutor
from app.tools.types import ToolCall, ToolOutcome


UNFINISHED_ANSWER = '本轮查询尚未完成，已达到安全停止条件。请补充问题或稍后再试。'


@dataclass(frozen=True)
class AgentTrace:
    call: ToolCall
    outcome: ToolOutcome


@dataclass
class BareAgentResult:
    answer: str
    trace: list[AgentTrace]
    usage: UsageLedger
    stop_reason: str

    @property
    def calls(self) -> list[str]:
        """按实际逻辑执行顺序提供工具名称轨迹。"""
        return [step.call.name for step in self.trace]


def _split_messages(messages: list[BaseMessage]):
    """提取系统、完整历史和当前问题，申请结果由循环单独维护。"""
    if not messages or not isinstance(messages[0], SystemMessage) or not isinstance(messages[-1], HumanMessage):
        raise ValueError('Bare agent requires system, complete history and a current user message.')
    turns, turn = [], []
    for message in messages[1:-1]:
        if isinstance(message, HumanMessage) and turn:
            turns.append(turn)
            turn = []
        turn.append(message)
    if turn:
        turns.append(turn)
    return messages[0], turns, messages[-1]


async def run_bare_agent(model, registry: Mapping[str, BaseTool], executor: ToolExecutor,
                         messages: list[BaseMessage], *, limits: AgentLimits, context=None) -> BareAgentResult:
    """整轮固定最多 240 秒，取消/期限不重试并原样传播。"""
    async with asyncio.timeout(240):
        return await _run_bare_agent(model, registry, executor, messages, limits=limits, context=context)


async def _run_bare_agent(model, registry: Mapping[str, BaseTool], executor: ToolExecutor,
                          messages: list[BaseMessage], *, limits: AgentLimits, context=None) -> BareAgentResult:
    """最多四次逻辑调用/五次决策；停止不追加请求，无工具直接回答。"""
    from app.tools.catalog_types import BoundCatalog
    registry = registry.subset(name for name in registry if name != 'create_ticket') if isinstance(registry, BoundCatalog) else {name: tool for name, tool in registry.items() if name != 'create_ticket'}
    schema = [convert_to_openai_tool(tool) for tool in registry.values()]
    system, turns, current = _split_messages(messages)
    ledger, trace, pending = UsageLedger(limits.total_token_budget), [], []
    signatures, identifiers = set(), set()
    bound = None
    for _ in range(limits.max_decisions):
        ensure_answer_active()
        try:
            prepared = build_tool_messages(system, turns, current, limits.input_token_budget,
                                           tool_schema=schema, current_tool_messages=pending)
            reserve_call(prepared, schema, ledger, output_limit=limits.decision_output_tokens,
                         final_reserve=limits.final_output_tokens)
        except (InputTooLong, ServiceError) as exc:
            if exc.code not in ('input_too_long', 'token_budget'):
                raise
            return BareAgentResult(UNFINISHED_ANSWER, trace, ledger, 'token_budget')
        if bound is None:
            bound = model.bind_tools(list(registry.values()), tool_choice='auto', parallel_tool_calls=False)
        selected = await bound.ainvoke(prepared)
        ensure_answer_active()
        record_usage(selected, ledger, estimated_input=estimate_call_input(prepared, schema),
                     output_limit=limits.decision_output_tokens)
        call = parse_tool_selection(selected, registry)
        if ledger.spent > ledger.budget:
            return BareAgentResult(UNFINISHED_ANSWER, trace, ledger, 'token_budget')
        if call is None:
            if not selected.content.strip() or len(selected.content.encode('utf-8')) > 65535:
                raise ServiceError('upstream_error', '模型回复未正常完成，请稍后重试。', 502)
            return BareAgentResult(selected.content, trace, ledger, 'completed')
        if call.id in identifiers:
            raise ServiceError('upstream_error', '模型重复使用了工具调用标识。', 502)
        signature = call_signature(call)
        if signature in signatures:
            return BareAgentResult(UNFINISHED_ANSWER, trace, ledger, 'repeat_call')
        if len(trace) >= limits.max_tool_calls:
            return BareAgentResult(UNFINISHED_ANSWER, trace, ledger, 'step_limit')
        # 执行前用匹配的空结果验证申请也满足当前必需输入预算。
        try:
            build_tool_messages(system, turns, current, limits.input_token_budget, tool_schema=schema,
                                current_tool_messages=[*pending, selected, ToolMessage('', tool_call_id=call.id)])
        except InputTooLong:
            return BareAgentResult(UNFINISHED_ANSWER, trace, ledger, 'token_budget')
        if ledger.remaining < limits.final_output_tokens:
            return BareAgentResult(UNFINISHED_ANSWER, trace, ledger, 'token_budget')
        identifiers.add(call.id)
        signatures.add(signature)
        outcome = await executor.execute(call, registry, context=context) if isinstance(registry, BoundCatalog) else await executor.execute(call, registry)
        ensure_answer_active()
        result = ToolMessage(json.dumps(outcome.content, ensure_ascii=False, separators=(',', ':'), allow_nan=False),
                             tool_call_id=call.id, name=call.name, status=outcome.status)
        pending.extend([selected, result])
        trace.append(AgentTrace(call, outcome))
    return BareAgentResult(UNFINISHED_ANSWER, trace, ledger, 'step_limit')
