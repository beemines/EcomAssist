# MySQL 命名锁绑定连接，因此获取、释放与取消清理必须使用同一条独占连接。
import asyncio
from contextlib import asynccontextmanager
import hashlib

from sqlalchemy import text

from app.db.session import Database


# 在独占连接上释放已获得的锁；释放失败则使连接失效，任何路径最终都关闭连接。
async def _finish(connection, name: str, acquired: bool) -> None:
    try:
        if acquired:
            try:
                released = await connection.scalar(text("SELECT RELEASE_LOCK(:name)"), {"name": name})
                if released != 1:
                    raise RuntimeError("job lock release failed")
            except BaseException:
                await connection.invalidate()
                raise
    finally:
        await connection.close()


# 为整个知识任务保留同一连接并获取数据库级互斥锁；取消时也等待清理完成。
@asynccontextmanager
async def job_lock(database: Database):
    """Reserve one connection until release or invalidation, including cancellation."""
    connection = await database.engine.connect()
    acquired = False
    name = ""
    try:
        try:
            database_name = await connection.scalar(text("SELECT DATABASE()"))
            if not database_name or database_name != database.engine.url.database:
                raise RuntimeError("job lock target database mismatch")
            # 锁名按实际数据库派生；超时为零，已有任务持锁时立即失败。
            name = "ch03:" + hashlib.sha256(database_name.encode("utf-8")).hexdigest()[:48]
            result = await connection.scalar(text("SELECT GET_LOCK(:name, 0)"), {"name": name})
            if result != 1:
                raise RuntimeError("job lock unavailable")
            acquired = True
            await connection.commit()
        except BaseException:
            # 等待获取锁被取消时，服务端仍可能已成功；使连接失效以消除遗留锁。
            await connection.invalidate()
            acquired = False
            raise
        yield
    finally:
        # 独立清理任务受 shield 保护；重复取消也先等释放或失效完成，再传播取消。
        cleanup = asyncio.create_task(_finish(connection, name, acquired))
        cancelled = False
        while not cleanup.done():
            try:
                await asyncio.shield(cleanup)
            except asyncio.CancelledError:
                cancelled = True
        cleanup.result()
        if cancelled:
            raise asyncio.CancelledError
