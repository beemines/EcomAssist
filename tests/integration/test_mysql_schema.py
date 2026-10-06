import pytest


@pytest.mark.asyncio
async def test_mysql_schema_matches_supplied_ddl(mysql_database):
    from sqlalchemy import text

    async with mysql_database.session() as session:
        tables = (await session.execute(text("""
            SELECT TABLE_NAME, ENGINE, TABLE_COLLATION FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
        """))).all()
        assert {row.TABLE_NAME for row in tables} == {"conversations", "messages", "faq", "tickets"}
        assert all(row.ENGINE == "InnoDB" and row.TABLE_COLLATION.startswith("utf8mb4_") for row in tables)
        columns = (await session.execute(text("""
            SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, EXTRA, COLUMN_KEY
            FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE()
        """))).all()
        by_name = {(row.TABLE_NAME, row.COLUMN_NAME): row for row in columns}
        expected = {
            "conversations": {"id", "user_id", "status", "created_at", "updated_at"},
            "messages": {"id", "conversation_id", "role", "content", "tool_calls", "tool_call_id", "created_at"},
            "faq": {"id", "question", "answer", "category", "created_at", "updated_at"},
            "tickets": {"ticket_no", "conversation_id", "description", "ticket_type", "status", "created_at"},
        }
        for table, names in expected.items():
            assert {r.COLUMN_NAME for r in columns if r.TABLE_NAME == table} == names
        for table in ("conversations", "messages", "faq"):
            column = by_name[table, "id"]
            assert column.COLUMN_TYPE == "bigint unsigned"
            assert column.COLUMN_KEY == "PRI" and column.EXTRA == "auto_increment"
        assert by_name["tickets", "ticket_no"].COLUMN_TYPE == "varchar(32)"
        assert by_name["tickets", "ticket_no"].COLUMN_KEY == "PRI"
        assert by_name["messages", "tool_calls"].COLUMN_TYPE == "json"
        for name in ("content", "tool_calls", "tool_call_id"):
            assert by_name["messages", name].IS_NULLABLE == "YES"
        assert by_name["conversations", "status"].COLUMN_TYPE == "enum('进行中','已转人工','已结束')"
        assert by_name["conversations", "status"].COLUMN_DEFAULT == "进行中"
        assert by_name["messages", "role"].COLUMN_TYPE == "enum('user','assistant','tool')"
        assert by_name["tickets", "ticket_type"].COLUMN_TYPE == "enum('售后','投诉','咨询')"
        assert by_name["tickets", "status"].COLUMN_TYPE == "enum('待处理','已处理')"
        assert by_name["tickets", "status"].COLUMN_DEFAULT == "待处理"
        for table in expected:
            assert by_name[table, "created_at"].COLUMN_DEFAULT.upper() == "CURRENT_TIMESTAMP"
        for table in ("conversations", "faq"):
            column = by_name[table, "updated_at"]
            assert column.COLUMN_DEFAULT.upper() == "CURRENT_TIMESTAMP"
            assert "on update CURRENT_TIMESTAMP" in column.EXTRA
        foreign_keys = (await session.execute(text("""
            SELECT TABLE_NAME, CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = DATABASE() AND REFERENCED_TABLE_NAME IS NOT NULL
        """))).all()
        assert set(foreign_keys) == {
            ("messages", "fk_messages_conversation", "conversation_id", "conversations", "id"),
            ("tickets", "fk_tickets_conversation", "conversation_id", "conversations", "id"),
        }
        for table in ("messages", "tickets"):
            assert by_name[table, "conversation_id"].COLUMN_TYPE == "bigint unsigned"
        indexes = (await session.execute(text("""
            SELECT TABLE_NAME, INDEX_NAME, COLUMN_NAME FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
        """))).all()
        assert set(indexes) == {
            ("conversations", "PRIMARY", "id"), ("conversations", "idx_user_id", "user_id"),
            ("messages", "PRIMARY", "id"), ("messages", "idx_conversation_id", "conversation_id"),
            ("faq", "PRIMARY", "id"), ("faq", "idx_category", "category"),
            ("tickets", "PRIMARY", "ticket_no"), ("tickets", "idx_conversation_id", "conversation_id"),
        }


@pytest.mark.asyncio
async def test_seed_is_complete_and_postage_misses(mysql_database):
    from sqlalchemy import select
    from app.db.models import Conversation, FAQ, Message, Ticket

    async with mysql_database.session() as session:
        conversation = (await session.scalars(select(Conversation).where(Conversation.user_id == "seed-user"))).one()
        assert conversation.status == "已转人工"
        messages = (await session.scalars(select(Message).where(Message.conversation_id == conversation.id).order_by(Message.id))).all()
        assert [message.role for message in messages] == ["user", "assistant"]
        assert all(message.content for message in messages)
        ticket = (await session.scalars(select(Ticket).where(Ticket.conversation_id == conversation.id))).one()
        assert ticket.ticket_type == "售后" and ticket.description
        faqs = (await session.scalars(select(FAQ))).all()
        assert any("退货" in faq.question for faq in faqs)
        assert any("运费" in faq.question for faq in faqs)
        assert all("邮费" not in faq.question for faq in faqs)
        assert not (await session.scalars(select(FAQ).where(FAQ.question.contains("邮费", autoescape=True)))).all()
        assert not (await session.scalars(select(Conversation).where(Conversation.user_id == "demo-user"))).all()
