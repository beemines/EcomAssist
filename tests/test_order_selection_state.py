"""真实文件检查点验证纯暂停、恢复身份和预算隔离，不连接业务数据库。"""
import json
from dataclasses import replace
from uuid import UUID

import pytest
from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.orders.demo import DemoOrderProvider
from app.workflow.persistence import checkpoint_config, open_checkpointer
from app.workflow.runtime import WorkflowRuntime
from app.workflow.selection import await_order_selection, prepare_order_selection, remaining_active_seconds
from app.workflow.state import WorkflowState, new_turn_state
from tests.workflow_fakes import workflow_runtime


def turn(identifier=101):
    """创建当前SQL用户消息身份绑定的普通输入。"""
    return new_turn_state(conversation_id='c1', user_message_id=identifier,
        raw_question='这个能退吗', category=None, messages=[HumanMessage('这个能退吗')])


def context():
    """旧构造方式仍有效，暂存新依赖供准备节点读取。"""
    runtime = workflow_runtime()
    runtime.order_provider = DemoOrderProvider()
    runtime.user_id = 'demo-user'
    return runtime


def selection_graph(saver, *, prepare=True):
    """使用生产选择节点的小图，绕开尚未接线的主图。"""
    builder = StateGraph(WorkflowState, context_schema=WorkflowRuntime)
    builder.add_node('await_selection', await_order_selection)
    if prepare:
        builder.add_node('prepare_selection', prepare_order_selection)
        builder.add_edge(START, 'prepare_selection')
        builder.add_edge('prepare_selection', 'await_selection')
    else:
        builder.add_edge(START, 'await_selection')
    builder.add_edge('await_selection', END)
    return builder.compile(checkpointer=saver)


async def test_sqlite_pause_close_reopen_resume_same_turn(tmp_path):
    """丢失准备候选、恢复重查或重做模型都会破坏同轮持久化。"""
    path = tmp_path / 'selection.sqlite'
    initial_runtime = context()
    state = turn()
    state.update(stage_usage={'understanding': {'actual': 42, 'actual_calls': 1}},
        active_elapsed_seconds=30.0, tool_call_count=1,
        usage={'actual': 42, 'estimated': 0, 'actual_calls': 1, 'estimated_calls': 0},
        retrieval_audit={'queries': [{'source': 'original'}]})
    async with open_checkpointer(path) as saver:
        graph = selection_graph(saver)
        result = await graph.ainvoke(state, checkpoint_config('c1'), context=initial_runtime, durability='sync')
        paused = await graph.aget_state(checkpoint_config('c1'))
        assert paused.values['turn_status'] == 'awaiting_order' and paused.next
        selection = paused.values['order_selection']
        assert str(UUID(selection['selection_id'])) == selection['selection_id']
        assert selection['turn_id'] == '101' and selection['selected_order_id'] is None
        assert selection['pause_checkpoint_id'] is None and 'checkpoint_id' not in selection
        assert selection['cards'][0]['order_id'] == '1001'
        assert selection['cards'][0]['amount_cents'] == 19900
        assert selection['cards'][0]['as_of'] == '2026-10-15'
        payload = result['__interrupt__'][0].value
        assert payload['selection_id'] == selection['selection_id']
        assert payload['cards'] == selection['cards'] and payload['turn_id'] == '101'
        assert all('user_id' not in card for card in payload['cards'])
        json.dumps(payload)
        pause_id = paused.config['configurable']['checkpoint_id']
        print('actual paused root:', pause_id, 'next:', paused.next, 'turn:', selection['turn_id'])
    with pytest.raises(ValueError):
        await saver.conn.execute('SELECT 1')
    async with open_checkpointer(path) as saver:
        graph = selection_graph(saver)
        saved = await graph.aget_state(checkpoint_config('c1'))
        assert saved.values['order_selection'] == selection
        # 恢复context缺少订单provider，纯暂停节点仍须只用已存候选完成。
        resumed_runtime = workflow_runtime()
        await graph.ainvoke(Command(resume={'order_id': '1001', 'pause_checkpoint_id': pause_id}),
            checkpoint_config('c1'), context=resumed_runtime, durability='sync')
        restored = await graph.aget_state(checkpoint_config('c1'))
        assert restored.values['order_selection']['selected_order_id'] == '1001'
        assert restored.values['order_selection']['pause_checkpoint_id'] == pause_id
        assert restored.values['order_selection']['selection_id'] == selection['selection_id']
        assert restored.values['user_message_id'] == '101' and not restored.next
        assert restored.values['turn_status'] == 'running'
        assert [message.id for message in restored.values['messages']] == ['101']
        assert restored.values['stage_usage'] == {'understanding': {'actual': 42, 'actual_calls': 1}}
        assert restored.values['usage'] == {'actual': 42, 'estimated': 0, 'actual_calls': 1, 'estimated_calls': 0}
        assert restored.values['active_elapsed_seconds'] == 30.0
        assert restored.values['retrieval_audit'] == {'queries': [{'source': 'original'}]}
        assert restored.values['tool_call_count'] == 1
        assert remaining_active_seconds(restored.values) == 210
        assert restored.values['order_snapshot'] is None
        assert not {'deadline', 'model', 'session', 'lease', 'order_provider', 'user_id'} & restored.values.keys()
    for runtime in (initial_runtime, resumed_runtime):
        assert runtime.model.decisions == runtime.model.intents == runtime.model.streams == 0
        assert runtime.repository.messages == []


async def test_prepare_uses_trusted_identity_and_creates_independent_candidates():
    """缺少身份不能退回默认演示用户，候选持久化必须与提供器对象隔离。"""
    runtime = context()
    prepared = await prepare_order_selection(turn(), Runtime(context=runtime))
    selection = prepared['order_selection']
    assert prepared['turn_status'] == 'awaiting_order'
    assert [card['order_id'] for card in selection['cards']] == ['1001', '1002', '1003', '1004']
    again = await prepare_order_selection(turn(), Runtime(context=runtime))
    assert again['order_selection']['selection_id'] != selection['selection_id']
    runtime.user_id = 'other-user'
    empty = await prepare_order_selection(turn(), Runtime(context=runtime))
    assert empty['order_selection']['cards'] == []
    runtime.user_id = None
    with pytest.raises(ValueError, match='user'):
        await prepare_order_selection(turn(), Runtime(context=runtime))
    runtime.user_id, runtime.order_provider = 'demo-user', None
    with pytest.raises(ValueError, match='provider'):
        await prepare_order_selection(turn(), Runtime(context=runtime))


@pytest.mark.parametrize('resume', [{'order_id': None}, '1001', {'order_id': 1001}, {'order_id': ''},
    {'order_id': '9999'}, {'order_id': '1001', 'pause_checkpoint_id': ''},
    {'order_id': '1001', 'pause_checkpoint_id': 123}])
async def test_resume_rejects_malformed_or_non_candidate_order(tmp_path, resume):
    """客户端不能通过类型转换或非候选订单绕过已保存的选择范围。"""
    async with open_checkpointer(tmp_path / 'invalid.sqlite') as saver:
        graph = selection_graph(saver)
        await graph.ainvoke(turn(), checkpoint_config('c1'), context=context(), durability='sync')
        with pytest.raises(ValueError):
            await graph.ainvoke(Command(resume=resume), checkpoint_config('c1'),
                context=workflow_runtime(), durability='sync')
        latest = await graph.aget_state(checkpoint_config('c1'))
        assert latest.values['order_selection']['selected_order_id'] is None


@pytest.mark.parametrize('change', [
    {'order_selection': None},
    {'state_version': 1},
    {'turn_status': 'superseded'},
])
async def test_legacy_or_superseded_pending_cannot_enter_new_selection(tmp_path, change):
    """没有合法本轮选择身份的旧pending及已取代状态不能伪造续办。"""
    runtime = context()
    state = turn()
    state.update(await prepare_order_selection(state, Runtime(context=runtime)))
    state.update(change)
    async with open_checkpointer(tmp_path / 'legacy.sqlite') as saver:
        with pytest.raises(ValueError):
            await selection_graph(saver, prepare=False).ainvoke(state, checkpoint_config('c1'),
                context=runtime, durability='sync')


async def test_graph_only_resume_may_omit_pause_receipt(tmp_path):
    """内部小图允许省略公开服务才核验的根身份，仍严格选择候选。"""
    async with open_checkpointer(tmp_path / 'private.sqlite') as saver:
        graph = selection_graph(saver)
        await graph.ainvoke(turn(), checkpoint_config('c1'), context=context(), durability='sync')
        result = await graph.ainvoke(Command(resume={'order_id': '1002'}), checkpoint_config('c1'),
            context=workflow_runtime(), durability='sync')
        assert result['order_selection']['selected_order_id'] == '1002'
        assert result['order_selection']['pause_checkpoint_id'] is None


async def test_selection_without_original_sql_turn_identity_is_rejected(tmp_path):
    """双方缺失不能因None相等而被当作合法同轮身份。"""
    runtime = context()
    state = turn()
    state.update(await prepare_order_selection(state, Runtime(context=runtime)))
    state.pop('user_message_id')
    state['order_selection']['turn_id'] = None
    async with open_checkpointer(tmp_path / 'missing-turn.sqlite') as saver:
        with pytest.raises(ValueError, match='identity'):
            await selection_graph(saver, prepare=False).ainvoke(state, checkpoint_config('c1'),
                context=runtime, durability='sync')


def test_fresh_turn_clears_selection_and_refund_offer():
    """新输入覆盖所有新派生字段，不能继承旧单或退款权限。"""
    previous = turn()
    previous.update(raw_intent='退款退货', confidence=.98, order_selection={'selected_order_id': '1001'},
        order_snapshot={'order_id': '1001'}, retrieval_queries=['旧查询'], retrieval_audit={'old': True},
        refund_decision='eligible', decision_reason='旧理由', refund_offer={'offer_id': 'old'},
        stage_usage={'agent': {'actual': 900}}, active_elapsed_seconds=30.0, supersedes_turn_id='99')
    fresh = {**previous, **turn(105)}
    assert fresh['state_version'] == 2
    assert fresh['order_selection'] is None and fresh['refund_offer'] is None
    assert fresh['order_snapshot'] is None and fresh['refund_decision'] is None
    assert fresh['decision_reason'] is None and fresh['raw_intent'] is None and fresh['confidence'] is None
    assert fresh['retrieval_queries'] == [] and fresh['retrieval_audit'] == {}
    assert fresh['stage_usage'] == {} and fresh['active_elapsed_seconds'] == 0
    assert fresh['supersedes_turn_id'] is None


def test_resume_retains_usage_and_active_time():
    """剩余预算仅由累计活动耗时决定，人等待及当前deadline不参与。"""
    saved_state = turn()
    saved_state.update(active_elapsed_seconds=30.0, stage_usage={'intent': {'actual': 12}},
        usage={'actual': 12, 'estimated': 0, 'actual_calls': 1, 'estimated_calls': 0})
    before = dict(saved_state)
    assert remaining_active_seconds(saved_state) == 210
    assert remaining_active_seconds(saved_state, limit=90) == 60
    assert saved_state == before


@pytest.mark.parametrize(('elapsed', 'remaining'), [(0, 240), (240, 0), (300, 0)])
def test_active_budget_never_becomes_negative(elapsed, remaining):
    """超出累计限额时不能通过负余量重新取得预算。"""
    assert remaining_active_seconds({'active_elapsed_seconds': elapsed}) == remaining


@pytest.mark.parametrize('elapsed', [-1, float('nan'), float('inf'), '30', True])
def test_invalid_active_time_fails_closed(elapsed):
    """坏检查点计时不得创造额外执行预算。"""
    with pytest.raises(ValueError):
        remaining_active_seconds({'active_elapsed_seconds': elapsed})


def test_runtime_optional_tail_keeps_existing_constructor():
    """旧runtime构造依然可用，新依赖仅在context中按需注入。"""
    old = workflow_runtime()
    assert old.order_provider is None and old.understanding is None
    assert old.workflow_retriever is None and old.expander is None and old.user_id is None
    injected = replace(old, order_provider=DemoOrderProvider(), user_id='demo-user')
    assert injected.user_id == 'demo-user'
