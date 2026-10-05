import importlib
import json

import anyio
import httpx
import pytest

from app.config import Settings


GOOD = {"order_id": None, "request_type": "unknown", "expected_solution": None}


def implementation():
    try:
        return importlib.import_module("evals.evaluate")
    except ModuleNotFoundError:
        pytest.fail("evaluation implementation is missing")


def cases_file(tmp_path, count):
    path = tmp_path / "cases.jsonl"
    path.write_text("\n".join(json.dumps({"id": str(i), "text": "你好", "expected": GOOD})
                              for i in range(count)), encoding="utf-8")
    return path


async def test_evaluate_preserves_each_failure_and_calls_first_case_once(tmp_path):
    module = implementation()
    seen = []

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


async def test_evaluate_wall_clock_deadline_and_owned_client_close(tmp_path, monkeypatch):
    module = implementation()
    monkeypatch.setattr(module, "REQUEST_DEADLINE_SECONDS", .02)

    async def handler(request):
        await anyio.sleep(.2)
        return httpx.Response(200, json=GOOD)

    owned = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    monkeypatch.setattr(module.httpx, "AsyncClient", lambda **kwargs: owned)
    report = await module.evaluate("http://application.invalid", cases_file(tmp_path, 1), tmp_path / "r.json")
    assert report["records"][0]["error_code"] == "timeout"
    assert owned.is_closed


async def test_evaluation_uses_real_application_schema_with_model_free_http(tmp_path):
    from app.main import create_app
    from tests.fakes import StructuredModel, structured_result

    settings = Settings(_env_file=None, llm_base_url="https://fake.invalid/v1/", llm_model="fake-test",
                        llm_api_key="fake-test-key")
    app = create_app(settings, model=StructuredModel(structured_result(GOOD)))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app)) as client:
        report = await implementation().evaluate("http://app.invalid", cases_file(tmp_path, 1), tmp_path / "r.json", http_client=client)
    assert report["metrics"]["valid_count"] == 1
    assert report["identity"]["configured_model"] is None
