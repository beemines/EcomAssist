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
    event: Literal["delta", "done", "error"]
    data: dict[str, str]


@dataclass
class PreparedChat:
    lease: SessionLease
    messages: list[BaseMessage]
    pending_completed: list[BaseMessage] = field(default_factory=list)
    upstream: AsyncIterator[Any] | None = field(default=None, repr=False)


class ChatService:
    def __init__(self, model: Any, memory: SessionStore, input_budget: int):
        self.model = model
        self.memory = memory
        self.input_budget = input_budget

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

    async def stream(self, prepared: PreparedChat) -> AsyncIterator[StreamEvent]:
        parts = []
        truncated = False
        try:
            prepared.upstream = self.model.astream(prepared.messages)
            async for chunk in prepared.upstream:
                if chunk.response_metadata.get("finish_reason") == "length":
                    truncated = True
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
        if truncated:
            yield StreamEvent("error", {"code": "upstream_error", "message": "模型回复被截断，请检查输出上限。"})
        elif not answer.strip():
            yield StreamEvent("error", {"code": "upstream_error", "message": "模型未返回有效回复，请稍后重试。"})
        else:
            prepared.pending_completed = [*prepared.messages[1:], AIMessage(content=answer)]
            yield StreamEvent("done", {"session_id": prepared.lease.session_id})

    def commit(self, prepared: PreparedChat) -> None:
        self.memory.commit(prepared.lease, prepared.pending_completed)

    def release(self, prepared: PreparedChat) -> None:
        self.memory.release(prepared.lease)
