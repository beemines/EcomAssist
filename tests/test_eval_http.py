import importlib
import json

import anyio
import httpx
import pytest

from app.config import Settings


GOOD = {"order_id": None, "request_type": "unknown", "expected_solution": None}


# 加载结构化抽取评测模块，缺失实现时报告明确失败。
def implementation():
    try:
        return importlib.import_module("evals.evaluate")
    except ModuleNotFoundError:
        pytest.fail("evaluation implementation is missing")


# 生成指定数量、带固定预期结果的临时 JSONL 样本文件。
def cases_file(tmp_path, count):
    path = tmp_path / "cases.jsonl"
    path.write_text("\n".join(json.dumps({"id": str(i), "text": "你好", "expected": GOOD})
                              for i in range(count)), encoding="utf-8")
    return path


# 验证首次兼容性样本只请求一次，后续各类故障均保留在脱敏报告与分母中。
async def test_evaluate_preserves_each_failure_and_calls_first_case_once(tmp_path):
    module = implementation()
    seen = []

    # 依次模拟正常响应、HTTP 错误、非法 JSON、缺失字段和读取超时。
    def handler(request):
        assert request.url.path == "/api/extract"
        assert json.loads(request.content) == {"text": "你好"}
        seen.append(request)
        i = len(seen)
        if i == 1:
            return httpx.Response(200, json=GOOD)
        if i == 2:
            return httpx.Response(502, json={"code": "upstream_error", "message": "SECRET"})
        if i == 3:
            return httpx.Response(200, content=b"SECRET invalid JSON")
        if i == 4:
            return httpx.Response(200, json={"order_id": None})
        raise httpx.ReadTimeout("SECRET")

    output = tmp_path / "report.json"
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        report = await module.evaluate("http://application.invalid", cases_file(tmp_path, 5), output, http_client=client)
        assert not client.is_closed
    assert len(seen) == report["request_count"] == 5
    assert report["metrics"]["valid_rate"] == .2
    assert [r["error_code"] for r in report["records"]] == [None, "http_error", "invalid_json", "invalid_schema", "timeout"]
    assert report["records"][-1]["status_code"] is None
    assert all(r["response"] is None for r in report["records"][1:])
    assert json.loads(output.read_text(encoding="utf-8")) == report
    assert "SECRET" not in output.read_text(encoding="utf-8")
    assert report["identity"]["provider_verified"] is False


# 验证首样本兼容性失败立即停止后续请求，但仍为全部样本保留记录与统计分母。
@pytest.mark.parametrize("failure,code,status", [
    ("http", "http_error", 502),
    ("json", "invalid_json", 200),
    ("schema", "invalid_schema", 200),
    ("timeout", "timeout", None),
    ("transport", "transport_error", None),
])
async def test_first_compatibility_failure_stops_requests_preserving_all_case_denominators(tmp_path, failure, code, status):
    module = implementation()
    seen = []

    # 按参数模拟首请求的 HTTP、JSON、结构、超时或连接故障，检验提前终止门槛。
    def handler(request):
        seen.append(request)
        if failure == "http":
            return httpx.Response(502, content=b"SECRET upstream details")
        if failure == "json":
            return httpx.Response(200, content=b"SECRET invalid JSON")
        if failure == "schema":
            return httpx.Response(200, json={"order_id": None})
        if failure == "timeout":
            raise httpx.ReadTimeout("SECRET timeout")
        raise httpx.ConnectError("SECRET connection")

    output = tmp_path / "gated-report.json"
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        report = await module.evaluate("http://app.invalid", cases_file(tmp_path, 5), output, http_client=client)
        assert not client.is_closed
    assert len(seen) == 1
    assert report["request_count"] == report["attempted_count"] == 1
    assert report["not_attempted_count"] == 4
    assert report["first_case_json_compatible"] is False
    assert len(report["records"]) == report["metrics"]["total"] == 5
    assert report["records"][0]["error_code"] == code
    assert report["records"][0]["status_code"] == status
    assert report["records"][0]["response"] is None
    assert [r["error_code"] for r in report["records"][1:]] == ["not_attempted"] * 4
    assert all(r["status_code"] is None and r["response"] is None for r in report["records"][1:])
    assert [r["id"] for r in report["records"]] == ["0", "1", "2", "3", "4"]
    assert all(r["text"] == "你好" and r["expected"] == GOOD for r in report["records"])
    assert report["metrics"]["valid_count"] == 0
    assert report["metrics"]["missing_value_total"] == 15
    assert report["metrics"]["missing_value_accuracy"] == 0
    assert report["metrics"]["order_id_accuracy"] == 0
    assert len(report["metrics"]["failures"]) == 5
    assert json.loads(output.read_text(encoding="utf-8")) == report
    assert "SECRET" not in output.read_text(encoding="utf-8")


# 验证首样本结构合法但答案不符时仍继续评测全部样本。
async def test_first_valid_json_with_gold_mismatch_continues_prompt_evaluation(tmp_path):
    module = implementation()
    seen = []

    # 仅让首次响应类别与标准答案不同，其余响应正常，以区分兼容性与准确率。
    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={**GOOD, "request_type": "other"} if len(seen) == 1 else GOOD)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        report = await module.evaluate("http://app.invalid", cases_file(tmp_path, 5), tmp_path / "mismatch.json", http_client=client)
        assert not client.is_closed
    assert len(seen) == report["request_count"] == 5
    assert report["first_case_json_compatible"] is True
    assert report["attempted_count"] == 5
    assert report["not_attempted_count"] == 0
    assert report["metrics"]["valid_count"] == 5
    assert report["metrics"]["request_type_accuracy"] == .8
    assert len(report["metrics"]["failures"]) == 1


# 验证整体墙钟截止时间能终止慢请求，并关闭评测自行创建的 HTTP 客户端。
async def test_evaluate_wall_clock_deadline_and_owned_client_close(tmp_path, monkeypatch):
    module = implementation()
    monkeypatch.setattr(module, "REQUEST_DEADLINE_SECONDS", .02)

    # 延迟超过评测截止时间再返回响应，模拟底层未主动超时的慢服务。
    async def handler(request):
        await anyio.sleep(.2)
        return httpx.Response(200, json=GOOD)

    owned = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    monkeypatch.setattr(module.httpx, "AsyncClient", lambda **kwargs: owned)
    report = await module.evaluate("http://application.invalid", cases_file(tmp_path, 1), tmp_path / "r.json")
    assert report["records"][0]["error_code"] == "timeout"
    assert owned.is_closed


# 验证评测通过真实应用接口与结构约束运行，同时无需外部模型。
async def test_evaluation_uses_real_application_schema_with_model_free_http(tmp_path):
    from app.main import create_app
    from tests.fakes import FAQStub, ConversationStore, StructuredModel, structured_result

    settings = Settings(_env_file=None, llm_base_url="https://fake.invalid/v1/", llm_model="fake-test",
                        llm_api_key="fake-test-key")
    app = create_app(settings, faq_repository=FAQStub(), model=StructuredModel(structured_result(GOOD)), repository=ConversationStore())
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app)) as client:
        report = await implementation().evaluate("http://app.invalid", cases_file(tmp_path, 1), tmp_path / "r.json", http_client=client)
    assert report["metrics"]["valid_count"] == 1
    assert report["identity"]["configured_model"] is None
