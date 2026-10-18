import asyncio
from dataclasses import asdict
import json
from types import SimpleNamespace

import pytest
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects.mysql import dialect

from app.tool_audit.types import ToolAuditRecord
from app.tool_audit.repository import BestEffortAuditSink
from app.db.models import ToolAuditLog


def record(**kwargs):
    return ToolAuditRecord(conversation_id=None, tool_call_id='call', tool_name='查询',
        source='mcp:logistics', arguments={'order_id': '中文'}, result_summary='结果',
        status=kwargs.get('status', 'permission_denied'), retry_count=0, elapsed_ms=2)


@pytest.mark.parametrize('status', ['success', 'failed', 'timeout', 'validation_blocked', 'permission_denied'])
def test_audit_contract_accepts_statuses_without_conversation_fk(status):
    value = record(status=status)
    assert value.status == status
    assert json.loads(json.dumps(asdict(value), ensure_ascii=False))['arguments'] == {'order_id': '中文'}
    assert not ToolAuditLog.__table__.foreign_keys
    assert not any(index.unique for index in ToolAuditLog.__table__.indexes)
    ddl = str(CreateTable(ToolAuditLog.__table__).compile(dialect=dialect()))
    assert 'JSON' in ddl and 'permission_denied' in ddl


@pytest.mark.parametrize('failure', ['exception', 'timeout'])
async def test_audit_failure_does_not_escape_or_block_business(failure, caplog):
    class BrokenRepository:
        async def append(self, value):
            if failure == 'timeout':
                await asyncio.Event().wait()
            raise ConnectionError('secret connection string')
    await asyncio.wait_for(BestEffortAuditSink(BrokenRepository(), timeout_seconds=.01).write(record()), .2)
    assert 'tool_audit' in caplog.text
    assert 'secret' not in caplog.text
