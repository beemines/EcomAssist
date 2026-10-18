# 工具调用数据契约，区分可信请求上下文、模型申请和执行结果。
from dataclasses import dataclass
from collections.abc import Awaitable, Callable
from typing import Literal


# 可信请求上下文由服务构造，闭包绑定后供业务工具使用。
@dataclass(frozen=True)
class ToolContext:
    conversation_id: str
    user_message_id: int
    user_question: str
    category: str | None = None


# 模型选择经校验后形成的单次工具申请。
@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    args: dict


# 工具执行后的安全业务数据、成功状态和实际尝试次数。
@dataclass(frozen=True)
class ToolOutcome:
    content: dict
    status: Literal["success", "error"]
    attempts: int


@dataclass(frozen=True)
class ConfirmationGrant:
    source: Literal['chat_preview', 'legacy_form']
    conversation_id: str
    user_message_id: int
    tool_call_id: str
    arguments_fingerprint: str


@dataclass(frozen=True)
class ExecutionContext:
    conversation_id: str
    user_message_id: int
    intent: str
    raw_question: str
    deadline: float | None = None
    ticket_requested: bool = False
    grant: ConfirmationGrant | None = None
    policy: object | None = None
    order_authorizer: Callable[[str], Awaitable[bool]] | None = None
