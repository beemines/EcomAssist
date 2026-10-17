# 会话仓储：创建会话、校验身份和状态、保存并读取消息流水。
import re
from typing import TYPE_CHECKING

from langchain_core.messages import BaseMessage
from sqlalchemy import func, select

from app.core.errors import ServiceError
from app.db.models import Conversation, Message
from app.db.session import Database
from app.repositories.records import MessageRecord, decode_tool_calls, record_from_message

if TYPE_CHECKING:
    from app.schemas.conversation import ConversationPage, MessagePage


# 把规范的正十进制字符串转换为无符号 BIGINT 范围内的会话主键。
def _conversation_id(value: str) -> int:
    if not isinstance(value, str) or not re.fullmatch(r"[1-9][0-9]{0,19}", value) or int(value) > 18446744073709551615:
        raise ServiceError("invalid_conversation_id", "Conversation id must be a positive decimal string.", 422)
    return int(value)


# 确认会话存在，并按调用要求拒绝已结束的会话。
def _require_conversation(conversation: Conversation | None, *, open_only: bool = True) -> None:
    if conversation is None:
        raise ServiceError("conversation_not_found", "Conversation does not exist.", 404)
    if open_only and conversation.status == "已结束":
        raise ServiceError("conversation_ended", "Conversation has ended.", 409)


class ConversationRepository:
    """每次操作独立短事务，返回脱离 Session 的纯数据。"""

    # 保存创建独立短事务所需的数据库依赖。
    def __init__(self, database: Database):
        self.database = database

    async def list_for_user(self, user_id: str, *, before_id: str | None, limit: int) -> 'ConversationPage':
        """只读keyset分页，首问通过一条相关子查询取得，不逐会话读取。"""
        from app.schemas.conversation import ConversationItem, ConversationPage
        _read_limit(limit)
        before = _conversation_id(before_id) if before_id is not None else None
        first_question = (select(Message.content).where(Message.conversation_id == Conversation.id,
            Message.role == 'user').order_by(Message.id).limit(1).correlate(Conversation).scalar_subquery())
        query = select(Conversation, first_question.label('first_question')).where(Conversation.user_id == user_id)
        if before is not None:
            query = query.where(Conversation.id < before)
        async with self.database.session() as session:
            rows = (await session.execute(query.order_by(Conversation.id.desc()).limit(limit + 1))).all()
            items = [ConversationItem(id=str(row.id), status=row.status, created_at=row.created_at,
                updated_at=row.updated_at, first_question_preview=question[:80] if question is not None else '新对话',
                has_summary=row.summary_upto_msg_id is not None or row.summary is not None)
                for row, question in rows[:limit]]
            return ConversationPage(items=items, next_before_id=items[-1].id if len(rows) > limit else None)

    async def read_page(self, conversation_id: str, *, user_id: str, after_id: str | None,
                        upto_id: str | None, limit: int) -> 'MessagePage':
        """先核验SQL归属，再固定上界读取有限条原文；已结束会话也可读。"""
        from app.schemas.conversation import HistoryMessage, MessagePage
        identifier = _conversation_id(conversation_id)
        _read_limit(limit)
        after = _conversation_id(after_id) if after_id is not None else 0
        upto = _conversation_id(upto_id) if upto_id is not None else None
        if upto is not None and after > upto:
            raise ServiceError('invalid_history_cursor', '消息分页范围不合法。', 422)
        async with self.database.session() as session:
            owned = (await session.execute(select(Conversation.id).where(
                Conversation.id == identifier, Conversation.user_id == user_id))).scalar_one_or_none()
            if owned is None:
                raise ServiceError('conversation_not_found', 'Conversation does not exist.', 404)
            maximum = await session.scalar(select(func.max(Message.id)).where(Message.conversation_id == identifier))
            # 外部提供的上界不能预订尚未存在的消息；首次读取冻结实际最大ID。
            bound = min(upto, maximum) if upto is not None and maximum is not None else maximum
            query = select(Message).where(Message.conversation_id == identifier,
                Message.id > after, Message.id <= (bound or 0)).order_by(Message.id).limit(limit + 1)
            rows = (await session.scalars(query)).all()
            messages = [HistoryMessage(id=str(row.id), role=row.role, content=row.content,
                tool_calls=row.tool_calls, tool_call_id=row.tool_call_id, created_at=row.created_at) for row in rows[:limit]]
            return MessagePage(conversation_id=conversation_id, messages=messages,
                upto_id=str(bound) if bound is not None else None,
                next_after_id=messages[-1].id if len(rows) > limit else None)

    # 校验用户标识并在短事务中创建会话，返回字符串主键。
    async def create(self, user_id: str) -> str:
        if not isinstance(user_id, str) or not user_id.strip() or len(user_id) > 64:
            raise ValueError("User id must be nonempty and within 64 characters.")
        # 事务上下文正常退出时提交，异常退出时回滚；flush 仅获取主键。
        async with self.database.session() as session, session.begin():
            conversation = Conversation(user_id=user_id)
            session.add(conversation)
            await session.flush()
            identifier = str(conversation.id)
        return identifier

    # 校验会话身份并确认会话仍可继续处理。
    async def require_open(self, conversation_id: str) -> None:
        identifier = _conversation_id(conversation_id)
        async with self.database.session() as session, session.begin():
            _require_conversation(await session.get(Conversation, identifier))

    # 从 SQL 会话记录读取可信演示身份，不使用模型或浏览器携带的用户标识。
    async def get_user_id(self, conversation_id: str) -> str:
        identifier = _conversation_id(conversation_id)
        async with self.database.session() as session, session.begin():
            conversation = await session.get(Conversation, identifier)
            _require_conversation(conversation, open_only=False)
            return conversation.user_id

    # 校验消息及工具对应关系后入库，事务提交成功才返回消息主键。
    async def append_message(self, conversation_id: str, message: BaseMessage) -> int:
        identifier = _conversation_id(conversation_id)
        row = record_from_message(message)
        async with self.database.session() as session, session.begin():
            _require_conversation(await session.get(Conversation, identifier))
            # 工具结果必须紧接其助手申请且调用标识匹配，防止写入孤立结果。
            if row.role == "tool":
                previous = (await session.scalars(select(Message).where(Message.conversation_id == identifier).order_by(Message.id.desc()).limit(1))).first()
                if previous is None or previous.role != "assistant" or previous.tool_calls is None:
                    raise ValueError("Tool result has no pending request.")
                calls = decode_tool_calls(previous.tool_calls)
                if row.tool_call_id != calls[0]["id"]:
                    raise ValueError("Tool result does not match the pending request.")
            stored = Message(conversation_id=identifier, role=row.role, content=row.content, tool_calls=row.tool_calls, tool_call_id=row.tool_call_id)
            session.add(stored)
            await session.flush()
            message_id = stored.id
        return message_id

    # 按主键顺序读取消息，返回脱离 Session 的记录供历史回放。
    async def load_messages(self, conversation_id: str) -> list[MessageRecord]:
        identifier = _conversation_id(conversation_id)
        async with self.database.session() as session, session.begin():
            _require_conversation(await session.get(Conversation, identifier), open_only=False)
            rows = (await session.scalars(select(Message).where(Message.conversation_id == identifier).order_by(Message.id))).all()
            return [MessageRecord(row.id, row.role, row.content, row.tool_calls, row.tool_call_id) for row in rows]


def _read_limit(limit: int) -> None:
    """HTTP和仓储直接调用使用同一有限分页约束。"""
    if type(limit) is not int or not 1 <= limit <= 200:
        raise ServiceError('invalid_history_limit', '分页大小必须在1到200之间。', 422)
