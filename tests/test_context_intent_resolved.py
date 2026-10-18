"""Resolved classification input changes only the model projection, never SQL state."""
import copy
import json

import httpx
import pytest
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import _convert_message_to_dict
from langgraph.runtime import Runtime

from app.context.acceptance import profile_settings
from app.context.service import serialize_snapshot
from app.context.types import ContextAnchors
from app.repositories.records import MessageRecord, message_from_record
from app.workflow import nodes
from app.workflow.context_budget import workflow_budget
from app.workflow.intent import IntentClassifier, intent_packet
from app.workflow.state import new_turn_state
from tests.test_context_agent import production_registry
from tests.test_context_view import segment, snapshot
from tests.workflow_fakes import ScriptedWorkflowModel, workflow_runtime


@pytest.mark.parametrize('raw,resolved,label', [
    ('最开始那个订单后来怎么说？我当时的诉求是什么？',
     '订单1001后来物流怎么说？我当时只查物流，不申请退款。', '物流'),
    ('不要退款，我要查这单物流。', '不要退款，我要查订单1001的物流。', '物流'),
    ('它能退吗？', '它能退吗？', '退款退货'),
])
async def test_node_sends_resolved_current_without_mutating_raw_state_or_history(monkeypatch, raw, resolved, label):
    """Sending raw instead of normalized, changing IDs/history, or diverging preview must fail."""
    history = [
        MessageRecord(11, 'user', '订单1001包裹没找到，只查物流，不申请退款。', None, None),
        MessageRecord(12, 'assistant', None, [{'id': 'saved-logistics', 'type': 'function',
            'function': {'name': 'query_logistics', 'arguments': '{"order_id":"1001"}'}}], None),
        MessageRecord(13, 'tool', '{"order_id":"1001","mock":true,"status":"已签收"}', None, 'saved-logistics'),
        MessageRecord(14, 'assistant', '当时模拟显示已签收，包裹仍待核实。', None, None),
    ]
    registry = production_registry()
    settings = profile_settings('default', offline=True)
    frozen = snapshot(rows=history, anchors=ContextAnchors(10, 10),
                      segments=[segment(1, '用户当时只查订单1001物流，未申请退款。')],
                      limits=workflow_budget(settings, registry))
    state = new_turn_state(conversation_id='42', user_message_id=99, raw_question=raw,
                           category=None, messages=[*[message_from_record(row) for row in history], HumanMessage(raw)])
    state['resolved_question'] = resolved
    before_state = copy.deepcopy(state)
    before_snapshot = serialize_snapshot(frozen)
    wire, previews = [], []
    original_stage = nodes.model_stage

    async def record_preview(state, runtime, stage, service, operation, messages, **kwargs):
        previews.append([message.model_copy(deep=True) for message in messages])
        return await original_stage(state, runtime, stage, service, operation, messages, **kwargs)

    monkeypatch.setattr(nodes, 'model_stage', record_preview)

    def respond(request):
        wire.append(json.loads(request.content))
        return httpx.Response(200, json={'id': 'offline', 'object': 'chat.completion', 'created': 0,
            'model': 'offline', 'choices': [{'index': 0, 'finish_reason': 'stop',
                'message': {'role': 'assistant', 'content': json.dumps({'intent': label, 'confidence': .95}, ensure_ascii=False)}}],
            'usage': {'prompt_tokens': 200, 'completion_tokens': 20, 'total_tokens': 220}})

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        model = ChatOpenAI(model='offline', api_key='offline', base_url='https://offline.invalid/v1',
                           http_async_client=client, max_retries=0, use_responses_api=False)
        context = workflow_runtime()
        context.settings, context.registry = settings, registry
        context.context_snapshot, context.intent_model = frozen, model
        try:
            result = await nodes.classify_intent(state, Runtime(context=context, stream_writer=lambda event: None))
        finally:
            model.root_client.close()
            await model.root_async_client.close()

    assert len(wire) == len(previews) == 1
    sent = wire[0]['messages']
    assert sent[-2] == {'role': 'user', 'content': resolved}
    assert previews[0][-2].id == '99'
    assert sent == [_convert_message_to_dict(message) for message in previews[0]]
    assert sent[1:-2] == [_convert_message_to_dict(message_from_record(row)) for row in history]
    assert len(sent) == 7, 'system + four historical messages + current + attachment; no raw duplicate'
    attachment = json.loads(sent[-1]['content'])
    assert attachment == {'kind': 'context_data', 'summaries': [{'seq': 1, 'from_msg_id': '1',
        'upto_msg_id': '10', 'content': '用户当时只查订单1001物流，未申请退款。'}],
        'data': {'resolved_question': resolved}}
    assert state == before_state
    assert state['messages'][-1].id == '99' and state['messages'][-1].content == raw
    assert serialize_snapshot(frozen) == before_snapshot
    assert result['intent'] == label and result['usage']['actual_calls'] == 1
    assert wire[0]['response_format'] == {'type': 'json_object'} and not wire[0].get('tools')


def test_no_resolved_value_keeps_raw_current_and_identity():
    frozen = snapshot()
    packet = intent_packet('它能退吗？', frozen)
    assert packet.messages[-2].content == '它能退吗？' and packet.messages[-2].id == '99'
    assert json.loads(packet.messages[-1].content)['data'] == {'resolved_question': '它能退吗？'}


async def test_social_fast_path_still_uses_raw_before_resolved_projection():
    # An incorrect later value must not turn a raw social fast path into a model call.
    service = IntentClassifier(ScriptedWorkflowModel(), input_budget=8000, timeout_seconds=1)
    result = await service.classify('谢谢', snapshot=snapshot(), resolved_question='查询订单1001物流')
    assert result.intent == '闲聊' and service.usage['actual_calls'] == service.usage['estimated_calls'] == 0
