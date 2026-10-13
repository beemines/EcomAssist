"""使用官方异步 SQLite 文件验证关闭重开、旧快照和故障传播。"""
import asyncio
import sqlite3

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime

from app.config import Settings
from app.workflow.persistence import checkpoint_config, checkpoint_path, open_checkpointer
from app.workflow.runtime import WorkflowRuntime
from app.workflow.state import WorkflowState, new_turn_state


def settings(**overrides):
    """显式使用虚假配置，关闭环境文件读取。"""
    return Settings(_env_file=None, llm_base_url='https://example.com/v1/',
                    llm_model='offline-test', llm_api_key='test-secret', **overrides)


def runtime_context():
    """不可序列化对象仅作为运行依赖，供真实图 context 验证。"""
    return WorkflowRuntime(model=object(), decision_model=object(), intent_model=object(),
                           repository=object(), faq_repository=object(), sufficiency=object(),
                           quality_repository=object(), registry={}, executor=object(),
                           settings=settings(), deadline=123.0, upstream=None)


def saving_graph(checkpointer):
    """只保存既有状态的小图，同时验证运行依赖与有序消息替换。"""
    def save(state: WorkflowState, runtime: Runtime[WorkflowRuntime]):
        """从运行 context 读期限，但只把本轮最终结果返回 State。"""
        assert runtime.context.deadline == 123.0
        return {'final_answer': '离线已完成', 'final_message_id': '104',
                'turn_status': 'completed',
                'messages': [*state['messages'], AIMessage('离线已完成', id='104')]}

    builder = StateGraph(WorkflowState, context_schema=WorkflowRuntime)
    builder.add_node('save', save)
    builder.add_edge(START, 'save')
    builder.add_edge('save', END)
    return builder.compile(checkpointer=checkpointer)


def turn(identifier=101):
    """构造可审计的单轮输入，不连接模型或业务数据库。"""
    return new_turn_state(conversation_id='c1', user_message_id=identifier,
                          raw_question='订单在哪', category=None,
                          messages=[HumanMessage('订单在哪')])


async def test_sqlite_reopen_recovers_state(tmp_path):
    """漏建父目录、用内存保存或提前关连接会使重开恢复失败。"""
    path = tmp_path / 'nested' / 'checkpoints.sqlite'
    async with open_checkpointer(path) as saver:
        graph = saving_graph(saver)
        await graph.ainvoke(turn(), checkpoint_config('c1'), context=runtime_context(), durability='sync')
        saved = await graph.aget_state(checkpoint_config('c1'))
        assert 'model' not in saved.values and 'deadline' not in saved.values
    assert path.is_file()
    async with open_checkpointer(path) as saver:
        restored = await saving_graph(saver).aget_state(checkpoint_config('c1'))
        assert restored.values['final_message_id'] == '104'
        assert [message.id for message in restored.values['messages']] == ['101', '104']
        assert restored.next == () and restored.values['turn_status'] == 'completed'
        assert (await saving_graph(saver).aget_state(checkpoint_config('other'))).values == {}
    with pytest.raises(ValueError):
        await saver.conn.execute('SELECT 1')
    pending = [task for task in asyncio.all_tasks() if task is not asyncio.current_task() and not task.done()]
    assert pending == []


async def test_old_snapshot_survives_new_turn(tmp_path):
    """新输入应替换消息与动作，旧 checkpoint_id 仍可跨重开读取。"""
    path = tmp_path / 'history.sqlite'
    async with open_checkpointer(path) as saver:
        graph = saving_graph(saver)
        old_input = turn()
        old_input['suggested_actions'] = ['handoff', 'create_ticket']
        await graph.ainvoke(old_input, checkpoint_config('c1'), context=runtime_context(), durability='sync')
        old_id = (await graph.aget_state(checkpoint_config('c1'))).config['configurable']['checkpoint_id']
        await graph.ainvoke(turn(105), checkpoint_config('c1'), context=runtime_context(), durability='sync')
    async with open_checkpointer(path) as saver:
        graph = saving_graph(saver)
        old = await graph.aget_state(checkpoint_config('c1', checkpoint_id=old_id))
        latest = await graph.aget_state(checkpoint_config('c1'))
        assert old.values['suggested_actions'] == ['handoff', 'create_ticket']
        assert old.values['user_message_id'] == '101'
        assert latest.values['suggested_actions'] == []
        assert [message.id for message in latest.values['messages']] == ['105', '104']


async def test_invalid_path_fails_without_memory_fallback(tmp_path):
    """父路径是文件时明确失败，不能悄悄改用内存后端。"""
    parent = tmp_path / 'not-a-directory'
    parent.write_text('blocked', encoding='utf-8')
    with pytest.raises((OSError, sqlite3.OperationalError)):
        async with open_checkpointer(parent / 'checkpoints.sqlite'):
            pytest.fail('invalid file path unexpectedly opened')


async def test_corrupt_database_fails_when_opening(tmp_path):
    """已损坏文件在启动时失败，不把坏文件当作空检查点。"""
    path = tmp_path / 'corrupt.sqlite'
    path.write_bytes(b'not a sqlite database')
    with pytest.raises(sqlite3.DatabaseError):
        async with open_checkpointer(path):
            pytest.fail('corrupt database unexpectedly opened')


async def test_directory_target_fails(tmp_path):
    """目标为目录时传播 SQLite 打开错误。"""
    with pytest.raises(sqlite3.OperationalError):
        async with open_checkpointer(tmp_path):
            pytest.fail('directory unexpectedly opened as database')


def test_checkpoint_path_is_anchored_to_project_root(tmp_path, monkeypatch):
    """改 cwd 不得改变默认检查点地址，绝对覆盖路径仍可使用。"""
    monkeypatch.delenv('WORKFLOW_CHECKPOINT_PATH', raising=False)
    root = tmp_path / 'project'
    root.mkdir()
    before = checkpoint_path(settings(), root)
    monkeypatch.chdir(tmp_path)
    assert before == checkpoint_path(settings(), root) == root / 'runtime/workflow/checkpoints.sqlite'
    absolute = tmp_path / 'override.sqlite'
    assert checkpoint_path(settings(workflow_checkpoint_path=absolute), root) == absolute


def test_checkpoint_path_environment_override(tmp_path, monkeypatch):
    """环境配置的相对路径仍锚定可信项目根目录。"""
    monkeypatch.setenv('WORKFLOW_CHECKPOINT_PATH', 'runtime/custom/checkpoints.sqlite')
    assert checkpoint_path(settings(), tmp_path) == tmp_path / 'runtime/custom/checkpoints.sqlite'


def test_checkpoint_config_uses_only_trusted_identity_and_root_namespace():
    """配置只由可信会话与可选快照身份派生，不接受外部命名空间。"""
    assert checkpoint_config('c1') == {'configurable': {'thread_id': 'c1', 'checkpoint_ns': ''}}
    assert checkpoint_config('c1', checkpoint_id='old') == {
        'configurable': {'thread_id': 'c1', 'checkpoint_ns': '', 'checkpoint_id': 'old'}}
