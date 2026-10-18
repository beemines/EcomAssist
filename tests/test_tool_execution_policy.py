import asyncio
from dataclasses import replace
import pytest
from app.tools.catalog import ToolCatalog
from app.tools.executor import ToolExecutor
from app.tools.types import ToolCall, ToolContext, ExecutionContext, ConfirmationGrant
from app.tools.catalog_types import fingerprint
from tests.tool_system_fakes import make_registration, allow_policy


class AuditSink:
    def __init__(self):
        self.records = []
    async def write(self, record):
        self.records.append(record)


def bound(item):
    catalog = ToolCatalog()
    catalog.register(item)
    return catalog.snapshot(policy=allow_policy(item)).bind(ToolContext('1', 2, '建工单'))


def ctx(**kwargs):
    return ExecutionContext(conversation_id='1', user_message_id=2,
        intent='工单', raw_question='帮我建工单', **kwargs)


async def test_unconfirmed_write_is_denied_and_audited_without_handler():
    calls = []
    async def handler():
        calls.append(True)
        return {'ticket_no': 'T1'}
    catalog = bound(make_registration('create_ticket', operation='write', handler=handler))
    audit = AuditSink()
    result = await ToolExecutor(audit_sink=audit).execute(ToolCall('call', 'create_ticket', {}), catalog, context=ctx())
    assert result.content['error']['code'] == 'permission_denied'
    assert calls == [] and audit.records[0].status == 'permission_denied'
    assert audit.records[0].retry_count == 0


@pytest.mark.parametrize('changed', ['conversation', 'message', 'call', 'args', 'request'])
async def test_grant_cannot_be_reused_for_different_write(changed):
    catalog = bound(make_registration('create_ticket', operation='write'))
    grant = ConfirmationGrant('chat_preview', '1', 2, 'call', fingerprint({}))
    if changed == 'conversation': grant = replace(grant, conversation_id='9')
    if changed == 'message': grant = replace(grant, user_message_id=3)
    if changed == 'call': grant = replace(grant, tool_call_id='other')
    if changed == 'args': grant = replace(grant, arguments_fingerprint=fingerprint({'x': 1}))
    result = await ToolExecutor().execute(ToolCall('call', 'create_ticket', {}), catalog,
        context=ctx(grant=grant, ticket_requested=changed != 'request'))
    assert result.attempts == 0 and result.content['error']['code'] == 'permission_denied'


@pytest.mark.parametrize('operation,want_attempts,want_retries', [('read', 2, 1), ('write', 1, 0)])
async def test_timeout_physical_attempts_and_audit(operation, want_attempts, want_retries):
    attempts = []
    async def handler():
        attempts.append(True)
        await asyncio.Event().wait()
    name = 'slow_read' if operation == 'read' else 'create_ticket'
    catalog = bound(make_registration(name, operation=operation, handler=handler))
    audit = AuditSink()
    grant = ConfirmationGrant('chat_preview', '1', 2, 'call', fingerprint({}))
    result = await ToolExecutor(timeout_seconds=.01, audit_sink=audit).execute(
        ToolCall('call', name, {}), catalog, context=ctx(grant=grant, ticket_requested=True))
    assert len(attempts) == result.attempts == want_attempts
    assert audit.records[0].status == 'timeout' and audit.records[0].retry_count == want_retries
    assert audit.records[0].elapsed_ms >= 10


async def test_strict_json_schema_blocks_missing_types_ranges_and_hidden_fields():
    calls = []
    async def handler(**kwargs):
        calls.append(kwargs)
        return {'answer': 'ok'}
    item = make_registration('read', handler=handler)
    item = replace(item, definition=replace(item.definition, input_schema={
        'type': 'object', 'properties': {'n': {'type': 'integer', 'minimum': 1, 'maximum': 4}},
        'required': ['n'], 'additionalProperties': False}))
    # Factory schema follows the definition for real invocation.
    from langchain_core.tools import StructuredTool
    item = replace(item, factory=lambda context: StructuredTool.from_function(coroutine=handler,
        name='read', description='read', args_schema=item.definition.input_schema))
    audit = AuditSink()
    for args in [{}, {'n': '1'}, {'n': True}, {'n': 0}, {'n': 5}, {'n': 1, 'approved': True}]:
        outcome = await ToolExecutor(audit_sink=audit).execute(ToolCall('call', 'read', args), bound(item), context=ctx())
        assert outcome.content['error']['code'] == 'invalid_arguments' and outcome.attempts == 0
    assert calls == [] and all(r.status == 'validation_blocked' for r in audit.records)


async def test_revoked_and_unknown_calls_are_denied_and_audited():
    catalog = bound(make_registration('read'))
    audit = AuditSink()
    executor = ToolExecutor(audit_sink=audit)
    for name in ['read', 'unknown']:
        result = await executor.execute(ToolCall('call', name, {}), catalog,
            context=ctx(policy=allow_policy()))
        assert result.attempts == 0
    assert [r.status for r in audit.records] == ['permission_denied', 'permission_denied']


async def test_empty_business_result_is_not_retried_and_audit_outage_keeps_success():
    attempts = []
    async def handler():
        attempts.append(True)
        return {'found': False}
    class BrokenSink:
        async def write(self, record):
            raise ConnectionError('secret')
    outcome = await ToolExecutor(audit_sink=BrokenSink()).execute(
        ToolCall('call', 'read', {}), bound(make_registration('read', handler=handler)), context=ctx())
    assert outcome.attempts == 1 and len(attempts) == 1
    assert outcome.content['error']['code'] == 'not_found'
