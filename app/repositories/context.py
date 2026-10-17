"""独立短事务保存分层锚点和追加式摘要；模型生成发生在仓储调用之外。"""
from dataclasses import astuple
import hashlib
import json

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.context.tokens import estimate_text_tokens
from app.context.types import ContextAnchors, FrozenMessage, SummaryBatch, SummarySegment
from app.db.models import Conversation, ConversationSummary, Message
from app.db.session import Database
from app.repositories.conversations import _conversation_id, _require_conversation
from app.core.tool_history import completed_boundaries as _completed_boundaries


def _anchors(row: Conversation) -> ContextAnchors:
    result = ContextAnchors(row.summary_upto_msg_id, row.layer1_from_msg_id)
    if (result.summary_upto or 0) > (result.layer1_from or 0):
        raise RuntimeError('context anchor invariant violated: summary exceeds layer1')
    return result


def _segment(row: ConversationSummary) -> SummarySegment:
    return SummarySegment(row.seq, row.from_msg_id, row.upto_msg_id, row.content, row.created_at)


def _frozen(rows) -> tuple[FrozenMessage, ...]:
    return tuple(FrozenMessage(str(row.id), row.role, row.content,
        json.dumps(row.tool_calls, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
        if row.tool_calls is not None else None, row.tool_call_id) for row in rows)


def _source_hash(rows: tuple[FrozenMessage, ...]) -> str:
    payload = json.dumps([astuple(row) for row in rows], ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def _projection(segments: tuple[SummarySegment, ...], budget: int) -> str:
    """投影只计以换行拼接的正文，同一版本启发式；实际附件另计包装。"""
    selected = []
    for segment in reversed(segments):
        candidate = '\n'.join([segment.content, *selected])
        if estimate_text_tokens(candidate) > budget:
            break
        selected.insert(0, segment.content)
    return '\n'.join(selected)


class ContextRepository:
    def __init__(self, database: Database):
        self.database = database

    async def list_downgraded(self, *, after_id: int = 0, limit: int = 100) -> tuple[str, ...]:
        """Keyset recovery page; never scan or summarize untouched legacy conversations."""
        if type(after_id) is not int or after_id < 0 or type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError('Recovery requires a nonnegative cursor and page size 1..100.')
        statement = select(Conversation.id).where(
            Conversation.id > after_id, Conversation.layer1_from_msg_id.is_not(None),
            Conversation.layer1_from_msg_id > func.coalesce(Conversation.summary_upto_msg_id, 0),
        ).order_by(Conversation.id).limit(limit)
        async with self.database.session() as session, session.begin():
            return tuple(str(identifier) for identifier in await session.scalars(statement))

    async def _conversation(self, session, identifier: int, *, lock: bool = False):
        statement = select(Conversation).where(Conversation.id == identifier)
        if lock:
            statement = statement.with_for_update()
        conversation = (await session.scalars(statement)).first()
        _require_conversation(conversation, open_only=False)
        return conversation

    async def _rows(self, session, identifier: int):
        return (await session.scalars(select(Message).where(Message.conversation_id == identifier).order_by(Message.id))).all()

    async def _segments(self, session, identifier: int) -> tuple[SummarySegment, ...]:
        rows = (await session.scalars(select(ConversationSummary)
            .where(ConversationSummary.conversation_id == identifier).order_by(ConversationSummary.seq))).all()
        return tuple(_segment(row) for row in rows)

    async def load(self, conversation_id: str) -> tuple[ContextAnchors, tuple[SummarySegment, ...]]:
        identifier = _conversation_id(conversation_id)
        async with self.database.session() as session, session.begin():
            conversation = await self._conversation(session, identifier)
            return _anchors(conversation), await self._segments(session, identifier)

    async def advance_layer1(self, conversation_id: str, *, expected: ContextAnchors, upto_msg_id: int) -> bool:
        identifier = _conversation_id(conversation_id)
        async with self.database.session() as session, session.begin():
            conversation = await self._conversation(session, identifier, lock=True)
            anchors = _anchors(conversation)
            if (anchors != expected or type(upto_msg_id) is not int
                    or upto_msg_id <= (anchors.layer1_from or 0)):
                return False
            if upto_msg_id not in _completed_boundaries(await self._rows(session, identifier)):
                return False
            conversation.layer1_from_msg_id = upto_msg_id
        return True

    async def _batch(self, session, conversation, conversation_id: str, target_upto: int) -> SummaryBatch | None:
        anchors = _anchors(conversation)
        if (type(target_upto) is not int or target_upto <= (anchors.summary_upto or 0)
                or target_upto > (anchors.layer1_from or 0)):
            return None
        rows = await self._rows(session, conversation.id)
        if target_upto not in _completed_boundaries(rows):
            return None
        source_rows = _frozen([row for row in rows if (anchors.summary_upto or 0) < row.id <= target_upto])
        segments = await self._segments(session, conversation.id)
        last = segments[-1] if segments else None
        if (last.upto_msg_id if last else None) != anchors.summary_upto:
            raise RuntimeError('context segment coverage does not match summary anchor')
        return SummaryBatch(conversation_id, anchors.summary_upto, last.seq if last else 0,
            int(source_rows[0].id), target_upto, source_rows, _source_hash(source_rows))

    async def load_batch(self, conversation_id: str, *, target_upto: int) -> SummaryBatch | None:
        identifier = _conversation_id(conversation_id)
        async with self.database.session() as session, session.begin():
            conversation = await self._conversation(session, identifier)
            return await self._batch(session, conversation, conversation_id, target_upto)

    async def append_segment(self, batch: SummaryBatch, content: str, *, summary_budget: int) -> SummarySegment | None:
        if not isinstance(content, str):
            raise ValueError('Summary content must be text.')
        if type(summary_budget) is not int or summary_budget < 0:
            raise ValueError('Summary projection budget must be a nonnegative integer.')
        identifier = _conversation_id(batch.conversation_id)
        try:
            async with self.database.session() as session, session.begin():
                conversation = await self._conversation(session, identifier, lock=True)
                anchors = _anchors(conversation)
                if anchors.summary_upto != batch.expected_summary_upto:
                    return None
                # 重新读所属范围/源哈希/seq；只允许S之后真实存在的第一行起步。
                actual = await self._batch(session, conversation, batch.conversation_id, batch.upto_msg_id)
                if actual is None or actual != batch:
                    return None
                row = ConversationSummary(conversation_id=identifier, seq=batch.expected_seq + 1,
                    from_msg_id=batch.from_msg_id, upto_msg_id=batch.upto_msg_id, content=content)
                session.add(row)
                await session.flush()
                # MySQL没有INSERT RETURNING；显式异步SELECT读取服务器时间，避免惰性IO。
                segments = await self._segments(session, identifier)
                segment = segments[-1]
                conversation.summary_upto_msg_id = batch.upto_msg_id
                conversation.summary = _projection(segments, summary_budget)
            return segment
        except IntegrityError as exc:
            # 上下文退出已回滚；仅重复唯一键按竞争处理，其他约束异常保留诊断。
            if getattr(exc.orig, 'args', ())[:1] == (1062,):
                return None
            raise
