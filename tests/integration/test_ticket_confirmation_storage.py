"""Actual MySQL + official SQLite + execution engine, scripted model only."""
import json
from pathlib import Path
from uuid import uuid4
import pytest
from langchain_core.messages import AIMessage
from sqlalchemy import text

from app.context.migration import migrate_context
from app.quality.migration import _statements
from app.tool_audit.migration import migrate_tool_audit
from app.tool_audit.repository import ToolAuditRepository, BestEffortAuditSink
from app.repositories.conversations import ConversationRepository
from app.repositories.tickets import TicketRepository
from app.tools.registry import build_catalog
from app.tools.policies import PolicyStore
from app.tools.mcp_client import ToolCatalogProvider, DiscoveryResult
from app.tools.executor import ToolExecutor
from app.core.conversation_locks import ConversationLocks
from app.workflow.persistence import open_checkpointer
from app.workflow.agent import build_agent_graph
from app.workflow.graph import build_workflow_graph
from app.workflow.service import WorkflowChatService
from app.workflow.ticket_actions import TicketConfirmationService
from app.schemas.ticket_confirmation import TicketConfirmationRequest
from tests.workflow_fakes import ScriptedWorkflowModel, workflow_call
from tests.test_workflow_api import intent
from tests.fakes import fake_settings, FAQStub


@pytest.mark.parametrize('choice,expected_count,status,audit_failure', [('confirm', 1, 'success', False), ('cancel', 0, 'permission_denied', False), ('confirm', 1, 'success', True)])
async def test_real_confirmation_ticket_delta_and_audit(migration_database, tmp_path, choice, expected_count, status, audit_failure, caplog):
    db = migration_database
    assert db.engine.url.database.startswith('ch03_migration_') and db.engine.url.port == 3308
    async with db.engine.begin() as connection:
        for statement in _statements(Path('sql/schema.sql').read_text(encoding='utf-8')):
            if statement.startswith(('CREATE TABLE conversations ', 'CREATE TABLE messages ', 'CREATE TABLE tickets ')):
                await connection.exec_driver_sql(statement)
    await migrate_context(db)
    await migrate_tool_audit(db)
    repository = ConversationRepository(db)
    conversation_id = await repository.create('ch08-' + uuid4().hex)
    question = '饮水机漏水，请帮我建工单'
    model = ScriptedWorkflowModel([workflow_call('create_ticket', {'description': '饮水机漏水', 'ticket_type': '售后'})],
        intent_replies=[AIMessage(json.dumps({'query': question}, ensure_ascii=False), response_metadata={'finish_reason': 'stop'}), intent('工单')])
    catalog = build_catalog(FAQStub(), TicketRepository(db))
    path = tmp_path / 'policy.json'
    path.write_text('{"tools":[{"source":"builtin","name":"create_ticket","operation":"write"}]}')
    policies = PolicyStore(path)
    class Discovery:
        async def discover(self, policy):
            return DiscoveryResult((), {})
    provider = ToolCatalogProvider(catalog, policies, Discovery())
    settings = fake_settings()
    async with open_checkpointer(tmp_path / 'tickets.sqlite') as saver:
        service = WorkflowChatService(model, repository, lambda context: catalog.snapshot(policy=policies.load()).bind(context),
            ConversationLocks(), settings, graph=build_workflow_graph(build_agent_graph(), checkpointer=saver),
            checkpointer=saver, faq_repository=FAQStub(), sufficiency_service=None, quality_repository=None,
            executor=ToolExecutor(audit_sink=BestEffortAuditSink(ToolAuditRepository(db))), catalog_provider=provider)
        async def consume(prepared):
            try:
                return [event async for event in service.stream(prepared)]
            finally:
                service.release(prepared)
        try:
            first = await consume(await service.prepare(conversation_id, question))
            assert first[-1].event == 'paused', first
            preview = next(event.data for event in first if event.event == 'ticket_confirmation')
            payload = TicketConfirmationRequest(**{key: preview[key] for key in ('turn_id', 'confirmation_id', 'checkpoint_id')}, decision=choice)
            if audit_failure:
                async with db.engine.begin() as connection:
                    await connection.exec_driver_sql('DROP TABLE tool_audit_logs')
            actions = TicketConfirmationService(service)
            for _ in range(2):
                result = await consume(await actions.confirm(conversation_id, payload))
                assert result[-1].event == 'done', result
            async with db.session() as session:
                tickets = (await session.execute(text('SELECT ticket_no,description FROM tickets'))).all()
                assert len(tickets) == expected_count
                if not audit_failure:
                    audit = (await session.execute(text('SELECT tool_name,status,retry_count FROM tool_audit_logs'))).all()
                    assert [tuple(row) for row in audit] == [('create_ticket', status, 0)]
                else:
                    assert 'stage=tool_audit status=unavailable' in caplog.text
                if tickets:
                    assert tickets[0].description == '饮水机漏水'
                    assert tickets[0].ticket_no in ''.join(event.data['delta'] for event in result if event.event == 'delta')
        finally:
            await service.shutdown()
