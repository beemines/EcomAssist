# 真实 MySQL 会话集成测试，验证消息回放、编号边界及工具申请与结果的关联。
from uuid import uuid4

import pytest
import pytest_asyncio
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from sqlalchemy import delete, select, update

from app.db.models import Conversation, Message


# 登记测试专属会话主键，并在结束后仅删除这些会话及其消息。
@pytest_asyncio.fixture
async def owned_conversations(mysql_database):
    # 只清理本用例创建的主键，不影响种子和其他测试数据。
    owned = []
    yield owned
    async with mysql_database.session() as session, session.begin():
        if owned:
            await session.execute(delete(Message).where(Message.conversation_id.in_(owned)))
            await session.execute(delete(Conversation).where(Conversation.id.in_(owned)))


# 验证重新创建仓储后可按顺序读回完整工具轮次，包含调用参数与结果关联。
@pytest.mark.asyncio
async def test_new_repository_reads_persisted_complete_tool_turn(mysql_database, owned_conversations):
    from app.core.tool_history import completed_turns
    from app.repositories.conversations import ConversationRepository

    repository = ConversationRepository(mysql_database)
    identifier = await repository.create("test-task2-" + uuid4().hex)
    assert isinstance(identifier, str) and identifier.isascii() and identifier.isdecimal()
    owned_conversations.append(int(identifier))
    await repository.require_open(identifier)
    user_id = await repository.append_message(identifier, HumanMessage("如何退货"))
    call_id = await repository.append_message(identifier, AIMessage("", tool_calls=[{"id": "call-1", "name": "search_faq", "args": {"keyword": "退货"}, "type": "tool_call"}]))
    result_id = await repository.append_message(identifier, ToolMessage("按规则退货", tool_call_id="call-1"))
    final_id = await repository.append_message(identifier, AIMessage("请按规则退货"))
    reopened = ConversationRepository(mysql_database)
    rows = await reopened.load_messages(identifier)
    assert [r.id for r in rows] == [user_id, call_id, result_id, final_id]
    assert rows[1].tool_calls == [{"id": "call-1", "type": "function", "function": {"name": "search_faq", "arguments": '{"keyword":"退货"}'}}]
    assert rows[1].content is None
    assert rows[2].tool_call_id == "call-1"
    turns = completed_turns(rows)
    assert len(turns) == 1
    assert [m.type for m in turns[0]] == ["human", "ai", "tool", "ai"]


# 验证超出 JavaScript 安全整数的主键无损往返，转人工可续聊而结束会话拒绝新消息。
@pytest.mark.asyncio
async def test_bigint_identifier_round_trip_and_status_checks(mysql_database, owned_conversations):
    from app.core.errors import ServiceError
    from app.repositories.conversations import ConversationRepository

    identifier = 9007199254740993
    async with mysql_database.session() as session, session.begin():
        assert await session.get(Conversation, identifier) is None
        session.add(Conversation(id=identifier, user_id="test-task2-" + uuid4().hex, status="已转人工"))
    owned_conversations.append(identifier)
    repository = ConversationRepository(mysql_database)
    async with mysql_database.session() as session:
        returned_id = str((await session.get(Conversation, identifier)).id)
    assert returned_id == '9007199254740993'
    # 大主键推进自增序列后，create 必须仍返回无精度损失的字符串。
    created_id = await repository.create("test-task2-" + uuid4().hex)
    owned_conversations.append(int(created_id))
    assert isinstance(created_id, str) and int(created_id) > identifier
    async with mysql_database.session() as session:
        assert str((await session.get(Conversation, int(created_id))).id) == created_id
    await repository.require_open(returned_id)
    assert await repository.append_message(returned_id, HumanMessage("转人工后继续")) > 0
    async with mysql_database.session() as session, session.begin():
        await session.execute(update(Conversation).where(Conversation.id == identifier).values(status="已结束"))
    with pytest.raises(ServiceError) as ended:
        await repository.require_open(returned_id)
    assert ended.value.code == "conversation_ended" and ended.value.status_code == 409
    with pytest.raises(ServiceError):
        await repository.append_message(returned_id, HumanMessage("拒绝新消息"))
    assert len(await repository.load_messages(returned_id)) == 1


# 验证不存在的会话在检查、读取和写入时均产生明确的服务错误。
@pytest.mark.asyncio
async def test_missing_conversation_has_explicit_error(mysql_database):
    from app.core.errors import ServiceError
    from app.repositories.conversations import ConversationRepository

    repository = ConversationRepository(mysql_database)
    for operation in (repository.require_open, repository.load_messages):
        with pytest.raises(ServiceError) as missing:
            await operation("18446744073709551615")
        assert missing.value.code == "conversation_not_found" and missing.value.status_code == 404
    with pytest.raises(ServiceError):
        await repository.append_message("18446744073709551615", HumanMessage("q"))


# 验证孤立、错配或重复工具结果被拒绝，仅匹配待处理调用的结果可以入库。
@pytest.mark.asyncio
async def test_tool_results_must_match_pending_call_and_not_duplicate(mysql_database, owned_conversations):
    from app.repositories.conversations import ConversationRepository

    repository = ConversationRepository(mysql_database)
    identifier = await repository.create("test-task2-" + uuid4().hex)
    owned_conversations.append(int(identifier))
    with pytest.raises(ValueError):
        await repository.append_message(identifier, ToolMessage("orphan", tool_call_id="call-1"))
    await repository.append_message(identifier, HumanMessage("q"))
    await repository.append_message(identifier, AIMessage("", tool_calls=[{"id": "call-1", "name": "search_faq", "args": {}, "type": "tool_call"}]))
    with pytest.raises(ValueError):
        await repository.append_message(identifier, ToolMessage("wrong", tool_call_id="wrong"))
    await repository.append_message(identifier, ToolMessage("result", tool_call_id="call-1"))
    with pytest.raises(ValueError):
        await repository.append_message(identifier, ToolMessage("duplicate", tool_call_id="call-1"))
    assert len(await repository.load_messages(identifier)) == 3
