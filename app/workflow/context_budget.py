"""Actual workflow phase inventory and pure packet composition."""
from dataclasses import replace
from types import SimpleNamespace
import json
from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from app.agent.controls import resolve_turn_token_limit
from app.context.budget import derive_budget
from app.context.layers import ContextCapacityError, plan_layers
from app.context.tokens import ESTIMATOR_VERSION, estimate_payload, estimate_text_tokens
from app.context.types import ContextAnchors, PhaseOverheads
from app.context.view import build_snapshot, compose_call
from app.core.evidence import prepare_workflow_evidence
from app.core.errors import InputTooLong
from app.core.prompts import build_query_messages, build_sufficiency_messages
from app.repositories.records import record_from_message
from app.workflow.controls import stable_read_schema
from app.workflow.prompts import (EXPANSION_SYSTEM, INTENT_SYSTEM, UNDERSTANDING_SYSTEM,
                                  agent_decision_system, agent_final_system)


def workflow_budget(settings, registry):
    """Deduct actual fixed prefixes and bounded dynamic/native envelopes."""
    source = Path(__file__).parents[1] / 'context' / 'steady_turns.json'
    try:
        fixture = json.loads(source.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise ValueError('Missing or invalid steady business turn budget data') from exc
    if fixture.get('estimator_version') != ESTIMATOR_VERSION:
        raise ValueError('Steady business turn estimator version mismatch')
    costs = []
    for turn in fixture['turns']:
        rows = turn['messages']
        costs.append(estimate_payload([HumanMessage(rows[0]['content']),
            AIMessage(rows[1]['content'], tool_calls=rows[1]['tool_calls']),
            ToolMessage(rows[2]['content'], tool_call_id=rows[2]['tool_call_id']), AIMessage(rows[3]['content'])]))
    # Includes one native request + receipt framing; each actual pair is checked
    # against this same allowance. FAQ body is charged once in E instead of P.
    peak = settings.tool_result_max_tokens + 256
    phases = [
        PhaseOverheads('understanding', UNDERSTANDING_SYSTEM, (), settings.intent_max_output_tokens, 32, 0, False),
        PhaseOverheads('classification', INTENT_SYSTEM, (), settings.intent_max_output_tokens,
                       settings.max_user_input_tokens + 128, 0, False),
        PhaseOverheads('expansion', EXPANSION_SYSTEM, (), settings.intent_max_output_tokens, peak, 0, False),
        PhaseOverheads('sufficiency', build_sufficiency_messages('', {})[0].content, (),
                       settings.sufficiency_max_output_tokens, peak, 0, True),
        PhaseOverheads('query_planner', build_query_messages('')[0].content, (),
                       settings.query_max_output_tokens, 32, 0, False),
        PhaseOverheads('decision', agent_decision_system(None).content, tuple(stable_read_schema(registry)),
                       settings.agent_decision_max_output_tokens, 640, peak, True),
        PhaseOverheads('final', agent_final_system(None, None).content, (), settings.max_output_tokens,
                       640, peak, True),
    ]
    return derive_budget(settings, phases, steady_turn_tokens=max(costs), minimum_turn_tokens=min(costs))


def turn_token_limit(settings, budget):
    return resolve_turn_token_limit(settings, budget, call_limits=workflow_call_limits(settings))


def workflow_call_limits(settings):
    limits = dict(understanding=1, classification=1, expansion=1,
                  sufficiency=settings.max_agent_steps + 2, query_planner=0,
                  decision=settings.max_agent_steps + 1, final=1)
    return limits


def fee_cap_diagnostic(settings, budget, registry):
    """Shortest model path: understanding + OTHER classification, no tools.

    Count actual canonical packets for a one-token question, then add the target
    history to each input. The runtime reserves decision/final even on this path.
    Below the initial reservation is incompatible. Between it and the fallback
    (unknown usage) path cost is usage-dependent, not a proven compatible cap.
    Pure social turns make zero calls and are reported separately.
    """
    from app.context.budget import derive_turn_token_limit
    from app.context.types import ContextSnapshot
    from app.workflow.state import new_turn_state
    from app.workflow.understanding import understanding_packet
    from app.workflow.intent import intent_packet
    if set(budget.phases) != set(workflow_call_limits(settings)):
        # Explicit dependency-injection budgets can omit the phase inventory;
        # report that limitation rather than inventing a derived cap at startup.
        explicit = settings.agent_total_token_budget if settings.agent_total_token_budget_explicit else None
        return {'explicit_limit': explicit, 'effective_limit': explicit, 'derived_limit': None,
                'history_allowance': budget.history, 'compatibility': 'unavailable',
                'reason': 'injected_budget_without_workflow_phase_inventory'}
    snapshot = ContextSnapshot('startup-diagnostic', '0', '1', ContextAnchors(None, None),
                               (), (), (), (), budget)
    state = new_turn_state(conversation_id='0', user_message_id=1, raw_question='?',
                           category=None, messages=[HumanMessage('?', id='1')])
    context = SimpleNamespace(settings=settings, registry=registry, context_snapshot=snapshot)
    understanding = understanding_packet('?', snapshot, output_tokens=settings.intent_max_output_tokens)
    classification = intent_packet('?', snapshot, output_tokens=settings.intent_max_output_tokens)
    final, _ = workflow_packet(state, context, phase='final')
    decision, _ = workflow_packet(state, context, phase='decision', tools=stable_read_schema(registry))
    def reservation(packet):
        return budget.history + packet.estimated_tokens + packet.output_tokens
    # model_stage(following=1) retains this additional classification output.
    following = reservation(final) + reservation(decision) + settings.intent_max_output_tokens
    minimum = max(reservation(understanding), reservation(classification)) + following
    conservative = reservation(understanding) + reservation(classification) + following
    effective = turn_token_limit(settings, budget)
    return {'explicit_limit': settings.agent_total_token_budget if settings.agent_total_token_budget_explicit else None,
            'effective_limit': effective,
            'derived_limit': derive_turn_token_limit(budget, call_limits=workflow_call_limits(settings)),
            'history_allowance': budget.history, 'shortest_model_calls': 2, 'social_fast_path_calls': 0,
            'basis': 'estimated_shortest_model_path_without_summary_or_tools',
            'minimum_reservation': minimum, 'conservative_shortest_path_cap': conservative,
            'compatibility': 'incompatible' if effective < minimum else
                'compatible' if effective >= conservative else 'usage_dependent'}


def reserve_context_call(messages, tools, ledger, *, output_limit, final_reserve):
    from app.core.errors import ServiceError
    if estimate_payload(messages, tools) + output_limit + final_reserve > ledger.remaining:
        raise ServiceError('token_budget', '本轮模型预算不足，无法继续查询。', 422)


def runtime_settings(settings):
    """Explicit legacy dependency-injection seam; production already owns Settings."""
    from app.config import Settings
    if isinstance(settings, Settings):
        return settings
    return Settings(_env_file=None, llm_model='injected', llm_api_key='injected',
        llm_base_url='https://injected.invalid', **{
            name: getattr(settings, name) for name in Settings.model_fields if hasattr(settings, name)})


def runtime_snapshot(state, context):
    if context.context_snapshot is not None:
        return context.context_snapshot
    settings = runtime_settings(context.settings)
    budget = workflow_budget(settings, context.registry)
    index = next(i for i, message in enumerate(state['messages'])
                 if isinstance(message, HumanMessage) and message.id == state['user_message_id'])
    # Direct graph injection owns full State but no persistent coordinator. Use
    # ordinal identities only inside this temporary projection, preserving source.
    offset = int(state['user_message_id'])
    rows = [record_from_message(message, identifier=offset+i+1) for i, message in enumerate(state['messages'][:index])]
    plan = plan_layers(rows, ContextAnchors(None, None), budget, current_user_id=offset+index+1)
    snapshot = build_snapshot(plan, (), conversation_id=state['conversation_id'],
                              user_message_id=str(offset+index+1), budget=budget)
    return replace(snapshot, user_message_id=state['user_message_id'])


def workflow_packet(state, context, *, phase, tools=()):
    settings = runtime_settings(context.settings)
    if estimate_text_tokens(state['raw_question']) > settings.max_user_input_tokens:
        raise ContextCapacityError('current user input limit')
    snapshot = runtime_snapshot(state, context)
    index = next(i for i, message in enumerate(state['messages'])
                 if isinstance(message, HumanMessage) and message.id == state['user_message_id'])
    pending = state['messages'][index+1:]
    payloads = [json.loads(message.content) for message in pending if isinstance(message, ToolMessage)]
    try:
        evidence = prepare_workflow_evidence(payloads, top_k=settings.rerank_top_k, token_budget=snapshot.budget.evidence)
    except InputTooLong as exc:
        raise ContextCapacityError('complete evidence block limit') from exc
    shown = [message.model_copy(deep=True) for message in pending]
    if len(shown) != len(payloads) * 2:
        raise ValueError('Current native tool pairs are incomplete')
    for i, receipt in enumerate(evidence.tool_receipts):
        text = json.dumps(receipt, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
        if estimate_text_tokens(text) > settings.tool_result_max_tokens:
            raise ContextCapacityError('tool result limit')
        shown[i*2+1].content = text
        if estimate_payload(shown[i*2:i*2+2]) > settings.tool_result_max_tokens + 256:
            raise ContextCapacityError('native tool peak limit')
    attachment = {key: state.get(key) for key in ('intent', 'route', 'reply_mode', 'refund_decision', 'decision_reason')}
    if state['resolved_question'] != state['raw_question']:
        attachment['resolved_question'] = state['resolved_question']
    if estimate_payload([HumanMessage(json.dumps(attachment, ensure_ascii=False))]) > 640:
        raise ContextCapacityError('dynamic control attachment limit')
    attachment['evidence'] = evidence.payload
    output = settings.agent_decision_max_output_tokens if phase == 'decision' else settings.max_output_tokens
    system = agent_decision_system(None) if phase == 'decision' else agent_final_system(None, None)
    packet = compose_call(snapshot, system=system, current=state['messages'][index],
        attachment=attachment, pending=shown, tools=tools, output_tokens=output)
    return packet, evidence


def stage_packet(snapshot, *, system, raw_question, attachment, output_tokens):
    return compose_call(snapshot, system=system, current=HumanMessage(raw_question, id=snapshot.user_message_id),
        attachment=attachment, pending=(), tools=(), output_tokens=output_tokens)


def standalone_packet(messages, *, output_tokens):
    """Capture a legacy standalone phase's actual messages, without imagined history."""
    import hashlib
    from app.context.types import ModelContextPacket
    prefix = hashlib.sha256(json.dumps({'system': messages[0].content, 'tools': []},
        ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
    return ModelContextPacket(messages, (), estimate_payload(messages), output_tokens, prefix, '')
