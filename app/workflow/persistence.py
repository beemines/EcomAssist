"""官方异步 SQLite 生命周期接口。"""
from collections.abc import AsyncIterator
from contextlib import aclosing, asynccontextmanager
from pathlib import Path

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.config import Settings


@asynccontextmanager
async def open_checkpointer(path: Path) -> AsyncIterator[AsyncSqliteSaver]:
    """创建父目录并托管官方连接；坏文件与权限错误直接传播，不回退内存。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    async with AsyncSqliteSaver.from_conn_string(str(path)) as saver:
        # 通过公开读取接口触发官方惰性建表，启动时即传播文件损坏与建表错误。
        await saver.aget_tuple(checkpoint_config('__workflow_startup__'))
        yield saver


def checkpoint_config(conversation_id: str, *, checkpoint_id: str | None = None) -> RunnableConfig:
    """只从可信会话身份与可选历史快照派生根命名空间配置。"""
    configurable = {'thread_id': conversation_id, 'checkpoint_ns': ''}
    if checkpoint_id is not None:
        configurable['checkpoint_id'] = checkpoint_id
    return {'configurable': configurable}


async def durable_completed_root(checkpointer, snapshot, conversation_id: str, *, checkpoint_id: str | None = None) -> bool:
    """核验saver实际completed根，最新模式拒绝pending writes投影；历史模式只读指定根。"""
    stored = await checkpointer.aget_tuple(checkpoint_config(conversation_id, checkpoint_id=checkpoint_id))
    if stored is None or stored.config != snapshot.config:
        return False
    raw, final = stored.checkpoint['channel_values'], snapshot.values
    identity = stored.config.get('configurable', {})
    return (identity.get('thread_id') == conversation_id and identity.get('checkpoint_ns') == ''
        and raw.get('turn_status') == 'completed' and raw.get('conversation_id') == conversation_id
        and bool(raw.get('final_message_id')) and all(raw.get(key) == final.get(key) for key in
        ('user_message_id', 'final_message_id', 'final_answer', 'order_selection', 'refund_offer',
         'suggested_actions', 'citations')))


def checkpoint_path(settings: Settings, project_root: Path) -> Path:
    """相对检查点路径始终锚定项目根目录，绝对配置不受进程 cwd 影响。"""
    configured = settings.workflow_checkpoint_path
    return configured if configured.is_absolute() else project_root / configured


async def completed_history_roots(checkpointer, conversation_id: str):
    """一次遍历原始根，不叠加pending writes或读取最新图展示状态。"""
    async with aclosing(checkpointer.alist(checkpoint_config(conversation_id))) as roots:
        async for stored in roots:
            identity = stored.config.get('configurable', {})
            raw = stored.checkpoint.get('channel_values', {})
            if (identity.get('thread_id') == conversation_id and identity.get('checkpoint_ns') == ''
                    and identity.get('checkpoint_id') == stored.checkpoint.get('id')
                    and raw.get('conversation_id') == conversation_id and raw.get('turn_status') == 'completed'
                    and '__start__' not in raw and not raw.get('__pregel_tasks')
                    and not any(key.startswith('branch:to:') for key in raw)):
                # 当前父图仅log_response写completed并直连END。输入/Send/分支待调度根都不是原终态。
                yield identity['checkpoint_id'], raw
