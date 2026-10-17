"""Shared frozen context, SQL provenance and current-turn priority."""
from dataclasses import replace
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from sqlalchemy import text
from app.core.errors import ServiceError

from app.context.types import ContextAnchors, SummarySegment
from app.repositories.records import MessageRecord
from tests.test_context_manager import repository, seed, budget


class Notifications:
    def __init__(self):
        self.calls = []

    def notify(self, conversation_id, **fields):
        self.calls.append((conversation_id, fields))
        return True


async def rows(repo):
    async with repo.database.session() as session:
        result = await session.execute(text('SELECT id,role,content,tool_calls,tool_call_id FROM messages ORDER BY id'))
        return [MessageRecord(*row) for row in result]


async def test_coordinator_advances_sql_and_freezes_before_background_commit(repository):
    from app.context.service import ContextCoordinator
    await seed(repository, downgraded=False, size=100)
    manager = Notifications()
    coordinator = ContextCoordinator(repository, manager, SimpleNamespace())
    snapshot = await coordinator.prepare('1', '103', await rows(repository), budget(layer1=30))
    assert snapshot.anchors == ContextAnchors(None, 102)
    assert snapshot.layer2[-1].content == '请等待核实。'
    batch = await repository.load_batch('1', target_upto=102)
    await repository.append_segment(batch, '订单 O-1 的包裹未找到。', summary_budget=1000)
    assert snapshot.summaries == () and snapshot.anchors.summary_upto is None
    coordinator.on_completed(snapshot)
    following = await coordinator.prepare('1', '105', await rows(repository), budget())
    assert following.summaries[0].content == '订单 O-1 的包裹未找到。'
    assert following.layer2 == () and following.layer1 == ()


async def test_capacity_failure_still_notifies_existing_downgraded_backlog(repository):
    from app.context.service import ContextCoordinator
    from app.context.layers import ContextCapacityError
    await seed(repository, size=100)
    manager = Notifications()
    coordinator = ContextCoordinator(repository, manager, SimpleNamespace())
    with pytest.raises(ContextCapacityError):
        await coordinator.prepare('1', '103', await rows(repository), budget(history=20, layer1=10, layer2=10))
    assert len(manager.calls) == 1 and manager.calls[0][1]['layer2_tokens'] > 10


def test_provenance_rejects_assistant_and_omitted_summary_entities():
    from app.workflow.entities import snapshot_provenance, validate_snapshot_entities
    from tests.test_context_view import snapshot
    source = [MessageRecord(1, 'user', '订单 A-1 有问题', None, None),
              MessageRecord(2, 'assistant', '订单 FAKE-9 已退款', None, None),
              MessageRecord(3, 'user', '订单 B-2 有问题', None, None),
              MessageRecord(4, 'assistant', '已记录', None, None)]
    segments = (SummarySegment(1, 1, 2, '订单 FAKE-9 已退款', datetime.now(timezone.utc)),
                SummarySegment(2, 3, 4, '订单 B-2 有问题', datetime.now(timezone.utc)))
    frozen = snapshot(anchors=ContextAnchors(4, 4), segments=segments)
    provenance = snapshot_provenance(frozen, source)
    with pytest.raises(ServiceError):
        validate_snapshot_entities('最开始那个订单呢', '订单 FAKE-9 呢', frozen, provenance)
    omitted = replace(frozen, summaries=(segments[1],), omitted_summary_seqs=(1,))
    with pytest.raises(ServiceError):
        validate_snapshot_entities('最开始那个订单呢', '订单 A-1 呢', omitted, snapshot_provenance(omitted, source))


@pytest.mark.parametrize('raw,resolved,valid', [
    ('最开始那个订单后来怎么说', '订单 A-1 后来怎么说', True),
    ('最开始那个订单后来怎么说', '订单 B-2 后来怎么说', False),
    ('那单呢', '订单 B-2 呢', True),
    ('改查订单 C-3，不要退款', '改查订单 C-3，不要退款', True),
    ('改查订单 C-3，不要退款', '订单 B-2 申请退款', False),
    ('手机号改为13900000000', '手机号改为13800000000', False),
])
def test_snapshot_identity_annotations(raw, resolved, valid):
    from app.workflow.entities import snapshot_provenance, validate_snapshot_entities
    from tests.test_context_view import snapshot
    source = [MessageRecord(1, 'user', '订单 A-1 手机号13800000000', None, None),
              MessageRecord(2, 'assistant', '记录', None, None),
              MessageRecord(3, 'user', '订单 B-2 有问题', None, None),
              MessageRecord(4, 'assistant', '记录', None, None)]
    segments = (SummarySegment(1, 1, 2, '订单 A-1 手机号13800000000', datetime.now(timezone.utc)),
                SummarySegment(2, 3, 4, '订单 B-2 有问题', datetime.now(timezone.utc)))
    frozen = snapshot(anchors=ContextAnchors(4, 4), segments=segments)
    provenance = snapshot_provenance(frozen, source)
    if valid:
        validate_snapshot_entities(raw, resolved, frozen, provenance)
    else:
        with pytest.raises(ServiceError):
            validate_snapshot_entities(raw, resolved, frozen, provenance)


async def test_understanding_and_intent_send_the_same_snapshot_without_8000_crop(tmp_path):
    import json
    from langchain_core.messages import AIMessage
    from app.context.logging import ContextLogger
    from app.workflow.understanding import QueryUnderstanding
    from app.workflow.intent import IntentClassifier
    from tests.test_context_view import snapshot
    from tests.test_context_layers import turn
    from tests.workflow_fakes import ScriptedWorkflowModel
    raw = '订单 A-1 怎么样' + '补充' * 300
    model = ScriptedWorkflowModel(intent_replies=[
        AIMessage(json.dumps({'query': raw}, ensure_ascii=False), response_metadata={'finish_reason': 'stop'}),
        AIMessage('{"intent":"订单","confidence":0.95}', response_metadata={'finish_reason': 'stop'})])
    frozen = snapshot(rows=turn(1, results=(), answer='原文' * 3000),
                      limits=budget(window=25000, history=12000, layer1=12000))
    logger = ContextLogger(tmp_path / 'app.log')
    understanding = QueryUnderstanding(model, input_budget=100, timeout_seconds=2)
    result = await understanding.resolve(raw, [], snapshot=frozen, provenance=(), context_logger=logger)
    classifier = IntentClassifier(model, input_budget=100, timeout_seconds=2)
    await classifier.classify(raw, snapshot=frozen, resolved_question=result.query, context_logger=logger)
    logger.close()
    assert result.query == raw and len(raw) > 512
    left, right = model.intent_inputs
    assert left[1:-2] == right[1:-2] and left[-2].content == right[-2].content == raw
    assert any(message.content == '原文' * 3000 for message in left)
    logged = [json.loads(line) for line in (tmp_path / 'app.log').read_text(encoding='utf-8').splitlines()]
    assert {item['snapshot_id'] for item in logged} == {frozen.snapshot_id}
    assert [item['consumer'] for item in logged if item['event'] == 'history_ctx'] == ['understanding', 'classification']


async def test_social_workflow_logs_unsent_and_preserves_full_state(tmp_path):
    import json
    from app.main import create_app
    from app.context.logging import ContextLogger
    from app.context.service import ContextCoordinator
    from tests.fakes import fake_settings, FAQStub, decode_sse
    from tests.test_workflow_api import Store, request
    from tests.workflow_fakes import ScriptedWorkflowModel
    from app.workflow.persistence import checkpoint_config

    class EmptyContext:
        async def load(self, cid):
            return ContextAnchors(None, None), ()
    manager, model = Notifications(), ScriptedWorkflowModel()
    logger = ContextLogger(tmp_path / 'app.log')
    app = create_app(fake_settings(workflow_checkpoint_path=tmp_path / 'root.sqlite'),
        model=model, repository=Store(), faq_repository=FAQStub(),
        context_coordinator=ContextCoordinator(EmptyContext(), manager, None),
        context_logger=logger, context_budget_provider=lambda registry: budget())
    async with app.router.lifespan_context(app):
        frames = decode_sse((await request(app, '你好')).text)
        assert frames[-1][0] == 'done'
        saved = await app.state.chat_service.graph.aget_state(checkpoint_config('1'))
        assert [message.content for message in saved.values['messages']][0] == '你好'
        assert saved.values['context_snapshot_id']
        assert len(manager.calls) == 1
    logger.close()
    records = [json.loads(line) for line in (tmp_path / 'app.log').read_text(encoding='utf-8').splitlines()]
    assert any(item['event'] == 'history_ctx' and item['sent'] is False for item in records)
    assert not any(item['event'] == 'model_ctx' for item in records)
    assert model.intents == model.decisions == model.streams == 0


def test_frozen_snapshot_json_roundtrip_and_smaller_deployment_conflict():
    import json
    from app.context.service import serialize_snapshot, restore_snapshot
    from tests.test_context_view import snapshot
    from tests.test_context_layers import turn
    frozen = snapshot(rows=turn(1, results=(), answer='原文' * 1000),
                      limits=budget(window=20000, history=10000, layer1=10000))
    saved = json.loads(json.dumps(serialize_snapshot(frozen)))
    restored = restore_snapshot(saved, budget(window=22000, history=10000, layer1=10000))
    assert restored.snapshot_id == frozen.snapshot_id and restored.layer1 == frozen.layer1
    assert restored.budget.window == 22000
    with pytest.raises(ServiceError) as conflict:
        restore_snapshot(saved, budget(window=1000, history=100, layer1=70))
    assert conflict.value.code == 'context_configuration_conflict'


async def test_long_query_retrieval_limit_is_explicit_before_tool_write():
    from app.workflow import nodes
    from langgraph.runtime import Runtime
    from tests.workflow_fakes import workflow_runtime
    from app.workflow.state import new_turn_state
    from langchain_core.messages import HumanMessage
    context = workflow_runtime()
    state = new_turn_state(conversation_id='1', user_message_id=1, raw_question='问题' * 300,
                          category=None, messages=[HumanMessage('问题' * 300, id='1')])
    state.update(route='knowledge', intent='商品咨询')
    with pytest.raises(ServiceError) as exc:
        await nodes.retrieve_knowledge(state, Runtime(context=context))
    assert exc.value.code == 'input_too_long'
    assert context.repository.messages == []


async def test_cas_race_reloads_committed_summary_without_double_injection(repository):
    from app.context.service import ContextCoordinator
    await seed(repository, downgraded=False, size=30)
    original = repository.advance_layer1
    async def competing_commit(cid, **kwargs):
        assert await original(cid, **kwargs)
        batch = await repository.load_batch(cid, target_upto=102)
        await repository.append_segment(batch, '订单 O-1 的包裹未找到。', summary_budget=1000)
        return False
    repository.advance_layer1 = competing_commit
    snapshot = await ContextCoordinator(repository, Notifications(), None).prepare(
        '1', '103', await rows(repository), budget(layer1=20))
    assert snapshot.anchors == ContextAnchors(102, 102)
    assert len(snapshot.summaries) == 1 and snapshot.layer1 == snapshot.layer2 == ()


@pytest.mark.parametrize('status', [{'status': 'error'}, {'success': False}])
def test_failed_paired_read_cannot_prove_summary_order(status):
    import json
    from app.workflow.entities import snapshot_provenance, validate_snapshot_entities
    from tests.test_context_view import snapshot
    from tests.test_context_layers import turn
    source = turn(1, user='查询一下', results=(json.dumps({'order_id': 'ORD-123', **status}),))
    frozen = snapshot(anchors=ContextAnchors(4, 4), segments=(SummarySegment(
        1, 1, 4, '订单 ORD-123 当时查询失败', datetime.now(timezone.utc)),))
    with pytest.raises(ServiceError):
        validate_snapshot_entities('那单呢', '订单 ORD-123 呢', frozen, snapshot_provenance(frozen, source))


def test_current_new_phone_cannot_be_combined_with_old_phone():
    from app.workflow.entities import IdentitySource, validate_snapshot_entities
    from tests.test_context_view import snapshot
    with pytest.raises(ServiceError):
        validate_snapshot_entities('改成13900000000', '改成13900000000或13800000000', snapshot(),
            (IdentitySource(1, None, frozenset(), ('13800000000',)),))


def test_layer2_request_id_does_not_turn_unknown_result_into_trusted_order():
    from app.workflow.entities import snapshot_provenance, validate_snapshot_entities
    from tests.test_context_view import snapshot
    from tests.test_context_layers import turn
    source = turn(1, user='查一下', results=('not-json' * 100,))
    frozen = snapshot(rows=source, anchors=ContextAnchors(None, 4))
    with pytest.raises(ServiceError):
        validate_snapshot_entities('那单呢', '订单 ORD-123 呢', frozen, snapshot_provenance(frozen, source))


def test_interrupted_user_identity_remains_visible_but_hidden_tool_fields_do_not():
    from app.workflow.entities import snapshot_provenance, validate_snapshot_entities
    from tests.test_context_view import snapshot
    source = [MessageRecord(1, 'user', '订单 A-1', None, None)]
    frozen = snapshot(rows=source)
    provenance = snapshot_provenance(frozen, source)
    validate_snapshot_entities('那单呢', '订单 A-1 呢', frozen, provenance)
    assert provenance[0].from_msg_id == 1


def test_summary_model_identity_must_match_whole_original_token():
    from app.workflow.entities import snapshot_provenance, validate_snapshot_entities
    from tests.test_context_view import snapshot
    source = [MessageRecord(1, 'user', '型号 M-10 有问题', None, None),
              MessageRecord(2, 'assistant', '记录', None, None)]
    frozen = snapshot(anchors=ContextAnchors(2, 2), segments=(SummarySegment(
        1, 1, 2, '型号 M-1 有问题', datetime.now(timezone.utc)),))
    with pytest.raises(ServiceError):
        validate_snapshot_entities('它呢', 'M-1 呢', frozen, snapshot_provenance(frozen, source))


async def test_understanding_output_reserve_counts_json_escaping_before_call():
    from app.workflow.understanding import QueryUnderstanding
    from tests.workflow_fakes import ScriptedWorkflowModel
    from tests.test_context_view import snapshot
    from app.core.errors import InputTooLong
    model = ScriptedWorkflowModel()
    service = QueryUnderstanding(model, input_budget=8000, timeout_seconds=2)
    with pytest.raises(InputTooLong):
        await service.resolve('"' * 4000, [], snapshot=snapshot(), output_tokens=2048)
    assert model.intents == 0


@pytest.mark.parametrize('raw,resolved', [('最开始那个订单呢', '订单 A-1 呢'), ('最近那个订单呢', '订单 B-2 呢')])
def test_single_injected_segment_preserves_original_turn_order(raw, resolved):
    from app.workflow.entities import snapshot_provenance, validate_snapshot_entities
    from tests.test_context_view import snapshot
    source = [MessageRecord(1, 'user', '订单 A-1 有问题', None, None),
              MessageRecord(2, 'assistant', '记录', None, None),
              MessageRecord(3, 'user', '订单 B-2 有问题', None, None),
              MessageRecord(4, 'assistant', '记录', None, None)]
    frozen = snapshot(anchors=ContextAnchors(4, 4), segments=(SummarySegment(
        1, 1, 4, '先询问订单 A-1，随后询问订单 B-2，均待处理。', datetime.now(timezone.utc)),))
    validate_snapshot_entities(raw, resolved, frozen, snapshot_provenance(frozen, source))


def test_multiple_orders_in_same_source_turn_remain_ambiguous():
    from app.workflow.entities import snapshot_provenance, validate_snapshot_entities
    from tests.test_context_view import snapshot
    source = [MessageRecord(1, 'user', '订单 A-1 和 B-2 都有问题', None, None),
              MessageRecord(2, 'assistant', '请明确是哪单', None, None)]
    frozen = snapshot(anchors=ContextAnchors(2, 2), segments=(SummarySegment(
        1, 1, 2, '订单 A-1 和 B-2 均有问题，未区分指代。', datetime.now(timezone.utc)),))
    with pytest.raises(ServiceError):
        validate_snapshot_entities('最开始那个订单呢', '订单 A-1 呢', frozen, snapshot_provenance(frozen, source))
