"""官方异步 SQLite 生命周期接口。"""
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
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


def checkpoint_path(settings: Settings, project_root: Path) -> Path:
    """相对检查点路径始终锚定项目根目录，绝对配置不受进程 cwd 影响。"""
    configured = settings.workflow_checkpoint_path
    return configured if configured.is_absolute() else project_root / configured
