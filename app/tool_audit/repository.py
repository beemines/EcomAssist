import asyncio
from dataclasses import asdict
import logging

from app.db.models import ToolAuditLog
from app.tool_audit.types import ToolAuditRecord

logger = logging.getLogger(__name__)


class ToolAuditRepository:
    def __init__(self, database):
        self.database = database

    async def append(self, record: ToolAuditRecord) -> None:
        async with self.database.session() as session, session.begin():
            session.add(ToolAuditLog(**asdict(record)))


class BestEffortAuditSink:
    def __init__(self, repository, *, timeout_seconds: float = .5):
        if timeout_seconds <= 0:
            raise ValueError('Audit timeout must be positive.')
        self.repository, self.timeout_seconds = repository, timeout_seconds

    async def write(self, record: ToolAuditRecord) -> None:
        try:
            async with asyncio.timeout(self.timeout_seconds):
                await self.repository.append(record)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.warning('stage=tool_audit status=unavailable type=%s', type(exc).__name__)
