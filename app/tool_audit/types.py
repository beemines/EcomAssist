from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ToolAuditRecord:
    conversation_id: int | None
    tool_call_id: str
    tool_name: str
    source: str
    arguments: dict
    result_summary: str
    status: Literal['success', 'failed', 'timeout', 'validation_blocked', 'permission_denied']
    retry_count: int
    elapsed_ms: int
    error_code: str | None = None
    error_message: str | None = None
