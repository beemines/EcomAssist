import asyncio
import json
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage, AIMessageChunk, ToolMessage

from app.core.errors import InputTooLong, SessionBusy
from app.core.tool_history import completed_turns
from app.tools.types import ToolOutcome
from tests.tool_fakes import ControlledExecutor, ToolModel, ToolRepository, collect, selected_call, setup_service


async def test_one_call_reinjects_matching_tool_and_streams():
    trace = []
    service, model, repository, executor, contexts = setup_service(repository=ToolRepository(trace))
    prepared = await service.prepare("42", "订单 A-42 怎么样")
    events = await collect(service, prepared, trace)
    assert model.selection_requests == executor.calls == model.final_stream_requests == model.bind_requests == 1
    assert model.bind_options == {"tool_choice": "auto", "parallel_tool_calls": False}
    assert isinstance(model.final_input[-1], ToolMessage)
    assert model.final_input[-1].tool_call_id == model.selected.tool_calls[0]["id"]
    assert events[-1].event == "done" and events[-1].data == {"conversation_id": "42"}
    assert trace.index("commit_final") < trace.index("done")
    assert contexts[-1].user_message_id == prepared.user_message_id == 101
    assert [event.data for event in events if event.event == "status"] == [
        {"phase": "selecting"}, {"phase": "tool_running", "tool_name": "query_order", "tool_call_id": "call_1"},
        {"phase": "tool_completed", "tool_name": "query_order", "tool_call_id": "call_1", "status": "success"}, {"phase": "answering"},
    ]
    assert len(completed_turns(repository.rows)) == 1


async def test_no_tool_still_uses_final_stream():
    service, model, repository, executor, _ = setup_service(model=ToolModel(AIMessage("selection text ignored", response_metadata={"finish_reason": "stop"})))
    events = await collect(service, await service.prepare("42", "你好"))
    assert executor.calls == 0 and model.selection_requests == model.final_stream_requests == 1
    assert model.final_input[-1].content == "你好"
    assert events[-1].event == "done"
    assert [row.role for row in repository.rows] == ["user", "assistant"]


def bad_selection(case):
    message = selected_call()
    if case == "multiple":
        message.tool_calls.append({"name": "query_order", "args": {}, "id": "call_2"})
    elif case == "unknown":
        message.tool_calls[0]["name"] = "refund"
    elif case == "blank_name":
        message.tool_calls[0]["name"] = " "
    elif case == "bad_args":
        message.tool_calls[0]["args"] = []
    elif case == "long_id":
        message.tool_calls[0]["id"] = "a" * 65
    elif case == "blank_id":
        message.tool_calls[0]["id"] = " "
    elif case == "invalid":
        message.invalid_tool_calls = [{"name": "query_order", "args": "{", "id": "bad", "error": "bad JSON"}]
    elif case in ("length", "content_filter", "missing"):
        message.response_metadata = {} if case == "missing" else {"finish_reason": case}
    elif case == "no_tool_nonstop":
        message = AIMessage("你好", response_metadata={"finish_reason": "tool_calls"})
    elif case == "raw_unparsed":
        message = AIMessage("", additional_kwargs={"tool_calls": [{"type": "unsupported"}]}, response_metadata={"finish_reason": "stop"})
    return message


@pytest.mark.parametrize("case", ["multiple", "unknown", "blank_name", "bad_args", "long_id", "blank_id", "invalid", "length", "content_filter", "missing", "no_tool_nonstop", "raw_unparsed"])
async def test_multiple_calls_execute_nothing(case):
    service, model, repository, executor, _ = setup_service(model=ToolModel(bad_selection(case)))
    events = await collect(service, await service.prepare("42", "查订单 A-42"))
    assert executor.calls == model.final_stream_requests == 0
    assert events[-1].event == "error"
    assert [row.role for row in repository.rows] == ["user"]
    assert completed_turns(repository.rows) == []


@pytest.mark.parametrize("chunks", [
    [AIMessageChunk("", response_metadata={"finish_reason": "stop"})],
    [AIMessageChunk("回答")],
    [AIMessageChunk("回答", response_metadata={"finish_reason": "length"})],
    [AIMessageChunk("回答", response_metadata={"finish_reason": "content_filter"}), AIMessageChunk("", response_metadata={"finish_reason": "stop"})],
    [AIMessageChunk("", tool_call_chunks=[{"name": "query_order", "args": "{}", "id": "again", "index": 0}], response_metadata={"finish_reason": "stop"})],
    [AIMessageChunk("回答"), RuntimeError("secret upstream failure")],
    [AIMessageChunk("回答"), TimeoutError()],
    [AIMessageChunk("a" * 20001, response_metadata={"finish_reason": "stop"})],
])
async def test_failed_final_has_audit_without_successful_answer(chunks):
    service, model, repository, executor, _ = setup_service(model=ToolModel(chunks=chunks))
    events = await collect(service, await service.prepare("42", "查订单 A-42"))
    assert executor.calls == 1 and events[-1].event == "error"
    assert [row.role for row in repository.rows] == ["user", "assistant", "tool"]
    assert completed_turns(repository.rows) == []
    assert "secret" not in json.dumps(events[-1].data)


@pytest.mark.parametrize("role", ["assistant", "tool", "final"])
async def test_database_commit_failure_never_done(role):
    service, _, repository, _, _ = setup_service(repository=ToolRepository(fail_role=role))
    events = await collect(service, await service.prepare("42", "查订单 A-42"))
    assert events[-1].event == "error"
    assert completed_turns(repository.rows) == []
    assert "secret" not in json.dumps(events[-1].data)


async def test_required_budget_checked_before_user_insert_and_lock_released():
    service, _, repository, _, _ = setup_service()
    with pytest.raises(InputTooLong):
        await service.prepare("42", "中" * 20000)
    assert repository.rows == []
    service.release(await service.prepare("42", "你好"))


async def test_prepare_database_failure_releases_lock():
    service, _, repository, _, _ = setup_service(repository=ToolRepository(fail_role="user"))
    with pytest.raises(RuntimeError):
        await service.prepare("42", "你好")
    repository.fail_role = None
    service.release(await service.prepare("42", "你好"))


async def test_result_budget_overflow_preserves_audit_without_final_request():
    executor = ControlledExecutor(ToolOutcome({"result": "中" * 10000}, "success", 1))
    service, model, repository, _, _ = setup_service(executor=executor)
    events = await collect(service, await service.prepare("42", "查订单 A-42"))
    assert events[-1].data["code"] == "input_too_long"
    assert model.final_stream_requests == 0 and completed_turns(repository.rows) == []


async def test_argument_error_reinjected_with_error_status():
    service, model, _, _, _ = setup_service(model=ToolModel(selected_call(args={})))
    from app.tools.executor import ToolExecutor
    service.executor = ToolExecutor()
    events = await collect(service, await service.prepare("42", "查订单 A-42"))
    assert json.loads(model.final_input[-1].content)["error"]["code"] == "invalid_arguments"
    assert model.final_input[-1].status == "error"
    assert next(event for event in events if event.data.get("phase") == "tool_completed").data["status"] == "error"
    assert events[-1].event == "done"


async def test_cancel_propagates_and_failed_turn_is_not_replayed():
    service, _, repository, _, _ = setup_service(model=ToolModel(chunks=[AIMessageChunk("回答"), asyncio.CancelledError()]))
    prepared = await service.prepare("42", "查订单 A-42")
    with pytest.raises(SessionBusy):
        await service.prepare("42", "你好")
    with pytest.raises(asyncio.CancelledError):
        await collect(service, prepared)
    assert completed_turns(repository.rows) == []
    service.release(await service.prepare("42", "你好"))


async def test_dynamic_schema_change_rejected_before_model_request():
    from langchain_core.tools import tool
    service, model, repository, _, _ = setup_service()
    @tool
    async def preview_tool(value: str) -> str:
        """预览工具。"""
        return value
    @tool
    async def changed_tool(value: str) -> str:
        """变化后的工具。"""
        return value
    service.registry_factory = lambda context: {"preview_tool": preview_tool} if context.user_message_id == 0 else {"changed_tool": changed_tool}
    from app.core.errors import ServiceError
    with pytest.raises(ServiceError, match="工具定义发生变化"):
        await service.prepare("42", "你好")
    assert model.selection_requests == model.bind_requests == 0
    assert [row.role for row in repository.rows] == ["user"]
    service.locks.acquire("42").release()


async def test_real_execution_uses_persisted_id_without_preview_execution():
    from app.tools.executor import ToolExecutor
    from app.tools.registry import build_registry
    from tests.tool_fakes import FAQ
    captured = []
    class Tickets:
        async def create(self, **kwargs):
            captured.append(kwargs)
            return {"ticket_no": "T-real", "status": "待处理"}
    service, model, _, _, contexts = setup_service(model=ToolModel(selected_call("create_ticket", {"description": "需要人工帮助", "ticket_type": "咨询"})))
    service.registry_factory = lambda context: build_registry(FAQ(), Tickets(), context)
    service.executor = ToolExecutor()
    prepared = await service.prepare("42", "需要人工帮助")
    events = await collect(service, prepared)
    assert events[-1].event == "done"
    assert len(captured) == 1 and captured[0]["user_message_id"] == prepared.user_message_id == 101


async def test_protocol_error_closes_current_iterator():
    model = ToolModel(chunks=[AIMessageChunk("", tool_call_chunks=[{"name": "query_order", "args": "{}", "id": "again", "index": 0}])])
    service, _, _, _, _ = setup_service(model=model)
    events = await collect(service, await service.prepare("42", "查订单 A-42"))
    assert events[-1].event == "error" and model.closed


async def test_selection_argument_budget_overflow_executes_nothing():
    service, model, repository, executor, _ = setup_service(model=ToolModel(selected_call(args={"order_id": "a" * 9000})))
    events = await collect(service, await service.prepare("42", "查订单 A-42"))
    assert events[-1].event == "error" and events[-1].data["code"] == "input_too_long"
    assert executor.calls == model.final_stream_requests == 0
    assert completed_turns(repository.rows) == []


@pytest.mark.parametrize("case", [json.loads(line) for line in (Path(__file__).parents[1] / "evals/tool_cases.jsonl").read_text(encoding="utf-8").splitlines()], ids=lambda case: case["id"])
async def test_annotated_cases_structure_and_controlled_reinjection(case):
    from app.core.prompts import build_tool_chat_system_prompt
    from app.tools.executor import ToolExecutor
    assert set(case) == {"id", "category", "message", "expected_tool", "expected_args", "expected_found", "answer_contains", "controlled_answer"}
    assert case["message"].strip() and isinstance(case["expected_args"], dict)
    assert case["expected_found"] is None or type(case["expected_found"]) is bool
    assert all(fragment in case["controlled_answer"] for fragment in case["answer_contains"])
    selected = selected_call(case["expected_tool"], case["expected_args"]) if case["expected_tool"] else AIMessage("", response_metadata={"finish_reason": "stop"})
    model = ToolModel(selected, [AIMessageChunk(case["controlled_answer"], response_metadata={"finish_reason": "stop"})])
    service, _, _, _, _ = setup_service(model=model)
    service.executor = ToolExecutor()
    events = await collect(service, await service.prepare("42", case["message"]))
    assert events[-1].event == "done"
    if case["expected_tool"]:
        result = json.loads(model.final_input[-1].content)
        assert model.final_input[-1].name == case["expected_tool"]
        if case["expected_found"] is not None:
            assert result["found"] is case["expected_found"]
            assert case["expected_args"]["keyword"] in case["message"]
        if case["expected_tool"] in {"query_order", "query_product", "query_logistics"}:
            assert result["mock"] is True
    else:
        assert model.final_input[-1].content == case["message"]
    prompt = build_tool_chat_system_prompt()
    assert "mock=true" in prompt and "禁止伪造商家政策" in prompt and "不能执行退款" in prompt


def test_annotated_cases_cover_exactly_eight_required_categories():
    cases = [json.loads(line) for line in (Path(__file__).parents[1] / "evals/tool_cases.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(cases) == len({case["id"] for case in cases}) == 8
    assert {case["category"] for case in cases} == {"物流", "订单", "商品", "退货 FAQ 命中", "邮费 FAQ Dense 命中", "人工工单", "普通问候无工具", "缺订单号先澄清无工具"}


async def test_model_swallowing_cancel_cannot_commit_success():
    class SwallowsCancellation(ToolModel):
        async def astream(self, messages):
            asyncio.current_task().cancel()
            try:
                await asyncio.sleep(0)
            except asyncio.CancelledError:
                pass
            yield AIMessageChunk("回答", response_metadata={"finish_reason": "stop"})
    service, _, repository, _, _ = setup_service(model=SwallowsCancellation())
    prepared = await service.prepare("42", "查订单 A-42")
    task = asyncio.create_task(collect(service, prepared))
    with pytest.raises(asyncio.CancelledError):
        await task
    assert completed_turns(repository.rows) == []
