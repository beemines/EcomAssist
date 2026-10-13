"""外层 Workflow 节点：固定分流、强制检索、闸前拒答与统一提交。"""
import asyncio
import json
import logging
import time
from dataclasses import asdict
from uuid import uuid4

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.runtime import Runtime

from app.core.errors import ServiceError
from app.core.evidence import build_agent_evidence
from app.core.llm import model_with_output_budget
from app.workflow.intent import IntentClassifier, route_intent, social_fast_path
from app.workflow.prompts import COMPLAINT_RESPONSE, EVIDENCE_SYSTEM, KNOWLEDGE_FALLBACK, SOCIAL_RESPONSE
from app.workflow.runtime import WorkflowRuntime
from app.workflow.state import WorkflowState

logger = logging.getLogger(__name__)


def remaining_timeout(context: WorkflowRuntime, limit: float) -> float:
    """所有外部等待使用本轮剩余期限，过期不再开始收费调用。"""
    remaining = context.deadline - time.monotonic()
    if remaining <= 0:
        raise ServiceError('upstream_timeout', '本轮处理超时，请稍后重试。', 504)
    return min(limit, remaining)


def log_node(state: WorkflowState, node: str, **metadata):
    """记录身份、节点及理由代码，不输出原话、证据或内部 JSON。"""
    logger.info('workflow_node', extra={'workflow': {'conversation_id': state['conversation_id'],
        'user_message_id': state['user_message_id'], 'node': node, 'intent': state['intent'],
        'route': state['route'], **metadata}})


def state_evidence(state: WorkflowState, context: WorkflowRuntime):
    """从稳定本轮用户身份拆出完整历史与原始配对，构造预算内证据。"""
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
    return build_agent_evidence(system=SystemMessage(EVIDENCE_SYSTEM), turns=turns,
        current=messages[index], current_tool_messages=pending, payloads=payloads,
        budget=context.settings.tool_input_token_budget)


async def resolve_reference(state: WorkflowState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """当前版本仅原样透传，不声称已解析用户指代。"""
    log_node(state, 'resolve_reference')
    return {'resolved_question': state['raw_question'], 'turn_status': 'running'}


async def classify_intent(state: WorkflowState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """明确社交零模型，否则用当前原话严格分类，禁止非法降级。"""
    context = runtime.context
    usage = dict(state['usage'])
    if social_fast_path(state['raw_question']):
        intent = '闲聊'
    else:
        model = model_with_output_budget(context.intent_model, context.settings, context.settings.intent_max_output_tokens)
        classifier = IntentClassifier(model, input_budget=context.settings.tool_input_token_budget,
            timeout_seconds=remaining_timeout(context, context.settings.llm_timeout_seconds))
        intent = await classifier.classify(state['raw_question'])
        usage = {key: usage[key] + classifier.usage[key] for key in usage}
    route = route_intent(intent)
    log_node(state, 'classify_intent', selected_intent=intent, selected_route=route)
    return {'intent': intent, 'route': route, 'usage': usage}


async def retrieve_knowledge(state: WorkflowState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """服务器申请强制 FAQ，可信检索使用本轮完整原话与已校验 category。"""
    context = runtime.context
    timeout = remaining_timeout(context, context.settings.faq_timeout_seconds)
    identifier = 'workflow_faq_' + uuid4().hex
    keyword = state['raw_question'][:128]
    args = {'keyword': keyword}
    request = AIMessage('', tool_calls=[{'id': identifier, 'name': 'query_faq', 'args': args}],
        response_metadata={'finish_reason': 'tool_calls'})
    request.id = str(await context.repository.append_message(state['conversation_id'], request))
    started = time.monotonic()
    runtime.stream_writer({'event': 'status', 'data': {'tool': 'query_faq', 'tool_call_id': identifier,
        'origin': 'workflow', 'status': 'running'}})
    try:
        async with asyncio.timeout(timeout):
            payload = await context.faq_repository.retrieve(keyword,
                raw_question=state['raw_question'], category=state['category'])
    except TimeoutError as exc:
        raise ServiceError('upstream_timeout', '知识检索超时，请稍后重试。', 504) from exc
    result = ToolMessage(json.dumps(payload, ensure_ascii=False, separators=(',', ':'), allow_nan=False),
        tool_call_id=identifier)
    result.id = str(await context.repository.append_message(state['conversation_id'], result))
    messages = [*state['messages'], request, result]
    packet = state_evidence({**state, 'messages': messages}, context)
    trace = {'node': 'retrieve_knowledge', 'origin': 'workflow', 'tool_call_id': identifier,
        'name': 'query_faq', 'elapsed_seconds': time.monotonic() - started}
    log_node(state, 'retrieve_knowledge', **{key: value for key, value in trace.items() if key != 'node'})
    runtime.stream_writer({'event': 'status', 'data': {'tool': 'query_faq', 'tool_call_id': identifier,
        'origin': 'workflow', 'status': 'completed', 'result_status': 'success'}})
    return {'messages': messages, 'evidence_payload': packet.payload,
        'citations': [asdict(citation) for citation in packet.citations],
        'tool_trace': [*state['tool_trace'], trace], 'tool_call_count': state['tool_call_count'] + 1}


async def confidence_gate(state: WorkflowState, runtime: Runtime[WorkflowRuntime]) -> dict:
    """空/低分先拒绝，达标才内容自评，任何服务异常保持错误。"""
    context = runtime.context
    runtime.stream_writer({'event': 'status', 'data': {'phase': 'checking', 'origin': 'workflow'}})
    packet = state_evidence(state, context)
    threshold = context.settings.rerank_min_score
    if packet.strategy != 'hybrid_rerank' or threshold is None:
        raise ValueError('online knowledge gate requires hybrid_rerank and calibrated threshold')
    if not packet.citations or packet.best_score is None or packet.best_score < threshold:
        quality = {'useful': False, 'reason': '当前知识证据为空或低于已校准重排门槛。',
            'response_kind': 'knowledge', 'source': 'retrieval_low_conf'}
    else:
        async with asyncio.timeout(remaining_timeout(context, context.settings.llm_timeout_seconds)):
            decision = await context.sufficiency.check(state['raw_question'], packet)
        quality = decision.model_dump()
    log_node(state, 'confidence_gate', useful=quality['useful'], reason_code=quality['source'])
    return {'quality': quality}


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
    return {'messages': [*state['messages'], answer], 'final_message_id': str(identifier), 'turn_status': 'completed'}
