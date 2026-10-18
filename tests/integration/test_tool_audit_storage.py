from dataclasses import replace
import pytest
from sqlalchemy import text

from app.tool_audit.migration import migrate_tool_audit, verify_tool_audit
from app.tool_audit.repository import ToolAuditRepository
from tests.test_tool_audit import record


async def test_audit_sql_identity_no_fk_and_independent_transactions(migration_database):
    db = migration_database
    assert db.engine.url.database.startswith('ch03_migration_')
    with pytest.raises(RuntimeError, match='missing'):
        await verify_tool_audit(db)
    await migrate_tool_audit(db)
    await migrate_tool_audit(db)
    await verify_tool_audit(db)
    repository = ToolAuditRepository(db)
    await repository.append(record())
    await repository.append(replace(record(), conversation_id=999999))
    async with db.session() as session:
        rows = (await session.execute(text('SELECT conversation_id,arguments,status FROM tool_audit_logs ORDER BY id'))).all()
        assert len(rows) == 2 and rows[0][0] is None and rows[1][0] == 999999
        assert await session.scalar(text("SELECT COUNT(*) FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='tool_audit_logs' AND REFERENCED_TABLE_NAME IS NOT NULL")) == 0
    async with db.engine.begin() as connection:
        await connection.exec_driver_sql('ALTER TABLE tool_audit_logs ADD unexpected INT NULL')
    with pytest.raises(RuntimeError, match='mismatch'):
        await verify_tool_audit(db)
