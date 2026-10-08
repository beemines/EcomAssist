from dataclasses import dataclass
from typing import Literal


# 可信请求上下文由服务构造，闭包绑定后供业务工具使用。
@dataclass(frozen=True)
class ToolContext:
    conversation_id: str
    user_message_id: int
    user_question: str


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
