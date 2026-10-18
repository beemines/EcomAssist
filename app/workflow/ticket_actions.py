"""Only the latest durable root + exact SQL request can issue a write grant."""
import asyncio
from copy import deepcopy
from dataclasses import replace
import time

from langgraph.types import Command
from app.core.errors import ServiceError
from app.repositories.conversations import _conversation_id
from app.repositories.records import decode_tool_calls
from app.tools.catalog_types import fingerprint
from app.tools.types import ConfirmationGrant, ToolCall, ToolContext, ExecutionContext
from app.workflow.persistence import checkpoint_config, durable_completed_root
from app.workflow.selection import remaining_active_seconds
from app.workflow.ticket_confirmation import preview_payload


def pending_ticket(snapshot, conversation_id):
    state = snapshot.values
    confirmation = state.get('ticket_confirmation') or {}
    config = snapshot.config.get('configurable', {})
    interrupts = [item for task in snapshot.tasks for item in task.interrupts]
    if (state.get('state_version') != 2 or state.get('turn_status') != 'awaiting_ticket'
            or state.get('conversation_id') != conversation_id or config.get('thread_id') != conversation_id
            or config.get('checkpoint_ns') != '' or tuple(snapshot.next) != ('await_ticket_confirmation',)
            or len(interrupts) != 1 or confirmation.get('decision') is not None
            or confirmation.get('turn_id') != state.get('user_message_id')
            or fingerprint(confirmation.get('args')) != confirmation.get('arguments_fingerprint')):
        return None
    payload = preview_payload(confirmation)
    if interrupts[0].value != payload:
        return None
    return payload | {'checkpoint_id': config['checkpoint_id']}


async def verify_ticket_sql(service, conversation_id, state):
    await service._verify_sql_turn(conversation_id, state)
    confirmation = state['ticket_confirmation']
    rows = await service.repository.load_messages(conversation_id)
    if state.get('turn_status') == 'awaiting_ticket' and any(row.id > int(state['user_message_id']) and row.tool_call_id == confirmation['tool_call_id'] for row in rows):
        raise ServiceError('ticket_confirmation_conflict', '', 409)
    requests = [row for row in rows if row.id > int(state['user_message_id']) and row.role == 'assistant' and row.tool_calls
        and decode_tool_calls(row.tool_calls)[0]['id'] == confirmation['tool_call_id']]
    if (len(requests) != 1 or requests[0].id <= int(state['user_message_id'])
            or decode_tool_calls(requests[0].tool_calls)[0]['name'] != 'create_ticket'
            or decode_tool_calls(requests[0].tool_calls)[0]['args'] != confirmation['args']):
        raise ServiceError('ticket_confirmation_conflict', '', 409)
    request = state.get('ticket_request') or {}
    sources = {str(row.id): row.content for row in rows if row.role == 'user'}
    if (not request or len(request.get('source_texts', [])) != len(request.get('source_message_ids', []))
            or not all(sources.get(identifier) == text for identifier, text in zip(
                request.get('source_message_ids', []), request.get('source_texts', [])))):
        raise ServiceError('ticket_confirmation_conflict', '', 409)


async def durable_ticket_root(service, snapshot):
    stored = await service.checkpointer.aget_tuple(checkpoint_config(snapshot.values['conversation_id']))
    if stored is None or stored.config != snapshot.config:
        return False
    raw = stored.checkpoint['channel_values']
    return all(raw.get(key) == snapshot.values.get(key) for key in (
        'conversation_id', 'user_message_id', 'raw_question', 'state_version',
        'ticket_confirmation', 'ticket_request', 'tool_manifest'))


async def expire_pending_ticket(service, snapshot):
    """New user input cancels an old proposal before any new SQL user row."""
    state = snapshot.values
    confirmation = state['ticket_confirmation']
    rows = await service.repository.load_messages(state['conversation_id'])
    if any(row.id > int(state['user_message_id']) and row.tool_call_id == confirmation['tool_call_id'] for row in rows):
        return
    registry = service.registry_factory(ToolContext(state['conversation_id'], int(state['user_message_id']),
        state['raw_question'], state.get('category')))
    trusted = ExecutionContext(state['conversation_id'], int(state['user_message_id']), '工单', state['raw_question'])
    outcome = await service.executor.execute(ToolCall(confirmation['tool_call_id'], 'create_ticket', confirmation['args']),
        registry, context=trusted)
    from langchain_core.messages import ToolMessage
    from app.workflow.ticket_confirmation import append_ticket_message
    import json
    message = ToolMessage(json.dumps(outcome.content, ensure_ascii=False, separators=(',', ':')),
        tool_call_id=confirmation['tool_call_id'], name='create_ticket', status='error')
    await append_ticket_message(service.repository, state['conversation_id'], message,
        user_message_id=state['user_message_id'])


class TicketConfirmationService:
    def __init__(self, service):
        self.service = service

    async def pending(self, conversation_id):
        _conversation_id(conversation_id)
        await self.service.repository.require_open(conversation_id)
        snapshot = await self.service.graph.aget_state(checkpoint_config(conversation_id))
        preview = pending_ticket(snapshot, conversation_id)
        if preview:
            try:
                await verify_ticket_sql(self.service, conversation_id, snapshot.values)
            except ServiceError:
                return {'pending': None}
            if not await durable_ticket_root(self.service, snapshot):
                return {'pending': None}
        return {'pending': preview}

    async def confirm(self, conversation_id, payload):
        from app.workflow.service import PreparedWorkflowChat
        _conversation_id(conversation_id)
        service = self.service
        if service._closing:
            raise ServiceError('service_unavailable', '', 503)
        started = time.monotonic()
        lease = service.locks.acquire(conversation_id)
        try:
            async with asyncio.timeout(service.settings.chat_timeout_seconds):
                await service.repository.require_open(conversation_id)
                snapshot = await service.graph.aget_state(checkpoint_config(conversation_id))
                state = deepcopy(snapshot.values)
                saved = snapshot.config.get('configurable', {})
                confirmation = state.get('ticket_confirmation') or {}
                pending = pending_ticket(snapshot, conversation_id)
                completed = (not snapshot.next and state.get('turn_status') == 'completed'
                    and state.get('state_version') == 2 and state.get('conversation_id') == conversation_id
                    and saved.get('thread_id') == conversation_id and saved.get('checkpoint_ns') == ''
                    and confirmation.get('decision') == payload.decision
                    and confirmation.get('pause_checkpoint_id') == payload.checkpoint_id
                    and await durable_completed_root(service.checkpointer, snapshot, conversation_id))
                stored = await service.checkpointer.aget_tuple(checkpoint_config(conversation_id))
                raw = stored.checkpoint['channel_values'] if stored is not None and stored.config == snapshot.config else {}
                raw_confirmation = raw.get('ticket_confirmation') or {}
                # A completed task's pending writes can overlay the last root
                # while snapshot.next is empty after saver.aput failed. Continue
                # that root with None; never start the Agent or invent a new call.
                recovering = (raw.get('turn_status') == 'running'
                    and raw_confirmation.get('decision') == payload.decision
                    and raw_confirmation.get('pause_checkpoint_id') == payload.checkpoint_id
                    and bool(snapshot.tasks) and all(task.name in (
                        'execute_ticket_confirmation', 'ticket_confirmation_response', 'log_response') for task in snapshot.tasks)
                    and all(raw_confirmation.get(key) == confirmation.get(key) for key in (
                        'confirmation_id', 'turn_id', 'tool_call_id', 'args', 'arguments_fingerprint'))
                    and all(raw.get(key) == state.get(key) for key in ('tool_manifest', 'ticket_request', 'user_message_id', 'raw_question')))
                matches = (confirmation.get('turn_id') == payload.turn_id == state.get('user_message_id')
                    and confirmation.get('confirmation_id') == payload.confirmation_id)
                if not matches or not (completed or recovering or pending and pending['checkpoint_id'] == payload.checkpoint_id):
                    raise ServiceError('ticket_confirmation_conflict', '', 409)
                if not recovering and not await durable_ticket_root(service, snapshot):
                    raise ServiceError('ticket_confirmation_conflict', '', 409)
                await verify_ticket_sql(service, conversation_id, state)
                if completed:
                    await service._verify_sql_turn(conversation_id, state, completed=True)
                remaining = remaining_active_seconds(state, limit=service.settings.chat_timeout_seconds)
                if not completed and remaining <= time.monotonic() - started:
                    raise ServiceError('upstream_timeout', '', 504)
                deadline = started + remaining
                try:
                    runtime = await service._runtime(conversation_id, int(payload.turn_id), state['raw_question'],
                        state.get('category'), deadline, started, state.get('active_elapsed_seconds', 0.0),
                        registry={} if completed else None, manifest=state.get('tool_manifest') if not completed else None)
                except ValueError:
                    raise ServiceError('ticket_confirmation_conflict', '', 409) from None
                runtime.model_recovery_used = state.get('model_recovery_used', False)
                if not completed:
                    # Pending native request intentionally has no result yet.
                    # No model call occurs on this deterministic resume path.
                    if payload.decision == 'confirm':
                        grant = ConfirmationGrant('chat_preview', conversation_id, int(payload.turn_id),
                            confirmation['tool_call_id'], confirmation['arguments_fingerprint'])
                        runtime.execution_context = replace(runtime.execution_context, grant=grant,
                            ticket_requested=True, intent='工单')
                prepared = PreparedWorkflowChat(conversation_id, int(payload.turn_id), lease, state, runtime, deadline)
                if completed:
                    prepared.replay_checkpoint_id = saved['checkpoint_id']
                elif recovering:
                    prepared.continue_pending = True
                else:
                    prepared.graph_input = Command(resume={'decision': payload.decision,
                                                          'pause_checkpoint_id': payload.checkpoint_id})
                return service._register(prepared)
        except TimeoutError:
            lease.release()
            raise ServiceError('upstream_timeout', '', 504) from None
        except BaseException:
            lease.release()
            raise
