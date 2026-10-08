from datetime import datetime, timedelta, timezone

from sqlalchemy import select, text

from app.db.models import Conversation, Message
from app.db.session import Database
from app.knowledge.types import ConversationTranscript
from app.repositories.records import MessageRecord

BEIJING = timezone(timedelta(hours=8))


def beijing_time(value: datetime) -> datetime:
    """Window inputs without a timezone mean Beijing wall time."""
    if not isinstance(value, datetime):
        raise ValueError('window must use datetime values')
    return value.astimezone(BEIJING).replace(tzinfo=None) if value.tzinfo is not None else value


def window(start: datetime, end: datetime) -> tuple[datetime, datetime]:
    start, end = beijing_time(start), beijing_time(end)
    if start >= end:
        raise ValueError('window start must precede end')
    return start, end


def validate_batch_size(limit: int) -> None:
    if type(limit) is not int or not 1 <= limit <= 20:
        raise ValueError('batch size must be between 1 and 20')


class KnowledgeHistory:
    def __init__(self, database: Database):
        self.database = database

    async def completed(self, start: datetime, end: datetime, after_id: int = 0, limit: int = 20) -> list[ConversationTranscript]:
        start, end = window(start, end)
        validate_batch_size(limit)
        if type(after_id) is not int or after_id < 0:
            raise ValueError('after_id must be a nonnegative integer')
        async with self.database.session() as session, session.begin():
            # Existing timestamps are server-generated CURRENT_TIMESTAMP.
            # DATETIME does not convert timezone-aware Python parameters.
            local_now, utc_now = (await session.execute(text('SELECT NOW(), UTC_TIMESTAMP()'))).one()
            storage_zone = timezone(local_now - utc_now)
            stored_start, stored_end = [v.replace(tzinfo=BEIJING).astimezone(storage_zone).replace(tzinfo=None) for v in (start, end)]
            ids = (await session.scalars(select(Conversation.id).where(
                Conversation.status == '已结束', Conversation.updated_at >= stored_start,
                Conversation.updated_at < stored_end, Conversation.id > after_id,
            ).order_by(Conversation.id).limit(limit))).all()
            if not ids:
                return []
            rows = (await session.scalars(select(Message).where(Message.conversation_id.in_(ids)).order_by(Message.id))).all()
            grouped = {i: [] for i in ids}
            for row in rows:
                grouped[row.conversation_id].append(MessageRecord(row.id, row.role, row.content, row.tool_calls, row.tool_call_id))
            return [ConversationTranscript(i, grouped[i][-1].id if grouped[i] else 0, grouped[i]) for i in ids]
