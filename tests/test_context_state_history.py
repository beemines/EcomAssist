"""Full SQL history survives reducer updates, restarts and legacy root recovery."""
import importlib
import sqlite3

import pytest
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, ToolMessage
from langgraph.types import Overwrite

from app.repositories.records import message_from_record, record_from_message
from app.workflow.persistence import checkpoint_config, durable_completed_root
from tests.fakes import decode_sse
from tests.test_workflow_api import Store, intent, request, workflow_app
from tests.workflow_fakes import ScriptedWorkflowModel, workflow_call


def history():
    try:
        return importlib.import_module('app.workflow.history')
    except ModuleNotFoundError:
        pytest.fail('SQL history synchronization is missing')


def records(messages):
    return [record_from_message(m, identifier=i) for i, m in enumerate(messages, 1)]


def native(rows):
    return [message_from_record(r).model_copy(update={'id': str(r.id)}) for r in rows]


def root_bytes(path, checkpoint_id):
    with sqlite3.connect(path) as conn:
        return conn.execute('SELECT checkpoint, metadata FROM checkpoints WHERE checkpoint_ns = ? AND checkpoint_id = ?',
                            ('', checkpoint_id)).fetchone()


def test_sql_delta_and_bootstrap_restore_order_without_mutating_previous():
    rows = records([HumanMessage('old'), AIMessage('answer'), HumanMessage('current')])
    previous = {'context_version': 1, 'messages': native(rows[:2])}
    delta, bootstrap = history().prepare_history_update(previous, list(reversed(rows)), current_user_id=3)
    assert not bootstrap and [m.id for m in delta] == ['3']
    assert [m.id for m in previous['messages']] == ['1', '2']
    for prior in ({}, {'messages': native(rows[1:2])}, {'context_version': 1, 'messages': native(rows[1:2])}):
        update, bootstrap = history().prepare_history_update(prior, rows, current_user_id=3)
        assert bootstrap and isinstance(update, Overwrite)
        assert [m.id for m in update.value] == ['1', '2', '3']
    delta, bootstrap = history().prepare_history_update({'context_version': 1, 'messages': native(rows)}, rows, current_user_id=3)
    assert delta == [] and not bootstrap


def test_legacy_anonymous_ids_recover_original_sql_identity():
    rows = records([HumanMessage('old'), AIMessage('answer'), HumanMessage('current')])
    previous = {'messages': [HumanMessage('old', id='model-user'), AIMessage('answer', id='model-answer')]}
    update, bootstrap = history().prepare_history_update(previous, rows, current_user_id=3)
    assert bootstrap and [m.id for m in update.value] == ['1', '2', '3']
    assert [m.id for m in previous['messages']] == ['model-user', 'model-answer']


@pytest.mark.parametrize('damage', ['missing_sql', 'missing_current', 'duplicate_sql', 'corrupt_sql'])
def test_recovery_refuses_unrecoverable_raw_history(damage):
    rows = records([HumanMessage('old'), AIMessage('answer'), HumanMessage('current')])
    previous = {'messages': native(rows[:2])}
    if damage == 'missing_sql':
        rows = rows[1:]
    elif damage == 'missing_current':
        rows = rows[:2]
    elif damage == 'duplicate_sql':
        rows.append(rows[0])
    else:
        from dataclasses import replace
        rows[0] = replace(rows[0], content=None)
    with pytest.raises(ValueError):
        history().prepare_history_update(previous, rows, current_user_id=3)


async def test_two_turns_reopen_keep_sql_ids_and_original_root_bytes(tmp_path):
    store = Store()
    async with workflow_app(tmp_path, store=store) as app:
        assert decode_sse((await request(app, '你好')).text)[-1][0] == 'done'
        first = await app.state.chat_service.graph.aget_state(checkpoint_config('1'))
        original_id = first.config['configurable']['checkpoint_id']
    path = tmp_path / 'checkpoints.sqlite'
    original_bytes = root_bytes(path, original_id)
    async with workflow_app(tmp_path, store=store) as app:
        prepared = await app.state.chat_service.prepare('1', '谢谢')
        assert [m.id for m in prepared.graph_input['messages']] == ['3']
        frames = [event async for event in app.state.chat_service.stream(prepared)]
        app.state.chat_service.release(prepared)
        assert frames[-1].event == 'done'
    async with workflow_app(tmp_path, store=store) as app:
        latest = await app.state.chat_service.graph.aget_state(checkpoint_config('1'))
        old = await app.state.chat_service.graph.aget_state(checkpoint_config('1', checkpoint_id=original_id))
        assert latest.values['state_version'] == 2 and latest.values['context_version'] == 1
        assert [m.id for m in latest.values['messages']] == ['1', '2', '3', '4']
        assert [m.id for m in latest.values['messages']] == [str(r.id) for r in await store.load_messages('1')]
        assert len({m.id for m in latest.values['messages']}) == 4
        assert old.values == first.values
        assert await durable_completed_root(app.state.chat_service.checkpointer, old, '1', checkpoint_id=original_id)
    assert root_bytes(path, original_id) == original_bytes


@pytest.mark.parametrize('truncated', [False, True])
async def test_legacy_completed_root_bootstraps_only_new_root(tmp_path, truncated):
    from langgraph.graph import END, START, StateGraph
    from app.workflow.state import WorkflowState, new_turn_state
    from app.workflow.persistence import open_checkpointer
    store = Store()
    await store.seed('1', [HumanMessage('first'), AIMessage('first answer'), HumanMessage('second'), AIMessage('second answer')])
    rows = await store.load_messages('1')
    old = new_turn_state(conversation_id='1', user_message_id=3, raw_question='second', category=None, messages=[])
    for key in list(old):
        if key.startswith('context_'):
            old.pop(key)
    old.update(messages=native(rows[2:] if truncated else rows), final_message_id='4', final_answer='second answer', turn_status='completed')
    path = tmp_path / 'checkpoints.sqlite'
    async with open_checkpointer(path) as saver:
        builder = StateGraph(WorkflowState)
        builder.add_node('save', lambda state: {})
        builder.add_edge(START, 'save'); builder.add_edge('save', END)
        graph = builder.compile(checkpointer=saver)
        await graph.ainvoke(old, checkpoint_config('1'))
        old_id = (await graph.aget_state(checkpoint_config('1'))).config['configurable']['checkpoint_id']
    before = root_bytes(path, old_id)
    async with workflow_app(tmp_path, store=store) as app:
        service = app.state.chat_service
        prepared = await service.prepare('1', '你好')
        assert isinstance(prepared.graph_input['messages'], Overwrite)
        assert prepared.state['context_bootstrap'] is True
        assert [m.id for m in prepared.state['messages']] == ['1', '2', '3', '4', '5']
        assert (await anext_to_end(service, prepared)).event == 'done'
        latest = await service.graph.aget_state(checkpoint_config('1'))
        assert [m.id for m in latest.values['messages']] == ['1', '2', '3', '4', '5', '6']
    assert root_bytes(path, old_id) == before


async def anext_to_end(service, prepared):
    try:
        events = [event async for event in service.stream(prepared)]
        return events[-1]
    finally:
        service.release(prepared)


async def test_cancelled_audit_survives_next_business_turn_and_child_delta(tmp_path):
    from tests.test_workflow_agent import control
    store = Store()
    await store.seed('1', [HumanMessage('cancelled user'), workflow_call(), ToolMessage('{"found":true}', tool_call_id='call_1'),
                           HumanMessage('another cancelled user'), workflow_call(identifier='orphan')])
    model = ScriptedWorkflowModel([control(mode='clarification')], intent_replies=[intent('订单')],
        final_chunks=[AIMessageChunk('请提供订单号。'), AIMessageChunk('', response_metadata={'finish_reason': 'stop'})])
    async with workflow_app(tmp_path, model=model, store=store) as app:
        frames = decode_sse((await request(app, '想查订单')).text)
        assert frames[-1][0] == 'done'
        latest = await app.state.chat_service.graph.aget_state(checkpoint_config('1'))
        assert [m.id for m in latest.values['messages']] == ['1', '2', '3', '4', '5', '6', '7']
        assert latest.values['messages'][4].tool_calls[0]['id'] == 'orphan'
        assert all(not isinstance(m, ToolMessage) for m in model.tool_inputs[0])


def test_child_output_contains_only_new_sql_messages():
    from app.workflow import agent
    assert hasattr(agent, 'agent_delta'), 'child output delta adapter is missing'
    result = {'messages': [HumanMessage('old', id='1'), AIMessage('new', id='2')], 'final_answer': 'new'}
    update = agent.agent_delta(frozenset({'1'}), result)
    assert [m.id for m in update['messages']] == ['2'] and update['final_answer'] == 'new'
    assert len(result['messages']) == 2


async def test_actual_parent_child_stream_emits_only_sql_deltas(tmp_path):
    from app.workflow.agent import build_agent_graph
    from app.workflow.graph import build_workflow_graph
    from app.workflow.persistence import open_checkpointer
    from tests.test_workflow_agent import control, setup
    ctx, state = setup([workflow_call(), control()], answer='模拟查询：订单待发货。')
    store = Store()
    await store.seed('1', [HumanMessage(state['raw_question'])])
    ctx.repository = ctx.quality_repository = store
    state['conversation_id'] = '1'
    async with open_checkpointer(tmp_path / 'child.sqlite') as saver:
        graph = build_workflow_graph(build_agent_graph(), checkpointer=saver)
        events = [event async for event in graph.astream(state, checkpoint_config('1'), context=ctx,
            stream_mode=['updates', 'custom'], subgraphs=True, durability='sync')]
        root = await graph.aget_state(checkpoint_config('1'))
        parent_updates = {name: update for ns, kind, event in events if not ns and kind == 'updates'
                          for name, update in event.items()}
        assert [m.id for m in parent_updates['agent']['messages']] == ['2', '3']
        assert [m.id for m in parent_updates['log_response']['messages']] == ['4']
        child_updates = [update for ns, kind, event in events if ns and kind == 'updates'
                         for name, update in event.items() if name == 'tool_node']
        assert len(child_updates) == 1 and [m.id for m in child_updates[0]['messages']] == ['2', '3']
        assert any(kind == 'custom' and event.get('event') == 'delta' for _, kind, event in events)
        assert [m.id for m in root.values['messages']] == ['1', '2', '3', '4']
        assert [m.id for m in root.values['messages']] == [str(r.id) for r in await store.load_messages('1')]


@pytest.mark.parametrize('resume', [True, False])
async def test_pending_restart_resumes_or_replaces_without_duplicating_user(tmp_path, resume):
    from tests.test_order_resume_lifecycle import OwnerStore, app_context, pause, reply, selection
    store = OwnerStore()
    async with app_context(tmp_path, store=store) as (_, client):
        card, _ = await pause(client)
    path = tmp_path / 'resume.sqlite'
    before = root_bytes(path, card['checkpoint_id'])
    model = ScriptedWorkflowModel(intent_replies=[reply({'queries': ['这个能退吗？', 'MH-LP200退货政策']})])
    async with app_context(tmp_path, store=store, model=model) as (app, client):
        if resume:
            response = await client.post('/api/conversations/1/actions/select-order', json=selection(card))
        else:
            response = await client.post('/api/chat', json={'conversation_id': '1', 'message': '你好'})
        assert decode_sse(response.text)[-1][0] == 'done'
        root = await app.state.chat_service.graph.aget_state(checkpoint_config('1'))
        rows = await store.load_messages('1')
        assert [m.id for m in root.values['messages']] == [str(r.id) for r in rows]
        assert len({m.id for m in root.values['messages']}) == len(rows)
        assert sum(r.role == 'user' for r in rows) == (1 if resume else 2)
        if resume:
            assert root.values['order_selection']['pause_checkpoint_id'] == card['checkpoint_id']
        else:
            assert root.values['supersedes_turn_id'] == card['turn_id']
            stale = await client.post('/api/conversations/1/actions/select-order', json=selection(card))
            assert stale.status_code == 409
    assert root_bytes(path, card['checkpoint_id']) == before


async def test_failed_request_is_synchronized_from_sql_as_delta_on_next_turn(tmp_path):
    from tests.fakes import FAQStub
    from tests.test_workflow_agent import control
    store = Store()
    model = ScriptedWorkflowModel([control(mode='clarification')], intent_replies=[intent('商品咨询'), intent('订单')],
        final_chunks=[AIMessageChunk('请提供订单号。'), AIMessageChunk('', response_metadata={'finish_reason': 'stop'})])
    async with workflow_app(tmp_path, store=store, model=model, faq=FAQStub(failure=RuntimeError('controlled failed read'))) as app:
        assert decode_sse((await request(app, '商品参数')).text)[-1][0] == 'error'
        service = app.state.chat_service
        failed = await service.graph.aget_state(checkpoint_config('1'))
        assert [m.id for m in failed.values['messages']] == ['1']
        assert [r.role for r in await store.load_messages('1')] == ['user', 'assistant']
        prepared = await service.prepare('1', '想查订单')
        assert [m.id for m in prepared.graph_input['messages']] == ['2', '3']
        assert prepared.state['context_bootstrap'] is False
        assert (await anext_to_end(service, prepared)).event == 'done'
        latest = await service.graph.aget_state(checkpoint_config('1'))
        assert [m.id for m in latest.values['messages']] == ['1', '2', '3', '4']
        assert latest.values['messages'][1].tool_calls
        assert all(not isinstance(m, ToolMessage) for m in model.tool_inputs[0])


async def test_model_history_trim_never_replaces_checkpoint_raw_text(tmp_path):
    from tests.test_workflow_agent import control
    store = Store()
    long_answer = '完整审计正文' * 2500
    await store.seed('1', [HumanMessage('旧问题'), AIMessage(long_answer)])
    model = ScriptedWorkflowModel([control(mode='clarification')], intent_replies=[intent('订单')],
        final_chunks=[AIMessageChunk('请提供订单号。'), AIMessageChunk('', response_metadata={'finish_reason': 'stop'})])
    async with workflow_app(tmp_path, store=store, model=model, model_context_window=18000,
            max_output_tokens=2000, max_user_input_tokens=2000, max_agent_steps=3,
            tool_result_max_tokens=1200, rerank_top_k=5) as app:
        assert decode_sse((await request(app, '想查订单')).text)[-1][0] == 'done'
        snapshot = await app.state.chat_service.graph.aget_state(checkpoint_config('1'))
        assert [m.id for m in snapshot.values['messages']] == ['1', '2', '3', '4']
        assert snapshot.values['messages'][1].content == long_answer
        assert all(m.content != long_answer for m in model.tool_inputs[0])
        assert any(m.content == long_answer[:80] + '后文已截短' for m in model.tool_inputs[0])
        assert store.rows['1'][1].content == long_answer
