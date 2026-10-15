"""只在3308随机自有schema验证退款迁移，永不迁移应用库。"""
from pathlib import Path
import re

import pytest
import pytest_asyncio
from sqlalchemy import text


@pytest_asyncio.fixture
async def refund_schema(migration_database):
    """随机自有库建立历史四表，保留本次测试之外的数据。"""
    ddl = re.sub(r'(?m)^\s*--.*$', '', Path('sql/schema.sql').read_text(encoding='utf-8'))
    async with migration_database.engine.begin() as connection:
        for statement in [s.strip() for s in ddl.split(';') if s.strip()]:
            await connection.exec_driver_sql(statement)
    return migration_database


async def test_verify_missing_never_creates_and_init_is_repeatable(refund_schema):
    """verify只读拒绝缺表，显式init才建表，重复init保留已有业务数据。"""
    from app.refunds.migration import migrate_refunds, verify_refunds
    with pytest.raises(RuntimeError, match='missing'):
        await verify_refunds(refund_schema)
    async with refund_schema.session() as session:
        assert await session.scalar(text("SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='refund_requests'")) == 0
    await migrate_refunds(refund_schema)
    await migrate_refunds(refund_schema)
    await verify_refunds(refund_schema)
    async with refund_schema.session() as session:
        fks = (await session.execute(text("SELECT COLUMN_NAME,REFERENCED_TABLE_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='refund_requests' AND REFERENCED_TABLE_NAME IS NOT NULL"))).all()
        assert set(fks) == {('conversation_id', 'conversations'), ('user_message_id', 'messages'), ('assistant_message_id', 'messages')}


@pytest.mark.parametrize('alter', [
    'ALTER TABLE refund_requests DROP INDEX uk_refund_request',
    'ALTER TABLE refund_requests DROP INDEX uk_refund_offer',
    'ALTER TABLE refund_requests DROP INDEX uk_refund_pending',
    'ALTER TABLE refund_requests DROP INDEX idx_refund_owner_order_status',
    'ALTER TABLE refund_requests MODIFY amount_cents DECIMAL(12,2) NOT NULL',
    "ALTER TABLE refund_requests MODIFY reason VARCHAR(32) NOT NULL",
    "ALTER TABLE refund_requests ALTER status DROP DEFAULT",
    'ALTER TABLE refund_requests DROP FOREIGN KEY fk_refund_assistant',
    'ALTER TABLE refund_requests ADD surprise INT NULL',
    "ALTER TABLE refund_requests COMMENT='drift'",
])
async def test_schema_drift_refused_without_repair(refund_schema, alter):
    """唯一键、复合索引、整数金额、默认状态和消息FK漂移必须显式处理。"""
    from app.refunds.migration import migrate_refunds, verify_refunds
    await migrate_refunds(refund_schema)
    async with refund_schema.engine.begin() as connection:
        await connection.exec_driver_sql(alter)
    for action in (verify_refunds, migrate_refunds):
        with pytest.raises(RuntimeError, match='schema'):
            await action(refund_schema)


async def test_mapping_matches_real_ddl(refund_schema):
    """ORM新表结构必须与独立DDL实际生成结果一致。"""
    from sqlalchemy.dialects.mysql import dialect
    from app.db.models import RefundRequest
    from app.refunds.migration import migrate_refunds
    await migrate_refunds(refund_schema)
    async with refund_schema.session() as session:
        rows = (await session.execute(text("SELECT COLUMN_NAME,COLUMN_TYPE,IS_NULLABLE,COLUMN_DEFAULT,COLUMN_COMMENT FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='refund_requests' ORDER BY ORDINAL_POSITION"))).all()
        assert [r.COLUMN_NAME for r in rows] == list(RefundRequest.__table__.c.keys())
        for row, col in zip(rows, RefundRequest.__table__.c):
            kind = col.type.compile(dialect=dialect())
            prefix, sep, suffix = kind.partition('(')
            assert row.COLUMN_TYPE == prefix.lower() + sep + suffix
            assert row.COLUMN_COMMENT == col.comment
            assert row.IS_NULLABLE == ('YES' if col.nullable else 'NO')
