# 质量仓储使用独立短事务：最终拒答与入池原子提交，编造按题号原子累计。
from dataclasses import asdict

from langchain_core.messages import AIMessage
from sqlalchemy import func, select
from sqlalchemy.dialects.mysql import insert

from app.db.models import Conversation, FaithCase, LowConfidenceQuestion, Message
from app.db.session import Database
from app.quality.types import CASE_STATUSES, CaseStatus, FaithCaseInput, RefusalSource, require_text, resolution_value
from app.repositories.conversations import _conversation_id, _require_conversation
from app.repositories.records import record_from_message


class QualityRepository:
    """只负责质量持久化；调用方先完成检索及 useful 判定，再开启短事务。"""

    # 保存独立 Session 工厂，不在仓储实例之间共享事务。
    def __init__(self, database: Database):
        self.database = database

    # 锁定仍开放的会话，在同一事务里写入最终助手拒答与问题池，不自动重试。
    async def commit_refusal(self, conversation_id: str, answer: AIMessage, *, raw_question: str, source: RefusalSource, reason: str,
                             user_message_id: str | None = None, snapshot=None) -> int:
        identifier = _conversation_id(conversation_id)
        if not isinstance(answer, AIMessage):
            raise ValueError("refusal must be an assistant message")
        record = record_from_message(answer)
        if record.tool_calls is not None or not record.content or not record.content.strip():
            raise ValueError("refusal must be a nonempty final answer without tool calls")
        require_text("answer", record.content, 65535, utf8=True)
        require_text("raw_question", raw_question, 65535, utf8=True)
        require_text("reason", reason, 65535, utf8=True)
        if source not in ("retrieval_low_conf", "self_check"):
            raise ValueError("invalid refusal source")
        if (snapshot is None) != (user_message_id is None):
            raise ValueError('Turn-bound refusal needs both user identity and snapshot')
        async with self.database.session() as session, session.begin():
            _require_conversation(await session.get(Conversation, identifier, with_for_update=True))
            if snapshot is not None:
                from app.flywheel.types import database_id
                user = await session.get(Message, int(database_id(user_message_id)))
                if (user is None or user.conversation_id != identifier or user.role != 'user'
                        or user.content != raw_question):
                    raise ValueError('Refusal must refer to its trusted original SQL user message')
            message = Message(conversation_id=identifier, role=record.role, content=record.content, tool_calls=record.tool_calls, tool_call_id=record.tool_call_id)
            session.add(message)
            await session.flush()
            message_id = message.id
            if snapshot is None:
                session.add(LowConfidenceQuestion(conversation_id=identifier, raw_question=raw_question, source=source, reason=reason))
            else:
                from app.flywheel.repository import FlywheelRepository
                from app.flywheel.types import PoolInput
                await FlywheelRepository(self.database).enqueue_in_session(session, PoolInput(
                    conversation_id=conversation_id, user_message_id=user_message_id,
                    assistant_message_id=str(message_id), raw_question=raw_question,
                    source=source, reason=reason, snapshot=snapshot))
        return message_id

    # 按唯一题号原子 upsert，刷新完整快照并累加次数，复发保留最近处置时间。
    async def record_fabrication(self, case: FaithCaseInput) -> None:
        if not isinstance(case, FaithCaseInput):
            raise ValueError("case must be FaithCaseInput")
        statement = insert(FaithCase).values(**asdict(case))
        updates = [(name, statement.inserted[name]) for name in ("bucket", "query", "strategy", "answer", "reason", "citations", "judge_model")]
        updates.extend([("seen_count", FaithCase.seen_count + 1), ("last_seen_at", func.current_timestamp()), ("status", "未解决"), ("resolution", None)])
        async with self.database.session() as session, session.begin():
            await session.execute(statement.on_duplicate_key_update(updates))

    # 锁定题号后修改处置；有结论必须有说明，重开只清说明并保留处置时间。
    async def resolve_case(self, eval_id: str, status: CaseStatus, resolution: str | None) -> None:
        require_text("eval_id", eval_id, 16)
        explanation = resolution_value(status, resolution)
        async with self.database.session() as session, session.begin():
            row = (await session.scalars(select(FaithCase).where(FaithCase.eval_id == eval_id).with_for_update())).one_or_none()
            if row is None:
                raise ValueError("faith case does not exist")
            row.status = status
            row.resolution = explanation
            if status != "未解决":
                row.resolved_at = func.current_timestamp()

    # 按可选处置状态读取台账，返回脱离 Session 的字典及完整证据快照。
    async def list_cases(self, status: str | None = None) -> list[dict]:
        if status is not None and status not in CASE_STATUSES:
            raise ValueError("invalid case status")
        statement = select(FaithCase.__table__).order_by(FaithCase.last_seen_at.desc(), FaithCase.id.desc())
        if status is not None:
            statement = statement.where(FaithCase.status == status)
        async with self.database.session() as session:
            return [dict(row) for row in (await session.execute(statement)).mappings()]
