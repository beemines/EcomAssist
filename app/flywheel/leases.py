"""A named lock and every protected write share the same physical connection."""
import asyncio
import hashlib
import logging
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class LeaseLost(RuntimeError):
    pass


class ProcessingLease:
    def __init__(self, connection, name, connection_id):
        self.connection, self.name, self.connection_id = connection, name, connection_id

    @asynccontextmanager
    async def transaction(self):
        if self.connection.closed or self.connection.invalidated:
            raise LeaseLost('Processing connection was lost')
        try:
            async with AsyncSession(bind=self.connection, expire_on_commit=False) as session, session.begin():
                row = (await session.execute(text('SELECT IS_USED_LOCK(:name),CONNECTION_ID()'),
                    {'name': self.name})).one()
                if row[0] != self.connection_id or row[1] != self.connection_id:
                    raise LeaseLost('Processing ownership changed')
                yield session
        except DBAPIError as exc:
            if self.connection.invalidated or exc.connection_invalidated:
                raise LeaseLost('Processing connection was lost') from None
            raise


async def _cleanup(connection, name, acquired):
    try:
        async with asyncio.timeout(3):
            if connection.in_transaction():
                await connection.rollback()
            if acquired and not connection.invalidated and not connection.closed:
                if await connection.scalar(text('SELECT RELEASE_LOCK(:name)'), {'name': name}) != 1:
                    raise LeaseLost('Processing lock release changed')
                await connection.commit()
    except Exception as exc:
        logger.warning('flywheel lease_cleanup error_type=%s', type(exc).__name__)
        try:
            async with asyncio.timeout(1):
                await connection.invalidate()
        except Exception:
            pass
    finally:
        async with asyncio.timeout(1):
            await connection.close()


@asynccontextmanager
async def processing_lease(database, *, prefix='ch09-flywheel:'):
    connection = await database.engine.connect()
    acquired, name = False, ''
    try:
        try:
            async with asyncio.timeout(5):
                target = await connection.scalar(text('SELECT DATABASE()'))
                if target != database.engine.url.database:
                    raise RuntimeError('Flywheel lease database mismatch')
                if prefix not in ('ch09-flywheel:', 'ch03:'):
                    raise ValueError('Unknown protected job lock')
                name = prefix + hashlib.sha256(target.encode()).hexdigest()[:48]
                identifier = await connection.scalar(text('SELECT CONNECTION_ID()'))
                acquired = await connection.scalar(text('SELECT GET_LOCK(:name,0)'), {'name': name}) == 1
                await connection.commit()
        except BaseException:
            await connection.invalidate()
            raise
        yield ProcessingLease(connection, name, identifier) if acquired else None
    finally:
        cleanup = asyncio.create_task(_cleanup(connection, name, acquired))
        cancelled = False
        while not cleanup.done():
            try:
                await asyncio.shield(cleanup)
            except asyncio.CancelledError:
                cancelled = True
        cleanup.result()
        if cancelled:
            raise asyncio.CancelledError
