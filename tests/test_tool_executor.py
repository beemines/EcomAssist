import asyncio
import json
from typing import Annotated

import pytest
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from pydantic import BaseModel, ConfigDict

from app.tools.executor import ToolExecutor
from app.tools.types import ToolCall


class Args(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    value: str


@pytest.mark.asyncio
async def test_timeout_retries_once():
    calls = 0

    @tool(args_schema=Args)
    async def controlled(value: str) -> dict:
        """受控超时工具。"""
        nonlocal calls
        calls += 1
        if calls == 1:
            raise TimeoutError("private timeout detail")
        return {"value": value}

    outcome = await ToolExecutor().execute(ToolCall("call", "controlled", {"value": "ok"}), {"controlled": controlled})
    assert outcome.attempts == 2
    assert outcome.status == "success" and outcome.content == {"value": "ok"}


@pytest.mark.asyncio
async def test_invalid_args_do_not_execute():
    calls = 0

    @tool(args_schema=Args)
    async def controlled(value: str) -> dict:
        """记录执行次数。"""
        nonlocal calls
        calls += 1
        return {"value": value}

    outcome = await ToolExecutor().execute(ToolCall("call", "controlled", {"value": 123}), {"controlled": controlled})
    assert calls == 0
    assert outcome.status == "error" and outcome.attempts == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("failure,code,attempts", [(TimeoutError, "tool_timeout", 2), (ConnectionError, "tool_connection_error", 2), (RuntimeError, "tool_execution_error", 1)])
async def test_bounded_failures_have_safe_error_content(failure, code, attempts):
    calls = 0

    @tool(args_schema=Args)
    async def controlled(value: str) -> dict:
        """抛出安全输出不可包含的细节。"""
        nonlocal calls
        calls += 1
        raise failure("SELECT secret FROM credentials")

    outcome = await ToolExecutor().execute(ToolCall("call", "controlled", {"value": "ok"}), {"controlled": controlled})
    assert calls == attempts and outcome.attempts == attempts
    assert outcome.status == "error" and outcome.content["error"]["code"] == code
    assert "secret" not in json.dumps(outcome.content)


@pytest.mark.asyncio
async def test_cancellation_propagates_without_retry():
    calls = 0
    entered = asyncio.Event()

    @tool(args_schema=Args)
    async def controlled(value: str) -> dict:
        """等待调用方取消。"""
        nonlocal calls
        calls += 1
        entered.set()
        await asyncio.Event().wait()
        return {}

    task = asyncio.create_task(ToolExecutor().execute(ToolCall("call", "controlled", {"value": "ok"}), {"controlled": controlled}))
    await entered.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert calls == 1


@pytest.mark.asyncio
async def test_actual_deadline_bounds_execution():
    calls = 0

    @tool(args_schema=Args)
    async def controlled(value: str) -> dict:
        """超过应用超时。"""
        nonlocal calls
        calls += 1
        await asyncio.Event().wait()
        return {}

    outcome = await ToolExecutor(timeout_seconds=0.01).execute(ToolCall("call", "controlled", {"value": "ok"}), {"controlled": controlled})
    assert calls == 2 and outcome.attempts == 2 and outcome.status == "error"


@pytest.mark.asyncio
async def test_injected_parameter_does_not_mutate_retry_input():
    class InjectedArgs(Args):
        tool_call_id: Annotated[str, InjectedToolCallId]

    calls = 0

    @tool(args_schema=InjectedArgs)
    async def controlled(value: str, tool_call_id: Annotated[str, InjectedToolCallId]) -> ToolMessage:
        """接收隐藏 ID 并返回业务错误消息。"""
        nonlocal calls
        calls += 1
        if calls == 1:
            raise TimeoutError()
        assert tool_call_id == "actual-id"
        return ToolMessage(json.dumps({"error": {"code": "rejected", "message": "业务拒绝"}}), tool_call_id=tool_call_id, status="error")

    args = {"value": "ok"}
    outcome = await ToolExecutor().execute(ToolCall("actual-id", "controlled", args), {"controlled": controlled})
    assert args == {"value": "ok"}
    assert outcome.attempts == 2 and outcome.status == "error"
    assert outcome.content["error"]["code"] == "rejected"


@pytest.mark.asyncio
async def test_unknown_tool_is_safe_without_attempt():
    outcome = await ToolExecutor().execute(ToolCall("call", "unknown", {}), {})
    assert outcome.status == "error" and outcome.attempts == 0
    assert outcome.content["error"]["code"] == "unknown_tool"


@pytest.mark.parametrize("kwargs", [{"max_retries": 2}, {"max_retries": -1}, {"timeout_seconds": 0}])
def test_configuration_cannot_remove_execution_bounds(kwargs):
    with pytest.raises(ValueError):
        ToolExecutor(**kwargs)


@pytest.mark.asyncio
@pytest.mark.parametrize("max_retries,cancel_attempt,return_after_cancel", [
    (1, 1, False), (0, 1, False), (1, 2, False),
    (1, 1, True), (0, 1, True), (1, 2, True),
])
async def test_pending_cancellation_cannot_be_normalized_as_outcome(max_retries, cancel_attempt, return_after_cancel):
    calls = 0
    entered = asyncio.Event()

    @tool(args_schema=Args)
    async def controlled(value: str) -> dict:
        """模拟下层将取消误转换为超时或正常返回。"""
        nonlocal calls
        calls += 1
        if calls < cancel_attempt:
            raise TimeoutError()
        entered.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            if return_after_cancel:
                return {"value": value}
            raise TimeoutError() from None
        return {}

    task = asyncio.create_task(ToolExecutor(max_retries=max_retries).execute(ToolCall("call", "controlled", {"value": "ok"}), {"controlled": controlled}))
    await entered.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert calls == cancel_attempt
    assert task.cancelled()


@pytest.mark.asyncio
@pytest.mark.parametrize("db_code,attempts,status", [(2006, 2, "success"), (2013, 2, "success"), (1064, 1, "error")])
async def test_mysql_connection_errors_retry_but_sql_errors_do_not(db_code, attempts, status):
    from pymysql.err import OperationalError as MySQLOperationalError
    from sqlalchemy.exc import OperationalError

    calls = 0

    @tool(args_schema=Args)
    async def controlled(value: str) -> dict:
        """模拟 MySQL 驱动失联与普通 SQL 错误。"""
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OperationalError("controlled statement", {}, MySQLOperationalError(db_code, "private detail"))
        return {"value": value}

    outcome = await ToolExecutor().execute(ToolCall("call", "controlled", {"value": "ok"}), {"controlled": controlled})
    assert calls == attempts and outcome.attempts == attempts and outcome.status == status
    assert "private detail" not in json.dumps(outcome.content)


@pytest.mark.asyncio
async def test_retries_can_be_disabled():
    calls = 0

    @tool(args_schema=Args)
    async def controlled(value: str) -> dict:
        """总是超时。"""
        nonlocal calls
        calls += 1
        raise TimeoutError()

    outcome = await ToolExecutor(max_retries=0).execute(ToolCall("call", "controlled", {"value": "ok"}), {"controlled": controlled})
    assert calls == 1 and outcome.attempts == 1 and outcome.status == "error"
