import pytest


def mappings():
    try:
        from app.db.models import Conversation, FAQ, Message, Ticket
    except ImportError:
        pytest.fail("四表 ORM 映射尚未实现")
    return Conversation, FAQ, Message, Ticket


def test_mapping_matches_all_supplied_columns_and_constraints():
    Conversation, FAQ, Message, Ticket = mappings()
    expected = {
        Conversation: ["id", "user_id", "status", "created_at", "updated_at"],
        Message: ["id", "conversation_id", "role", "content", "tool_calls", "tool_call_id", "created_at"],
        FAQ: ["id", "question", "answer", "category", "created_at", "updated_at"],
        Ticket: ["ticket_no", "conversation_id", "description", "ticket_type", "status", "created_at"],
    }
    assert set(Conversation.metadata.tables) == {"conversations", "messages", "faq", "tickets"}
    for model, columns in expected.items():
        table = model.__table__
        assert list(table.columns.keys()) == columns
        assert table.dialect_options["mysql"]["engine"] == "InnoDB"
        assert table.dialect_options["mysql"]["charset"] == "utf8mb4"
    for model in (Conversation, FAQ, Message):
        assert model.__table__.c.id.type.unsigned
        assert model.__table__.c.id.primary_key
        assert model.__table__.c.id.autoincrement is True
    assert Ticket.__table__.c.ticket_no.primary_key
    assert Ticket.__table__.c.ticket_no.type.length == 32
    for model in (Message, Ticket):
        column = model.__table__.c.conversation_id
        assert column.type.unsigned
        assert {fk.target_fullname for fk in column.foreign_keys} == {"conversations.id"}
    assert Message.__table__.c.content.nullable
    assert Message.__table__.c.tool_calls.nullable
    assert Message.__table__.c.tool_calls.type.__class__.__name__ == "JSON"
    assert Message.__table__.c.tool_calls.type.none_as_null
    assert Message.__table__.c.tool_call_id.type.length == 64
    assert FAQ.__table__.c.question.type.length == 512
    assert {idx.name for idx in Conversation.__table__.indexes} == {"idx_user_id"}
    assert {idx.name for idx in FAQ.__table__.indexes} == {"idx_category"}
    for model in (Message, Ticket):
        assert {idx.name for idx in model.__table__.indexes} == {"idx_conversation_id"}


def test_mapping_persists_chinese_enums_and_server_timestamps():
    Conversation, FAQ, Message, Ticket = mappings()
    assert Conversation.__table__.c.status.type.enums == ["进行中", "已转人工", "已结束"]
    assert Message.__table__.c.role.type.enums == ["user", "assistant", "tool"]
    assert Ticket.__table__.c.ticket_type.type.enums == ["售后", "投诉", "咨询"]
    assert Ticket.__table__.c.status.type.enums == ["待处理", "已处理"]
    for model in (Conversation, FAQ, Message, Ticket):
        assert str(model.__table__.c.created_at.server_default.arg) == "CURRENT_TIMESTAMP"
    for model in (Conversation, FAQ):
        assert str(model.__table__.c.updated_at.server_default.arg) == "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        assert model.__table__.c.updated_at.server_onupdate is not None


@pytest.mark.asyncio
async def test_database_provides_distinct_short_lived_sessions():
    try:
        from app.db.session import Database
        from sqlalchemy.engine import URL
        from sqlalchemy.ext.asyncio import AsyncSession
    except ImportError:
        pytest.fail("异步数据库运行时尚未实现")
    database = Database(URL.create("mysql+aiomysql", username="test", password="test", host="127.0.0.1", database="test"))
    try:
        async with database.session() as first, database.session() as second:
            assert isinstance(first, AsyncSession)
            assert first is not second
            assert not first.in_transaction()
            assert not second.in_transaction()
    finally:
        await database.dispose()
