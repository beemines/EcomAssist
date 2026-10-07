import asyncio
from contextlib import asynccontextmanager
import hashlib

from sqlalchemy import text

from app.db.session import Database


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
            name = "ch03:" + hashlib.sha256(database_name.encode("utf-8")).hexdigest()[:48]
            result = await connection.scalar(text("SELECT GET_LOCK(:name, 0)"), {"name": name})
            if result != 1:
                raise RuntimeError("job lock unavailable")
            acquired = True
            await connection.commit()
        except BaseException:
            # Acquisition can have succeeded server-side even if the await was cancelled.
            await connection.invalidate()
            acquired = False
            raise
        yield
    finally:
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
