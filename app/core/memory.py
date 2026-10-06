from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.messages.utils import trim_messages

from app.core.errors import InputTooLong, SessionBusy


def estimate_tokens(messages: list[BaseMessage]) -> int:
    """按 UTF-8 字节数加固定开销保守估算，不代表模型的精确 token 数。

    该估算仅用于纯文本对话，结果非负，各条消息的估算值可以相加。
    """
    return sum(len(message.content.encode("utf-8")) + 12 for message in messages)


def _validate_completed(messages: Sequence[BaseMessage]) -> None:
    if len(messages) % 2 or any(
        not isinstance(message, HumanMessage if index % 2 == 0 else AIMessage)
        for index, message in enumerate(messages)
    ):
        raise ValueError("History must contain complete human/assistant pairs.")


def prepare_messages(
    system: str,
    history: Sequence[BaseMessage],
    message: str,
    budget: int,
    *,
    counter: Callable[[list[BaseMessage]], int] = estimate_tokens,
) -> list[BaseMessage]:
    required = [SystemMessage(content=system), HumanMessage(content=message)]
    if counter(required) > budget:
        raise InputTooLong()
    _validate_completed(history)

    # 显式标注列表类型，避免 trim_messages 将调用方未标注类型的函数
    # 误判为只接收单条消息的 token 计数器。
    def list_counter(messages: list[BaseMessage]) -> int:
        return counter(messages)

    prepared = trim_messages(
        [required[0], *history, required[1]],
        max_tokens=budget,
        token_counter=list_counter,
        strategy="last",
        include_system=True,
        start_on="human",
        end_on="human",
        allow_partial=False,
    )
    if (
        len(prepared) < 2
        or not isinstance(prepared[0], SystemMessage)
        or prepared[0].content != system
        or not isinstance(prepared[-1], HumanMessage)
        or prepared[-1].content != message
        or counter(prepared) > budget
    ):
        raise InputTooLong()
    _validate_completed(prepared[1:-1])
    return prepared


@dataclass(frozen=True)
class SessionLease:
    session_id: str
    history: tuple[BaseMessage, ...]
    _identity: object = field(default_factory=object, repr=False, compare=False)


class SessionStore:
    """在单个事件循环内管理进程内的历史消息与会话占用凭证。

    各项操作不包含 await。快照由消息的防御性副本组成元组，
    调用方修改拿到的 LangChain 消息不会影响已保存的历史。
    """

    def __init__(self):
        self._history: dict[str, tuple[BaseMessage, ...]] = {}
        self._occupied: dict[str, object] = {}

    def acquire(self, session_id: str) -> SessionLease:
        if session_id in self._occupied:
            raise SessionBusy()
        lease = SessionLease(session_id=session_id, history=self.snapshot(session_id))
        self._occupied[session_id] = lease._identity
        return lease

    def commit(self, lease: SessionLease, completed_messages: Sequence[BaseMessage]) -> None:
        if self._occupied.get(lease.session_id) is not lease._identity:
            raise ValueError("Session lease is no longer active in this store.")
        _validate_completed(completed_messages)
        self._history[lease.session_id] = tuple(
            message.model_copy(deep=True) for message in completed_messages
        )

    def release(self, lease: SessionLease) -> None:
        if self._occupied.get(lease.session_id) is lease._identity:
            del self._occupied[lease.session_id]

    def snapshot(self, session_id: str) -> tuple[BaseMessage, ...]:
        return tuple(message.model_copy(deep=True) for message in self._history.get(session_id, ()))
