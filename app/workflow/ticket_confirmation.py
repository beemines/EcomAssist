"""Ticket proposal, durable wait, execution and receipt are separate root nodes."""
from copy import deepcopy
from dataclasses import replace
import json
from uuid import uuid4, UUID

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.types import interrupt
from app.tools.catalog_types import fingerprint
from app.tools.schemas import TicketArgs
from app.tools.types import ToolCall, ConfirmationGrant
from app.repositories.records import decode_tool_calls, message_from_record
from app.workflow.selection import active_elapsed
from app.workflow.ticket_requests import grounded_description
from app.workflow.tool_calls import execution_context


def preview_payload(confirmation):
    return {key: deepcopy(confirmation[key]) for key in ('turn_id', 'confirmation_id')} | {
        'ticket_type': confirmation['args']['ticket_type'], 'description': confirmation['args']['description']}


async def append_ticket_message(repository, conversation_id, message, *, user_message_id):
    """Reconcile SQL success / checkpoint failure with the stable native call ID."""
    rows = await repository.load_messages(conversation_id)
    for row in rows:
        if row.id <= int(user_message_id):
            continue
        if isinstance(message, AIMessage) and row.tool_calls:
            calls = decode_tool_calls(row.tool_calls)
            if calls[0]['id'] == message.tool_calls[0]['id']:
                if calls[0] != message.tool_calls[0]:
                    raise ValueError('Ticket request identity conflict')
                message.id = str(row.id)
                return message
        elif isinstance(message, ToolMessage) and row.tool_call_id == message.tool_call_id:
            if row.content != message.content:
                raise ValueError('Ticket receipt identity conflict')
            message.id = str(row.id)
            return message
    message.id = str(await repository.append_message(conversation_id, message))
    return message


async def prepare_ticket_confirmation(state, runtime):
    proposal = state.get('ticket_proposal') or {}
    args = deepcopy(proposal.get('args'))
    identifier = proposal.get('tool_call_id')
    TicketArgs.model_validate({**args, 'tool_call_id': identifier})
    if not grounded_description(args['description'], state.get('ticket_request')):
        raise ValueError('Ticket description has no user source')
    request = AIMessage('', tool_calls=[{'id': identifier, 'name': 'create_ticket', 'args': args}],
                        response_metadata={'finish_reason': 'tool_calls'})
    request = await append_ticket_message(runtime.context.repository, state['conversation_id'], request,
        user_message_id=state['user_message_id'])
    confirmation = {'confirmation_id': str(uuid4()), 'turn_id': state['user_message_id'],
        'tool_call_id': identifier, 'args': args, 'arguments_fingerprint': fingerprint(args),
        'pause_checkpoint_id': None, 'decision': None, 'result': None}
    return {'messages': [request], 'ticket_confirmation': confirmation, 'ticket_proposal': None,
        'turn_status': 'awaiting_ticket', 'active_elapsed_seconds': active_elapsed(state, runtime.context)}


def await_ticket_confirmation(state, runtime):
    confirmation = state.get('ticket_confirmation') or {}
    if (state.get('turn_status') != 'awaiting_ticket' or confirmation.get('decision') is not None
            or confirmation.get('turn_id') != state['user_message_id']
            or fingerprint(confirmation.get('args')) != confirmation.get('arguments_fingerprint')):
        raise ValueError('Invalid durable ticket proposal')
    UUID(confirmation['confirmation_id'])
    response = interrupt(preview_payload(confirmation))
    if (not isinstance(response, dict) or set(response) != {'decision', 'pause_checkpoint_id'}
            or response['decision'] not in ('confirm', 'cancel')):
        raise ValueError('Invalid ticket decision')
    UUID(response['pause_checkpoint_id'])
    return {'ticket_confirmation': {**confirmation, **response}, 'turn_status': 'running'}


async def execute_ticket_confirmation(state, runtime):
    context = runtime.context
    confirmation = state['ticket_confirmation']
    args = confirmation['args']
    if (confirmation.get('decision') not in ('confirm', 'cancel')
            or fingerprint(args) != confirmation['arguments_fingerprint']):
        raise ValueError('Invalid confirmed ticket contract')
    call = ToolCall(confirmation['tool_call_id'], 'create_ticket', args)
    trusted = execution_context(state, context)
    grant = None
    if confirmation['decision'] == 'confirm':
        grant = ConfirmationGrant('chat_preview', state['conversation_id'], int(state['user_message_id']),
            call.id, confirmation['arguments_fingerprint'])
    # The root node alone cannot grant authority: the public resume preflight
    # must have bound this exact grant in the runtime after checking SQL/root.
    if grant is not None and getattr(context.execution_context, 'grant', None) != grant:
        grant = None
    trusted = replace(trusted, grant=grant)
    rows = await context.repository.load_messages(state['conversation_id'])
    existing = next((row for row in rows if row.id > int(state['user_message_id']) and row.tool_call_id == call.id), None)
    if existing is not None:
        result = message_from_record(existing)
        result.id = str(existing.id)
        content = json.loads(result.content)
        success = 'error' not in content
    else:
        outcome = await context.executor.execute(call, context.registry, context=trusted)
        content, success = outcome.content, outcome.status == 'success'
        result = ToolMessage(json.dumps(content, ensure_ascii=False, separators=(',', ':'), allow_nan=False),
            tool_call_id=call.id, name=call.name, status=outcome.status)
        result = await append_ticket_message(context.repository, state['conversation_id'], result,
            user_message_id=state['user_message_id'])
    return {'messages': [result], 'ticket_confirmation': {**confirmation, 'result': content},
        'active_elapsed_seconds': active_elapsed(state, context),
        'tool_call_count': state['tool_call_count'] + 1,
        'tool_trace': [*state['tool_trace'], {'node': 'execute_ticket_confirmation', 'origin': 'workflow',
            'name': 'create_ticket', 'tool_call_id': call.id, 'status': 'success' if success else 'error'}]}


async def ticket_confirmation_response(state, runtime):
    confirmation = state['ticket_confirmation']
    result = confirmation.get('result') or {}
    if confirmation['decision'] == 'cancel':
        answer = '已取消，本次未创建工单。'
    elif isinstance(result.get('ticket_no'), str) and result.get('status') in ('待处理', '已处理'):
        answer = f'工单已提交，工单号：{result["ticket_no"]}。'
    elif result.get('error', {}).get('code') == 'tool_timeout':
        answer = '工单提交超时，结果尚未确认；本次未自动重试，请保留本次申请供核对。'
    else:
        answer = '本次工单未能确认提交，请稍后重试或联系人工核对。'
    runtime.stream_writer({'event': 'delta', 'data': {'text': answer}})
    return {'final_answer': answer, 'reply_mode': 'answer', 'suggested_actions': [],
        'quality': {}, 'citations': [], 'evidence_payload': {}}
