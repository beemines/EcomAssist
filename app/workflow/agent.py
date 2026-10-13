"""主力 ReAct 子图：受限读取、完整 SQL 配对、证据闸及唯一最终流。"""
import asyncio
import json
import time
from dataclasses import asdict
from typing import Literal

import httpx
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.utils.function_calling import convert_to_openai_tool
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from openai import APITimeoutError
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.agent.bare import UNFINISHED_ANSWER
from app.agent.controls import AgentLimits, UsageLedger, call_signature, estimate_call_input, parse_tool_selection, record_usage, reserve_call
from app.core.answer_validation import FinalAnswerStream, close_answer_stream, ensure_answer_active, validate_answer, validate_business_answer
from app.core.errors import InputTooLong, ServiceError
from app.core.evidence import build_agent_evidence
from app.core.extraction import invalid_output, validate_structured_output
from app.core.llm import model_with_output_budget
from app.core.sufficiency import QualityDecision
from app.tools.schemas import FAQArgs
from app.tools.types import ToolCall
from app.workflow.nodes import log_node, remaining_timeout
from app.workflow.prompts import KNOWLEDGE_FALLBACK, agent_decision_system, agent_final_system
from app.workflow.runtime import WorkflowRuntime
from app.workflow.state import WorkflowState


class AgentControl(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    reply_mode: Literal['answer', 'clarification']
    suggested_actions: list[Literal['handoff', 'create_ticket']] = Field(max_length=2)

    @field_validator('suggested_actions')
    @classmethod
    def unique_actions(cls, actions):
        """保留原顺序去重，合法两项之外的长列表仍由 Schema 拒绝。"""
        return list(dict.fromkeys(actions))


class _AgentState(WorkflowState, total=False):
    selected: AIMessage | None
    stop_reason: str | None
    tool_error: dict | None


def _limits(context: WorkflowRuntime) -> AgentLimits:
    """读取已批准配置；决策五步和最终512输出保留固定上限。"""
    return AgentLimits(max_tool_calls=getattr(context.settings, 'agent_max_tool_calls', 4),
        total_token_budget=getattr(context.settings, 'agent_total_token_budget', 32000),
        decision_output_tokens=getattr(context.settings, 'agent_decision_max_output_tokens', 2048),
        input_token_budget=context.settings.tool_input_token_budget)


def _ledger(state, limits):
    """从持久化四项成本恢复账本，包含父图已发生的分类成本。"""
    return UsageLedger(budget=limits.total_token_budget, **state['usage'])


def _usage(ledger):
    """只把可序列化成本写入状态，不将运行期客户端持久化。"""
    return {key: getattr(ledger, key) for key in ('actual', 'estimated', 'actual_calls', 'estimated_calls')}


def _registry(state, context):
    """只开放读取工具，已强制检索的知识轮排除 FAQ。"""
    allowed = {'query_order', 'query_logistics', 'query_product', 'query_faq'}
    if state['route'] == 'knowledge':
        allowed.remove('query_faq')
    return {name: tool for name, tool in context.registry.items() if name in allowed}


def _parts(state):
    """以 SQL 用户消息身份拆出完整历史及当前所有原始申请/结果。"""
    messages = state['messages']
    index = next((i for i, message in enumerate(messages)
        if isinstance(message, HumanMessage) and message.id == state['user_message_id']), None)
    if index is None:
        raise ValueError('current SQL user message identity missing')
    turns, turn = [], []
    for message in messages[:index]:
        if isinstance(message, HumanMessage) and turn:
            turns.append(turn)
            turn = []
        turn.append(message)
    if turn:
        turns.append(turn)
    pending = messages[index + 1:]
    payloads = [json.loads(message.content) for message in pending if isinstance(message, ToolMessage)]
    return turns, messages[index], pending, payloads


def _packet(state, context, system: SystemMessage, schema=()):
    """使用实际完整系统和全部原始结果计费，Schema 占用也从输入额度扣除。"""
    turns, current, pending, payloads = _parts(state)
    schema_cost = estimate_call_input([], list(schema)) - estimate_call_input([], [])
    budget = context.settings.tool_input_token_budget - schema_cost
    if budget <= 0:
        raise InputTooLong()
    return build_agent_evidence(system=system, turns=turns, current=current,
        current_tool_messages=pending, payloads=payloads, budget=budget)


def _control(reply):
    """严格校验 untouched JSON 和 parsed 值，不接受回答正文或混合工具申请。"""
    try:
        parsed = AgentControl.model_validate_json(reply.text)
    except ValidationError as exc:
        raise invalid_output() from exc
    return validate_structured_output({'raw': reply, 'parsed': parsed, 'parsing_error': None}, AgentControl)


def _normalize(selected, call, question):
    """仅合法 FAQ Schema 可归一成可信原话片段，非法参数留给执行器反馈。"""
    if call.name != 'query_faq':
        return selected, call
    try:
        arguments = FAQArgs.model_validate(call.args)
    except ValidationError:
        return selected, call
    if arguments.keyword in question:
        return selected, call
    args = {'keyword': question.lstrip()[:128]}
    effective = selected.model_copy(deep=True)
    effective.tool_calls[0]['args'] = args
    if 'tool_calls' in effective.additional_kwargs:
        effective.additional_kwargs['tool_calls'] = [{'id': call.id, 'type': 'function',
            'function': {'name': call.name, 'arguments': json.dumps(args, ensure_ascii=False)}}]
    return effective, ToolCall(call.id, call.name, args)


async def _check_evidence(state, context, packet):
    """新增 FAQ 与实际最终副本均执行真实重排门槛，外部故障保持 ServiceError。"""
    threshold = context.settings.rerank_min_score
    if packet.strategy != 'hybrid_rerank' or threshold is None:
        raise ValueError('online knowledge gate requires hybrid_rerank and calibrated threshold')
    if not packet.citations or packet.best_score is None or packet.best_score < threshold:
        return {'useful': False, 'reason': '当前知识证据为空或低于已校准重排门槛。',
            'response_kind': 'knowledge', 'source': 'retrieval_low_conf'}
    async with asyncio.timeout(remaining_timeout(context, context.settings.llm_timeout_seconds)):
        decision = await context.sufficiency.check(state['raw_question'], packet)
    return decision.model_dump()


async def llm_call(state: _AgentState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """最多五次决策；执行前保留完整最终输入和输出，控制正文从不输出或入库。"""
    context, limits = runtime.context, _limits(runtime.context)
    ensure_answer_active(context.deadline)
    if state['decision_count'] >= limits.max_decisions:
        return {'stop_reason': 'step_limit', 'selected': None}
    registry = _registry(state, context)
    schema = [convert_to_openai_tool(tool) for tool in registry.values()]
    ledger = _ledger(state, limits)
    try:
        packet = _packet(state, context, agent_decision_system(state['intent']), schema)
        final_packet = _packet(state, context, agent_final_system(state['intent'], state['reply_mode']))
        final_reserve = estimate_call_input(final_packet.messages, []) + limits.final_output_tokens
        reserve_call(packet.messages, schema, ledger, output_limit=limits.decision_output_tokens,
            final_reserve=final_reserve)
    except (InputTooLong, ServiceError) as exc:
        if exc.code not in ('input_too_long', 'token_budget'):
            raise
        return {'stop_reason': 'token_budget', 'selected': None}
    model = model_with_output_budget(context.decision_model, context.settings, limits.decision_output_tokens)
    bound = model.bind_tools(list(registry.values()), tool_choice='auto', parallel_tool_calls=False)
    try:
        async with asyncio.timeout(remaining_timeout(context, context.settings.llm_timeout_seconds)):
            selected = await bound.ainvoke(packet.messages)
    except (TimeoutError, httpx.TimeoutException, APITimeoutError) as exc:
        raise ServiceError('upstream_timeout', '模型响应超时，请稍后重试。', 504) from exc
    except ServiceError:
        raise
    except Exception as exc:
        raise ServiceError('upstream_error', '模型服务暂时不可用，请稍后重试。', 502) from exc
    ensure_answer_active(context.deadline)
    record_usage(selected, ledger, estimated_input=estimate_call_input(packet.messages, schema),
        output_limit=limits.decision_output_tokens)
    call = parse_tool_selection(selected, registry)
    update = {'decision_count': state['decision_count'] + 1, 'usage': _usage(ledger), 'selected': None, 'stop_reason': None}
    log_node(state, 'llm_call', decision_count=update['decision_count'], usage=update['usage'])
    if ledger.remaining < final_reserve:
        return {**update, 'stop_reason': 'token_budget'}
    if call is None:
        control = _control(selected)
        return {**update, 'reply_mode': control.reply_mode, 'suggested_actions': control.suggested_actions}
    if selected.text.strip():
        raise invalid_output()
    selected, call = _normalize(selected, call, state['raw_question'])
    _, _, pending, _ = _parts(state)
    requests = [message for message in pending if isinstance(message, AIMessage)]
    if any(request.tool_calls[0]['id'] == call.id for request in requests):
        raise ServiceError('upstream_error', '模型重复使用了工具调用标识。', 502)
    if any(call_signature(ToolCall(request.tool_calls[0]['id'], request.tool_calls[0]['name'],
            request.tool_calls[0]['args'])) == call_signature(call) for request in requests):
        return {**update, 'stop_reason': 'repeat_call'}
    if state['tool_call_count'] >= limits.max_tool_calls:
        return {**update, 'stop_reason': 'step_limit'}
    # 完整占位配对先验证参数输入，停止时不持久化孤立请求。
    placeholder = ToolMessage('{}', tool_call_id=call.id)
    try:
        future = {**state, 'messages': [*state['messages'], selected, placeholder]}
        future_packet = _packet(future, context, agent_final_system(state['intent'], 'answer'))
        reserve_call(future_packet.messages, [], ledger, output_limit=limits.final_output_tokens, final_reserve=0)
    except (InputTooLong, ServiceError) as exc:
        if exc.code not in ('input_too_long', 'token_budget'):
            raise
        return {**update, 'stop_reason': 'token_budget'}
    return {**update, 'selected': selected}


async def tool_node(state: _AgentState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """执行器负责工具超时，外层仅限制整轮期限；逐个保存配对并在回灌前检查新FAQ。"""
    context = runtime.context
    ensure_answer_active(context.deadline)
    selected = state['selected'].model_copy(deep=True)
    call = parse_tool_selection(selected, _registry(state, context))
    selected.id = str(await context.repository.append_message(state['conversation_id'], selected))
    identity = {'tool': call.name, 'tool_call_id': call.id, 'origin': 'agent'}
    runtime.stream_writer({'event': 'status', 'data': {**identity, 'status': 'running'}})
    started = time.monotonic()
    # 同值外层工具期限会抢先取消执行器，必须只让执行器拥有匹配 tool_timeout 的机会。
    async with asyncio.timeout_at(context.deadline):
        outcome = await context.executor.execute(call, _registry(state, context))
    ensure_answer_active(context.deadline)
    result = ToolMessage(json.dumps(outcome.content, ensure_ascii=False, separators=(',', ':'), allow_nan=False),
        tool_call_id=call.id, name=call.name, status=outcome.status)
    result.id = str(await context.repository.append_message(state['conversation_id'], result))
    trace = {'node': 'tool_node', 'origin': 'agent', 'name': call.name, 'tool_call_id': call.id,
        'status': outcome.status, 'attempts': outcome.attempts, 'elapsed_seconds': time.monotonic() - started}
    update = {'messages': [*state['messages'], selected, result], 'selected': None,
        'tool_trace': [*state['tool_trace'], trace], 'tool_call_count': state['tool_call_count'] + 1}
    runtime.stream_writer({'event': 'status', 'data': {**identity, 'status': 'completed', 'result_status': outcome.status}})
    log_node(state, 'tool_node', **{key: value for key, value in trace.items() if key != 'node'})
    if call.name == 'query_faq' and outcome.status == 'error':
        error = outcome.content.get('error', {})
        if error.get('code') not in ('invalid_arguments', 'invalid_keyword'):
            # 先形成完整状态更新，再由收敛节点抛服务错误，不能丢失配对和计数。
            return {**update, 'tool_error': error}
    try:
        packet = _packet({**state, **update}, context, agent_final_system(state['intent'], 'answer'))
        reserve_call(packet.messages, [], _ledger(state, _limits(context)),
            output_limit=_limits(context).final_output_tokens, final_reserve=0)
    except (InputTooLong, ServiceError) as exc:
        if exc.code not in ('input_too_long', 'token_budget'):
            raise
        return {**update, 'stop_reason': 'token_budget'}
    if call.name == 'query_faq' and outcome.status == 'success':
        quality = await _check_evidence(state, context, packet)
        update.update(quality=quality, evidence_payload=packet.payload, citations=[asdict(c) for c in packet.citations])
    return update


def _after_decision(state):
    """合法单申请才执行工具；控制或安全停止统一进入收敛节点。"""
    return 'tool_node' if state.get('selected') is not None else 'finalize_answer'


def _after_tool(state):
    """限额或新证据拒绝立即结束，其他完整结果回灌到下一决策。"""
    return 'finalize_answer' if state.get('tool_error') or state.get('stop_reason') or state['quality'].get('useful') is False else 'llm_call'


async def finalize_answer(state: _AgentState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """只用原512模型流式回答一次，正常结束/引用/非事实守卫通过后才设置 final 状态。"""
    context, limits = runtime.context, _limits(runtime.context)
    ensure_answer_active(context.deadline)
    if state.get('tool_error'):
        error = state['tool_error']
        raise ServiceError(error.get('code', 'tool_execution_error'),
            error.get('message', '知识检索未能完成，请稍后重试。'), 502)
    if state.get('stop_reason'):
        runtime.stream_writer({'event': 'citations', 'data': {'citations': []}})
        runtime.stream_writer({'event': 'delta', 'data': {'text': UNFINISHED_ANSWER}})
        return {'final_answer': UNFINISHED_ANSWER, 'reply_mode': 'answer', 'suggested_actions': ['handoff'], 'quality': {}, 'citations': []}
    try:
        packet = _packet(state, context, agent_final_system(state['intent'], state['reply_mode']))
        ledger = _ledger(state, limits)
        reserve_call(packet.messages, [], ledger, output_limit=limits.final_output_tokens, final_reserve=0)
    except (InputTooLong, ServiceError) as exc:
        if exc.code not in ('input_too_long', 'token_budget'):
            raise
        runtime.stream_writer({'event': 'citations', 'data': {'citations': []}})
        runtime.stream_writer({'event': 'delta', 'data': {'text': UNFINISHED_ANSWER}})
        return {'final_answer': UNFINISHED_ANSWER, 'reply_mode': 'answer', 'suggested_actions': ['handoff'], 'quality': {}, 'citations': []}
    _, _, _, payloads = _parts(state)
    has_faq = any('matches' in payload for payload in payloads)
    clarification = state['reply_mode'] == 'clarification' and state['route'] == 'business'
    quality = {}
    if has_faq and not clarification:
        quality = state['quality'] if packet.payload == state['evidence_payload'] and state['quality'] else await _check_evidence(state, context, packet)
        if not quality['useful']:
            runtime.stream_writer({'event': 'citations', 'data': {'citations': [asdict(c) for c in packet.citations]}})
            runtime.stream_writer({'event': 'delta', 'data': {'text': KNOWLEDGE_FALLBACK}})
            return {'quality': quality, 'final_answer': KNOWLEDGE_FALLBACK, 'reply_mode': 'answer',
                'suggested_actions': ['handoff'], 'citations': [asdict(c) for c in packet.citations], 'evidence_payload': packet.payload}
    elif not clarification and (state['route'] == 'knowledge' or not any('error' not in p and 'matches' not in p for p in payloads)):
        raise ServiceError('invalid_answer', '当前结果不足以生成事实回答，请补充必要信息。', 502)
    if clarification:
        quality = QualityDecision(useful=True, reason='本轮只追问必要业务参数。', response_kind='clarification', source=None).model_dump()
    model = model_with_output_budget(context.model, context.settings, limits.final_output_tokens)
    runtime.stream_writer({'event': 'citations', 'data': {'citations': [] if clarification else [asdict(c) for c in packet.citations]}})
    collector, aggregate = FinalAnswerStream(), None
    context.upstream = model.astream(packet.messages)
    try:
        async with asyncio.timeout(remaining_timeout(context, context.settings.llm_timeout_seconds)):
            async for chunk in context.upstream:
                ensure_answer_active(context.deadline)
                text = collector.accept(chunk)
                aggregate = chunk if aggregate is None else aggregate + chunk
                if text:
                    runtime.stream_writer({'event': 'delta', 'data': {'text': text}})
        answer = collector.complete(context.deadline)
        if quality:
            validate_answer(answer, collector.reasons, packet, QualityDecision.model_validate(quality))
        if not clarification:
            validate_business_answer(answer, packet, payloads)
        record_usage(aggregate, ledger, estimated_input=estimate_call_input(packet.messages, []), output_limit=limits.final_output_tokens)
        if ledger.spent > ledger.budget:
            raise ServiceError('token_budget', '本轮模型预算不足，无法保存回答。', 422)
        ensure_answer_active(context.deadline)
        log_node(state, 'finalize_answer', usage=_usage(ledger))
        return {'final_answer': answer, 'quality': quality, 'usage': _usage(ledger), 'evidence_payload': packet.payload,
            'citations': [] if clarification else [asdict(c) for c in packet.citations]}
    except (TimeoutError, httpx.TimeoutException, APITimeoutError) as exc:
        raise ServiceError('upstream_timeout', '模型响应超时，请稍后重试。', 504) from exc
    except ServiceError:
        raise
    except Exception as exc:
        raise ServiceError('upstream_error', '模型服务暂时不可用，请稍后重试。', 502) from exc
    finally:
        upstream, context.upstream = context.upstream, None
        await close_answer_stream(upstream)


def build_agent_graph():
    """编译每次调用作用域子图，父图负责检查点和唯一最终 SQL 提交。"""
    builder = StateGraph(_AgentState, context_schema=WorkflowRuntime, output_schema=WorkflowState)
    builder.add_node('llm_call', llm_call)
    builder.add_node('tool_node', tool_node)
    builder.add_node('finalize_answer', finalize_answer)
    builder.add_edge(START, 'llm_call')
    builder.add_conditional_edges('llm_call', _after_decision, ['tool_node', 'finalize_answer'])
    builder.add_conditional_edges('tool_node', _after_tool, ['llm_call', 'finalize_answer'])
    builder.add_edge('finalize_answer', END)
    return builder.compile(checkpointer=None).with_config({'recursion_limit': 32})
