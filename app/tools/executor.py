# 受控工具执行器，处理参数校验、超时、有限重试、取消及安全错误结果。
import asyncio
from copy import deepcopy
import json
import logging
import math
from dataclasses import replace
from time import monotonic
from collections.abc import Mapping

from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool, InjectedToolCallId
from pydantic import ValidationError
from sqlalchemy.exc import DBAPIError
import httpx

from app.core.errors import ServiceError
from app.tools.types import ToolCall, ToolOutcome
from app.tools.catalog_types import BoundCatalog, ToolDefinition
from app.tools.authorization import authorize_call, denied
from app.tools.validation import validate_arguments
from app.tools.results import normalize_result
from app.tool_audit.types import ToolAuditRecord


logger = logging.getLogger(__name__)


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
    "upstream_timeout": "模型响应超时，请稍后重试。",
    "upstream_error": "模型服务暂时不可用，请稍后重试。",
    "invalid_structured_output": "模型返回的结构化结果无效，请稍后重试。",
    "input_too_long": "Input exceeds the context budget.",
}


# 生成只含安全业务提示及尝试次数的工具失败结果。
def _error(code: str, attempts: int) -> ToolOutcome:
    return ToolOutcome({"error": {"code": code, "message": _ERROR_MESSAGES[code]}}, "error", attempts)


# 识别可重试的暂时连接故障，排除一般 SQL 和约束错误。
def _temporary_connection_error(exc: Exception) -> bool:
    if isinstance(exc, ExceptionGroup):
        return bool(exc.exceptions) and all(_temporary_connection_error(item) for item in exc.exceptions)
    if isinstance(exc, (ConnectionError, httpx.TransportError)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in (408, 429, 502, 503, 504)
    if isinstance(exc, DBAPIError):
        # 只识别失联类 MySQL 错误，不把任意 SQL/约束错误当作可重试故障。
        code = exc.orig.args[0] if exc.orig.args else None
        return exc.connection_invalidated or code in (2002, 2003, 2006, 2013, 2055)
    return False


def _timeout_error(exc):
    if isinstance(exc, ExceptionGroup):
        return bool(exc.exceptions) and all(_timeout_error(item) for item in exc.exceptions)
    return isinstance(exc, (TimeoutError, httpx.TimeoutException))


class ToolExecutor:
    """每次逻辑调用至多重试一次；取消直接传播，结果只含安全业务数据。"""

    # 校验有限正超时和至多一次重试的配置。
    def __init__(self, timeout_seconds: float = 5, max_retries: int = 1,
                 *, overrides: Mapping[str, tuple[float, int]] | None = None, audit_sink=None):
        if isinstance(timeout_seconds, bool) or not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("Timeout must be finite and positive.")
        if type(max_retries) is not int or max_retries not in (0, 1):
            raise ValueError("At most one retry is allowed.")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.overrides = dict(overrides or {})
        self.audit_sink = audit_sink
        for name, (timeout, retries) in self.overrides.items():
            if (not isinstance(name, str) or not name or type(timeout) not in (int, float)
                    or not math.isfinite(timeout) or timeout <= 0 or type(retries) is not int or retries not in (0, 1)):
                raise ValueError('Invalid tool execution override.')

    # 校验完整工具参数、注入可信调用标识，并在有限重试内执行同一次逻辑调用。
    async def execute(self, call: ToolCall, registry: Mapping[str, BaseTool], *, context=None) -> ToolOutcome:
        started = monotonic()
        outcome = None
        definition = None
        try:
            if isinstance(registry, BoundCatalog) and call.name in registry:
                definition = registry.definition(call.name)
            elif call.name == 'create_ticket' and call.name in registry:
                tool = registry[call.name]
                schema = tool.tool_call_schema
                schema = schema if isinstance(schema, dict) else schema.model_json_schema()
                definition = ToolDefinition('create_ticket', tool.description, schema, operation='write')
            outcome = await self._execute(call, registry, context=context, definition=definition)
            return outcome
        finally:
            if self.audit_sink is not None:
                try:
                    await self._audit(call, context, definition, outcome, started)
                except Exception as exc:
                    logger.warning('stage=tool_audit status=unavailable type=%s', type(exc).__name__)

    async def _audit(self, call, context, definition, outcome, started):
        error = outcome.content.get('error', {}) if outcome is not None else {'code': 'cancelled', 'message': '调用已取消。'}
        code = error.get('code') if isinstance(error, dict) else 'tool_execution_error'
        audit_status = ('success' if outcome is not None and outcome.status == 'success' else
            'timeout' if code == 'tool_timeout' else
            'validation_blocked' if code == 'invalid_arguments' else
            'permission_denied' if code in ('permission_denied', 'unknown_tool') else 'failed')
        conv = getattr(context, 'conversation_id', None)
        conv = int(conv) if isinstance(conv, str) and conv.isdecimal() and 0 < int(conv) < 2**64 else None
        row = ToolAuditRecord(conversation_id=conv,
            tool_call_id=str(call.id)[:64], tool_name=str(call.name)[:64],
            source=definition.source if definition else 'unknown',
            arguments=deepcopy(call.args) if isinstance(call.args, dict) else {'invalid': True},
            result_summary=json.dumps(outcome.content if outcome else {'error': 'cancelled'}, ensure_ascii=False, default=str)[:4000],
            status=audit_status, error_code=code,
            error_message=str(error.get('message') or '')[:512] if isinstance(error, dict) else '工具执行失败。',
            retry_count=max(0, outcome.attempts - 1) if outcome else 0,
            elapsed_ms=max(0, round((monotonic() - started) * 1000)))
        async with asyncio.timeout(.5):
            await self.audit_sink.write(row)

    async def _execute(self, call, registry, *, context, definition):
        tool = registry.get(call.name)
        if tool is None:
            return _error("unknown_tool", 0)
        if not isinstance(call.id, str) or not 1 <= len(call.id) <= 64 or not isinstance(call.args, dict):
            return _error("invalid_arguments", 0)
        if definition is not None:
            if context is None:
                return denied('缺少可信执行上下文。')
            try:
                rejection = authorize_call(definition, call, context)
            except (ValueError, OSError):
                return denied('本地权限规则不可用。')
            if rejection is not None:
                return rejection
            validated = validate_arguments(definition, call.args)
            if isinstance(validated, ToolOutcome):
                return validated
            if definition.source.startswith('mcp:') and definition.order_id_arg:
                if context.order_authorizer is None:
                    return denied('缺少订单归属核验。')
                try:
                    allowed = await context.order_authorizer(call.args.get(definition.order_id_arg, ''))
                except asyncio.CancelledError:
                    raise
                except Exception:
                    return _error('tool_execution_error', 0)
                if not allowed:
                    return denied('该订单不属于当前会话身份。')
        try:
            schema = tool.get_input_schema()
            hidden = {name for name, field in getattr(schema, 'model_fields', {}).items() if any(marker is InjectedToolCallId or isinstance(marker, InjectedToolCallId) for marker in field.metadata)}
            # 模型参数不得包含隐藏字段，调用标识只能取自本次已校验的申请。
            if hidden.intersection(call.args):
                return _error("invalid_arguments", 0)
            # 全参数模型保留 strict/forbid；LangChain 的模型可见子模型不保留所有配置。
            if hasattr(schema, 'model_validate'):
                schema.model_validate({**call.args, **dict.fromkeys(hidden, call.id)})
        except (ValidationError, TypeError, ValueError):
            return _error("invalid_arguments", 0)
        timeout, max_retries = self.overrides.get(call.name, (self.timeout_seconds, self.max_retries))
        if definition is not None:
            timeout = definition.timeout_seconds or timeout
            max_retries = definition.max_retries if definition.max_retries is not None else max_retries
            if definition.operation == 'write' or call.name == 'query_faq':
                max_retries = 0
        for attempt in range(1, max_retries + 2):
            task = asyncio.current_task()
            if task is not None and task.cancelling():
                raise asyncio.CancelledError()
            try:
                # LangChain 注入会修改字典，因此每次执行都深拷贝原始参数。
                full_call = {"type": "tool_call", "name": call.name, "args": deepcopy(call.args), "id": call.id}
                remaining = context.deadline - monotonic() if context is not None and context.deadline is not None else timeout
                if remaining <= 0:
                    return _error('tool_timeout', attempt - 1)
                async with asyncio.timeout(min(timeout, remaining)):
                    result = await tool.ainvoke(full_call)
                # 下层可能吞掉调用方取消并返回；不能将其归一为成功。
                if task is not None and task.cancelling():
                    raise asyncio.CancelledError()
                if definition is not None:
                    return replace(normalize_result(result, definition), attempts=attempt)
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
                if _timeout_error(exc):
                    code, retry = "tool_timeout", True
                elif _temporary_connection_error(exc):
                    code, retry = "tool_connection_error", True
                elif isinstance(exc, ServiceError) and exc.code in _ERROR_MESSAGES:
                    code, retry = exc.code, False
                else:
                    code, retry = "tool_execution_error", False
                # 仅记录固定阶段、白名单错误码和类型，不记录工具参数或异常正文。
                logger.warning('stage=tool code=%s type=%s', code, type(exc).__name__)
                if not retry or attempt > max_retries:
                    return _error(code, attempt)
        raise AssertionError("Unreachable execution state.")
