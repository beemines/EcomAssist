"""聊天边界：新轮输入、图任务与最终检查点确认。"""
import asyncio
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from copy import deepcopy
import time
import json

import anyio
from langchain_core.messages import HumanMessage
from langchain_core.utils.function_calling import convert_to_openai_tool
from langgraph.types import Command

from app.core.chat import StreamEvent
from app.core.conversation_locks import Lease
from app.core.errors import ServiceError
from app.core.provider_errors import is_bigmodel_quota_failure
from app.core.llm import model_with_output_budget
from app.core.tool_history import build_tool_messages
from app.retrieval.types import validate_category
from app.tools.executor import ToolExecutor
from app.tools.types import ToolContext, ExecutionContext
from app.workflow.logging import configure_workflow_logging, log_lifecycle, log_terminal, safe_fields
from app.workflow.persistence import checkpoint_config, durable_completed_root
from app.workflow.prompts import agent_decision_system, build_intent_messages
from app.agent.controls import estimate_call_input
from app.core.errors import InputTooLong
from app.workflow.runtime import WorkflowRuntime
from app.workflow.state import WorkflowState, new_turn_state
from app.workflow.history import prepare_history_update, replay_turns, sql_messages
from app.workflow.order_actions import pending_selection
from app.workflow.selection import remaining_active_seconds
from app.workflow.understanding import QueryUnderstanding
from app.workflow.expansion import QueryExpander
from app.schemas.order_actions import OrderSelectionRequest
from app.orders.types import OrderSnapshot
from app.refunds.types import REFUND_REASONS
from app.repositories.conversations import _conversation_id
from app.context.layers import ContextCapacityError
from app.context.logging import budget_fields
from app.context.service import serialize_snapshot, restore_snapshot
from app.context.tokens import estimate_text_tokens
from app.workflow.entities import snapshot_provenance
from app.workflow.understanding import understanding_packet


_LABELS = {'handoff': '转人工', 'create_ticket': '建工单'}
_PHASES = {'selecting', 'checking', 'answering', 'tool_running', 'tool_completed'}


@dataclass
class PreparedWorkflowChat:
    # Set only by validated server-side recovery of an already running root.
    conversation_id: str
    user_message_id: int
    lease: Lease
    state: WorkflowState
    runtime: WorkflowRuntime
    deadline: float
    task: asyncio.Task | None = field(default=None, repr=False)
    audit: dict = field(default_factory=dict)
    terminal_logged: bool = False
    continue_pending: bool = False
    cancel_outcome: str = 'cancelled'
    graph_input: dict | Command | None = None
    replay_checkpoint_id: str | None = None


def _history(rows):
    """旧预算预检仅使用合法回放；State 始终从全部 SQL 原文恢复。"""
    return replay_turns(sql_messages(rows))


def _status(data):
    """只翻译已识别公开阶段及受控工具身份，屏蔽任意内部阶段。"""
    phase = data.get('phase')
    if data.get('status') in ('running', 'completed') and data.get('tool_call_id'):
        phase = 'tool_' + data['status']
    if phase not in _PHASES:
        return None
    public = {'phase': phase}
    if phase.startswith('tool_'):
        if not isinstance(data.get('tool'), str) or not isinstance(data.get('tool_call_id'), str):
            return None
        public.update(tool_name=data['tool'], tool_call_id=data['tool_call_id'])
        if data.get('result_status') in ('success', 'error'):
            public['status'] = data['result_status']
    if data.get('origin') in ('workflow', 'agent'):
        public['origin'] = data['origin']
    return StreamEvent('status', public)


def _citations(data):
    """检查公开引用结构并限制十条，非法载荷不降级为可信证据。"""
    values = data.get('citations')
    if not isinstance(values, list) or len(values) > 10 or any(not isinstance(item, dict) for item in values):
        raise ValueError('invalid workflow citations')
    seen = set()
    for item in values:
        if (set(item) != {'n', 'chunk_id', 'section_path', 'question', 'answer'}
                or type(item['n']) is not int or not 1 <= item['n'] <= 10 or item['n'] in seen
                or any(not isinstance(item[key], str) or not item[key] for key in ('chunk_id', 'question', 'answer'))
                or (item['section_path'] is not None and not isinstance(item['section_path'], str))):
            raise ValueError('invalid workflow citation')
        seen.add(item['n'])
    return StreamEvent('citations', {'citations': values})


class WorkflowChatService:
    """只在 SQL 与根 completed 检查点均已完成后发布动作及 done。"""
    def __init__(self, model, repository, registry_factory, locks, settings, *, graph, checkpointer,
                 faq_repository, sufficiency_service, quality_repository, executor=None,
                 order_provider=None, workflow_retriever=None, context_coordinator=None,
                 context_logger=None, context_budget_provider=None, catalog_provider=None, observability=None):
        """保存依赖并幂等启用专用审计，每轮单独组装运行环境及任务。"""
        configure_workflow_logging()
        self.model, self.repository, self.registry_factory = model, repository, registry_factory
        self.locks, self.settings, self.graph, self.checkpointer = locks, settings, graph, checkpointer
        self.faq_repository, self.sufficiency_service = faq_repository, sufficiency_service
        self.quality_repository = quality_repository
        self.order_provider, self.workflow_retriever = order_provider, workflow_retriever
        self.context_coordinator, self.context_logger = context_coordinator, context_logger
        self.context_budget_provider = context_budget_provider
        self.catalog_provider = catalog_provider
        self.observability = observability
        if (context_coordinator is None) != (context_budget_provider is None):
            raise ValueError('Context coordinator and actual budget provider must be supplied together.')
        self.executor = executor if executor is not None else ToolExecutor(settings.tool_timeout_seconds,
            settings.tool_max_retries, overrides={'query_faq': (settings.faq_timeout_seconds, 0)})
        self._tasks, self._prepared = set(), {}
        self._closing = False

    async def _runtime(self, conversation_id, identifier, message, category, deadline, started, baseline=0.0, *, registry=None, manifest=None, required_tools=None):
        """每次重建调用级理解/扩写器，SQL owner与工具使用同一权威。"""
        if registry is None:
            if self.catalog_provider is not None:
                if manifest:
                    options = {'required': required_tools} if required_tools is not None else {}
                    snapshot = await self.catalog_provider.restore(manifest, **options)
                else:
                    snapshot = await self.catalog_provider.acquire()
                registry = snapshot.bind(ToolContext(conversation_id, identifier, message, category))
            else:
                registry = self.registry_factory(ToolContext(conversation_id, identifier, message, category))
        control_model = model_with_output_budget(self.model, self.settings, self.settings.intent_max_output_tokens)
        runtime = WorkflowRuntime(model_with_output_budget(self.model, self.settings, self.settings.max_output_tokens),
            model_with_output_budget(self.model, self.settings, self.settings.agent_decision_max_output_tokens),
            control_model, self.repository, self.faq_repository, self.sufficiency_service, self.quality_repository,
            registry, self.executor, self.settings, deadline, order_provider=self.order_provider,
            workflow_retriever=self.workflow_retriever,
            understanding=QueryUnderstanding(control_model, input_budget=self.settings.tool_input_token_budget,
                timeout_seconds=self.settings.llm_timeout_seconds),
            expander=QueryExpander(control_model, input_budget=self.settings.tool_input_token_budget,
                timeout_seconds=self.settings.llm_timeout_seconds),
            user_id=await self.repository.get_user_id(conversation_id), active_started_at=started,
            active_elapsed_baseline=baseline)
        async def authorize_order(order_id):
            if self.order_provider is None:
                return False
            owner = await self.repository.get_user_id(conversation_id)
            return await self.order_provider.get_order(user_id=owner, order_id=order_id) is not None
        runtime.execution_context = ExecutionContext(conversation_id, identifier, '其他', message,
            deadline=deadline, policy=self.catalog_provider.policies if self.catalog_provider else None,
            order_authorizer=authorize_order)
        return runtime

    async def _prepare_context(self, state, runtime, rows, *, resume=False):
        if self.context_coordinator is None:
            return
        budget = self.context_budget_provider(runtime.registry)
        try:
            if resume and state.get('context_snapshot'):
                frozen = restore_snapshot(state['context_snapshot'], budget)
                if (frozen.conversation_id != state['conversation_id']
                        or frozen.user_message_id != state['user_message_id']):
                    raise ValueError('Frozen snapshot identity mismatch.')
            else:
                # Legacy pending roots have no frozen context. Establish one only
                # for the resumed execution; never rewrite the stored paused root.
                frozen = await self.context_coordinator.prepare(state['conversation_id'],
                    state['user_message_id'], rows, budget)
            # Pre-call check includes the full user text, summary JSON and output.
            understanding_packet(state['raw_question'], frozen, output_tokens=self.settings.intent_max_output_tokens)
            if resume:
                from app.workflow.context_budget import workflow_packet, stage_packet
                from app.workflow.controls import stable_tool_schema as stable_read_schema
                from app.workflow.prompts import EXPANSION_SYSTEM
                from app.core.prompts import build_sufficiency_messages, build_query_messages
                from langchain_core.messages import SystemMessage
                # Reuse the exact frozen view with today's output and native-result
                # caps before resuming any graph node or initiating a paid call.
                runtime.context_snapshot = frozen
                workflow_packet(state, runtime, phase='decision', tools=stable_read_schema(runtime.registry))
                _, evidence = workflow_packet(state, runtime, phase='final')
                if state.get('order_snapshot'):
                    stage_packet(frozen, system=SystemMessage(EXPANSION_SYSTEM), raw_question=state['raw_question'],
                        attachment={'resolved_question': state['resolved_question'], 'order': state['order_snapshot']},
                        output_tokens=self.settings.intent_max_output_tokens)
                if evidence.citations:
                    stage_packet(frozen, system=build_sufficiency_messages('', {})[0], raw_question=state['raw_question'],
                        attachment={'resolved_question': state['resolved_question'], 'evidence': evidence.payload,
                                    'order_context': state.get('order_snapshot')},
                        output_tokens=self.settings.sufficiency_max_output_tokens)
                stage_packet(frozen, system=build_query_messages('')[0], raw_question=state['raw_question'],
                             attachment={}, output_tokens=self.settings.query_max_output_tokens)
        except ContextCapacityError as exc:
            if self.context_logger is not None:
                self.context_logger.event('context_error', {'conversation_id': state['conversation_id'],
                    'user_message_id': state['user_message_id'], 'reason': 'capacity'})
            raise ServiceError('context_configuration_conflict' if resume else 'context_capacity',
                '当前上下文无法放入部署窗口，请检查上下文预算配置。', 409 if resume else 422) from exc
        runtime.context_snapshot = frozen
        runtime.context_provenance = snapshot_provenance(frozen, rows)
        runtime.context_logger = self.context_logger
        state.update(context_snapshot_id=frozen.snapshot_id, context_snapshot=serialize_snapshot(frozen),
            context_budget=budget_fields(budget), context_anchors=serialize_snapshot(frozen)['anchors'])
        if self.context_logger is not None:
            self.context_logger.history(frozen, consumer='prepare_resume' if resume else 'prepare', packet=None, sent=False)
            if state.get('context_bootstrap'):
                self.context_logger.event('context_bootstrap', {'conversation_id': state['conversation_id'],
                    'user_message_id': state['user_message_id'], 'snapshot_id': frozen.snapshot_id})

    def _register(self, prepared):
        """新输入、恢复和重放共用占用及计数审计注册。"""
        prepared.audit = safe_fields({key: prepared.state[key] for key in ('decision_count', 'tool_call_count', 'usage', 'stage_usage') if key in prepared.state})
        def observe_usage(update):
            """覆盖已记录的安全快照，不累加，取消与稍后事件都不会重复计费。"""
            prepared.audit.update(safe_fields({key: update.get(key) for key in ('usage', 'stage_usage')}))
        prepared.runtime.usage_observer = observe_usage
        self._prepared[id(prepared)] = prepared
        return prepared

    async def prepare(self, conversation_id: str, message: str, *, category=None) -> PreparedWorkflowChat:
        """SSE前检查预算和锁；提交新轮输入并初始化安全审计计数。"""
        validate_category(category)
        if self._closing:
            raise ServiceError('service_unavailable', '服务正在关闭，请稍后重试。', 503)
        started = time.monotonic()
        deadline = started + self.settings.chat_timeout_seconds
        lease = self.locks.acquire(conversation_id)
        try:
            async with asyncio.timeout_at(deadline):
                await self.repository.require_open(conversation_id)
                previous = await self.graph.aget_state(checkpoint_config(conversation_id))
                from app.workflow.ticket_actions import pending_ticket, expire_pending_ticket
                superseding_ticket = pending_ticket(previous, conversation_id)
                if superseding_ticket:
                    await expire_pending_ticket(self, previous)
                turns = _history(await self.repository.load_messages(conversation_id))
                current = HumanMessage(message)
                snapshot = await self.catalog_provider.acquire() if self.catalog_provider is not None else None
                preview = snapshot.bind(ToolContext(conversation_id, 0, message, category)) if snapshot else self.registry_factory(ToolContext(conversation_id, 0, message, category))
                schema = [convert_to_openai_tool(tool) for name, tool in preview.items() if name != 'create_ticket']
                if self.context_coordinator is None:
                    build_tool_messages(agent_decision_system(None), turns, current,
                        self.settings.tool_input_token_budget, tool_schema=schema)
                    if estimate_call_input(build_intent_messages(message), []) > self.settings.tool_input_token_budget:
                        raise InputTooLong()
                elif len(message) > 20000 or estimate_text_tokens(message) > self.settings.max_user_input_tokens:
                    raise InputTooLong()
                prior_ticket_verified = False
                if previous.values.get('ticket_request') and not previous.next and await durable_completed_root(self.checkpointer, previous, conversation_id):
                    try:
                        await self._verify_sql_turn(conversation_id, previous.values, completed=True)
                        prior_ticket_verified = True
                    except ServiceError:
                        # A stale prior root cannot authorize a continuation or block a new turn.
                        pass
                identifier = await self.repository.append_message(conversation_id, current)
                registry = snapshot.bind(ToolContext(conversation_id, identifier, message, category)) if snapshot else self.registry_factory(ToolContext(conversation_id, identifier, message, category))
                actual = [convert_to_openai_tool(tool) for name, tool in registry.items() if name != 'create_ticket']
                if actual != schema:
                    raise ServiceError('tool_schema_changed', '工具定义发生变化，请稍后重试。', 500)
                rows = await self.repository.load_messages(conversation_id)
                history_update, bootstrap = prepare_history_update(previous.values, rows, current_user_id=identifier)
                state = new_turn_state(conversation_id=conversation_id, user_message_id=identifier,
                    raw_question=message, category=category, messages=sql_messages(rows))
                state['context_bootstrap'] = bootstrap
                from app.workflow.ticket_requests import ticket_request_for_turn
                state['ticket_request'] = ticket_request_for_turn(identifier, message, previous.values,
                    previous_verified=prior_ticket_verified)
                if snapshot:
                    state.update(tool_catalog_version=snapshot.version, tool_manifest=snapshot.to_manifest())
                if pending_selection(previous, conversation_id) or superseding_ticket:
                    state['supersedes_turn_id'] = previous.values['user_message_id']
                runtime = await self._runtime(conversation_id, identifier, message, category, deadline, started, registry=registry)
                await self._prepare_context(state, runtime, rows)
                prepared = PreparedWorkflowChat(conversation_id, identifier, lease, state, runtime, deadline)
                prepared.graph_input = {**state, 'messages': history_update}
                self._register(prepared)
                log_lifecycle(prepared, 'prepared', prior_pending=bool(previous.next))
                return prepared
        except BaseException:
            lease.release()
            raise

    async def _verify_sql_turn(self, conversation_id, state, *, completed=False):
        """校验原轮用户/完成答复均属于SQL会话，拒绝新消息之后的旧身份。"""
        rows = await self.repository.load_messages(conversation_id)
        user = next((row for row in rows if str(row.id) == state.get('user_message_id')), None)
        valid = user is not None and user.role == 'user' and user.content == state.get('raw_question')
        if valid and any(row.role == 'user' and row.id > user.id for row in rows):
            valid = False
        if completed:
            assistant = next((row for row in rows if str(row.id) == state.get('final_message_id')), None)
            valid = (valid and assistant is not None and assistant.role == 'assistant'
                and assistant.tool_calls is None and assistant.content == state.get('final_answer')
                and user.id < assistant.id)
        if not valid:
            raise ServiceError('selection_conflict', '', 409)

    async def prepare_resume(self, conversation_id: str, payload: OrderSelectionRequest) -> PreparedWorkflowChat:
        """锁内核验最新根与原轮SQL；只用当前thread恢复，完成回执只读重放。"""
        _conversation_id(conversation_id)
        if self._closing:
            raise ServiceError('service_unavailable', '', 503)
        started = time.monotonic()
        lease = self.locks.acquire(conversation_id)
        try:
            async with asyncio.timeout(self.settings.chat_timeout_seconds):
                await self.repository.require_open(conversation_id)
                snapshot = await self.graph.aget_state(checkpoint_config(conversation_id))
                state = deepcopy(snapshot.values)
                receipt = state.get('order_selection') or {}
                pending = pending_selection(snapshot, conversation_id)
                saved = snapshot.config.get('configurable', {})
                completed = (not snapshot.next and state.get('turn_status') == 'completed'
                    and state.get('state_version') == 2 and state.get('conversation_id') == conversation_id
                    and saved.get('thread_id') == conversation_id and saved.get('checkpoint_ns') == ''
                    and receipt.get('selected_order_id') == payload.order_id
                    and receipt.get('pause_checkpoint_id') == payload.checkpoint_id
                    and await durable_completed_root(self.checkpointer, snapshot, conversation_id))
                matches = (receipt.get('turn_id') == payload.turn_id == state.get('user_message_id')
                    and receipt.get('selection_id') == payload.selection_id
                    and payload.order_id in {card['order_id'] for card in receipt.get('cards', [])})
                if not matches or not (completed or pending and pending['checkpoint_id'] == payload.checkpoint_id):
                    raise ServiceError('selection_conflict', '', 409)
                remaining = remaining_active_seconds(state, limit=self.settings.chat_timeout_seconds)
                if not completed and remaining <= time.monotonic() - started:
                    raise ServiceError('upstream_timeout', '', 504)
                deadline = started + remaining
                async with asyncio.timeout_at(deadline if not completed else started + self.settings.chat_timeout_seconds):
                    await self._verify_sql_turn(conversation_id, state, completed=completed)
                    runtime = await self._runtime(conversation_id, int(payload.turn_id), state['raw_question'],
                        state.get('category'), deadline, started, state.get('active_elapsed_seconds', 0.0), manifest=state.get('tool_manifest'))
                    runtime.model_recovery_used = state.get('model_recovery_used', False)
                    if not completed:
                        await self._prepare_context(state, runtime,
                            await self.repository.load_messages(conversation_id), resume=True)
                prepared = PreparedWorkflowChat(conversation_id, int(payload.turn_id), lease, deepcopy(state), runtime, deadline)
                if completed:
                    prepared.replay_checkpoint_id = saved['checkpoint_id']
                else:
                    context_update = {key: state[key] for key in ('context_snapshot', 'context_snapshot_id',
                        'context_anchors', 'context_budget') if key in state} if self.context_coordinator else None
                    prepared.graph_input = Command(resume={'order_id': payload.order_id,
                        'pause_checkpoint_id': payload.checkpoint_id}, update=context_update)
                return self._register(prepared)
        except TimeoutError:
            lease.release()
            raise ServiceError('upstream_timeout', '本轮处理超时，请重新发起。', 504) from None
        except BaseException:
            lease.release()
            raise

    async def _completed_events(self, prepared, final, checkpoint_id, queue, *, replay=False):
        """完成根通过SQL核验后才投影许可；重放正文来自保存答案。"""
        if replay:
            await queue.put(_citations({'citations': final.get('citations', [])}))
            await queue.put(StreamEvent('delta', {'delta': final['final_answer']}))
        options = [{'action': action, 'label': _LABELS[action]}
            for action in dict.fromkeys(final['suggested_actions']) if action in _LABELS]
        if options:
            await queue.put(StreamEvent('actions', {'assistant_message_id': final['final_message_id'],
                'checkpoint_id': checkpoint_id, 'options': options}))
        offer = final.get('refund_offer')
        if offer:
            order = OrderSnapshot.model_validate_json(json.dumps(offer['order_snapshot']))
            await queue.put(StreamEvent('refund_offer', {'assistant_message_id': final['final_message_id'],
                'checkpoint_id': checkpoint_id, 'offer_id': offer['offer_id'], 'order': order.to_card(),
                'refund_decision': offer['refund_decision'], 'decision_reason': offer['decision_reason'],
                'reasons': [{'code': code, 'label': label} for code, label in REFUND_REASONS]}))
        await queue.put(StreamEvent('done', {'conversation_id': prepared.conversation_id, 'message_id': final['final_message_id']}))

    async def _produce(self, prepared, queue):
        from app.observability.tracing import ExecutionIdentity, begin_execution
        identity = ExecutionIdentity(prepared.conversation_id, str(prepared.user_message_id),
            uuid4().hex, 'chat', replay=bool(prepared.replay_checkpoint_id))
        with begin_execution(self.observability, identity) as trace:
            if prepared.runtime is not None:
                prepared.runtime.observation_trace = trace
            if prepared.state.get('intent'):
                trace.set_intent(prepared.state['intent'], prepared.state.get('confidence'),
                                 prepared.state.get('route', 'other'))
            await self._produce_turn(prepared, queue)

    async def _produce_turn(self, prepared, queue):
        """同步持久化每步并汇总安全更新；根完成才发布done，每个退出记录唯一终态。"""
        config = checkpoint_config(prepared.conversation_id)
        config['recursion_limit'] = 64
        stream = None
        citations_sent = answering_started = False
        outcome, terminal = 'cancelled', {}
        try:
            if prepared.replay_checkpoint_id:
                await self._completed_events(prepared, prepared.state, prepared.replay_checkpoint_id, queue, replay=True)
                outcome = 'success'
                return
            graph_input = None if prepared.continue_pending else prepared.graph_input if prepared.graph_input is not None else prepared.state
            stream = self.graph.astream(graph_input,
                config=config, context=prepared.runtime, stream_mode=['custom', 'updates'], subgraphs=True, durability='sync')
            async with asyncio.timeout_at(prepared.deadline):
                await queue.put(StreamEvent('status', {'phase': 'selecting'}))
                async for namespace, kind, event in stream:
                    if kind == 'updates':
                        for update in event.values():
                            if isinstance(update, dict):
                                prepared.audit.update(safe_fields({key: update[key] for key in
                                    ('decision_count', 'tool_call_count', 'usage', 'stage_usage') if key in update}))
                        continue
                    if not isinstance(event, dict) or not isinstance(event.get('data'), dict):
                        continue
                    name, data = event.get('event'), event['data']
                    if name == 'usage':
                        prepared.audit.update(safe_fields({key: data.get(key) for key in ('usage', 'stage_usage')}))
                    elif name == 'status':
                        public = _status(data)
                        if public is not None:
                            await queue.put(public)
                            answering_started = answering_started or public.data['phase'] == 'answering'
                    elif name == 'citations' and not citations_sent:
                        await queue.put(_citations(data))
                        citations_sent = True
                    elif name == 'delta' and isinstance(data.get('text'), str) and data['text']:
                        if not citations_sent:
                            await queue.put(StreamEvent('citations', {'citations': []}))
                            citations_sent = True
                        if not answering_started:
                            await queue.put(StreamEvent('status', {'phase': 'answering'}))
                            answering_started = True
                        await queue.put(StreamEvent('delta', {'delta': data['text']}))
                snapshot = await self.graph.aget_state(config)
                final = snapshot.values
                from app.workflow.ticket_actions import pending_ticket
                ticket = pending_ticket(snapshot, prepared.conversation_id)
                if ticket and ticket['turn_id'] == str(prepared.user_message_id):
                    from app.workflow.ticket_actions import verify_ticket_sql
                    await verify_ticket_sql(self, prepared.conversation_id, final)
                    prepared.state = final
                    await queue.put(StreamEvent('ticket_confirmation', ticket))
                    await queue.put(StreamEvent('paused', {key: ticket[key] for key in
                        ('turn_id', 'confirmation_id', 'checkpoint_id')} | {'reason': 'ticket_confirmation'}))
                    outcome = 'paused'
                    return
                pending = pending_selection(snapshot, prepared.conversation_id)
                if pending and pending['turn_id'] == str(prepared.user_message_id):
                    await self._verify_sql_turn(prepared.conversation_id, final)
                    prepared.state = final
                    await queue.put(StreamEvent('order_selection', pending))
                    await queue.put(StreamEvent('paused', {key: pending[key] for key in
                        ('turn_id', 'selection_id', 'checkpoint_id')} | {'reason': 'order_selection'}))
                    outcome = 'paused'
                    return
                if (snapshot.next or final.get('turn_status') != 'completed'
                        or final.get('user_message_id') != str(prepared.user_message_id)
                        or final.get('conversation_id') != prepared.conversation_id or not final.get('final_message_id')
                        or not await durable_completed_root(self.checkpointer, snapshot, prepared.conversation_id)):
                    raise ValueError('workflow final snapshot incomplete')
                checkpoint_id = snapshot.config['configurable']['checkpoint_id']
                UUID(checkpoint_id)
                await self._verify_sql_turn(prepared.conversation_id, final, completed=True)
                prepared.state = final
                if self.context_coordinator is not None and prepared.runtime.context_snapshot is not None:
                    self.context_coordinator.on_completed(prepared.runtime.context_snapshot)
                log_lifecycle(prepared, 'checkpoint_complete', checkpoint_id=checkpoint_id,
                    final_message_id=final['final_message_id'])
                await self._completed_events(prepared, final, checkpoint_id, queue)
                outcome = 'success'
                terminal = {'final_message_id': final['final_message_id'], 'checkpoint_id': checkpoint_id}
        except ServiceError as exc:
            if is_bigmodel_quota_failure(exc):
                exc = ServiceError('upstream_quota_exhausted',
                    '模型服务账户余额不足或无可用资源包，请联系管理员处理后再试。', 503)
            outcome, terminal = ('timeout' if exc.code == 'upstream_timeout' else 'error'), {'code': exc.code}
            await queue.put(StreamEvent('error', {'code': exc.code, 'message': exc.message}))
        except TimeoutError:
            outcome, terminal = 'timeout', {'code': 'upstream_timeout'}
            await queue.put(StreamEvent('error', {'code': 'upstream_timeout', 'message': '本轮处理超时，请稍后重试。'}))
        except Exception:
            outcome, terminal = 'error', {'code': 'upstream_error'}
            await queue.put(StreamEvent('error', {'code': 'upstream_error', 'message': '本次回答未能完成，请稍后重试。'}))
        finally:
            trace = getattr(prepared.runtime, 'observation_trace', None)
            if trace is not None:
                if prepared.state.get('intent'):
                    trace.set_intent(prepared.state['intent'], prepared.state.get('confidence'),
                                     prepared.state.get('route', 'other'))
                trace.finish(prepared.cancel_outcome if outcome == 'cancelled' else outcome)
            log_terminal(prepared, prepared.cancel_outcome if outcome == 'cancelled' else outcome, **terminal)
            if stream is not None:
                await stream.aclose()

    async def stream(self, prepared):
        """有界队列保留增量响应；响应关闭标记断连，停机保持取消原因。"""
        if self._closing:
            raise asyncio.CancelledError()
        queue = asyncio.Queue(maxsize=1)
        task = asyncio.create_task(self._produce(prepared, queue), name='workflow-chat')
        prepared.task = task
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        try:
            while True:
                get = asyncio.create_task(queue.get())
                try:
                    done, _ = await asyncio.wait({get, task}, return_when=asyncio.FIRST_COMPLETED)
                    if get not in done:
                        await task
                        if queue.empty():
                            return
                    event = await get
                finally:
                    if not get.done():
                        get.cancel()
                    await asyncio.gather(get, return_exceptions=True)
                yield event
                if event.event in ('done', 'error', 'paused'):
                    return
        finally:
            with anyio.move_on_after(5, shield=True):
                if not task.done():
                    if not self._closing:
                        prepared.cancel_outcome = 'disconnected'
                    task.cancel()
                await asyncio.gather(task, return_exceptions=True)

    def release(self, prepared):
        """幂等归还凭证；尚未启动或清理超时也补唯一断连/停机终态。"""
        log_terminal(prepared, 'cancelled' if self._closing else 'disconnected')
        prepared.lease.release()
        self._prepared.pop(id(prepared), None)

    async def shutdown(self):
        """应用退出先有界取消全部图任务，再允许外层关闭 SQLite。"""
        self._closing = True
        tasks = tuple(self._tasks)
        for task in tasks:
            task.cancel()
        try:
            with anyio.move_on_after(5, shield=True):
                await asyncio.gather(*tasks, return_exceptions=True)
        finally:
            for prepared in tuple(self._prepared.values()):
                self.release(prepared)
