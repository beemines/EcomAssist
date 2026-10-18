from contextlib import asynccontextmanager
from types import SimpleNamespace
from pathlib import Path
import json
import httpx
import pytest
from langchain_core.messages import AIMessageChunk

from app.tools.registry import build_catalog
from app.tools.mcp_client import ToolCatalogProvider, DiscoveryResult
from app.tools.policies import PolicyStore
from app.tools.executor import ToolExecutor
from tests.test_workflow_api import workflow_app, intent
from tests.workflow_fakes import ScriptedWorkflowModel, workflow_call
from tests.test_workflow_agent import control
from tests.test_tool_execution_policy import AuditSink
from tests.fakes import decode_sse


class Tickets:
    def __init__(self):
        self.rows = {}
        self.calls = 0
    async def create(self, **kwargs):
        self.calls += 1
        key = kwargs['conversation_id'], kwargs['user_message_id'], kwargs['tool_call_id']
        return self.rows.setdefault(key, {'ticket_no': 'Tconfirmed001', 'status': '待处理'})


@asynccontextmanager
async def ticket_app(tmp_path, *, model=None, store=None, tickets=None):
    tickets = tickets or Tickets()
    model = model or ScriptedWorkflowModel([workflow_call('create_ticket', {'ticket_type': '售后', 'description': '饮水机漏水'})], intent_replies=[intent('工单')])
    async with workflow_app(tmp_path, model=model, store=store) as app:
        service = app.state.chat_service
        catalog = build_catalog(service.faq_repository, tickets)
        policy_path = tmp_path / 'tool-policy.json'
        policy_path.write_text(json.dumps({'tools': [
            {'source': 'builtin', 'name': 'create_ticket', 'operation': 'write'},
            {'source': 'builtin', 'name': 'query_order', 'operation': 'read'}]}))
        class Discovery:
            async def discover(self, policy):
                return DiscoveryResult((), {})
        service.catalog_provider = ToolCatalogProvider(catalog, PolicyStore(policy_path), Discovery())
        service.registry_factory = lambda context: catalog.snapshot(policy=service.catalog_provider.policies.load()).bind(context)
        service.executor = ToolExecutor(audit_sink=AuditSink())
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://127.0.0.1:8005') as client:
            yield app, client, tickets


async def proposal(client, question='饮水机漏水，请帮我建工单'):
    response = await client.post('/api/chat', json={'conversation_id': '1', 'message': question})
    frames = decode_sse(response.text)
    assert not any(name == 'error' for name, _ in frames), frames
    return next(data for name, data in frames if name == 'ticket_confirmation'), frames


def decision(preview, value='confirm'):
    return {key: preview[key] for key in ('turn_id', 'confirmation_id', 'checkpoint_id')} | {'decision': value}


@pytest.mark.parametrize('value,expected', [('confirm', '工单已提交'), ('cancel', '已取消')])
async def test_confirm_cancel_and_duplicate_receipt_are_durable(tmp_path, value, expected):
    async with ticket_app(tmp_path) as (app, client, tickets):
        preview, frames = await proposal(client)
        assert frames[-1][0] == 'paused' and tickets.calls == 0
        assert (await client.get('/api/conversations/1/pending-ticket')).json()['pending'] == preview
        for _ in range(2):
            response = await client.post('/api/conversations/1/actions/confirm-ticket', json=decision(preview, value))
            actual = decode_sse(response.text)
            assert actual[-1][0] == 'done', actual
            assert expected in ''.join(data['delta'] for name, data in actual if name == 'delta')
        assert tickets.calls == (1 if value == 'confirm' else 0)
        assert len(tickets.rows) == (1 if value == 'confirm' else 0)
        assert (await client.get('/api/conversations/1/pending-ticket')).json() == {'pending': None}
        audit = app.state.chat_service.executor.audit_sink.records
        assert len(audit) == 1 and audit[0].retry_count == 0
        assert audit[0].status == ('success' if value == 'confirm' else 'permission_denied')


async def test_missing_description_clarifies_then_uses_verified_user_supplement(tmp_path):
    model = ScriptedWorkflowModel([control('clarification'), workflow_call('create_ticket', {'ticket_type': '售后', 'description': '饮水机漏水'})],
        intent_replies=[intent('工单'), intent('工单')], final_chunks=[AIMessageChunk('请描述具体问题。'), AIMessageChunk('', response_metadata={'finish_reason': 'stop'})])
    async with ticket_app(tmp_path, model=model) as (_, client, tickets):
        first = decode_sse((await client.post('/api/chat', json={'conversation_id': '1', 'message': '帮我建个工单'})).text)
        assert first[-1][0] == 'done' and not any(name == 'ticket_confirmation' for name, _ in first), first
        preview, _ = await proposal(client, '饮水机漏水')
        assert preview['description'] == '饮水机漏水' and tickets.calls == 0


async def test_stale_tampered_cross_origin_and_revoked_confirmation_do_not_write(tmp_path):
    async with ticket_app(tmp_path) as (app, client, tickets):
        preview, _ = await proposal(client)
        response = await client.post('/api/conversations/1/actions/confirm-ticket', json=decision(preview) | {'description': '篡改'})
        assert response.status_code == 422
        response = await client.post('/api/conversations/1/actions/confirm-ticket', json=decision(preview), headers={'Origin': 'http://evil.invalid'})
        assert response.status_code == 403
        response = await client.post('/api/conversations/1/actions/confirm-ticket', json=decision(preview) | {'turn_id': '99'})
        assert response.status_code == 409
        app.state.chat_service.catalog_provider.policies.path.write_text('{"tools": []}')
        response = await client.post('/api/conversations/1/actions/confirm-ticket', json=decision(preview))
        assert response.status_code == 409
        assert tickets.calls == 0


async def test_restart_pending_keeps_request_and_usage_without_model_replay(tmp_path):
    from tests.test_workflow_api import Store
    from app.workflow.persistence import checkpoint_config
    store, tickets = Store(), Tickets()
    async with ticket_app(tmp_path, store=store, tickets=tickets) as (app, client, _):
        preview, _ = await proposal(client)
        before = (await app.state.chat_service.graph.aget_state(checkpoint_config('1'))).values
    async with ticket_app(tmp_path, store=store, tickets=tickets) as (app, client, _):
        assert (await client.get('/api/conversations/1/pending-ticket')).json()['pending'] == preview
        result = decode_sse((await client.post('/api/conversations/1/actions/confirm-ticket', json=decision(preview))).text)
        assert result[-1][0] == 'done', result
        after = (await app.state.chat_service.graph.aget_state(checkpoint_config('1'))).values
        assert after['usage'] == before['usage'] and after['decision_count'] == before['decision_count']
        assert app.state.chat_service.model.decisions == app.state.chat_service.model.intents == 0
        assert tickets.calls == 1


@pytest.mark.parametrize('change', ['unrelated_revocation', 'server_outage'])
@pytest.mark.parametrize('value', ['confirm', 'cancel'])
async def test_unrelated_catalog_changes_do_not_block_deterministic_ticket_resume(tmp_path, change, value):
    async with ticket_app(tmp_path) as (app, client, tickets):
        service = app.state.chat_service
        if change == 'server_outage':
            from tests.tool_system_fakes import make_registration
            item = make_registration('remote_status', source='mcp:logistics')
            class ChangingDiscovery:
                available = True
                calls = 0
                async def discover(self, policy):
                    self.calls += 1
                    return DiscoveryResult((item,) if self.available else (), {} if self.available else {'logistics': 'offline'})
            service.catalog_provider.discovery = ChangingDiscovery()
            policy = json.loads(service.catalog_provider.policies.path.read_text())
            policy['tools'].append({'source': 'mcp:logistics', 'name': 'remote_status', 'operation': 'read'})
            service.catalog_provider.policies.path.write_text(json.dumps(policy))
        preview, _ = await proposal(client)
        discoveries = service.catalog_provider.discovery.calls if change == 'server_outage' else None
        if change == 'server_outage':
            service.catalog_provider.discovery.available = False
        else:
            policy = json.loads(service.catalog_provider.policies.path.read_text())
            policy['tools'] = [rule for rule in policy['tools'] if rule['name'] != 'query_order']
            service.catalog_provider.policies.path.write_text(json.dumps(policy))
        response = await client.post('/api/conversations/1/actions/confirm-ticket', json=decision(preview, value))
        assert response.status_code == 200, response.text
        frames = decode_sse(response.text)
        assert frames[-1][0] == 'done', frames
        assert tickets.calls == (1 if value == 'confirm' else 0)
        if change == 'server_outage':
            assert service.catalog_provider.discovery.calls == discoveries


async def test_new_user_message_expires_old_preview_and_pairs_denial(tmp_path):
    async with ticket_app(tmp_path) as (app, client, tickets):
        preview, _ = await proposal(client)
        next_turn = decode_sse((await client.post('/api/chat', json={'conversation_id': '1', 'message': '你好'})).text)
        assert next_turn[-1][0] == 'done', next_turn
        response = await client.post('/api/conversations/1/actions/confirm-ticket', json=decision(preview))
        assert response.status_code == 409 and tickets.calls == 0
        audit = app.state.chat_service.executor.audit_sink.records
        assert audit[0].status == 'permission_denied'
        assert (await client.get('/api/conversations/1/pending-ticket')).json() == {'pending': None}


async def test_resume_revalidates_user_issue_source_against_sql(tmp_path):
    from copy import deepcopy
    from app.core.errors import ServiceError
    from app.workflow.persistence import checkpoint_config
    from app.workflow.ticket_actions import verify_ticket_sql
    async with ticket_app(tmp_path) as (app, client, _):
        await proposal(client)
        service = app.state.chat_service
        state = deepcopy((await service.graph.aget_state(checkpoint_config('1'))).values)
        state['ticket_request']['source_texts'] = ['用户从未说过的内容']
        with pytest.raises(ServiceError):
            await verify_ticket_sql(service, '1', state)


async def test_checkpoint_failure_after_ticket_commit_reconciles_without_another_write(tmp_path):
    async with ticket_app(tmp_path) as (app, client, tickets):
        preview, _ = await proposal(client)
        service = app.state.chat_service
        original = service.checkpointer.aput
        failed = False
        async def fail_after_execute(config, checkpoint, metadata, versions):
            nonlocal failed
            state = checkpoint['channel_values']
            if not failed and state.get('ticket_confirmation', {}).get('result'):
                failed = True
                raise OSError('simulated checkpoint boundary failure')
            return await original(config, checkpoint, metadata, versions)
        service.checkpointer.aput = fail_after_execute
        first = decode_sse((await client.post('/api/conversations/1/actions/confirm-ticket', json=decision(preview))).text)
        assert first[-1][0] == 'error' and tickets.calls == 1
        service.checkpointer.aput = original
        second = await client.post('/api/conversations/1/actions/confirm-ticket', json=decision(preview))
        from app.workflow.persistence import checkpoint_config
        projected = await service.graph.aget_state(checkpoint_config('1'))
        stored = await service.checkpointer.aget_tuple(checkpoint_config('1'))
        raw = stored.checkpoint['channel_values']
        assert second.status_code == 200, json.dumps({'next': projected.next,
            'projected_status': projected.values.get('turn_status'), 'raw_status': raw.get('turn_status'),
            'projected_result': projected.values['ticket_confirmation'].get('result'),
            'raw_result': raw['ticket_confirmation'].get('result'),
            'raw_decision': raw['ticket_confirmation'].get('decision'),
            'tasks': [task.name for task in projected.tasks],
            'branches': [key for key in raw if key.startswith('branch:')],
            'final': projected.values.get('final_message_id')}, ensure_ascii=True)
        frames = decode_sse(second.text)
        assert second.status_code == 200 and frames[-1][0] == 'done', second.text
        assert tickets.calls == 1 and len(tickets.rows) == 1


async def test_reused_model_call_id_in_later_turn_has_its_own_sql_pair_and_ticket(tmp_path):
    call = lambda: workflow_call('create_ticket', {'ticket_type': '售后', 'description': '饮水机漏水'}, identifier='reused')
    model = ScriptedWorkflowModel([call(), call()], intent_replies=[intent('工单'), intent('工单')])
    async with ticket_app(tmp_path, model=model) as (_, client, tickets):
        for _ in range(2):
            preview, _ = await proposal(client)
            result = await client.post('/api/conversations/1/actions/confirm-ticket', json=decision(preview))
            assert result.status_code == 200 and decode_sse(result.text)[-1][0] == 'done', result.text
        assert tickets.calls == 2 and len(tickets.rows) == 2
