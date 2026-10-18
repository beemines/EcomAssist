"""Explicit migration; online verification never changes the target."""
from pathlib import Path
from sqlalchemy import text
from app.quality.migration import _statements, _verify

_COLUMNS = [
    ('id', 'bigint unsigned', False), ('conversation_id', 'bigint unsigned', True),
    ('tool_call_id', 'varchar(64)', False), ('tool_name', 'varchar(64)', False),
    ('source', 'varchar(128)', False), ('arguments', 'json', False),
    ('result_summary', 'text', False),
    ('status', "enum('success','failed','timeout','validation_blocked','permission_denied')", False),
    ('error_code', 'varchar(64)', True), ('error_message', 'varchar(512)', True),
    ('retry_count', 'int unsigned', False), ('elapsed_ms', 'bigint unsigned', False),
    ('created_at', 'datetime', False),
]


def contract():
    return {'comment': '工具调用审计，无外键', 'foreign_keys': set(),
        'columns': [(name, kind, 'YES' if nullable else 'NO',
            'current_timestamp' if name == 'created_at' else None,
            'auto_increment' if name == 'id' else '', '',
            'utf8mb4' if kind.startswith(('varchar', 'enum', 'text')) else None)
            for name, kind, nullable in _COLUMNS],
        'indexes': {('PRIMARY', 'id', 1, 0, None, 'BTREE'),
            ('idx_tool_audit_conversation_time', 'conversation_id', 1, 1, None, 'BTREE'),
            ('idx_tool_audit_conversation_time', 'created_at', 2, 1, None, 'BTREE'),
            ('idx_tool_audit_call', 'tool_call_id', 1, 1, None, 'BTREE')}}


async def _check(database, *, initialize):
    async with database.engine.begin() as connection:
        target = await connection.scalar(text('SELECT DATABASE()'))
        if not target or target != database.engine.url.database:
            raise RuntimeError('tool audit target database mismatch')
        exists = await connection.scalar(text("SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='tool_audit_logs'"))
        if not exists:
            if not initialize:
                raise RuntimeError('tool audit schema missing; explicit init required')
            ddl = Path(__file__).resolve().parents[2] / 'sql/ch08-tool-audit.sql'
            for statement in _statements(ddl.read_text(encoding='utf-8')):
                await connection.exec_driver_sql(statement)
        await _verify(connection, 'tool_audit_logs', contract(), target)


async def migrate_tool_audit(database) -> None:
    await _check(database, initialize=True)


async def verify_tool_audit(database) -> None:
    await _check(database, initialize=False)
