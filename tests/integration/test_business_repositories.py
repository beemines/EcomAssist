import asyncio
from hashlib import sha256
from uuid import uuid4

import pytest
import pytest_asyncio
from langchain_core.messages import HumanMessage
from sqlalchemy import delete, func, select

from app.db.models import Conversation, FAQ, Message, Ticket
from app.repositories.conversations import ConversationRepository
from app.repositories.faq import FAQRepository
from app.repositories.tickets import TicketRepository
from app.tools.executor import ToolExecutor
from app.tools.registry import build_registry
from app.tools.types import ToolCall, ToolContext


@pytest_asyncio.fixture
async def owned_rows(mysql_database):
    conversations, faqs = [], []
    yield conversations, faqs
    # 仅清理本测试拥有的记录；不修改演示种子或其他测试数据。
    async with mysql_database.session() as session, session.begin():
        if conversations:
            await session.execute(delete(Ticket).where(Ticket.conversation_id.in_(conversations)))
            await session.execute(delete(Message).where(Message.conversation_id.in_(conversations)))
            await session.execute(delete(Conversation).where(Conversation.id.in_(conversations)))
        if faqs:
            await session.execute(delete(FAQ).where(FAQ.id.in_(faqs)))


async def new_turn(database, owned_rows, question="请求人工"):
    conversations = ConversationRepository(database)
    identifier = await conversations.create("test-task3-" + uuid4().hex)
    owned_rows[0].append(int(identifier))
    message_id = await conversations.append_message(identifier, HumanMessage(question))
    return identifier, message_id


@pytest.mark.asyncio
async def test_faq_actual_like_is_question_only_literal_and_limited(mysql_database, owned_rows):
    repository = FAQRepository(mysql_database)
    assert any("退货" in row["question"] for row in await repository.search("退货"))
    assert await repository.search("邮费") == []
    token = "task3-" + uuid4().hex
    async with mysql_database.session() as session, session.begin():
        rows = [FAQ(question=token + suffix, answer="answer-only-marker", category="测试") for suffix in ("%", "_", "plain", "a", "b")]
        session.add_all(rows)
        await session.flush()
        owned_rows[1].extend(row.id for row in rows)
    assert [r["question"] for r in await repository.search(token + "%")] == [token + "%"]
    assert [r["question"] for r in await repository.search(token + "_")] == [token + "_"]
    assert await repository.search("answer-only-marker") == []
    assert len(await repository.search(token, limit=10)) == 3


@pytest.mark.asyncio
async def test_ticket_retry_is_same_but_next_user_message_is_new(mysql_database, owned_rows):
    identifier, message_id = await new_turn(mysql_database, owned_rows)
    other, _ = await new_turn(mysql_database, owned_rows)
    repository = TicketRepository(mysql_database)
    args = {"conversation_id": identifier, "user_message_id": message_id, "tool_call_id": "same-id", "description": "损坏", "ticket_type": "售后"}
    first = await repository.create(**args)
    retry = await repository.create(**args)
    next_message_id = await ConversationRepository(mysql_database).append_message(identifier, HumanMessage("再次请求人工"))
    next_turn = await repository.create(**{**args, "user_message_id": next_message_id})
    assert first["ticket_no"] == retry["ticket_no"]
    assert next_turn["ticket_no"] != first["ticket_no"]
    assert first["ticket_no"] == "T" + sha256(f"{identifier}:{message_id}:same-id".encode()).hexdigest()[:31]
    assert first["status"] == "待处理"
    async with mysql_database.session() as session:
        assert await session.scalar(select(func.count()).select_from(Ticket).where(Ticket.conversation_id == int(identifier))) == 2
        assert await session.scalar(select(func.count()).select_from(Ticket).where(Ticket.conversation_id == int(other))) == 0
        assert (await session.get(Conversation, int(identifier))).status == "已转人工"
        assert (await session.get(Conversation, int(other))).status == "进行中"


@pytest.mark.asyncio
async def test_blank_ticket_descriptions_cannot_write_or_transfer(mysql_database, owned_rows):
    identifier, message_id = await new_turn(mysql_database, owned_rows)
    repository = TicketRepository(mysql_database)
    for description in ("   ", "\t", "\n", "\u3000\u00a0"):
        with pytest.raises(ValueError, match="Invalid ticket arguments"):
            await repository.create(
                conversation_id=identifier, user_message_id=message_id, tool_call_id="blank",
                description=description, ticket_type="咨询",
            )
    async with mysql_database.session() as session:
        assert await session.scalar(select(func.count()).select_from(Ticket).where(Ticket.conversation_id == int(identifier))) == 0
        assert (await session.get(Conversation, int(identifier))).status == "进行中"


@pytest.mark.asyncio
async def test_ticket_keeps_nonblank_description_whitespace_in_storage(mysql_database, owned_rows):
    identifier, message_id = await new_turn(mysql_database, owned_rows)
    result = await TicketRepository(mysql_database).create(
        conversation_id=identifier, user_message_id=message_id, tool_call_id="spaced",
        description="\u3000损坏\t\n ", ticket_type="售后",
    )
    async with mysql_database.session() as session:
        row = await session.get(Ticket, result["ticket_no"])
        assert row.description == "\u3000损坏\t\n " and row.ticket_type == "售后"
        assert (await session.get(Conversation, int(identifier))).status == "已转人工"


@pytest.mark.asyncio
async def test_ticket_commit_then_timeout_keeps_one_row(mysql_database, owned_rows):
    identifier, message_id = await new_turn(mysql_database, owned_rows)
    real = TicketRepository(mysql_database)

    class CommitThenTimeout:
        def __init__(self):
            self.calls = 0

        async def create(self, **kwargs):
            result = await real.create(**kwargs)
            self.calls += 1
            if self.calls == 1:
                raise TimeoutError("已提交后响应超时")
            return result

    tickets = CommitThenTimeout()
    registry = build_registry(FAQRepository(mysql_database), tickets, ToolContext(identifier, message_id, "请求人工"))
    outcome = await ToolExecutor().execute(ToolCall("same-id", "create_ticket", {"description": "损坏", "ticket_type": "售后"}), registry)
    assert outcome.status == "success" and outcome.attempts == 2
    async with mysql_database.session() as session:
        ticket_count = await session.scalar(select(func.count()).select_from(Ticket).where(Ticket.conversation_id == int(identifier)))
        conversation = await session.get(Conversation, int(identifier))
        assert ticket_count == 1
        assert conversation.status == "已转人工"


@pytest.mark.asyncio
async def test_ticket_conflicting_retry_cannot_overwrite_business_fields(mysql_database, owned_rows):
    from app.core.errors import ServiceError

    identifier, message_id = await new_turn(mysql_database, owned_rows)
    repository = TicketRepository(mysql_database)
    args = {"conversation_id": identifier, "user_message_id": message_id, "tool_call_id": "same-id", "description": "原描述", "ticket_type": "咨询"}
    first = await repository.create(**args)
    with pytest.raises(ServiceError) as error:
        await repository.create(**{**args, "description": "不能覆盖", "ticket_type": "投诉"})
    assert error.value.code == "ticket_conflict"
    async with mysql_database.session() as session:
        row = await session.get(Ticket, first["ticket_no"])
        assert row.description == "原描述" and row.ticket_type == "咨询"


@pytest.mark.asyncio
async def test_ticket_concurrent_same_call_and_message_produce_one_row(mysql_database, owned_rows):
    identifier, message_id = await new_turn(mysql_database, owned_rows)
    repository = TicketRepository(mysql_database)
    args = {"conversation_id": identifier, "user_message_id": message_id, "tool_call_id": "same-id", "description": "并发请求", "ticket_type": "咨询"}
    first, second = await asyncio.gather(repository.create(**args), repository.create(**args))
    assert first == second
    async with mysql_database.session() as session:
        assert await session.scalar(select(func.count()).select_from(Ticket).where(Ticket.conversation_id == int(identifier))) == 1


@pytest.mark.asyncio
async def test_ticket_rejects_foreign_user_message_without_writes(mysql_database, owned_rows):
    from app.core.errors import ServiceError

    identifier, _ = await new_turn(mysql_database, owned_rows)
    _, foreign_message = await new_turn(mysql_database, owned_rows)
    with pytest.raises(ServiceError) as error:
        await TicketRepository(mysql_database).create(conversation_id=identifier, user_message_id=foreign_message, tool_call_id="call", description="人工", ticket_type="咨询")
    assert error.value.code == "invalid_user_message"
    async with mysql_database.session() as session:
        assert (await session.get(Conversation, int(identifier))).status == "进行中"
        assert await session.scalar(select(func.count()).select_from(Ticket).where(Ticket.conversation_id == int(identifier))) == 0


@pytest.mark.asyncio
async def test_ticket_primary_key_conflict_reads_and_checks_existing_row(mysql_database, owned_rows, monkeypatch):
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.core.errors import ServiceError

    identifier, message_id = await new_turn(mysql_database, owned_rows)
    repository = TicketRepository(mysql_database)
    args = {"conversation_id": identifier, "user_message_id": message_id, "tool_call_id": "same-id", "description": "原描述", "ticket_type": "咨询"}
    first = await repository.create(**args)
    original_get = AsyncSession.get
    suppressed = False

    async def stale_read(session, entity, key, **kwargs):
        nonlocal suppressed
        # 仅模拟首次读取不可见，真实 INSERT 会触发 MySQL 主键冲突。
        if entity is Ticket and key == first["ticket_no"] and not suppressed:
            suppressed = True
            return None
        return await original_get(session, entity, key, **kwargs)

    monkeypatch.setattr(AsyncSession, "get", stale_read)
    assert await repository.create(**args) == first
    suppressed = False
    with pytest.raises(ServiceError) as error:
        await repository.create(**{**args, "description": "冲突描述"})
    assert error.value.code == "ticket_conflict"
    async with mysql_database.session() as session:
        assert (await session.get(Ticket, first["ticket_no"])).description == "原描述"
        assert await session.scalar(select(func.count()).select_from(Ticket).where(Ticket.conversation_id == int(identifier))) == 1


@pytest.mark.asyncio
async def test_ticket_insert_failure_rolls_back_transfer(mysql_database, owned_rows, monkeypatch):
    from sqlalchemy.ext.asyncio import AsyncSession

    identifier, message_id = await new_turn(mysql_database, owned_rows)
    original_flush = AsyncSession.flush

    async def failed_flush(session, *args, **kwargs):
        if any(isinstance(row, Ticket) for row in session.new):
            raise RuntimeError("controlled insert failure")
        return await original_flush(session, *args, **kwargs)

    monkeypatch.setattr(AsyncSession, "flush", failed_flush)
    with pytest.raises(RuntimeError):
        await TicketRepository(mysql_database).create(conversation_id=identifier, user_message_id=message_id, tool_call_id="call", description="人工", ticket_type="咨询")
    async with mysql_database.session() as session:
        assert (await session.get(Conversation, int(identifier))).status == "进行中"
        assert await session.scalar(select(func.count()).select_from(Ticket).where(Ticket.conversation_id == int(identifier))) == 0


@pytest.mark.asyncio
async def test_ticket_non_duplicate_integrity_failure_is_not_reported_as_success(mysql_database, owned_rows, monkeypatch):
    from pymysql.err import IntegrityError as MySQLIntegrityError
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.ext.asyncio import AsyncSession

    identifier, message_id = await new_turn(mysql_database, owned_rows)
    repository = TicketRepository(mysql_database)
    args = {"conversation_id": identifier, "user_message_id": message_id, "tool_call_id": "same-id", "description": "原描述", "ticket_type": "咨询"}
    first = await repository.create(**args)
    original_get, original_flush = AsyncSession.get, AsyncSession.flush
    suppressed = False

    async def stale_read(session, entity, key, **kwargs):
        nonlocal suppressed
        if entity is Ticket and key == first["ticket_no"] and not suppressed:
            suppressed = True
            return None
        return await original_get(session, entity, key, **kwargs)

    async def foreign_key_failure(session, *args, **kwargs):
        if any(isinstance(row, Ticket) for row in session.new):
            raise IntegrityError("controlled statement", {}, MySQLIntegrityError(1452, "controlled FK failure"))
        return await original_flush(session, *args, **kwargs)

    monkeypatch.setattr(AsyncSession, "get", stale_read)
    monkeypatch.setattr(AsyncSession, "flush", foreign_key_failure)
    with pytest.raises(IntegrityError):
        await repository.create(**args)


@pytest.mark.asyncio
async def test_ticket_cancel_after_commit_does_not_retry(mysql_database, owned_rows):
    identifier, message_id = await new_turn(mysql_database, owned_rows)
    real = TicketRepository(mysql_database)
    committed = asyncio.Event()
    calls = 0

    class CommitThenWait:
        async def create(self, **kwargs):
            nonlocal calls
            calls += 1
            await real.create(**kwargs)
            committed.set()
            await asyncio.Event().wait()

    registry = build_registry(FAQRepository(mysql_database), CommitThenWait(), ToolContext(identifier, message_id, "人工"))
    task = asyncio.create_task(ToolExecutor().execute(ToolCall("same-id", "create_ticket", {"description": "人工", "ticket_type": "咨询"}), registry))
    await committed.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert calls == 1
    async with mysql_database.session() as session:
        assert (await session.get(Conversation, int(identifier))).status == "已转人工"
        assert await session.scalar(select(func.count()).select_from(Ticket).where(Ticket.conversation_id == int(identifier))) == 1
