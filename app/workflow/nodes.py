"""外层 Workflow 节点：固定分流、强制检索、闸前拒答与统一提交。"""
import asyncio
import json
import time
from dataclasses import asdict
from uuid import uuid4

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.runtime import Runtime

from app.core.errors import InputTooLong, ServiceError
from app.core.evidence import prepare_workflow_evidence
from app.workflow.context_budget import (runtime_settings, runtime_snapshot, workflow_packet, stage_packet,
                                        turn_token_limit, reserve_context_call)
from app.context.tokens import estimate_payload
from app.core.llm import model_with_output_budget
from app.agent.controls import UsageLedger
from app.orders.types import OrderSnapshot
from app.workflow.after_sales import make_refund_offer, resolve_order_anchor
from app.workflow.policy_scoring import refund_policy_question
from app.workflow.understanding import build_understanding_messages, understanding_packet
from app.workflow.intent import intent_packet
from app.workflow.entities import validate_snapshot_entities, explicit_order_ids
from app.workflow.selection import prepare_order_selection, await_order_selection
from app.workflow.prompts import EXPANSION_SYSTEM, build_intent_messages
from app.workflow.intent import IntentClassifier, route_intent, social_fast_path
from app.workflow.prompts import COMPLAINT_RESPONSE, KNOWLEDGE_FALLBACK, OTHER_RESPONSE, SOCIAL_RESPONSE
from app.workflow.runtime import WorkflowRuntime
from app.workflow.state import WorkflowState
from app.workflow.history import replay_turns
from app.workflow.logging import log_audit
from app.workflow.recovery import recover_generation


def remaining_timeout(context: WorkflowRuntime, limit: float) -> float:
    """所有外部等待使用本轮剩余期限，过期不再开始收费调用。"""
    remaining = context.deadline - time.monotonic()
    if remaining <= 0:
        raise ServiceError('upstream_timeout', '本轮处理超时，请稍后重试。', 504)
    return min(limit, remaining)


def log_node(state: WorkflowState, node: str, **metadata):
    """经统一白名单写出默认可见节点身份、路由及理由代码。"""
    log_audit('workflow_node', **{'conversation_id': state['conversation_id'],
        'user_message_id': state['user_message_id'], 'node': node, 'intent': state['intent'],
        'route': state['route'], **metadata})


def prompt_current(state, current):
    """规范问题仅投影到模型消息，保留SQL原文和身份不受提示构造影响。"""
    return current.model_copy(update={'content': state['resolved_question']}, deep=True)


def state_evidence(state: WorkflowState, context: WorkflowRuntime):
    """从稳定本轮用户身份拆出完整历史与原始配对，构造预算内证据。"""
    messages = state['messages']
    index = next((i for i, message in enumerate(messages)
        if isinstance(message, HumanMessage) and message.id == state['user_message_id']), None)
    if index is None:
        raise ValueError('current SQL user message identity missing')
    replay_turns(messages[:index])
    pending = messages[index + 1:]
    payloads = [json.loads(message.content) for message in pending if isinstance(message, ToolMessage)]
    settings = runtime_settings(context.settings)
    return prepare_workflow_evidence(payloads, top_k=settings.rerank_top_k,
        token_budget=runtime_snapshot(state, context).budget.evidence)


def prior_history(state):
    """按本轮SQL消息身份截断，理解只接收已完成历史。"""
    index = next(i for i, message in enumerate(state['messages'])
        if isinstance(message, HumanMessage) and message.id == state['user_message_id'])
    return [message for turn in replay_turns(state['messages'][:index]) for message in turn]


def observe_usage(context, update):
    """同步递交已记录阶段快照，审计接收失败不能遮蔽原模型异常或取消。"""
    observer = context.usage_observer
    if observer is not None:
        try:
            observer(update)
        except Exception:
            pass


async def model_stage(state, runtime, stage, service, operation, messages, *, following=0):
    """预留后续输出和完整最终输入，成功及失败尝试都记录独立阶段成本。"""
    context = runtime.context
    from app.workflow.controls import stable_tool_schema as stable_read_schema
    settings = runtime_settings(context.settings)
    budget = runtime_snapshot(state, context).budget
    ledger = UsageLedger(budget=turn_token_limit(settings, budget), **state['usage'])
    final, _ = workflow_packet(state, context, phase='final')
    control, _ = workflow_packet(state, context, phase='decision', tools=stable_read_schema(context.registry))
    reserve = final.estimated_tokens + final.output_tokens + control.estimated_tokens + control.output_tokens + following * settings.intent_max_output_tokens
    def reserve_attempt():
        reserve_context_call(messages, [], ledger, output_limit=settings.intent_max_output_tokens, final_reserve=reserve)
    reserve_attempt()
    started = time.monotonic()
    consumed = dict.fromkeys(state['usage'], 0)
    def update_usage():
        for key in consumed:
            consumed[key] += service.usage[key]
            setattr(ledger, key, state['usage'][key] + consumed[key])
        previous = state['stage_usage'].get(stage, {})
        return {'model_recovery_used': context.model_recovery_used,
            'usage': {key: state['usage'][key] + consumed[key] for key in consumed},
            'stage_usage': {**state['stage_usage'], stage: {
                **{key: previous.get(key, 0) + consumed[key] for key in consumed},
                'elapsed_seconds': previous.get('elapsed_seconds', 0) + time.monotonic() - started}}}
    for attempt in range(2):
        service.usage = dict.fromkeys(consumed, 0)
        try:
            async with asyncio.timeout(remaining_timeout(context, context.settings.llm_timeout_seconds)):
                result = await operation(attempt)
        except BaseException as exc:
            if isinstance(exc, TimeoutError):
                exc = ServiceError('upstream_timeout', '模型响应超时，请稍后重试。', 504)
            update = update_usage()
            observe_usage(context, update)
            runtime.stream_writer({'event': 'usage', 'data': {'stage': stage, **update}})
            log_node(state, stage if stage != 'understanding' else 'resolve_reference', usage=update['usage'])
            if recover_generation(context, state, runtime, stage, exc, update['usage'],
                    attempted=service.usage['actual_calls'] + service.usage['estimated_calls'] > 0,
                    reserve=reserve_attempt):
                continue
            raise exc
        update = update_usage()
        observe_usage(context, update)
        return result, update


def stage_update(state, stage, service, started, messages):
    """复用服务在调用前设定的估算；输入拒绝等未尝试调用保留零。"""
    consumed = dict(service.usage)
    return {'usage': {key: state['usage'][key] + consumed[key] for key in state['usage']},
        'stage_usage': {**state['stage_usage'], stage: {**consumed, 'elapsed_seconds': time.monotonic() - started}}}


async def resolve_reference(state: WorkflowState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """社交整轮零模型，其余用完整SQL历史完成理解，不猜缺失运行依赖。"""
    context = runtime.context
    log_node(state, 'resolve_reference')
    if social_fast_path(state['raw_question']):
        return {'resolved_question': state['raw_question'], 'turn_status': 'running'}
    if context.understanding is None:
        raise ValueError('query understanding is required')
    history = prior_history(state)
    kwargs = {}
    if context.context_snapshot is not None:
        kwargs = dict(snapshot=context.context_snapshot, provenance=context.context_provenance,
                      context_logger=context.context_logger, output_tokens=context.settings.intent_max_output_tokens)
        messages = list(understanding_packet(state['raw_question'], context.context_snapshot,
            output_tokens=context.settings.intent_max_output_tokens).messages)
    else:
        messages = build_understanding_messages(state['raw_question'], history, context.settings.tool_input_token_budget)
    result, update = await model_stage(state, runtime, 'understanding', context.understanding,
        lambda attempt: context.understanding.resolve(state['raw_question'], history, **kwargs,
            call_index=1 + attempt), messages, following=2)
    return {**update, 'resolved_question': result.query, 'turn_status': 'running'}


async def classify_intent(state: WorkflowState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """明确社交零模型，否则用规范问题严格分类，禁止非法降级。"""
    context = runtime.context
    update = {}
    if social_fast_path(state['raw_question']):
        intent, raw_intent, confidence = '闲聊', '闲聊', 1.0
    else:
        model = model_with_output_budget(context.intent_model, context.settings, context.settings.intent_max_output_tokens)
        classifier = IntentClassifier(model, input_budget=context.settings.tool_input_token_budget,
            timeout_seconds=remaining_timeout(context, context.settings.llm_timeout_seconds))
        if context.context_snapshot is not None:
            kwargs = dict(snapshot=context.context_snapshot, resolved_question=state['resolved_question'],
                context_logger=context.context_logger, output_tokens=context.settings.intent_max_output_tokens,
                ticket_request=state.get('ticket_request'))
            messages = list(intent_packet(state['raw_question'], context.context_snapshot,
                resolved_question=state['resolved_question'], output_tokens=context.settings.intent_max_output_tokens,
                ticket_request=state.get('ticket_request')).messages)
            question = state['raw_question']
        else:
            kwargs, question = {}, state['resolved_question']
            messages = build_intent_messages(question)
            if state.get('ticket_request'):
                kwargs['ticket_request'] = state['ticket_request']
                messages.append(HumanMessage('当前为用户主动要求建单后的补充轮，先核对是否仍在补充问题描述；明确切换/否定优先。'))
        result, update = await model_stage(state, runtime, 'classification', classifier,
            lambda attempt: classifier.classify(question, **kwargs, call_index=2 + attempt), messages, following=1)
        intent = result.intent
        raw_intent, confidence = result.raw_intent, result.confidence
    route = route_intent(intent)
    log_node(state, 'classify_intent', selected_intent=intent, selected_route=route)
    return {**update, 'intent': intent, 'raw_intent': raw_intent, 'confidence': confidence, 'route': route,
            'ticket_request': state.get('ticket_request') if intent == '工单' else None}


async def resolve_order(state: WorkflowState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """独立订单锚定节点不查列表，不自动选择唯一候选。"""
    log_node(state, 'resolve_order')
    if runtime.context.context_snapshot is not None:
        validate_snapshot_entities(state['raw_question'], state['resolved_question'],
            runtime.context.context_snapshot, runtime.context.context_provenance)
    else:
        resolve_order_anchor(state['raw_question'], state['resolved_question'], prior_history(state))
    return {'turn_status': 'running'}


def selected_order_id(state):
    """先使用已核验选单回执，否则只接受可追溯明确实体。"""
    selected = state.get('order_selection') or {}
    if state.get('context_snapshot_id'):
        identifiers = explicit_order_ids(state['raw_question']) or explicit_order_ids(state['resolved_question'])
        return selected.get('selected_order_id') or (next(iter(identifiers)) if len(identifiers) == 1 else None)
    return selected.get('selected_order_id') or resolve_order_anchor(
        state['raw_question'], state['resolved_question'], prior_history(state))


async def workflow_tool(state, runtime, node, name, args, operation):
    """强制读取按一次逻辑工具保存真实申请结果，并占用原四次限额。"""
    context = runtime.context
    if state['tool_call_count'] >= getattr(context.settings, 'agent_max_tool_calls', 4):
        raise ServiceError('token_budget', '本轮工具调用次数已达上限。', 422)
    identifier = ('workflow_faq_' if name == 'query_faq' else 'workflow_order_') + uuid4().hex
    request = AIMessage('', tool_calls=[{'id': identifier, 'name': name, 'args': args}],
        response_metadata={'finish_reason': 'tool_calls'})
    request.id = str(await context.repository.append_message(state['conversation_id'], request))
    started = time.monotonic()
    identity = {'tool': name, 'tool_call_id': identifier, 'origin': 'workflow'}
    runtime.stream_writer({'event': 'status', 'data': {**identity, 'status': 'running'}})
    from app.tools.catalog_types import BoundCatalog
    if isinstance(context.registry, BoundCatalog):
        from app.workflow.tool_calls import run_workflow_tool, forced_read_registration, execution_context
        from app.tools.types import ToolCall
        definition = context.registry.definition(name)
        registered = forced_read_registration(definition, operation)
        outcome = await run_workflow_tool(ToolCall(identifier, name, args), registered,
            context=execution_context(state, context), executor=context.executor)
        payload, result_status = outcome.content, outcome.status
    else:
        payload = await operation()
        result_status = 'error' if isinstance(payload, dict) and 'error' in payload else 'success'
    result = ToolMessage(json.dumps(payload, ensure_ascii=False, separators=(',', ':'), allow_nan=False),
        tool_call_id=identifier, name=name, status=result_status)
    result.id = str(await context.repository.append_message(state['conversation_id'], result))
    trace = {'node': node, 'origin': 'workflow', 'name': name, 'tool_call_id': identifier,
        'status': result_status,
        'elapsed_seconds': time.monotonic() - started}
    log_node(state, node, **{k: v for k, v in trace.items() if k != 'node'})
    runtime.stream_writer({'event': 'status', 'data': {**identity, 'status': 'completed', 'result_status': trace['status']}})
    return {'messages': [request, result], 'tool_trace': [*state['tool_trace'], trace],
        'tool_call_count': state['tool_call_count'] + 1}


async def load_order(state: WorkflowState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """在服务器身份范围重新读取已明确订单，不用客户端事实或随机工具。"""
    context = runtime.context
    if context.order_provider is None or not context.user_id:
        raise ValueError('trusted order provider and user_id are required')
    order = None
    async def read():
        """查不到订单时保存真实未找到结果，随后准备当前身份候选。"""
        nonlocal order
        async with asyncio.timeout(remaining_timeout(context, context.settings.llm_timeout_seconds)):
            order = await context.order_provider.get_order(user_id=context.user_id, order_id=selected_order_id(state))
        return order.model_dump(mode='json') if order is not None else {'found': False, 'mock': True}
    update = await workflow_tool(state, runtime, 'load_order', 'query_order', {'order_id': selected_order_id(state)}, read)
    return {**update, 'order_snapshot': order.model_dump(mode='json') if order else None}


async def expand_queries(state: WorkflowState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """订单事实已落State后才扩写，不改变请求过滤条件。"""
    context = runtime.context
    if context.expander is None:
        raise ValueError('query expander is required')
    if len(state['resolved_question']) > 512:
        raise InputTooLong()
    order = OrderSnapshot.model_validate_json(json.dumps(state['order_snapshot']))
    messages = [SystemMessage(EXPANSION_SYSTEM), HumanMessage(json.dumps(
        {'question': state['resolved_question'], 'order': state['order_snapshot']}, ensure_ascii=False))]
    kwargs = {}
    if context.context_snapshot is not None:
        kwargs = dict(snapshot=context.context_snapshot, raw_question=state['raw_question'],
                      context_logger=context.context_logger, output_tokens=context.settings.intent_max_output_tokens)
        messages = stage_packet(context.context_snapshot, system=messages[0], raw_question=state['raw_question'],
            attachment={'resolved_question': state['resolved_question'], 'order': state['order_snapshot']},
            output_tokens=context.settings.intent_max_output_tokens).messages
    queries, update = await model_stage(state, runtime, 'expansion', context.expander,
        lambda attempt: context.expander.expand(state['resolved_question'], order, **kwargs,
            call_index=1 + attempt), messages)
    log_node(state, 'expand_queries', usage=update['usage'])
    return {**update, 'retrieval_queries': list(queries)}


async def retrieve_knowledge(state: WorkflowState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """纯FAQ只走可信单查询，明确跳过旧planner。"""
    return await retrieve_policies(state, runtime, node='retrieve_knowledge')


async def retrieve_policies(state: WorkflowState, runtime: Runtime[WorkflowRuntime], *, node='retrieve_policies') -> dict:
    """全部查询共用一次FAQ期限，聚合检索按一次逻辑工具保存。"""
    context = runtime.context
    if context.workflow_retriever is None:
        raise ValueError('workflow retriever is required')
    queries = tuple(state['retrieval_queries']) or (state['resolved_question'],)
    if len(state['resolved_question']) > 512 or any(len(query) > 512 for query in queries):
        raise InputTooLong()
    scoring = {}
    top_k = runtime_settings(context.settings).rerank_top_k
    if top_k != 10:
        scoring['top_k'] = top_k
    if (state['route'] == 'after_sales' and state['intent'] == '退款退货'
            and len(queries) > 1 and state.get('order_snapshot')):
        order = OrderSnapshot.model_validate_json(json.dumps(state['order_snapshot']))
        if order.user_id == context.user_id and order.order_id == selected_order_id(state):
            question = refund_policy_question(state['resolved_question'], order)
            if question != state['resolved_question']:
                scoring['rerank_question'] = question
    audit = {}
    async def retrieve():
        """仅成功的完整聚合结果成为本轮证据；失败不入低置信池。"""
        nonlocal audit
        try:
            async with asyncio.timeout(remaining_timeout(context, context.settings.faq_timeout_seconds)):
                result = await context.workflow_retriever.retrieve(question=state['resolved_question'],
                    queries=queries, category=state['category'], **scoring)
        except TimeoutError as exc:
            raise ServiceError('upstream_timeout', '知识检索超时，请稍后重试。', 504) from exc
        audit = result.audit
        return result.payload
    update = await workflow_tool(state, runtime, node, 'query_faq',
        {'keyword': state['resolved_question'][:128]}, retrieve)
    packet = state_evidence({**state, **update, 'messages': [*state['messages'], *update['messages']]}, context)
    return {**update, 'retrieval_queries': list(queries), 'retrieval_audit': audit,
        'evidence_payload': packet.payload, 'citations': [asdict(citation) for citation in packet.citations]}

async def confidence_gate(state: WorkflowState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """空/低分先拒绝，达标才内容自评，任何服务异常保持错误。"""
    context = runtime.context
    stages = state['stage_usage']
    runtime.stream_writer({'event': 'status', 'data': {'phase': 'checking', 'origin': 'workflow'}})
    packet = state_evidence(state, context)
    threshold = context.settings.rerank_min_score
    if packet.strategy != 'hybrid_rerank' or threshold is None:
        raise ValueError('online knowledge gate requires hybrid_rerank and calibrated threshold')
    if not packet.citations or packet.best_score is None or packet.best_score < threshold:
        quality = {'useful': False, 'reason': '当前知识证据为空或低于已校准重排门槛。',
            'response_kind': 'knowledge', 'source': 'retrieval_low_conf'}
    else:
        decision, stages = await assess_sufficiency(state, runtime, packet)
        quality = decision.model_dump()
    log_node(state, 'confidence_gate', useful=quality['useful'], reason_code=quality['source'])
    return {'quality': quality, 'stage_usage': stages}


async def assess_sufficiency(state, runtime, packet):
    """内部评估独立累计实测或估算，失败上报观测成本但不伪造成功更新。"""
    from app.core.prompts import build_sufficiency_messages
    context = runtime.context
    settings = runtime_settings(context.settings)
    kwargs = {'order_context': state['order_snapshot']} if state['route'] == 'after_sales' else {}
    messages = build_sufficiency_messages(state['resolved_question'], packet.payload, **kwargs)
    if context.context_snapshot is not None:
        kwargs.update(snapshot=context.context_snapshot, original_question=state['raw_question'],
            context_logger=context.context_logger, output_tokens=settings.sufficiency_max_output_tokens)
        messages = stage_packet(context.context_snapshot, system=messages[0], raw_question=state['raw_question'],
            attachment={'resolved_question': state['resolved_question'], 'evidence': packet.payload,
                        'order_context': kwargs.get('order_context')},
            output_tokens=settings.sufficiency_max_output_tokens).messages
    previous = state['stage_usage'].get('sufficiency', {})
    spent = sum(previous.get(key, 0) for key in ('actual', 'estimated'))
    ledger = UsageLedger(budget=turn_token_limit(settings, runtime_snapshot(state, context).budget),
        **{**state['usage'], 'estimated': state['usage']['estimated'] + spent})
    final, _ = workflow_packet(state, context, phase='final')
    reserve_context_call(messages, [], ledger, output_limit=settings.sufficiency_max_output_tokens,
                         final_reserve=final.estimated_tokens + final.output_tokens)
    started = time.monotonic()
    def consumption():
        """单列充分性累计，由本轮总预算共同约束。"""
        consumed = getattr(context.sufficiency, 'usage', None) or {
            'actual': 0, 'estimated': estimate_payload(messages) + settings.sufficiency_max_output_tokens,
            'actual_calls': 0, 'estimated_calls': 1}
        old = state['stage_usage'].get('sufficiency', {})
        return {**state['stage_usage'], 'sufficiency': {
            **{key: old.get(key, 0) + consumed[key] for key in state['usage']},
            'elapsed_seconds': old.get('elapsed_seconds', 0) + time.monotonic() - started}}
    try:
        async with asyncio.timeout(remaining_timeout(context, context.settings.llm_timeout_seconds)):
            decision = await context.sufficiency.check(state['resolved_question'], packet, **kwargs)
    except BaseException:
        update = {'stage_usage': consumption(), 'usage': state['usage']}
        observe_usage(context, update)
        runtime.stream_writer({'event': 'usage', 'data': {'stage': 'sufficiency', **update}})
        raise
    consumed = consumption()
    observe_usage(context, {'stage_usage': consumed, 'usage': state['usage']})
    if sum(consumed['sufficiency'][key] + state['usage'][key] for key in ('actual', 'estimated')) > ledger.budget:
        raise ServiceError('token_budget', '本轮模型预算不足，无法继续回答。', 422)
    return decision, consumed


async def knowledge_fallback(state: WorkflowState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """闸拒绝只生成明确资料不足回复，提交与入池统一留给 log_response。"""
    log_node(state, 'knowledge_fallback', reason_code=state['quality']['source'])
    runtime.stream_writer({'event': 'citations', 'data': {'citations': state['citations']}})
    runtime.stream_writer({'event': 'status', 'data': {'phase': 'answering', 'origin': 'workflow'}})
    runtime.stream_writer({'event': 'delta', 'data': {'text': KNOWLEDGE_FALLBACK}})
    return {'final_answer': KNOWLEDGE_FALLBACK, 'reply_mode': 'answer', 'suggested_actions': ['handoff']}


async def complaint_response(state: WorkflowState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """投诉固定安抚并提供两个独立选项，不执行工具或修改会话状态。"""
    log_node(state, 'complaint_response')
    runtime.stream_writer({'event': 'citations', 'data': {'citations': []}})
    runtime.stream_writer({'event': 'status', 'data': {'phase': 'answering', 'origin': 'workflow'}})
    runtime.stream_writer({'event': 'delta', 'data': {'text': COMPLAINT_RESPONSE}})
    return {'final_answer': COMPLAINT_RESPONSE, 'reply_mode': 'answer',
        'suggested_actions': ['handoff', 'create_ticket']}


async def social_response(state: WorkflowState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """固定社交话术不使用最终生成模型。"""
    log_node(state, 'social_response')
    runtime.stream_writer({'event': 'citations', 'data': {'citations': []}})
    runtime.stream_writer({'event': 'status', 'data': {'phase': 'answering', 'origin': 'workflow'}})
    runtime.stream_writer({'event': 'delta', 'data': {'text': SOCIAL_RESPONSE}})
    return {'final_answer': SOCIAL_RESPONSE, 'reply_mode': 'answer', 'suggested_actions': []}


async def other_response(state: WorkflowState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """无法识别的诉求固定澄清，不查单、检索或自动建议动作。"""
    log_node(state, 'other_response')
    runtime.stream_writer({'event': 'citations', 'data': {'citations': []}})
    runtime.stream_writer({'event': 'status', 'data': {'phase': 'answering', 'origin': 'workflow'}})
    runtime.stream_writer({'event': 'delta', 'data': {'text': OTHER_RESPONSE}})
    return {'final_answer': OTHER_RESPONSE, 'reply_mode': 'clarification', 'suggested_actions': []}


async def no_order_response(state: WorkflowState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """当前身份没有可办候选时提示核对订单，不进入知识不足池。"""
    log_node(state, 'no_order_response')
    answer = '未找到可办理订单，请核对订单信息，也可以选择转人工协助。'
    runtime.stream_writer({'event': 'citations', 'data': {'citations': []}})
    runtime.stream_writer({'event': 'status', 'data': {'phase': 'answering', 'origin': 'workflow'}})
    runtime.stream_writer({'event': 'delta', 'data': {'text': answer}})
    return {'final_answer': answer, 'reply_mode': 'clarification', 'suggested_actions': ['handoff']}


async def log_response(state: WorkflowState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """正常路径最终答复统一短事务提交；拒答与低置信池使用原子仓储。"""
    answer = AIMessage(state['final_answer'])
    quality = state['quality']
    if quality.get('useful') is False:
        identifier = await runtime.context.quality_repository.commit_refusal(state['conversation_id'], answer,
            raw_question=state['raw_question'], source=quality['source'], reason=quality['reason'])
    else:
        identifier = await runtime.context.repository.append_message(state['conversation_id'], answer)
    answer.id = str(identifier)
    log_node(state, 'log_response', final_message_id=str(identifier), turn_status='completed', usage=state['usage'])
    from app.workflow.selection import active_elapsed
    update = {'messages': [answer], 'final_message_id': str(identifier), 'turn_status': 'completed',
              'active_elapsed_seconds': active_elapsed(state, runtime.context)}
    return {**update, 'refund_offer': make_refund_offer({**state, **update})}
