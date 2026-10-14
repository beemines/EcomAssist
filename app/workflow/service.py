"""聊天边界：新轮输入、图任务与最终检查点确认。"""
import asyncio
from dataclasses import dataclass, field
from uuid import UUID

import anyio
from langchain_core.messages import HumanMessage
from langchain_core.utils.function_calling import convert_to_openai_tool

from app.core.chat import StreamEvent
from app.core.conversation_locks import Lease
from app.core.errors import ServiceError
from app.core.llm import model_with_output_budget
from app.core.tool_history import build_tool_messages, completed_turns
from app.retrieval.types import validate_category
from app.tools.executor import ToolExecutor
from app.tools.types import ToolContext
from app.workflow.logging import configure_workflow_logging, log_lifecycle, log_terminal, safe_fields
from app.workflow.persistence import checkpoint_config
from app.workflow.prompts import agent_decision_system, build_intent_messages
from app.agent.controls import estimate_call_input
from app.core.errors import InputTooLong
from app.workflow.runtime import WorkflowRuntime
from app.workflow.state import WorkflowState, new_turn_state


_LABELS = {'handoff': '转人工', 'create_ticket': '建工单'}
_PHASES = {'selecting', 'checking', 'answering', 'tool_running', 'tool_completed'}


@dataclass
class PreparedWorkflowChat:
    conversation_id: str
    user_message_id: int
    lease: Lease
    state: WorkflowState
    runtime: WorkflowRuntime
    deadline: float
    task: asyncio.Task | None = field(default=None, repr=False)
    audit: dict = field(default_factory=dict)
    terminal_logged: bool = False
    cancel_outcome: str = 'cancelled'


def _history(rows):
    """按完整 SQL 轮次恢复稳定身份，忽略未完成申请及孤立审计。"""
    result, group = [], []
    for row in sorted(rows, key=lambda item: item.id):
        if row.role == 'user':
            group = []
        group.append(row)
        if row.role == 'assistant' and row.tool_calls is None:
            turns = completed_turns(group)
            if turns:
                for message, stored in zip(turns[0], group):
                    message.id = str(stored.id)
                result.extend(turns)
            group = []
    return result


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
                 faq_repository, sufficiency_service, quality_repository, executor=None):
        """保存依赖并幂等启用专用审计，每轮单独组装运行环境及任务。"""
        configure_workflow_logging()
        self.model, self.repository, self.registry_factory = model, repository, registry_factory
        self.locks, self.settings, self.graph, self.checkpointer = locks, settings, graph, checkpointer
        self.faq_repository, self.sufficiency_service = faq_repository, sufficiency_service
        self.quality_repository = quality_repository
        self.executor = executor if executor is not None else ToolExecutor(settings.tool_timeout_seconds,
            settings.tool_max_retries, overrides={'query_faq': (settings.faq_timeout_seconds, 0)})
        self._tasks, self._prepared = set(), {}
        self._closing = False

    async def prepare(self, conversation_id: str, message: str, *, category=None) -> PreparedWorkflowChat:
        """SSE前检查预算和锁；提交新轮输入并初始化安全审计计数。"""
        validate_category(category)
        if self._closing:
            raise ServiceError('service_unavailable', '服务正在关闭，请稍后重试。', 503)
        deadline = asyncio.get_running_loop().time() + self.settings.chat_timeout_seconds
        lease = self.locks.acquire(conversation_id)
        try:
            async with asyncio.timeout_at(deadline):
                await self.repository.require_open(conversation_id)
                turns = _history(await self.repository.load_messages(conversation_id))
                current = HumanMessage(message)
                preview = self.registry_factory(ToolContext(conversation_id, 0, message, category))
                schema = [convert_to_openai_tool(tool) for name, tool in preview.items() if name != 'create_ticket']
                build_tool_messages(agent_decision_system(None), turns, current,
                    self.settings.tool_input_token_budget, tool_schema=schema)
                if estimate_call_input(build_intent_messages(message), []) > self.settings.tool_input_token_budget:
                    raise InputTooLong()
                previous = await self.graph.aget_state(checkpoint_config(conversation_id))
                identifier = await self.repository.append_message(conversation_id, current)
                registry = self.registry_factory(ToolContext(conversation_id, identifier, message, category))
                actual = [convert_to_openai_tool(tool) for name, tool in registry.items() if name != 'create_ticket']
                if actual != schema:
                    raise ServiceError('tool_schema_changed', '工具定义发生变化，请稍后重试。', 500)
                state = new_turn_state(conversation_id=conversation_id, user_message_id=identifier,
                    raw_question=message, category=category, messages=[*(m for turn in turns for m in turn), current])
                runtime = WorkflowRuntime(model_with_output_budget(self.model, self.settings, 512),
                    model_with_output_budget(self.model, self.settings, self.settings.agent_decision_max_output_tokens),
                    model_with_output_budget(self.model, self.settings, self.settings.intent_max_output_tokens),
                    self.repository, self.faq_repository, self.sufficiency_service, self.quality_repository,
                    registry, self.executor, self.settings, deadline)
                prepared = PreparedWorkflowChat(conversation_id, identifier, lease, state, runtime, deadline)
                prepared.audit = safe_fields({key: state[key] for key in ('decision_count', 'tool_call_count', 'usage')})
                self._prepared[id(prepared)] = prepared
                log_lifecycle(prepared, 'prepared', prior_pending=bool(previous.next))
                return prepared
        except BaseException:
            lease.release()
            raise

    async def _produce(self, prepared, queue):
        """同步持久化每步并汇总安全更新；根完成才发布done，每个退出记录唯一终态。"""
        config = checkpoint_config(prepared.conversation_id)
        config['recursion_limit'] = 64
        stream = self.graph.astream(prepared.state, config=config, context=prepared.runtime,
            stream_mode=['custom', 'updates'], subgraphs=True, durability='sync')
        citations_sent = answering_started = False
        outcome, terminal = 'cancelled', {}
        try:
            async with asyncio.timeout_at(prepared.deadline):
                await queue.put(StreamEvent('status', {'phase': 'selecting'}))
                async for namespace, kind, event in stream:
                    if kind == 'updates':
                        for update in event.values():
                            if isinstance(update, dict):
                                prepared.audit.update(safe_fields({key: update[key] for key in
                                    ('decision_count', 'tool_call_count', 'usage') if key in update}))
                        continue
                    if not isinstance(event, dict) or not isinstance(event.get('data'), dict):
                        continue
                    name, data = event.get('event'), event['data']
                    if name == 'status':
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
                if (snapshot.next or final.get('turn_status') != 'completed'
                        or final.get('user_message_id') != str(prepared.user_message_id)
                        or final.get('conversation_id') != prepared.conversation_id or not final.get('final_message_id')):
                    raise ValueError('workflow final snapshot incomplete')
                checkpoint_id = snapshot.config['configurable']['checkpoint_id']
                UUID(checkpoint_id)
                prepared.state = final
                log_lifecycle(prepared, 'checkpoint_complete', checkpoint_id=checkpoint_id,
                    final_message_id=final['final_message_id'])
                options = [{'action': action, 'label': _LABELS[action]}
                    for action in dict.fromkeys(final['suggested_actions']) if action in _LABELS]
                if options:
                    await queue.put(StreamEvent('actions', {'assistant_message_id': final['final_message_id'],
                        'checkpoint_id': checkpoint_id, 'options': options}))
                await queue.put(StreamEvent('done', {'conversation_id': prepared.conversation_id,
                    'message_id': final['final_message_id']}))
                outcome = 'success'
                terminal = {'final_message_id': final['final_message_id'], 'checkpoint_id': checkpoint_id}
        except ServiceError as exc:
            outcome, terminal = ('timeout' if exc.code == 'upstream_timeout' else 'error'), {'code': exc.code}
            await queue.put(StreamEvent('error', {'code': exc.code, 'message': exc.message}))
        except TimeoutError:
            outcome, terminal = 'timeout', {'code': 'upstream_timeout'}
            await queue.put(StreamEvent('error', {'code': 'upstream_timeout', 'message': '本轮处理超时，请稍后重试。'}))
        except Exception:
            outcome, terminal = 'error', {'code': 'upstream_error'}
            await queue.put(StreamEvent('error', {'code': 'upstream_error', 'message': '本次回答未能完成，请稍后重试。'}))
        finally:
            log_terminal(prepared, prepared.cancel_outcome if outcome == 'cancelled' else outcome, **terminal)
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
                if event.event in ('done', 'error'):
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
