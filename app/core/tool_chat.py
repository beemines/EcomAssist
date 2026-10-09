# 单轮工具聊天服务：模型选工具、执行并回灌结果，最后流式输出回答。
import asyncio
import json
from collections.abc import AsyncIterator, Callable, Mapping
from dataclasses import asdict, dataclass, field
from typing import Any

import anyio
import httpx
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool
from openai import APITimeoutError

from app.config import Settings
from app.core.chat import StreamEvent
from app.core.conversation_locks import ConversationLocks, Lease
from app.core.errors import ServiceError
from app.core.prompts import build_grounded_answer_system_prompt, build_tool_chat_system_prompt
from app.core.evidence import build_evidence
from app.core.sufficiency import SufficiencyService
from app.core.answer_validation import REFUSAL_TEXT, validate_answer
from app.quality.repository import QualityRepository
from app.knowledge.types import validate_text
from app.core.tool_history import build_tool_messages, completed_turns
from app.repositories.conversations import ConversationRepository
from app.repositories.records import record_from_message
from app.tools.executor import ToolExecutor
from app.tools.types import ToolCall, ToolContext


# 将当前工具注册表转换为模型可见的 OpenAI 工具 Schema。
def _schema(registry: Mapping[str, BaseTool]) -> list[dict]:
    return [convert_to_openai_tool(tool) for tool in registry.values()]


# 为工具选择或最终回复违反协议的情况构造统一上游错误。
def _protocol_error(message: str) -> ServiceError:
    return ServiceError("upstream_error", message, 502)


@dataclass
class PreparedToolChat:
    conversation_id: str
    lease: Lease
    user_message_id: int
    messages: list[BaseMessage]
    registry: Mapping[str, BaseTool] = field(repr=False)
    turns: list[list[BaseMessage]] = field(repr=False)
    current: HumanMessage = field(repr=False)
    deadline: float = field(repr=False)
    upstream: AsyncIterator[Any] | None = field(default=None, repr=False)


class ToolChatService:
    """一次选择、至多一次逻辑工具调用，再以原模型真实流式收敛。"""

    # 保存工具聊天依赖，并按配置建立具有超时和有限重试的执行器。
    def __init__(self, model: Any, repository: ConversationRepository,
                 registry_factory: Callable[[ToolContext], Mapping[str, BaseTool]],
                 locks: ConversationLocks, settings: Settings, *, executor: ToolExecutor | None = None,
                 sufficiency_service: SufficiencyService | None = None,
                 quality_repository: QualityRepository | None = None):
        self.model = model
        self.repository = repository
        self.registry_factory = registry_factory
        self.locks = locks
        self.settings = settings
        self.executor = executor if executor is not None else ToolExecutor(settings.tool_timeout_seconds, settings.tool_max_retries,
            overrides={'query_faq': (settings.faq_timeout_seconds, 0)})
        self.sufficiency_service = sufficiency_service if sufficiency_service is not None else SufficiencyService(
            model, input_budget=settings.tool_input_token_budget, timeout=settings.sufficiency_timeout_seconds,
            minimum_rerank_score=settings.rerank_min_score)
        self.quality_repository = quality_repository
        if self.quality_repository is None and getattr(repository, 'database', None) is not None:
            self.quality_repository = QualityRepository(repository.database)

    # 占用会话、校验完整历史和必需输入预算，再保存用户消息并绑定工具上下文。
    async def prepare(self, conversation_id: str, message: str, *, category: str | None = None) -> PreparedToolChat:
        validate_text('category', category, 255, nullable=True)
        deadline = asyncio.get_running_loop().time() + self.settings.chat_timeout_seconds
        lease = self.locks.acquire(conversation_id)
        try:
            async with asyncio.timeout_at(deadline):
                await self.repository.require_open(conversation_id)
                turns = completed_turns(await self.repository.load_messages(conversation_id))
                current = HumanMessage(message)
                system = SystemMessage(build_tool_chat_system_prompt())
                # 0 仅用于不可执行的 Schema 预览，必需输入预算先于任何消息入库。
                preview = _schema(self.registry_factory(ToolContext(conversation_id, 0, message, category)))
                messages = build_tool_messages(system, turns, current, self.settings.tool_input_token_budget, tool_schema=preview)
                user_message_id = await self.repository.append_message(conversation_id, current)
                registry = self.registry_factory(ToolContext(conversation_id, user_message_id, message, category))
                if _schema(registry) != preview:
                    raise ServiceError("tool_schema_changed", "工具定义发生变化，请稍后重试。", 500)
                return PreparedToolChat(conversation_id, lease, user_message_id, messages, registry, turns, current, deadline)
        except BaseException:
            lease.release()
            raise

    # 检查模型正常结束且至多申请一个已注册工具，返回合法调用或空选择。
    def _validate_selection(self, selected: Any, registry: Mapping[str, BaseTool]) -> ToolCall | None:
        if not isinstance(selected, AIMessage) or selected.invalid_tool_calls or len(selected.tool_calls) > 1:
            raise _protocol_error("模型返回了无效或多个工具申请。")
        # 不允许 SDK 无法解析的原始申请被误当成无工具回复。
        raw = selected.additional_kwargs.get("tool_calls")
        if raw is not None and (not isinstance(raw, list) or len(raw) != len(selected.tool_calls)):
            raise _protocol_error("模型返回了无法解析的工具申请。")
        reason = selected.response_metadata.get("finish_reason")
        allowed = {"tool_calls", "stop"} if selected.tool_calls else {"stop"}
        if reason not in allowed:
            raise _protocol_error("模型选择未正常完成，请稍后重试。")
        if not selected.tool_calls:
            return None
        call = selected.tool_calls[0]
        if (not isinstance(call, dict) or not isinstance(call.get("id"), str)
                or not call["id"].strip() or len(call["id"]) > 64
                or not isinstance(call.get("name"), str) or call["name"] not in registry
                or not isinstance(call.get("args"), dict)):
            raise _protocol_error("模型返回了无效工具申请。")
        # 同时验证有限 JSON 参数及数据库审计的文本界限。
        try:
            record_from_message(selected)
        except (ValueError, TypeError, RecursionError):
            raise _protocol_error("模型返回了无效工具申请。") from None
        return ToolCall(call["id"], call["name"], call["args"])

    # 进行一次工具选择、至多一次逻辑调用，流式生成并保存正常完成的回答。
    async def stream(self, prepared: PreparedToolChat) -> AsyncIterator[StreamEvent]:
        try:
            async with asyncio.timeout_at(prepared.deadline):
                yield StreamEvent("status", {"phase": "selecting"})
                # 选择阶段只调用一次模型；最终回答阶段不会再绑定工具。
                bound = self.model.bind_tools(list(prepared.registry.values()), tool_choice="auto", parallel_tool_calls=False)
                selected = await bound.ainvoke(prepared.messages)
                call = self._validate_selection(selected, prepared.registry)
                pending: list[BaseMessage] = []
                knowledge_path = call is None or call.name == 'query_faq'
                evidence = None
                decision = None
                if call is not None:
                    await self.repository.append_message(prepared.conversation_id, selected)
                    # 执行前也检查申请参数预算；占位结果只用于保持匹配组合结构。
                    build_tool_messages(SystemMessage(build_tool_chat_system_prompt()), prepared.turns,
                        prepared.current, self.settings.tool_input_token_budget, tool_schema=_schema(prepared.registry),
                        current_tool_messages=[selected, ToolMessage("", tool_call_id=call.id)])
                    identity = {"tool_name": call.name, "tool_call_id": call.id}
                    yield StreamEvent("status", {"phase": "tool_running", **identity})
                    outcome = await self.executor.execute(call, prepared.registry)
                    if call.name == 'query_faq':
                        if outcome.status != 'success':
                            error = outcome.content.get('error', {})
                            raise ServiceError(error.get('code', 'tool_execution_error'),
                                               error.get('message', '知识检索未能完成，请稍后重试。'), 502)
                        evidence = build_evidence(system=SystemMessage(build_grounded_answer_system_prompt()),
                            turns=prepared.turns, current=prepared.current, request=selected, payload=outcome.content,
                            budget=self.settings.tool_input_token_budget)
                        yield StreamEvent('status', {'phase': 'checking'})
                        decision = await self.sufficiency_service.check(prepared.current.content, evidence)
                        # 只持久化本次实际选中证据；消息正文与最终 Prompt 精确一致。
                        outcome_content = evidence.payload
                    else:
                        outcome_content = outcome.content
                    result = ToolMessage(json.dumps(outcome_content, ensure_ascii=False, separators=(",", ":"), allow_nan=False),
                                         tool_call_id=call.id, name=call.name, status=outcome.status)
                    if evidence is not None:
                        # 直接使用预算已核验的实际工具消息，连元数据也不二次改写。
                        result = evidence.messages[-1]
                    await self.repository.append_message(prepared.conversation_id, result)
                    yield StreamEvent("status", {"phase": "tool_completed", **identity, "status": outcome.status})
                    pending = [selected, result]
                # 最终请求不绑定工具；申请和结果作为不可裁断的完整组合重新核对。
                if knowledge_path:
                    if evidence is None:
                        evidence = build_evidence(system=SystemMessage(build_grounded_answer_system_prompt()),
                            turns=prepared.turns, current=prepared.current, request=None, payload=None,
                            budget=self.settings.tool_input_token_budget)
                        yield StreamEvent('status', {'phase': 'checking'})
                        decision = await self.sufficiency_service.check(prepared.current.content, evidence)
                    prepared.messages = evidence.messages
                    yield StreamEvent('citations', {'citations': [asdict(item) for item in evidence.citations]})
                    if not decision.useful:
                        yield StreamEvent('status', {'phase': 'answering'})
                        yield StreamEvent('delta', {'delta': REFUSAL_TEXT})
                        task = asyncio.current_task()
                        if task is not None and task.cancelling():
                            raise asyncio.CancelledError()
                        if self.quality_repository is None:
                            raise ServiceError('quality_unavailable', '质量记录暂时不可用，请稍后重试。', 503)
                        message_id = await self.quality_repository.commit_refusal(prepared.conversation_id, AIMessage(REFUSAL_TEXT),
                            raw_question=prepared.current.content, source=decision.source, reason=decision.reason)
                        yield StreamEvent('done', {'conversation_id': prepared.conversation_id, 'message_id': str(message_id)})
                        return
                else:
                    prepared.messages = build_tool_messages(SystemMessage(build_tool_chat_system_prompt()), prepared.turns,
                        prepared.current, self.settings.tool_input_token_budget, tool_schema=[], current_tool_messages=pending)
                yield StreamEvent("status", {"phase": "answering"})
                parts: list[str] = []
                size = 0
                utf8_size = 0
                reasons: set[str] = set()
                prepared.upstream = self.model.astream(prepared.messages)
                async for chunk in prepared.upstream:
                    if (chunk.tool_calls or chunk.invalid_tool_calls or getattr(chunk, "tool_call_chunks", None)
                            or chunk.additional_kwargs.get("tool_calls")):
                        raise _protocol_error("最终回复再次申请工具，无法完成本次回答。")
                    reason = chunk.response_metadata.get("finish_reason")
                    if reason is not None:
                        reasons.add(reason)
                    text = chunk.text
                    if text:
                        size += len(text)
                        utf8_size += len(text.encode('utf-8'))
                        if size > 20000 or utf8_size > 65535:
                            raise _protocol_error("模型回复超出可保存长度。")
                        parts.append(text)
                        yield StreamEvent("delta", {"delta": text})
                answer = "".join(parts)
                if reasons != {"stop"} or not answer.strip():
                    raise _protocol_error("模型回复未正常完成，请稍后重试。")
                if knowledge_path:
                    validate_answer(answer, reasons, evidence, decision)
                # 下层吞掉取消时仍不得把断开的流程提交为成功回答。
                task = asyncio.current_task()
                if task is not None and task.cancelling():
                    raise asyncio.CancelledError()
                # 只有正常结束且未取消的完整回答才入库，提交成功后才产生 done。
                message_id = await self.repository.append_message(prepared.conversation_id, AIMessage(answer))
                yield StreamEvent("done", {"conversation_id": prepared.conversation_id, 'message_id': str(message_id)})
        # 取消异常向外传播，由响应层关闭生成器并归还会话凭证。
        except ServiceError as exc:
            yield StreamEvent("error", {"code": exc.code, "message": exc.message})
        except (TimeoutError, httpx.TimeoutException, APITimeoutError):
            yield StreamEvent("error", {"code": "upstream_timeout", "message": "模型响应超时，请稍后重试。"})
        except Exception:
            yield StreamEvent("error", {"code": "upstream_error", "message": "本次回答未能完成，请稍后重试。"})
        finally:
            # 校验失败可能提前退出 async for，主动关闭当前迭代器以归还上游连接。
            upstream, prepared.upstream = prepared.upstream, None
            close = getattr(upstream, "aclose", None)
            if close is not None:
                with anyio.move_on_after(5, shield=True):
                    try:
                        await close()
                    except Exception:
                        pass

    # 归还本次工具聊天持有的会话占用凭证。
    def release(self, prepared: PreparedToolChat) -> None:
        prepared.lease.release()
