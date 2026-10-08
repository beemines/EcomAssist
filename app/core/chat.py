# 纯对话服务：准备预算内的历史消息，流式生成并保存正常结束的回答。
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any, Literal

import httpx
from langchain_core.messages import AIMessage, BaseMessage
from openai import APITimeoutError

from app.core.memory import SessionLease, SessionStore, prepare_messages
from app.core.prompts import build_chat_system_prompt


@dataclass
class StreamEvent:
    event: Literal["status", "delta", "done", "error"]
    data: dict[str, Any]


@dataclass
class PreparedChat:
    lease: SessionLease
    messages: list[BaseMessage]
    pending_completed: list[BaseMessage] = field(default_factory=list)
    upstream: AsyncIterator[Any] | None = field(default=None, repr=False)


class ChatService:
    # 保存纯文本聊天所需的模型、内存会话仓储和输入预算。
    def __init__(self, model: Any, memory: SessionStore, input_budget: int):
        self.model = model
        self.memory = memory
        self.input_budget = input_budget

    # 取得会话凭证并裁剪历史；预处理失败时立即归还凭证。
    def prepare(self, session_id: str, message: str) -> PreparedChat:
        lease = self.memory.acquire(session_id)
        try:
            messages = prepare_messages(
                build_chat_system_prompt(), lease.history, message, self.input_budget,
            )
            return PreparedChat(lease, messages)
        except BaseException:
            self.memory.release(lease)
            raise

    # 流式输出文本，仅在正常且非空的回复结束后准备可提交的历史。
    async def stream(self, prepared: PreparedChat) -> AsyncIterator[StreamEvent]:
        parts = []
        finish_reasons = set()
        try:
            prepared.upstream = self.model.astream(prepared.messages)
            async for chunk in prepared.upstream:
                reason = chunk.response_metadata.get("finish_reason")
                if reason is not None:
                    # 空块或合成的末尾块不能抹除已确认的结束原因；
                    # 后续的 stop 也不能抹除先前出现的异常结束原因。
                    finish_reasons.add(reason)
                text = chunk.text
                if text:
                    parts.append(text)
                    yield StreamEvent("delta", {"delta": text})
        except (TimeoutError, httpx.TimeoutException, APITimeoutError):
            yield StreamEvent("error", {"code": "upstream_timeout", "message": "模型响应超时，请稍后重试。"})
            return
        except Exception:
            yield StreamEvent("error", {"code": "upstream_error", "message": "模型服务暂时不可用，请稍后重试。"})
            return

        answer = "".join(parts)
        if "length" in finish_reasons:
            yield StreamEvent("error", {"code": "upstream_error", "message": "模型回复被截断，请检查输出上限。"})
        elif not answer.strip():
            yield StreamEvent("error", {"code": "upstream_error", "message": "模型未返回有效回复，请稍后重试。"})
        elif finish_reasons != {"stop"}:
            yield StreamEvent("error", {"code": "upstream_error", "message": "模型回复未正常完成，请稍后重试。"})
        else:
            # 这里只准备完整历史，实际保存由调用方显式 commit 完成。
            prepared.pending_completed = [*prepared.messages[1:], AIMessage(content=answer)]
            yield StreamEvent("done", {"session_id": prepared.lease.session_id})

    # 将已准备的完整对话历史提交到当前会话的内存仓储。
    def commit(self, prepared: PreparedChat) -> None:
        self.memory.commit(prepared.lease, prepared.pending_completed)

    # 归还此次聊天持有的会话占用凭证。
    def release(self, prepared: PreparedChat) -> None:
        self.memory.release(prepared.lease)
