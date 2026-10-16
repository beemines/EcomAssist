"""主力 ReAct 子图：受限读取、完整 SQL 配对、证据闸及唯一最终流。"""
import asyncio
import json
import logging
import time
from dataclasses import asdict
from typing import Literal
from uuid import uuid4

import httpx
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from openai import APITimeoutError
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.agent.bare import UNFINISHED_ANSWER
from app.agent.controls import AgentLimits, ToolProtocolError, UsageLedger, call_signature, estimate_call_input, parse_tool_selection, record_usage, reserve_call, tool_protocol_diagnostic
from app.core.answer_validation import FinalAnswerStream, close_answer_stream, ensure_answer_active, validate_answer, validate_business_answer
from app.core.errors import InputTooLong, ServiceError
from app.core.evidence import build_agent_evidence
from app.core.extraction import invalid_output, validate_structured_output
from app.core.llm import model_with_output_budget
from app.core.sufficiency import QualityDecision
from app.tools.schemas import FAQArgs
from app.tools.types import ToolCall
from app.workflow.nodes import assess_sufficiency, log_node, remaining_timeout, prompt_current, observe_usage
from app.workflow.after_sales import AfterSalesControl, parse_after_sales_control, resolve_order_anchor, validate_after_sales_control
from app.workflow.prompts import KNOWLEDGE_FALLBACK, agent_decision_system, agent_final_system
from app.workflow.runtime import WorkflowRuntime
from app.workflow.state import WorkflowState


logger = logging.getLogger(__name__)
INTERNAL_RESPONSE_CONTROL = 'internal_response_control'
MOCK_DATA_NOTICE = '本轮订单、物流等业务信息为模拟演示数据，仅供参考。\n\n'


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
    selected_origin: Literal['agent', 'workflow']
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
    if state['route'] in ('knowledge', 'after_sales'):
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
    return build_agent_evidence(system=system, turns=turns, current=prompt_current(state, current),
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


async def _check_evidence(state, runtime, packet):
    """新增 FAQ 与实际最终副本均执行真实重排门槛，外部故障保持 ServiceError。"""
    context = runtime.context
    threshold = context.settings.rerank_min_score
    if packet.strategy != 'hybrid_rerank' or threshold is None:
        raise ValueError('online knowledge gate requires hybrid_rerank and calibrated threshold')
    if not packet.citations or packet.best_score is None or packet.best_score < threshold:
        return {'useful': False, 'reason': '当前知识证据为空或低于已校准重排门槛。',
            'response_kind': 'knowledge', 'source': 'retrieval_low_conf'}, state['stage_usage']
    decision, stages = await assess_sufficiency(state, runtime, packet)
    return decision.model_dump(), stages


def _current_read(state):
    """完整查单/物流只认可同轮同工具同订单的成功配对；失败读取禁止自动重试。"""
    if state['route'] != 'business' or state['intent'] not in ('订单', '物流'):
        return None
    turns, _, pending, _ = _parts(state)
    order = resolve_order_anchor(state['raw_question'], state['resolved_question'],
        [message for turn in turns for message in turn])
    if order is None:
        return None
    name = 'query_logistics' if state['intent'] == '物流' else 'query_order'
    for request, result in zip(pending[::2], pending[1::2]):
        if not isinstance(request, AIMessage) or not isinstance(result, ToolMessage):
            continue
        call = request.tool_calls[0]
        if call['name'] == name and call['args'].get('order_id') == order and result.tool_call_id == call['id']:
            payload = json.loads(result.content)
            success = result.status == 'success' and 'error' not in payload and payload.get('order_id') == order
            return name, order, 'success' if success else 'failed'
    return name, order, 'missing'


def _attempt(ledger, messages, schema, output):
    """进入收费边界前保守记一次尝试，后续用实际usage替换本次估算。"""
    estimate = estimate_call_input(messages, schema)
    record_usage(None, ledger, estimated_input=estimate, output_limit=output)
    return estimate


def _settle(state, context, ledger, reply, estimate, output):
    """替换本次预留并同步发布快照，失败/取消不依赖丢失的图更新。"""
    ledger.estimated -= estimate + output
    ledger.estimated_calls -= 1
    record_usage(reply, ledger, estimated_input=estimate, output_limit=output)
    observe_usage(context, {'usage': _usage(ledger), 'stage_usage': state['stage_usage']})


async def llm_call(state: _AgentState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """最多五次决策并预留最终预算；协议失败仅记录不含正文的白名单诊断。"""
    context, limits = runtime.context, _limits(runtime.context)
    ensure_answer_active(context.deadline)
    if state['decision_count'] >= limits.max_decisions:
        return {'stop_reason': 'step_limit', 'selected': None}
    registry = _registry(state, context)
    if INTERNAL_RESPONSE_CONTROL in context.registry:
        raise ValueError('Internal response control conflicts with business registry')
    control_type = AfterSalesControl if state['route'] == 'after_sales' else AgentControl
    control_schema = convert_to_openai_tool(control_type)
    control_schema['function'].update(name=INTERNAL_RESPONSE_CONTROL,
        description='内部响应控制：证据已足够或需要澄清时选择，只设置最终回复模式与建议，不执行业务动作。')
    schema = [convert_to_openai_tool(tool) for tool in registry.values()] + [control_schema]
    ledger = _ledger(state, limits)
    try:
        packet = _packet(state, context, agent_decision_system(state['intent'], after_sales=state['route'] == 'after_sales'), schema)
        final_packet = _packet(state, context, agent_final_system(state['intent'], state['reply_mode'], after_sales=state['route'] == 'after_sales', refund_decision=state.get('refund_decision'), decision_reason=state.get('decision_reason')))
        final_reserve = estimate_call_input(final_packet.messages, []) + limits.final_output_tokens
        reserve_call(packet.messages, schema, ledger, output_limit=limits.decision_output_tokens,
            final_reserve=final_reserve)
    except (InputTooLong, ServiceError) as exc:
        if exc.code not in ('input_too_long', 'token_budget'):
            raise
        return {'stop_reason': 'token_budget', 'selected': None}
    model = model_with_output_budget(context.decision_model, context.settings, limits.decision_output_tokens)
    if isinstance(model, ChatOpenAI):
        # BigModel仅支持auto；JSON模式经extra_body进入同次HTTP请求，避免SDK
        # 顶层response_format触发strict工具自动解析。仅改副本，最终流不带该格式。
        model = model.model_copy(update={'extra_body': {**(model.extra_body or {}),
            'response_format': {'type': 'json_object'}}}, deep=False)
    required = _current_read(state)
    bound = model.bind_tools([*registry.values(), control_schema], tool_choice='auto', parallel_tool_calls=False)
    selected = None
    estimate = _attempt(ledger, packet.messages, schema, limits.decision_output_tokens)
    try:
        async with asyncio.timeout(remaining_timeout(context, context.settings.llm_timeout_seconds)):
            selected = await bound.ainvoke(packet.messages)
    except (TimeoutError, httpx.TimeoutException, APITimeoutError) as exc:
        raise ServiceError('upstream_timeout', '模型响应超时，请稍后重试。', 504) from exc
    except ServiceError:
        raise
    except Exception as exc:
        raise ServiceError('upstream_error', '模型服务暂时不可用，请稍后重试。', 502) from exc
    finally:
        _settle(state, context, ledger, selected, estimate, limits.decision_output_tokens)
    ensure_answer_active(context.deadline)
    try:
        # 仅本次协议解析允许内部控制；执行器和持久化仍只持有业务注册表。
        call = parse_tool_selection(selected, {**registry, INTERNAL_RESPONSE_CONTROL: control_type})
    except ToolProtocolError as exc:
        # 默认 WARNING 和普通消息格式也可见，不能附带上游异常或整个模型对象。
        logger.warning(json.dumps({'event': 'agent_tool_protocol_failure',
            'conversation_id': state['conversation_id'], 'user_message_id': state['user_message_id'],
            'reason': exc.reason.value, **tool_protocol_diagnostic(selected), 'usage': _usage(ledger)},
            ensure_ascii=True, separators=(',', ':'), allow_nan=False))
        raise
    update = {'decision_count': state['decision_count'] + 1, 'usage': _usage(ledger), 'selected': None, 'selected_origin': 'agent', 'stop_reason': None}
    native_control = call is not None and call.name == INTERNAL_RESPONSE_CONTROL
    transport = 'native_control' if native_control else 'json_control' if call is None else 'business_tool'
    log_node(state, 'llm_call', decision_count=update['decision_count'], usage=update['usage'], decision_transport=transport)
    if ledger.remaining < final_reserve:
        return {**update, 'stop_reason': 'token_budget'}
    if call is not None and selected.text.strip():
        logger.warning(json.dumps({'event': 'agent_decision_protocol_failure',
            'conversation_id': state['conversation_id'], 'user_message_id': state['user_message_id'],
            'reason': 'tool_body', **tool_protocol_diagnostic(selected), 'usage': _usage(ledger)},
            ensure_ascii=True, separators=(',', ':'), allow_nan=False))
        raise invalid_output()
    _, _, pending, _ = _parts(state)
    requests = [message for message in pending if isinstance(message, AIMessage)]
    if call is not None and any(request.tool_calls[0]['id'] == call.id for request in requests):
        raise ServiceError('upstream_error', '模型重复使用了工具调用标识。', 502)
    if call is None or native_control:
        try:
            if native_control:
                try:
                    control = control_type.model_validate(call.args)
                except ValidationError as exc:
                    raise invalid_output() from exc
                if state['route'] == 'after_sales':
                    control = validate_after_sales_control(control, state['intent'])
            else:
                # JSON模式只约束语法；正文仍按原严格Schema校验，不做修补。
                control = parse_after_sales_control(selected, state['intent']) if state['route'] == 'after_sales' else _control(selected)
        except ServiceError as exc:
            if exc.code == 'invalid_structured_output':
                logger.warning(json.dumps({'event': 'agent_decision_protocol_failure',
                    'conversation_id': state['conversation_id'], 'user_message_id': state['user_message_id'],
                    'reason': 'control_schema', **tool_protocol_diagnostic(selected), 'usage': _usage(ledger)},
                    ensure_ascii=True, separators=(',', ':'), allow_nan=False))
            raise
        if required is None:
            return {**update, **control.model_dump()}
        name, order, status = required
        if status == 'failed':
            raise ServiceError('invalid_answer', '当前订单读取未成功，请稍后重试。', 502)
        if status == 'success':
            return {**update, **control.model_dump(), 'reply_mode': 'answer'}
        # 只替代缺当前观测的终止控制，不增加决策循环或绕过既有四次工具/预算检查。
        identifier = 'agent_current_' + uuid4().hex
        selected = AIMessage('', tool_calls=[{'id': identifier, 'name': name, 'args': {'order_id': order}}],
            response_metadata={'finish_reason': 'tool_calls', 'origin': 'workflow'})
        update['selected_origin'] = 'workflow'
        call = ToolCall(identifier, name, {'order_id': order})
    selected, call = _normalize(selected, call, state['raw_question'])
    if any(call_signature(ToolCall(request.tool_calls[0]['id'], request.tool_calls[0]['name'],
            request.tool_calls[0]['args'])) == call_signature(call) for request in requests):
        return {**update, 'stop_reason': 'repeat_call'}
    if state['tool_call_count'] >= limits.max_tool_calls:
        return {**update, 'stop_reason': 'step_limit'}
    # 完整占位配对先验证参数输入，停止时不持久化孤立请求。
    placeholder = ToolMessage('{}', tool_call_id=call.id)
    try:
        future = {**state, 'messages': [*state['messages'], selected, placeholder]}
        future_packet = _packet(future, context, agent_final_system(state['intent'], 'answer', after_sales=state['route'] == 'after_sales', refund_decision=state.get('refund_decision'), decision_reason=state.get('decision_reason')))
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
    origin = state.get('selected_origin', 'agent')
    identity = {'tool': call.name, 'tool_call_id': call.id, 'origin': origin}
    runtime.stream_writer({'event': 'status', 'data': {**identity, 'status': 'running'}})
    started = time.monotonic()
    # 同值外层工具期限会抢先取消执行器，必须只让执行器拥有匹配 tool_timeout 的机会。
    async with asyncio.timeout_at(context.deadline):
        outcome = await context.executor.execute(call, _registry(state, context))
    ensure_answer_active(context.deadline)
    result = ToolMessage(json.dumps(outcome.content, ensure_ascii=False, separators=(',', ':'), allow_nan=False),
        tool_call_id=call.id, name=call.name, status=outcome.status)
    result.id = str(await context.repository.append_message(state['conversation_id'], result))
    trace = {'node': 'tool_node', 'origin': origin, 'name': call.name, 'tool_call_id': call.id,
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
        packet = _packet({**state, **update}, context, agent_final_system(state['intent'], 'answer', after_sales=state['route'] == 'after_sales', refund_decision=state.get('refund_decision'), decision_reason=state.get('decision_reason')))
        reserve_call(packet.messages, [], _ledger(state, _limits(context)),
            output_limit=_limits(context).final_output_tokens, final_reserve=0)
    except (InputTooLong, ServiceError) as exc:
        if exc.code not in ('input_too_long', 'token_budget'):
            raise
        return {**update, 'stop_reason': 'token_budget'}
    if call.name == 'query_faq' and outcome.status == 'success':
        quality, stages = await _check_evidence(state, runtime, packet)
        update.update(quality=quality, stage_usage=stages, evidence_payload=packet.payload, citations=[asdict(c) for c in packet.citations])
    return update


def _after_decision(state):
    """合法单申请才执行工具；控制或安全停止统一进入收敛节点。"""
    return 'tool_node' if state.get('selected') is not None else 'finalize_answer'


def _after_tool(state):
    """限额或新证据拒绝立即结束，其他完整结果回灌到下一决策。"""
    return 'finalize_answer' if state.get('tool_error') or state.get('stop_reason') or state['quality'].get('useful') is False else 'llm_call'


async def finalize_answer(state: _AgentState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """证据闸后按实际回复模式验证唯一512流；两路澄清都必须通过非事实守卫。"""
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
        packet = _packet(state, context, agent_final_system(state['intent'], state['reply_mode'], after_sales=state['route'] == 'after_sales', refund_decision=state.get('refund_decision'), decision_reason=state.get('decision_reason')))
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
    clarification = state['reply_mode'] == 'clarification'
    quality = {}
    stages = state['stage_usage']
    if has_faq:
        if packet.payload == state['evidence_payload'] and state['quality']:
            quality = state['quality']
        else:
            quality, stages = await _check_evidence(state, runtime, packet)
        if not quality['useful']:
            runtime.stream_writer({'event': 'citations', 'data': {'citations': [asdict(c) for c in packet.citations]}})
            runtime.stream_writer({'event': 'delta', 'data': {'text': KNOWLEDGE_FALLBACK}})
            return {'quality': quality, 'stage_usage': stages, 'final_answer': KNOWLEDGE_FALLBACK, 'reply_mode': 'answer',
                'suggested_actions': ['handoff'], 'citations': [asdict(c) for c in packet.citations], 'evidence_payload': packet.payload}
    elif not clarification and (state['route'] == 'knowledge' or not any('error' not in p and 'matches' not in p for p in payloads)):
        raise ServiceError('invalid_answer', '当前结果不足以生成事实回答，请补充必要信息。', 502)
    if clarification:
        quality = QualityDecision(useful=True, reason='本轮只追问必要业务参数。', response_kind='clarification', source=None).model_dump()
    model = model_with_output_budget(context.model, context.settings, limits.final_output_tokens)
    runtime.stream_writer({'event': 'citations', 'data': {'citations': [] if clarification else [asdict(c) for c in packet.citations]}})
    collector, aggregate = FinalAnswerStream(), None
    notice = MOCK_DATA_NOTICE if not clarification and any(
        p.get('mock') is True and 'error' not in p and 'matches' not in p for p in payloads) else ''
    notice_sent = False
    estimate = _attempt(ledger, packet.messages, [], limits.final_output_tokens)
    try:
        context.upstream = model.astream(packet.messages)
        async with asyncio.timeout(remaining_timeout(context, context.settings.llm_timeout_seconds)):
            async for chunk in context.upstream:
                aggregate = chunk if aggregate is None else aggregate + chunk
                ensure_answer_active(context.deadline)
                text = collector.accept(chunk)
                # 静态说明计入最终保存限制，但不进入原始流校验或模型usage。
                if collector.characters + len(notice) > 20000 or collector.utf8_bytes + len(notice.encode('utf-8')) > 65535:
                    raise ServiceError('upstream_error', '模型回复超出可保存长度。', 502)
                if text and not clarification:
                    if notice and not notice_sent:
                        runtime.stream_writer({'event': 'delta', 'data': {'text': notice}})
                        notice_sent = True
                    runtime.stream_writer({'event': 'delta', 'data': {'text': text}})
        answer = notice + collector.complete(context.deadline)
        if quality:
            validate_answer(answer, collector.reasons, packet, QualityDecision.model_validate(quality))
        if not clarification:
            validate_business_answer(answer, packet, payloads)
        _settle(state, context, ledger, aggregate, estimate, limits.final_output_tokens)
        estimate = None
        if ledger.spent > ledger.budget:
            raise ServiceError('token_budget', '本轮模型预算不足，无法保存回答。', 422)
        ensure_answer_active(context.deadline)
        if clarification:
            runtime.stream_writer({'event': 'delta', 'data': {'text': answer}})
        log_node(state, 'finalize_answer', usage=_usage(ledger))
        return {'final_answer': answer, 'quality': quality, 'stage_usage': stages, 'usage': _usage(ledger), 'evidence_payload': packet.payload,
            'citations': [] if clarification else [asdict(c) for c in packet.citations]}
    except (TimeoutError, httpx.TimeoutException, APITimeoutError) as exc:
        raise ServiceError('upstream_timeout', '模型响应超时，请稍后重试。', 504) from exc
    except ServiceError:
        raise
    except Exception as exc:
        raise ServiceError('upstream_error', '模型服务暂时不可用，请稍后重试。', 502) from exc
    finally:
        if estimate is not None:
            _settle(state, context, ledger, aggregate, estimate, limits.final_output_tokens)
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
