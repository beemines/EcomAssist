import asyncio
import json
from collections.abc import AsyncIterator, Callable, Mapping
from dataclasses import dataclass, field
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
from app.core.prompts import build_tool_chat_system_prompt
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
    upstream: AsyncIterator[Any] | None = field(default=None, repr=False)


class ToolChatService:
    """一次选择、至多一次逻辑工具调用，再以原模型真实流式收敛。"""

    # 保存工具聊天依赖，并按配置建立具有超时和有限重试的执行器。
    def __init__(self, model: Any, repository: ConversationRepository,
                 registry_factory: Callable[[ToolContext], Mapping[str, BaseTool]],
                 locks: ConversationLocks, settings: Settings, *, executor: ToolExecutor | None = None):
        self.model = model
        self.repository = repository
        self.registry_factory = registry_factory
        self.locks = locks
        self.settings = settings
        self.executor = executor if executor is not None else ToolExecutor(settings.tool_timeout_seconds, settings.tool_max_retries)

    # 占用会话、校验完整历史和必需输入预算，再保存用户消息并绑定工具上下文。
    async def prepare(self, conversation_id: str, message: str) -> PreparedToolChat:
        lease = self.locks.acquire(conversation_id)
        try:
            await self.repository.require_open(conversation_id)
            turns = completed_turns(await self.repository.load_messages(conversation_id))
            current = HumanMessage(message)
            system = SystemMessage(build_tool_chat_system_prompt())
            # 0 仅用于不可执行的 Schema 预览，必需输入预算先于任何消息入库。
            preview = _schema(self.registry_factory(ToolContext(conversation_id, 0, message)))
            messages = build_tool_messages(system, turns, current, self.settings.tool_input_token_budget, tool_schema=preview)
            user_message_id = await self.repository.append_message(conversation_id, current)
            registry = self.registry_factory(ToolContext(conversation_id, user_message_id, message))
            if _schema(registry) != preview:
                raise ServiceError("tool_schema_changed", "工具定义发生变化，请稍后重试。", 500)
            return PreparedToolChat(conversation_id, lease, user_message_id, messages, registry, turns, current)
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
            yield StreamEvent("status", {"phase": "selecting"})
            # 选择阶段只调用一次模型；最终回答阶段不会再绑定工具。
            bound = self.model.bind_tools(list(prepared.registry.values()), tool_choice="auto", parallel_tool_calls=False)
            selected = await bound.ainvoke(prepared.messages)
            call = self._validate_selection(selected, prepared.registry)
            pending: list[BaseMessage] = []
            if call is not None:
                await self.repository.append_message(prepared.conversation_id, selected)
                # 执行前也检查申请参数预算；占位结果只用于保持匹配组合结构。
                build_tool_messages(SystemMessage(build_tool_chat_system_prompt()), prepared.turns,
                    prepared.current, self.settings.tool_input_token_budget, tool_schema=_schema(prepared.registry),
                    current_tool_messages=[selected, ToolMessage("", tool_call_id=call.id)])
                identity = {"tool_name": call.name, "tool_call_id": call.id}
                yield StreamEvent("status", {"phase": "tool_running", **identity})
                outcome = await self.executor.execute(call, prepared.registry)
                result = ToolMessage(json.dumps(outcome.content, ensure_ascii=False, separators=(",", ":"), allow_nan=False),
                                     tool_call_id=call.id, name=call.name, status=outcome.status)
                await self.repository.append_message(prepared.conversation_id, result)
                yield StreamEvent("status", {"phase": "tool_completed", **identity, "status": outcome.status})
                pending = [selected, result]
            # 最终请求不绑定工具；申请和结果作为不可裁断的完整组合重新核对。
            prepared.messages = build_tool_messages(SystemMessage(build_tool_chat_system_prompt()), prepared.turns,
                prepared.current, self.settings.tool_input_token_budget, tool_schema=[], current_tool_messages=pending)
            yield StreamEvent("status", {"phase": "answering"})
            parts: list[str] = []
            size = 0
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
                    if size > 20000:
                        raise _protocol_error("模型回复超出可保存长度。")
                    parts.append(text)
                    yield StreamEvent("delta", {"delta": text})
            answer = "".join(parts)
            if reasons != {"stop"} or not answer.strip():
                raise _protocol_error("模型回复未正常完成，请稍后重试。")
            # 下层吞掉取消时仍不得把断开的流程提交为成功回答。
            task = asyncio.current_task()
            if task is not None and task.cancelling():
                raise asyncio.CancelledError()
            # 只有正常结束且未取消的完整回答才入库，提交成功后才产生 done。
            await self.repository.append_message(prepared.conversation_id, AIMessage(answer))
            yield StreamEvent("done", {"conversation_id": prepared.conversation_id})
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
