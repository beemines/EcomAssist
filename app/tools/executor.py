import asyncio
from copy import deepcopy
import json
import math
from collections.abc import Mapping

from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool, InjectedToolCallId
from pydantic import ValidationError
from sqlalchemy.exc import DBAPIError

from app.core.errors import ServiceError
from app.tools.types import ToolCall, ToolOutcome


_ERROR_MESSAGES = {
    "unknown_tool": "未注册该工具。",
    "invalid_arguments": "工具参数不符合要求。",
    "invalid_conversation_id": "会话身份无效。",
    "conversation_not_found": "会话不存在。",
    "conversation_ended": "会话已经结束。",
    "invalid_user_message": "用户消息不属于当前会话。",
    "ticket_conflict": "工单编号与已有业务内容冲突。",
    "tool_timeout": "工具执行超时，请稍后重试。",
    "tool_connection_error": "工具连接暂时不可用，请稍后重试。",
    "tool_execution_error": "工具执行失败。",
}


# 生成只含安全业务提示及尝试次数的工具失败结果。
def _error(code: str, attempts: int) -> ToolOutcome:
    return ToolOutcome({"error": {"code": code, "message": _ERROR_MESSAGES[code]}}, "error", attempts)


# 识别可重试的暂时连接故障，排除一般 SQL 和约束错误。
def _temporary_connection_error(exc: Exception) -> bool:
    if isinstance(exc, ConnectionError):
        return True
    if isinstance(exc, DBAPIError):
        # 只识别失联类 MySQL 错误，不把任意 SQL/约束错误当作可重试故障。
        code = exc.orig.args[0] if exc.orig.args else None
        return exc.connection_invalidated or code in (2002, 2003, 2006, 2013, 2055)
    return False


class ToolExecutor:
    """每次逻辑调用至多重试一次；取消直接传播，结果只含安全业务数据。"""

    # 校验有限正超时和至多一次重试的配置。
    def __init__(self, timeout_seconds: float = 5, max_retries: int = 1):
        if isinstance(timeout_seconds, bool) or not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("Timeout must be finite and positive.")
        if type(max_retries) is not int or max_retries not in (0, 1):
            raise ValueError("At most one retry is allowed.")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    # 校验完整工具参数、注入可信调用标识，并在有限重试内执行同一次逻辑调用。
    async def execute(self, call: ToolCall, registry: Mapping[str, BaseTool]) -> ToolOutcome:
        tool = registry.get(call.name)
        if tool is None:
            return _error("unknown_tool", 0)
        if not isinstance(call.id, str) or not 1 <= len(call.id) <= 64 or not isinstance(call.args, dict):
            return _error("invalid_arguments", 0)
        try:
            schema = tool.get_input_schema()
            hidden = {name for name, field in schema.model_fields.items() if any(marker is InjectedToolCallId or isinstance(marker, InjectedToolCallId) for marker in field.metadata)}
            # 模型参数不得包含隐藏字段，调用标识只能取自本次已校验的申请。
            if hidden.intersection(call.args):
                return _error("invalid_arguments", 0)
            # 全参数模型保留 strict/forbid；LangChain 的模型可见子模型不保留所有配置。
            schema.model_validate({**call.args, **dict.fromkeys(hidden, call.id)})
        except (ValidationError, TypeError, ValueError):
            return _error("invalid_arguments", 0)
        for attempt in range(1, self.max_retries + 2):
            task = asyncio.current_task()
            if task is not None and task.cancelling():
                raise asyncio.CancelledError()
            try:
                # LangChain 注入会修改字典，因此每次执行都深拷贝原始参数。
                full_call = {"type": "tool_call", "name": call.name, "args": deepcopy(call.args), "id": call.id}
                async with asyncio.timeout(self.timeout_seconds):
                    result = await tool.ainvoke(full_call)
                # 下层可能吞掉调用方取消并返回；不能将其归一为成功。
                if task is not None and task.cancelling():
                    raise asyncio.CancelledError()
                if not isinstance(result, ToolMessage) or not isinstance(result.content, str):
                    return _error("tool_execution_error", attempt)
                content = json.loads(result.content)
                if not isinstance(content, dict):
                    return _error("tool_execution_error", attempt)
                status = "error" if result.status == "error" or "error" in content else "success"
                return ToolOutcome(content, status, attempt)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                # 最后一次尝试也必须传播取消，不能落入终止错误结果。
                if task is not None and task.cancelling():
                    raise asyncio.CancelledError() from None
                # 仅超时或暂时失联可重试；参数、业务冲突和其他执行错误直接返回。
                if isinstance(exc, TimeoutError):
                    code, retry = "tool_timeout", True
                elif _temporary_connection_error(exc):
                    code, retry = "tool_connection_error", True
                elif isinstance(exc, ServiceError) and exc.code in _ERROR_MESSAGES:
                    code, retry = exc.code, False
                else:
                    code, retry = "tool_execution_error", False
                if not retry or attempt > self.max_retries:
                    return _error(code, attempt)
        raise AssertionError("Unreachable execution state.")
