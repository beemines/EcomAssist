"""主力 ReAct 子图：受限读取、完整 SQL 配对、证据闸及唯一最终流。"""
import asyncio
import json
import logging
import time
from dataclasses import asdict
from collections.abc import Mapping
from typing import Literal
from uuid import uuid4

import httpx
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from openai import APITimeoutError, ContentFilterFinishReasonError, LengthFinishReasonError
from pydantic import ValidationError

from app.agent.bare import UNFINISHED_ANSWER
from app.agent.controls import AgentLimits, ToolProtocolError, UsageLedger, call_signature, parse_tool_selection, record_usage, tool_protocol_diagnostic
from app.core.answer_validation import FinalAnswerStream, close_answer_stream, ensure_answer_active, validate_answer, validate_business_answer
from app.core.errors import InputTooLong, ServiceError
from app.core.evidence import EvidencePacket
from app.core.extraction import invalid_output
from app.core.llm import model_with_output_budget
from app.core.sufficiency import QualityDecision
from app.tools.schemas import FAQArgs
from app.tools.types import ToolCall
from app.tools.catalog_types import BoundCatalog
from app.workflow.tool_calls import execution_context
from app.workflow.nodes import assess_sufficiency, log_node, remaining_timeout, observe_usage
from app.workflow.after_sales import resolve_order_anchor
from app.workflow.controls import UnifiedAgentControl, parse_control, validate_control, stable_tool_schema
from app.workflow.context_budget import workflow_packet, runtime_settings, runtime_snapshot, turn_token_limit, reserve_context_call
from app.context.tokens import estimate_payload as estimate_call_input
from app.context.layers import ContextCapacityError
from app.context.logging import log_model_call, log_calibration
from app.workflow.entities import validate_snapshot_entities, explicit_order_ids
from app.workflow.prompts import KNOWLEDGE_FALLBACK, agent_decision_system, agent_final_system
from app.workflow.runtime import WorkflowRuntime
from app.workflow.recovery import recover_generation
from app.workflow.state import WorkflowState
from app.workflow.history import replay_turns


logger = logging.getLogger(__name__)
INTERNAL_RESPONSE_CONTROL = 'internal_response_control'
MOCK_DATA_NOTICE = '本轮订单、物流等业务信息为模拟演示数据，仅供参考。\n\n'
ORDER_NOT_FOUND_ANSWER = '当前账号下未找到该订单，请核对订单号后再查询。'


AgentControl = UnifiedAgentControl
reserve_call = reserve_context_call


class _AgentState(WorkflowState, total=False):
    selected: AIMessage | None
    selected_origin: Literal['agent', 'workflow']
    stop_reason: str | None
    tool_error: dict | None


def _limits(context: WorkflowRuntime) -> AgentLimits:
    from app.workflow.context_budget import workflow_budget
    settings = runtime_settings(context.settings)
    budget = context.context_snapshot.budget if context.context_snapshot else workflow_budget(settings, context.registry)
    return AgentLimits(max_tool_calls=settings.max_agent_steps, max_decisions=settings.max_agent_steps+1,
        total_token_budget=turn_token_limit(settings, budget), final_output_tokens=settings.max_output_tokens,
        decision_output_tokens=settings.agent_decision_max_output_tokens, input_token_budget=budget.window)


def _ledger(state, limits):
    """从持久化四项成本恢复账本，包含父图已发生的分类成本。"""
    sufficiency = state['stage_usage'].get('sufficiency', {})
    spent = sum(sufficiency.get(key, 0) for key in ('actual', 'estimated'))
    return UsageLedger(budget=max(1, limits.total_token_budget-spent), **state['usage'])


def _usage(ledger):
    """只把可序列化成本写入状态，不将运行期客户端持久化。"""
    return {key: getattr(ledger, key) for key in ('actual', 'estimated', 'actual_calls', 'estimated_calls')}


def _registry(state, context):
    """只开放读取工具，已强制检索的知识轮排除 FAQ。"""
    if isinstance(context.registry, BoundCatalog):
        names = []
        for name in context.registry:
            definition = context.registry.definition(name)
            if definition.allowed_intents and state['intent'] not in definition.allowed_intents:
                continue
            if definition.operation == 'write' and (state['intent'] != '工单' or not state.get('ticket_request')):
                continue
            if name == 'query_faq' and state['route'] in ('knowledge', 'after_sales'):
                continue
            names.append(name)
        return context.registry.subset(names)
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
    turns = replay_turns(messages[:index])
    pending = messages[index + 1:]
    payloads = [json.loads(message.content) for message in pending if isinstance(message, ToolMessage)]
    return turns, messages[index], pending, payloads


def _packet(state, context, system: SystemMessage, schema=()):
    return workflow_packet(state, context, phase='decision' if schema else 'final', tools=schema)


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


def _current_read(state, context):
    """同轮同工具同订单配对区分成功、业务未找到与真正失败，均不自动重试。"""
    if state['route'] != 'business' or state['intent'] not in ('订单', '物流'):
        return None
    turns, _, pending, _ = _parts(state)
    if context.context_snapshot is not None:
        validate_snapshot_entities(state['raw_question'], state['resolved_question'],
            context.context_snapshot, context.context_provenance)
        identifiers = explicit_order_ids(state['raw_question']) or explicit_order_ids(state['resolved_question'])
        order = next(iter(identifiers)) if len(identifiers) == 1 else None
    else:
        order = resolve_order_anchor(state['raw_question'], state['resolved_question'],
            [message for turn in turns for message in turn])
    if order is None:
        return None
    name = 'query_logistics' if state['intent'] == '物流' else 'query_order'
    for request, result in zip(pending[::2], pending[1::2]):
        if not isinstance(request, AIMessage) or not isinstance(result, ToolMessage):
            continue
        call = request.tool_calls[0]
        argument = 'order_id'
        eligible = call['name'] == name
        if isinstance(context.registry, BoundCatalog) and call['name'] in context.registry:
            definition = context.registry.definition(call['name'])
            if (definition.operation == 'read' and definition.order_id_arg
                    and (not definition.allowed_intents or state['intent'] in definition.allowed_intents)):
                eligible, argument = True, definition.order_id_arg
        if eligible and call['args'].get(argument) == order and result.tool_call_id == call['id']:
            name = call['name']
            payload = json.loads(result.content)
            success = result.status == 'success' and 'error' not in payload and payload.get('order_id') == order
            if (result.status == 'error' and set(payload) == {'error'}
                    and isinstance(payload['error'], dict) and payload['error'].get('code') == 'not_found'):
                return name, order, 'not_found'
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


def _native_read_stop(selected, state, context, registry):
    """Native stop can request final generation; its unchecked prose is discarded."""
    if (not isinstance(registry, BoundCatalog) or state['route'] != 'business'
            or state['intent'] not in ('订单', '物流') or state.get('ticket_request')
            or not selected.text.strip() or selected.text.lstrip().startswith(('{', '[', '`'))):
        return False
    current = _current_read(state, context)
    if current is None or current[2] != 'success':
        return False
    _, _, pending, _ = _parts(state)
    if not pending or len(pending) % 2:
        return False
    for request, result in zip(pending[::2], pending[1::2]):
        if (not isinstance(request, AIMessage) or len(request.tool_calls) != 1
                or not isinstance(result, ToolMessage) or result.status != 'success'):
            return False
        call = request.tool_calls[0]
        if (call['name'] not in registry or registry.definition(call['name']).operation != 'read'
                or result.tool_call_id != call['id']):
            return False
        payload = json.loads(result.content)
        if not isinstance(payload, dict) or 'error' in payload:
            return False
    return True


async def _decision_attempt(state, context, limits, ledger, packet, schema, registry, bound):
    """Generate and strictly parse once, before any selected tool escapes the node."""
    control_type = UnifiedAgentControl
    timeout = remaining_timeout(context, context.settings.llm_timeout_seconds)
    selected = None
    control = None
    estimate = _attempt(ledger, packet.messages, schema, limits.decision_output_tokens)
    log_model_call(context.context_logger, packet, conversation_id=state['conversation_id'],
                   user_message_id=state['user_message_id'], phase='decision', call_index=state['decision_count']+1,
                   on_packet=context.context_packet_observer)
    try:
        async with asyncio.timeout(timeout):
            selected = await bound.ainvoke(packet.messages)
    except LengthFinishReasonError as exc:
        raise invalid_output(finish_reason='length') from exc
    except ContentFilterFinishReasonError as exc:
        raise invalid_output(finish_reason='content_filter') from exc
    except (TimeoutError, httpx.TimeoutException, APITimeoutError) as exc:
        raise ServiceError('upstream_timeout', '模型响应超时，请稍后重试。', 504) from exc
    except ServiceError:
        raise
    except Exception as exc:
        raise ServiceError('upstream_error', '模型服务暂时不可用，请稍后重试。', 502) from exc
    finally:
        _settle(state, context, ledger, selected, estimate, limits.decision_output_tokens)
        log_calibration(context.context_logger, packet, selected, phase='decision',
                        on_calibration=context.context_calibration_observer)
    ensure_answer_active(context.deadline)
    try:
        # 仅本次协议解析允许内部控制；执行器和持久化仍只持有业务注册表。
        call = parse_tool_selection(selected, {**registry, INTERNAL_RESPONSE_CONTROL: control_type},
            allow_unknown=isinstance(registry, BoundCatalog))
    except ToolProtocolError as exc:
        # 默认 WARNING 和普通消息格式也可见，不能附带上游异常或整个模型对象。
        logger.warning(json.dumps({'event': 'agent_tool_protocol_failure',
            'conversation_id': state['conversation_id'], 'user_message_id': state['user_message_id'],
            'reason': exc.reason.value, **tool_protocol_diagnostic(selected), 'usage': _usage(ledger)},
            ensure_ascii=True, separators=(',', ':'), allow_nan=False))
        exc.finish_reason = selected.response_metadata.get('finish_reason') if isinstance(selected, AIMessage) else None
        raise
    native_control = call is not None and call.name == INTERNAL_RESPONSE_CONTROL
    transport = 'native_control' if native_control else 'json_control' if call is None else 'business_tool'
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
    if call is None and _native_read_stop(selected, state, context, registry):
        # parse_tool_selection already verified finish=stop and no hidden/native calls.
        # Never persist, stream, or feed the draft into final generation. Existing
        # final reserve, evidence and answer validators still govern that stage.
        control = UnifiedAgentControl(reply_mode='answer', suggested_actions=[],
            refund_decision=None, decision_reason=None)
        return selected, None, control, 'native_read_stop'
    if call is None or native_control:
        try:
            if native_control:
                try:
                    control = control_type.model_validate(call.args)
                except ValidationError as exc:
                    raise invalid_output() from exc
                control = validate_control(control, route=state['route'], intent=state['intent'])
            else:
                # JSON模式只约束语法；正文仍按原严格Schema校验，不做修补。
                control = parse_control(selected, route=state['route'], intent=state['intent'])
        except ServiceError as exc:
            if exc.code == 'invalid_structured_output':
                logger.warning(json.dumps({'event': 'agent_decision_protocol_failure',
                    'conversation_id': state['conversation_id'], 'user_message_id': state['user_message_id'],
                    'reason': 'control_schema', **tool_protocol_diagnostic(selected), 'usage': _usage(ledger)},
                    ensure_ascii=True, separators=(',', ':'), allow_nan=False))
                if context.context_logger is not None:
                    try:
                        text = selected.text
                        fields = {'conversation_id': state['conversation_id'],
                            'user_message_id': state['user_message_id'], 'transport': transport,
                            'finish_reason': selected.response_metadata.get('finish_reason'),
                            'control_text': text[:8192], 'control_text_length': len(text),
                            'control_text_truncated': len(text) > 8192}
                        if native_control:
                            arguments = json.dumps(call.args, ensure_ascii=False, allow_nan=False)
                            fields.update(arguments_text=arguments[:8192],
                                arguments_text_length=len(arguments), arguments_text_truncated=len(arguments) > 8192)
                        context.context_logger.event('decision_control_rejected', fields)
                    except Exception:
                        # Optional evidence must never replace the original rejection or leak its body.
                        pass
            raise
    return selected, call, control, transport


def decision_transport_model(model, *, ticket_requested=False, native_catalog=False):
    if not isinstance(model, ChatOpenAI):
        return model
    body = dict(model.extra_body or {})
    if ticket_requested or native_catalog:
        # GLM在工单函数与JSON正文模式并用时会把参数作为正文；保留原生调用，
        # 控制正文仍由同一严格四字段解析器校验，绝不把正文解析成业务动作。
        body.pop('response_format', None)
    else:
        body['response_format'] = {'type': 'json_object'}
    return model.model_copy(update={'extra_body': body}, deep=False)


async def llm_call(state: _AgentState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """最多五次决策并预留最终预算；拒绝正文仅写入专用内容日志。"""
    context, limits = runtime.context, _limits(runtime.context)
    ensure_answer_active(context.deadline)
    if state['decision_count'] >= limits.max_decisions:
        return {'stop_reason': 'step_limit', 'selected': None}
    registry = _registry(state, context)
    if INTERNAL_RESPONSE_CONTROL in context.registry:
        raise ValueError('Internal response control conflicts with business registry')
    schema = stable_tool_schema(context.registry, intent=state['intent'], ticket_requested=bool(state.get('ticket_request')))
    ledger = _ledger(state, limits)
    try:
        packet, evidence = _packet(state, context, agent_decision_system(None), schema)
        final_packet, _ = _packet(state, context, agent_final_system(None, None))
        final_reserve = estimate_call_input(final_packet.messages, []) + limits.final_output_tokens
        reserve_call(packet.messages, schema, ledger, output_limit=limits.decision_output_tokens,
            final_reserve=final_reserve)
    except (InputTooLong, ServiceError) as exc:
        if isinstance(exc, ContextCapacityError):
            raise
        if exc.code not in ('input_too_long', 'token_budget'):
            raise
        return {'stop_reason': 'token_budget', 'selected': None}
    required = _current_read(state, context)
    if required is not None and required[2] == 'not_found':
        # 已完成当前账号查询且无此单，无需再付费让模型解释固定业务结果。
        log_node(state, 'order_lookup_result', name=required[0], status='not_found')
        return {'selected': None, 'reply_mode': 'answer', 'suggested_actions': [],
                'refund_decision': None, 'decision_reason': None}
    model = model_with_output_budget(context.decision_model, context.settings, limits.decision_output_tokens)
    model = decision_transport_model(model, ticket_requested=bool(state.get('ticket_request')),
                                     native_catalog=isinstance(context.registry, BoundCatalog))
    bound = model.bind_tools(schema, tool_choice='auto', parallel_tool_calls=False)
    started = time.monotonic()
    initial_usage = _usage(ledger)
    decision_count = state['decision_count']
    previous = state['stage_usage'].get('decision', {})
    def observed():
        return {'model_recovery_used': context.model_recovery_used,
            'usage': _usage(ledger), 'stage_usage': {**state['stage_usage'], 'decision': {
            **{key: previous.get(key, 0) + getattr(ledger, key) - initial_usage[key] for key in initial_usage},
            'elapsed_seconds': previous.get('elapsed_seconds', 0) + time.monotonic() - started}}}
    def reserve_recovery():
        if decision_count >= limits.max_decisions:
            raise ServiceError('token_budget', '本轮决策次数已达上限。', 422)
        reserve_call(packet.messages, schema, ledger, output_limit=limits.decision_output_tokens,
                     final_reserve=final_reserve)
    for attempt in range(2):
        before_calls = ledger.actual_calls + ledger.estimated_calls
        try:
            selected, call, control, transport = await _decision_attempt(
                {**state, 'decision_count': decision_count}, context, limits, ledger, packet, schema, registry, bound)
        except BaseException as exc:
            attempted = ledger.actual_calls + ledger.estimated_calls > before_calls
            decision_count += int(attempted)
            update = observed()
            observe_usage(context, update)
            runtime.stream_writer({'event': 'usage', 'data': {'stage': 'decision', **update}})
            if recover_generation(context, state, runtime, 'decision', exc, update['usage'],
                    attempted=attempted, reserve=reserve_recovery):
                continue
            raise
        decision_count += 1
        break
    update = {**observed(), 'decision_count': decision_count, 'selected': None,
              'selected_origin': 'agent', 'stop_reason': None}
    observe_usage(context, update)
    log_node(state, 'llm_call', decision_count=decision_count, usage=update['usage'], decision_transport=transport)
    if ledger.remaining < final_reserve:
        return {**update, 'stop_reason': 'token_budget'}
    native_control = call is not None and call.name == INTERNAL_RESPONSE_CONTROL
    _, _, pending, _ = _parts(state)
    requests = [message for message in pending if isinstance(message, AIMessage)]
    if call is None or native_control:
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
    if call.name == 'create_ticket' and isinstance(registry, BoundCatalog) and call.name in registry:
        from app.tools.validation import validate_arguments
        from app.tools.types import ToolOutcome
        validated = validate_arguments(registry.definition(call.name), call.args)
        request = state.get('ticket_request') or {}
        description = call.args.get('description')
        from app.workflow.ticket_requests import grounded_description
        if (not isinstance(validated, ToolOutcome) and isinstance(description, str)
                and grounded_description(description, request)):
            return {**update, 'ticket_proposal': {'tool_call_id': call.id, 'args': call.args},
                    'selected': None, 'final_answer': None}
    if any(call_signature(ToolCall(request.tool_calls[0]['id'], request.tool_calls[0]['name'],
            request.tool_calls[0]['args'])) == call_signature(call) for request in requests):
        return {**update, 'stop_reason': 'repeat_call'}
    if state['tool_call_count'] >= limits.max_tool_calls:
        return {**update, 'stop_reason': 'step_limit'}
    # 完整占位配对先验证参数输入，停止时不持久化孤立请求。
    placeholder = ToolMessage('{}', tool_call_id=call.id)
    try:
        future = {**state, 'messages': [*state['messages'], selected, placeholder]}
        future_packet, _ = _packet(future, context, agent_final_system(None, None))
        reserve_call(future_packet.messages, [], ledger, output_limit=limits.final_output_tokens, final_reserve=0)
    except (InputTooLong, ServiceError) as exc:
        if isinstance(exc, ContextCapacityError):
            raise
        if exc.code not in ('input_too_long', 'token_budget'):
            raise
        return {**update, 'stop_reason': 'token_budget'}
    return {**update, 'selected': selected}


async def tool_node(state: _AgentState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """执行器负责工具超时，外层仅限制整轮期限；逐个保存配对并在回灌前检查新FAQ。"""
    context = runtime.context
    ensure_answer_active(context.deadline)
    selected = state['selected'].model_copy(deep=True)
    registry = _registry(state, context)
    call = parse_tool_selection(selected, registry, allow_unknown=isinstance(registry, BoundCatalog))
    from app.repositories.faq import FAQRepository
    if call.name == 'query_faq' and isinstance(context.faq_repository, FAQRepository):
        from app.tools.business import contextual_tools
        from app.tools.types import ToolContext
        from app.retrieval.types import QueryPlan
        # Bind backend-only options for this execution, leaving model schemas and
        # other owner-bound registry tools unchanged. Injected legacy fakes keep
        # their existing retrieve signature and never gain a shared mutable plan.
        scoped = contextual_tools(context.faq_repository, None,
            ToolContext(state['conversation_id'], int(state['user_message_id']), state['raw_question'], state['category']),
            faq_options={'query_plan': QueryPlan(standard=state['resolved_question'], expansions=[]),
                         'top_k': runtime_settings(context.settings).rerank_top_k})
        scoped_tool = next(tool for tool in scoped if tool.name == 'query_faq')
        registry = registry.with_tool('query_faq', scoped_tool) if isinstance(registry, BoundCatalog) else {**registry, 'query_faq': scoped_tool}
    selected.id = str(await context.repository.append_message(state['conversation_id'], selected))
    origin = state.get('selected_origin', 'agent')
    identity = {'tool': call.name, 'tool_call_id': call.id, 'origin': origin}
    runtime.stream_writer({'event': 'status', 'data': {**identity, 'status': 'running'}})
    started = time.monotonic()
    # 同值外层工具期限会抢先取消执行器，必须只让执行器拥有匹配 tool_timeout 的机会。
    async with asyncio.timeout_at(context.deadline):
        outcome = await context.executor.execute(call, registry, context=execution_context(state, context)) if isinstance(registry, BoundCatalog) else await context.executor.execute(call, registry)
    ensure_answer_active(context.deadline)
    result = ToolMessage(json.dumps(outcome.content, ensure_ascii=False, separators=(',', ':'), allow_nan=False),
        tool_call_id=call.id, name=call.name, status=outcome.status)
    result.id = str(await context.repository.append_message(state['conversation_id'], result))
    trace = {'node': 'tool_node', 'origin': origin, 'name': call.name, 'tool_call_id': call.id,
        'status': outcome.status, 'attempts': outcome.attempts, 'elapsed_seconds': time.monotonic() - started}
    update = {'messages': [selected, result], 'selected': None,
        'tool_trace': [*state['tool_trace'], trace], 'tool_call_count': state['tool_call_count'] + 1}
    runtime.stream_writer({'event': 'status', 'data': {**identity, 'status': 'completed', 'result_status': outcome.status}})
    log_node(state, 'tool_node', **{key: value for key, value in trace.items() if key != 'node'})
    if call.name == 'query_faq' and outcome.status == 'error':
        error = outcome.content.get('error', {})
        if error.get('code') not in ('invalid_arguments', 'invalid_keyword'):
            # 先形成完整状态更新，再由收敛节点抛服务错误，不能丢失配对和计数。
            return {**update, 'tool_error': error}
    try:
        packet, evidence = _packet({**state, **update, 'messages': [*state['messages'], *update['messages']]}, context, agent_final_system(None, None))
        reserve_call(packet.messages, [], _ledger(state, _limits(context)),
            output_limit=_limits(context).final_output_tokens, final_reserve=0)
    except (InputTooLong, ServiceError) as exc:
        if exc.code not in ('input_too_long', 'token_budget'):
            raise
        return {**update, 'stop_reason': 'context_capacity' if isinstance(exc, ContextCapacityError) else 'token_budget'}
    if call.name == 'query_faq' and outcome.status == 'success':
        quality, stages = await _check_evidence(state, runtime, evidence)
        update.update(quality=quality, stage_usage=stages, evidence_payload=evidence.payload, citations=[asdict(c) for c in evidence.citations])
    return update


def _after_decision(state):
    """合法单申请才执行工具；控制或安全停止统一进入收敛节点。"""
    if state.get('ticket_proposal'):
        return END
    return 'tool_node' if state.get('selected') is not None else 'finalize_answer'


def _after_tool(state):
    """限额或新证据拒绝立即结束，其他完整结果回灌到下一决策。"""
    return 'finalize_answer' if state.get('tool_error') or state.get('stop_reason') or state['quality'].get('useful') is False else 'llm_call'


async def finalize_answer(state: _AgentState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """证据闸后按实际回复模式验证唯一最终流；澄清须通过非事实守卫。"""
    context, limits = runtime.context, _limits(runtime.context)
    ensure_answer_active(context.deadline)
    if (state.get('intent') == '工单' and state.get('reply_mode') == 'clarification'
            and not state.get('tool_error') and not state.get('stop_reason')):
        answer = '请补充问题描述。'
        runtime.stream_writer({'event': 'delta', 'data': {'text': answer}})
        return {'final_answer': answer, 'quality': {}, 'citations': [], 'evidence_payload': {}}
    if state.get('tool_error'):
        error = state['tool_error']
        raise ServiceError(error.get('code', 'tool_execution_error'),
            error.get('message', '知识检索未能完成，请稍后重试。'), 502)
    if state.get('stop_reason'):
        if state['stop_reason'] == 'context_capacity':
            raise InputTooLong()
        runtime.stream_writer({'event': 'citations', 'data': {'citations': []}})
        runtime.stream_writer({'event': 'delta', 'data': {'text': UNFINISHED_ANSWER}})
        return {'final_answer': UNFINISHED_ANSWER, 'reply_mode': 'answer', 'suggested_actions': ['handoff'], 'quality': {}, 'citations': []}
    required = _current_read(state, context)
    if required is not None and required[2] == 'not_found':
        # 不回显提供器错误正文，也不泄露其他账号是否存在该订单。
        answer = ORDER_NOT_FOUND_ANSWER
        validate_business_answer(answer, EvidencePacket({}, [], [], None, 'none'), [])
        ensure_answer_active(context.deadline)
        runtime.stream_writer({'event': 'citations', 'data': {'citations': []}})
        runtime.stream_writer({'event': 'status', 'data': {'phase': 'answering', 'origin': 'workflow'}})
        runtime.stream_writer({'event': 'delta', 'data': {'text': answer}})
        log_node(state, 'finalize_answer', usage=state['usage'])
        return {'final_answer': answer, 'reply_mode': 'answer', 'quality': {}, 'citations': [],
                'suggested_actions': [], 'evidence_payload': {}, 'refund_decision': None, 'decision_reason': None}
    if (state['reply_mode'] == 'clarification' and state['route'] == 'business' and state['tool_call_count'] == 0
            and state['intent'] in ('订单', '物流') and _current_read(state, context) is None):
        # Agent已决定追问，读取工具只缺订单号；固定呈现这个槽位，
        # 不再让自由生成添加手机号、未验证事实或白名单之外的措辞。
        answer = '请提供订单号。'
        quality = QualityDecision(useful=True, reason='需要用户明确要查询的订单号。',
                                  response_kind='clarification', source=None)
        validate_answer(answer, {'stop'}, EvidencePacket({}, [], [], None, 'none'), quality)
        ensure_answer_active(context.deadline)
        runtime.stream_writer({'event': 'citations', 'data': {'citations': []}})
        runtime.stream_writer({'event': 'status', 'data': {'phase': 'answering', 'origin': 'workflow'}})
        runtime.stream_writer({'event': 'delta', 'data': {'text': answer}})
        log_node(state, 'finalize_answer', usage=state['usage'])
        return {'final_answer': answer, 'quality': quality.model_dump(), 'citations': [], 'evidence_payload': {}}
    try:
        packet, evidence = _packet(state, context, agent_final_system(None, None))
        ledger = _ledger(state, limits)
        reserve_call(packet.messages, [], ledger, output_limit=limits.final_output_tokens, final_reserve=0)
    except (InputTooLong, ServiceError) as exc:
        if isinstance(exc, ContextCapacityError):
            raise
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
        if evidence.payload == state['evidence_payload'] and state['quality']:
            quality = state['quality']
        else:
            quality, stages = await _check_evidence(state, runtime, evidence)
        if not quality['useful']:
            runtime.stream_writer({'event': 'citations', 'data': {'citations': [asdict(c) for c in evidence.citations]}})
            runtime.stream_writer({'event': 'delta', 'data': {'text': KNOWLEDGE_FALLBACK}})
            return {'quality': quality, 'stage_usage': stages, 'final_answer': KNOWLEDGE_FALLBACK, 'reply_mode': 'answer',
                'suggested_actions': ['handoff'], 'citations': [asdict(c) for c in evidence.citations], 'evidence_payload': evidence.payload}
    elif not clarification and (state['route'] == 'knowledge' or not any('error' not in p and 'matches' not in p for p in payloads)):
        raise ServiceError('invalid_answer', '当前结果不足以生成事实回答，请补充必要信息。', 502)
    if clarification:
        quality = QualityDecision(useful=True, reason='本轮只追问必要业务参数。', response_kind='clarification', source=None).model_dump()
    # Sufficiency is itemized separately, but its actual cost still reduces the
    # same turn allowance before the final paid stream is opened.
    ledger = _ledger({**state, 'stage_usage': stages}, limits)
    reserve_call(packet.messages, [], ledger, output_limit=limits.final_output_tokens, final_reserve=0)
    model = model_with_output_budget(context.model, context.settings, limits.final_output_tokens)
    runtime.stream_writer({'event': 'citations', 'data': {'citations': [] if clarification else [asdict(c) for c in evidence.citations]}})
    collector, aggregate = FinalAnswerStream(), None
    notice = MOCK_DATA_NOTICE if not clarification and any(
        p.get('mock') is True and 'error' not in p and 'matches' not in p for p in payloads) else ''
    notice_sent = False
    estimate = _attempt(ledger, packet.messages, [], limits.final_output_tokens)
    log_model_call(context.context_logger, packet, conversation_id=state['conversation_id'],
        user_message_id=state['user_message_id'], phase='final', call_index=1,
        on_packet=context.context_packet_observer)
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
            validate_answer(answer, collector.reasons, evidence, QualityDecision.model_validate(quality))
        if not clarification:
            validate_business_answer(answer, evidence, payloads)
        _settle(state, context, ledger, aggregate, estimate, limits.final_output_tokens)
        estimate = None
        if ledger.spent > ledger.budget:
            raise ServiceError('token_budget', '本轮模型预算不足，无法保存回答。', 422)
        ensure_answer_active(context.deadline)
        if clarification:
            runtime.stream_writer({'event': 'delta', 'data': {'text': answer}})
        log_node(state, 'finalize_answer', usage=_usage(ledger))
        return {'final_answer': answer, 'quality': quality, 'stage_usage': stages, 'usage': _usage(ledger), 'evidence_payload': evidence.payload,
            'citations': [] if clarification else [asdict(c) for c in evidence.citations]}
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


def agent_delta(before_ids: frozenset[str], result: Mapping) -> dict:
    """Child returns full state internally; parent reducer receives only new SQL IDs."""
    return {**result, 'messages': [message for message in result.get('messages', []) if message.id not in before_ids]}


def build_agent_graph():
    """编译每次调用作用域子图，父图负责检查点和唯一最终 SQL 提交。"""
    builder = StateGraph(_AgentState, context_schema=WorkflowRuntime, output_schema=WorkflowState)
    builder.add_node('llm_call', llm_call)
    builder.add_node('tool_node', tool_node)
    builder.add_node('finalize_answer', finalize_answer)
    builder.add_edge(START, 'llm_call')
    builder.add_conditional_edges('llm_call', _after_decision, ['tool_node', 'finalize_answer', END])
    builder.add_conditional_edges('tool_node', _after_tool, ['llm_call', 'finalize_answer'])
    builder.add_edge('finalize_answer', END)
    return builder.compile(checkpointer=None).with_config({'recursion_limit': 32})
