from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ToolContext:
    conversation_id: str
    user_message_id: int
    user_question: str


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    args: dict


@dataclass(frozen=True)
class ToolOutcome:
    content: dict
    status: Literal["success", "error"]
    attempts: int
