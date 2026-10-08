# 人工工单仓储：以调用上下文生成稳定编号，事务内创建工单并更新会话状态。
from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.errors import ServiceError
from app.db.models import Conversation, Message, Ticket
from app.db.session import Database
from app.repositories.conversations import _conversation_id, _require_conversation


# 核对已存工单的业务字段，返回编号和状态或抛出身份冲突错误。
def _result(ticket: Ticket, identifier: int, description: str, ticket_type: str) -> dict:
    if (ticket.conversation_id, ticket.description, ticket.ticket_type) != (identifier, description, ticket_type):
        raise ServiceError("ticket_conflict", "Ticket identity conflicts with existing business fields.", 409)
    return {"ticket_no": ticket.ticket_no, "status": ticket.status}


class TicketRepository:
    """稳定编号保证重试复用，工单与转人工状态在同一短事务提交。"""

    # 保存创建工单与更新会话状态所需的数据库依赖。
    def __init__(self, database: Database):
        self.database = database

    # 以会话、用户消息和调用标识生成稳定工单编号，原子地创建工单并转人工。
    async def create(self, *, conversation_id: str, user_message_id: int, tool_call_id: str, description: str, ticket_type: str) -> dict:
        identifier = _conversation_id(conversation_id)
        if type(user_message_id) is not int or not 1 <= user_message_id <= 18446744073709551615:
            raise ServiceError("invalid_user_message", "Invalid user message identity.", 422)
        if not isinstance(tool_call_id, str) or not 1 <= len(tool_call_id) <= 64:
            raise ValueError("Invalid tool call identity.")
        if not isinstance(description, str) or not 1 <= len(description) <= 2000 or not description.strip() or ticket_type not in ("售后", "投诉", "咨询"):
            raise ValueError("Invalid ticket arguments.")
        # 重试复用同一逻辑调用编号，避免超时后的重复提交产生第二张工单。
        ticket_no = "T" + sha256(f"{conversation_id}:{user_message_id}:{tool_call_id}".encode()).hexdigest()[:31]
        try:
            async with self.database.session() as session, session.begin():
                # 同会话并发也串行核对；不同消息仍生成独立编号。
                conversation = await session.scalar(select(Conversation).where(Conversation.id == identifier).with_for_update())
                _require_conversation(conversation, open_only=False)
                message = await session.get(Message, user_message_id)
                if message is None or message.conversation_id != identifier or message.role != "user":
                    raise ServiceError("invalid_user_message", "User message does not belong to this conversation.", 422)
                existing = await session.get(Ticket, ticket_no)
                if existing is not None:
                    return _result(existing, identifier, description, ticket_type)
                _require_conversation(conversation)
                ticket = Ticket(ticket_no=ticket_no, conversation_id=identifier, description=description, ticket_type=ticket_type)
                session.add(ticket)
                # 工单和会话转人工状态共用事务，异常时一并回滚。
                conversation.status = "已转人工"
                await session.flush()
                # MySQL 不支持 INSERT RETURNING，显式加载服务端默认状态。
                await session.refresh(ticket, attribute_names=["status"])
                result = _result(ticket, identifier, description, ticket_type)
            return result
        except IntegrityError as exc:
            if not exc.orig.args or exc.orig.args[0] != 1062:
                raise
            # 冲突事务已退出并回滚；新 Session 读取已提交行，绝不覆盖。
            async with self.database.session() as session, session.begin():
                existing = await session.get(Ticket, ticket_no)
                if existing is None:
                    raise
                return _result(existing, identifier, description, ticket_type)
