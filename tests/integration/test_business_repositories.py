import asyncio
from hashlib import sha256
from uuid import uuid4

import pytest
import pytest_asyncio
from langchain_core.messages import HumanMessage
from sqlalchemy import delete, func, select

from app.db.models import Conversation, FAQ, KnowledgeChunk, Message, Ticket
from app.knowledge.types import ChunkDraft, VectorHit
from app.knowledge.vectors import MilvusIndex
from app.repositories.knowledge import KnowledgeRepository
from app.repositories.conversations import ConversationRepository
from app.repositories.faq import FAQRepository
from app.repositories.tickets import TicketRepository
from app.tools.executor import ToolExecutor
from app.tools.registry import build_registry
from app.tools.types import ToolCall, ToolContext
from tests.ch03_fakes import RecordingEmbedder
from tests.fakes import FAQStub


# 记录本测试创建的会话和 FAQ 主键，并在结束后按依赖顺序清理这些行。
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


# 创建独立用户会话及首条用户消息，并登记会话以便后续清理。
async def new_turn(database, owned_rows, question="请求人工"):
    conversations = ConversationRepository(database)
    identifier = await conversations.create("test-task3-" + uuid4().hex)
    owned_rows[0].append(int(identifier))
    message_id = await conversations.append_message(identifier, HumanMessage(question))
    return identifier, message_id


# 验证 FAQ 保留原始查询与向量排序，仅返回 MySQL 已完成记录且不回退旧 LIKE 查询。
@pytest.mark.asyncio
async def test_faq_real_mysql_done_filter_raw_query_order_and_no_legacy_like(knowledge_rows, owned_rows):
    database, token = knowledge_rows.database, knowledge_rows.token
    knowledge = KnowledgeRepository(database)
    ids = await knowledge.add_chunks([
        ChunkDraft(token, '退货规则', '七天'), ChunkDraft(token, '运费规则', '八元'),
        ChunkDraft(token, '未审核正文', '不得返回'), ChunkDraft(token, '缺失正文', '不得返回'),
    ])
    await knowledge.mark_done(ids[:2])
    async with database.session() as session, session.begin():
        await session.execute(delete(KnowledgeChunk).where(KnowledgeChunk.id == ids[3]))
        old = FAQ(question=token + '邮费是多少', answer='旧 LIKE 正文不得返回', category='旧数据')
        session.add(old)
        await session.flush()
        owned_rows[1].append(old.id)

    class Index:
        hits = [VectorHit(ids[1], .9), VectorHit(ids[0], .8), VectorHit(ids[2], .7)]
        # 返回受数量上限约束的预设向量命中，供真实 SQL 过滤与排序断言使用。
        async def search(self, vector, limit=3):
            assert limit == 3
            return self.hits[:limit]

    embedder, index = RecordingEmbedder(), Index()
    repository = FAQRepository(database, embedder, index)
    raw = ' \t邮费是多少\n '
    assert await repository.search(raw, limit=10) == [
        {'id': ids[1], 'question': '运费规则', 'answer': '八元', 'category': token},
        {'id': ids[0], 'question': '退货规则', 'answer': '七天', 'category': token},
    ]
    assert embedder.texts == [raw]
    index.hits = [VectorHit(ids[3], .95), VectorHit(ids[0], .9)]
    assert [row['id'] for row in await repository.search('邮费是多少')] == [ids[0]]
    index.hits = []
    assert await repository.search(token + '邮费是多少') == []


# 验证真实 Milvus 命中只投影到 MySQL 中已完成且仍存在的知识原文。
async def test_faq_real_milvus_search_projects_only_real_mysql_done_rows(knowledge_rows, milvus_collection):
    database, token = knowledge_rows.database, knowledge_rows.token
    knowledge = KnowledgeRepository(database)
    ids = await knowledge.add_chunks([
        ChunkDraft(token, '退货规则', '七天'), ChunkDraft(token, '运费规则', '八元'),
        ChunkDraft(token, '待向量提交', '不得返回'), ChunkDraft(token, '已删除正文', '不得返回'),
    ])
    await knowledge.mark_done(ids[:2])
    service = milvus_collection
    index = MilvusIndex(service.uri, collection=service.name, client=service.client)
    await index.upsert([
        (ids[0], [.8, .6] + [0.0] * 1022), (ids[1], [1.0] + [0.0] * 1023),
        (ids[2], [.6, .8] + [0.0] * 1022),
    ])
    embedder = RecordingEmbedder()
    repository = FAQRepository(database, embedder, index)
    assert await repository.search('邮费是多少', limit=10) == [
        {'id': ids[1], 'question': '运费规则', 'answer': '八元', 'category': token},
        {'id': ids[0], 'question': '退货规则', 'answer': '七天', 'category': token},
    ]
    # A missing SQL row can still have a dense hit; never return vector text.
    async with database.session() as session, session.begin():
        await session.execute(delete(KnowledgeChunk).where(KnowledgeChunk.id == ids[3]))
    await index.upsert([(ids[3], [.99, .01] + [0.0] * 1022)])
    assert [row['id'] for row in await repository.search('邮费是多少')] == [ids[1], ids[0]]
    assert embedder.texts == ['邮费是多少', '邮费是多少']


# 验证同一轮工具调用重试复用工单，而新用户消息生成新工单且只转移所属会话状态。
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


# 验证各种纯空白工单描述被拒绝，既不写工单也不转人工。
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


# 验证有效描述的前后空白原样入库，且成功创建工单后会话转人工。
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


# 验证首次提交成功后响应超时触发重试，最终仍只存在一条工单。
@pytest.mark.asyncio
async def test_ticket_commit_then_timeout_keeps_one_row(mysql_database, owned_rows):
    identifier, message_id = await new_turn(mysql_database, owned_rows)
    real = TicketRepository(mysql_database)

    class CommitThenTimeout:
        # 初始化提交后超时替身的调用计数，以便仅让第一次请求失败。
        def __init__(self):
            self.calls = 0

        # 先真实提交工单再在首次调用抛超时，模拟客户端未收到成功响应的重试场景。
        async def create(self, **kwargs):
            result = await real.create(**kwargs)
            self.calls += 1
            if self.calls == 1:
                raise TimeoutError("已提交后响应超时")
            return result

    tickets = CommitThenTimeout()
    registry = build_registry(FAQStub(), tickets, ToolContext(identifier, message_id, "请求人工"))
    outcome = await ToolExecutor().execute(ToolCall("same-id", "create_ticket", {"description": "损坏", "ticket_type": "售后"}), registry)
    assert outcome.status == "success" and outcome.attempts == 2
    async with mysql_database.session() as session:
        ticket_count = await session.scalar(select(func.count()).select_from(Ticket).where(Ticket.conversation_id == int(identifier)))
        conversation = await session.get(Conversation, int(identifier))
        assert ticket_count == 1
        assert conversation.status == "已转人工"


# 验证同一幂等键的冲突描述或类型返回冲突错误，并保留原工单业务字段。
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


# 验证同一消息与工具调用并发创建时返回相同结果且只落库一行。
@pytest.mark.asyncio
async def test_ticket_concurrent_same_call_and_message_produce_one_row(mysql_database, owned_rows):
    identifier, message_id = await new_turn(mysql_database, owned_rows)
    repository = TicketRepository(mysql_database)
    args = {"conversation_id": identifier, "user_message_id": message_id, "tool_call_id": "same-id", "description": "并发请求", "ticket_type": "咨询"}
    first, second = await asyncio.gather(repository.create(**args), repository.create(**args))
    assert first == second
    async with mysql_database.session() as session:
        assert await session.scalar(select(func.count()).select_from(Ticket).where(Ticket.conversation_id == int(identifier))) == 1


# 验证不能借用其他会话的用户消息创建工单或改变会话状态。
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


# 验证首次读不到已有工单而插入冲突时重新读取，并核对幂等参数是否一致。
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

    # 仅隐藏第一次目标工单读取，迫使真实插入触发主键冲突以检验竞态恢复。
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


# 验证工单插入失败会同时回滚转人工状态，避免留下半完成业务操作。
@pytest.mark.asyncio
async def test_ticket_insert_failure_rolls_back_transfer(mysql_database, owned_rows, monkeypatch):
    from sqlalchemy.ext.asyncio import AsyncSession

    identifier, message_id = await new_turn(mysql_database, owned_rows)
    original_flush = AsyncSession.flush

    # 仅在待插入数据含工单时让刷新失败，模拟工单写入故障而保留其他数据库操作。
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


# 验证外键完整性错误即使已有同编号工单也不能被当作幂等成功。
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

    # 隐藏首次已有工单读取，使后续插入进入完整性错误处理分支。
    async def stale_read(session, entity, key, **kwargs):
        nonlocal suppressed
        if entity is Ticket and key == first["ticket_no"] and not suppressed:
            suppressed = True
            return None
        return await original_get(session, entity, key, **kwargs)

    # 为工单刷新注入 MySQL 外键错误，验证它与重复主键错误严格区分。
    async def foreign_key_failure(session, *args, **kwargs):
        if any(isinstance(row, Ticket) for row in session.new):
            raise IntegrityError("controlled statement", {}, MySQLIntegrityError(1452, "controlled FK failure"))
        return await original_flush(session, *args, **kwargs)

    monkeypatch.setattr(AsyncSession, "get", stale_read)
    monkeypatch.setattr(AsyncSession, "flush", foreign_key_failure)
    with pytest.raises(IntegrityError):
        await repository.create(**args)


# 验证工单提交后取消等待会传播取消且不重试，已提交的工单与转人工状态仍存在。
@pytest.mark.asyncio
async def test_ticket_cancel_after_commit_does_not_retry(mysql_database, owned_rows):
    identifier, message_id = await new_turn(mysql_database, owned_rows)
    real = TicketRepository(mysql_database)
    committed = asyncio.Event()
    calls = 0

    class CommitThenWait:
        # 真实提交后发出同步信号并永久等待，允许测试在提交边界精确取消请求。
        async def create(self, **kwargs):
            nonlocal calls
            calls += 1
            await real.create(**kwargs)
            committed.set()
            await asyncio.Event().wait()

    registry = build_registry(FAQStub(), CommitThenWait(), ToolContext(identifier, message_id, "人工"))
    task = asyncio.create_task(ToolExecutor().execute(ToolCall("same-id", "create_ticket", {"description": "人工", "ticket_type": "咨询"}), registry))
    await committed.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert calls == 1
    async with mysql_database.session() as session:
        assert (await session.get(Conversation, int(identifier))).status == "已转人工"
        assert await session.scalar(select(func.count()).select_from(Ticket).where(Ticket.conversation_id == int(identifier))) == 1
