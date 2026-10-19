"""Assistant offers and completed tickets cannot create a new user request."""
import json
from contextlib import asynccontextmanager

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from app.core.errors import ServiceError
from app.workflow.intent import IntentClassifier
from app.workflow.understanding import QueryUnderstanding
from app.workflow.entities import IdentitySource, validate_resolved_entities, validate_snapshot_entities
from tests.workflow_fakes import ScriptedWorkflowModel


@pytest.fixture
def immediate_generation(monkeypatch):
    """No I/O occurs in these scripted calls; do not require a Windows socket loop.

    Timeout behavior belongs to the existing real-loop tests, not these guards.
    Reject an unexpected suspension instead of silently running external work.
    """
    @asynccontextmanager
    async def deadline(_):
        yield
    monkeypatch.setattr('app.workflow.intent.asyncio.timeout', deadline)
    def complete(coroutine):
        try:
            coroutine.send(None)
        except StopIteration as result:
            return result.value
        finally:
            coroutine.close()
        raise AssertionError('scripted guard test unexpectedly suspended for I/O')
    return complete


@pytest.mark.parametrize('snapshot_mode', [False, True])
@pytest.mark.parametrize('query', [
    '订单2002物流信息异常，创建异常处理工单',
    '订单2002物流信息异常，请帮我建个工单',
    '订单2002物流信息异常，需要建单',
])
def test_identity_projection_rejects_invented_ticket_action(snapshot_mode, query):
    from types import SimpleNamespace
    with pytest.raises(ServiceError) as caught:
        if snapshot_mode:
            frozen = SimpleNamespace(summaries=(), omitted_summary_seqs=())
            sources = (IdentitySource(1, None, frozenset({'2002'}), ()),)
            validate_snapshot_entities('物流信息异常', query, frozen, sources)
        else:
            validate_resolved_entities('物流信息异常', query,
                [HumanMessage('2002物流信息异常'), AIMessage('模拟物流已查到。')])
    assert caught.value.code == 'invalid_structured_output'


def reply(body):
    return AIMessage(json.dumps(body, ensure_ascii=False), response_metadata={'finish_reason': 'stop'})


@pytest.mark.parametrize('query', [
    '订单2002物流信息异常，创建异常处理工单',
    '订单2002物流信息异常，请帮我建个工单',
    '订单2002物流信息异常，需要建单',
])
def test_resolver_rejects_new_ticket_action_added_to_issue_report(query, immediate_generation):
    model = ScriptedWorkflowModel(intent_replies=[reply({'query': query})])
    history = [HumanMessage('2002物流信息异常'),
               AIMessage('已查订单2002。如确认存在问题，我可以为您创建物流异常工单，是否需要？')]
    resolver = QueryUnderstanding(model, input_budget=20000, timeout_seconds=1)
    with pytest.raises(ServiceError) as caught:
        immediate_generation(resolver.resolve('物流信息异常', history))
    assert caught.value.code == 'invalid_structured_output'


@pytest.mark.parametrize('raw,query', [
    ('物流信息异常', '订单2002物流信息异常'),
    ('帮我建个工单', '帮我建个工单'),
    ('物流信息异常', '物流信息异常'),
])
def test_resolver_preserves_issue_or_user_requested_action(raw, query, immediate_generation):
    model = ScriptedWorkflowModel(intent_replies=[reply({'query': query})])
    resolver = QueryUnderstanding(model, input_budget=20000, timeout_seconds=1)
    history = [HumanMessage('2002物流信息异常'), AIMessage('订单2002的物流结果已查到。')]
    result = immediate_generation(resolver.resolve(raw, history))
    assert result.query == query


def test_ticket_label_requires_current_user_or_verified_pending_request(immediate_generation):
    model = ScriptedWorkflowModel(intent_replies=[reply({'intent': '工单', 'confidence': .98})])
    service = IntentClassifier(model, input_budget=20000, timeout_seconds=1)
    with pytest.raises(ServiceError) as caught:
        immediate_generation(service.classify('物流信息异常'))
    assert caught.value.code == 'invalid_structured_output'


@pytest.mark.parametrize('raw,ticket_request', [
    ('帮我建个工单', None),
    ('物流信息异常', {'origin_user_message_id': '1'}),
])
def test_explicit_ticket_and_verified_description_continuation_stay_available(raw, ticket_request, immediate_generation):
    model = ScriptedWorkflowModel(intent_replies=[reply({'intent': '工单', 'confidence': .98})])
    service = IntentClassifier(model, input_budget=20000, timeout_seconds=1)
    result = immediate_generation(service.classify(raw, ticket_request=ticket_request))
    assert result.intent == '工单'


@pytest.mark.parametrize('question,description', [
    ('饮水机不出水帮我建个工单', '饮水机不出水'),
    ('饮水机不能开机请帮我创建售后工单', '饮水机不能开机'),
    ('订单1001没收到货帮我建个工单', '订单1001没收到货'),
    ('订单一直未发货请帮我建工单', '订单一直未发货'),
    ('猫砂盆不能启动请帮我建个工单', '猫砂盆不能启动'),
    ('订单没收到包裹请帮我创建售后工单', '订单没收到包裹'),
])
def test_negative_fault_description_keeps_explicit_ticket_request(question, description, immediate_generation):
    """A fault's 不/没/未 must not negate the customer's later ticket action."""
    from app.workflow.ticket_requests import ticket_request_for_turn, grounded_description
    request = ticket_request_for_turn('9', question, {})
    assert request is not None
    assert request['source_message_ids'] == ['9']
    assert request['request_text'] == question
    assert request['source_texts'] == [question]
    assert grounded_description(description, request)
    model = ScriptedWorkflowModel(intent_replies=[reply({'intent': '工单', 'confidence': .98})])
    service = IntentClassifier(model, input_budget=20000, timeout_seconds=1)
    assert immediate_generation(service.classify(question)).intent == '工单'


@pytest.mark.parametrize('question', [
    '饮水机不出水不要帮我建工单',
    '我没有要求创建工单',
    '我没让你帮我建工单',
    '不用给我建工单',
    '不能帮我创建工单',
    '取消创建售后工单',
    '不要现在创建工单',
    '别急着帮我建工单',
    '不需要帮我立即创建工单',
    '不要未经确认就创建工单',
    '我没让你现在帮我建工单',
    '我没有说过要立即创建工单',
    '我不同意现在创建工单',
    '不应该帮我创建工单',
    '不能立刻创建工单',
    '别因为饮水机不出水帮我建工单',
    '饮水机不出水请帮我建工单但不要提交',
    '怎么建工单',
])
def test_ticket_action_denials_still_cannot_supply_write_evidence(question, immediate_generation):
    from app.workflow.ticket_requests import ticket_request_for_turn
    assert ticket_request_for_turn('9', question, {}) is None
    model = ScriptedWorkflowModel(intent_replies=[reply({'intent': '工单', 'confidence': .98})])
    service = IntentClassifier(model, input_budget=20000, timeout_seconds=1)
    with pytest.raises(ServiceError) as caught:
        immediate_generation(service.classify(question))
    assert caught.value.code == 'invalid_structured_output'
