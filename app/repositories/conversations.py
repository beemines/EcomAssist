import re

from langchain_core.messages import BaseMessage
from sqlalchemy import select

from app.core.errors import ServiceError
from app.db.models import Conversation, Message
from app.db.session import Database
from app.repositories.records import MessageRecord, decode_tool_calls, record_from_message


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
