# 售后抽取 API 测试，覆盖固定 JSON、字段校验、输入预算及上游失败响应。
import json

import httpx
import pytest
from langchain_core.messages import AIMessage, HumanMessage
from openai import APITimeoutError

from app.main import create_app
from app.schemas.extract import AfterSalesResult
from tests.fakes import FAQStub, ConversationStore, StructuredModel, fake_settings, structured_result


TEXT = "订单 20261005001 的杯子收到就碎了，我想退货退款。"
RESULT = {"order_id": "20261005001", "request_type": "return_refund", "expected_solution": "退货退款"}
UNKNOWN = {"order_id": None, "request_type": "unknown", "expected_solution": None}
INVALID = {"code": "invalid_structured_output", "message": "模型返回的结构化结果无效，请稍后重试。"}


# 以结构化模型替身和可选会话仓储创建离线抽取接口客户端。
def client_for(model, repository=None, **settings):
    app = create_app(fake_settings(**settings), faq_repository=FAQStub(), model=model, repository=repository if repository is not None else ConversationStore())
    return httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url="http://test")


# 验证抽取只返回三个精确字段及原文值，并且结构化输出模式只绑定一次。
async def test_extract_returns_exact_three_keys_with_source_values():
    model = StructuredModel(structured_result(RESULT))
    async with client_for(model) as client:
        response = await client.post("/api/extract", json={"text": TEXT})
        second = await client.post("/api/extract", json={"text": TEXT})
    assert response.status_code == second.status_code == 200
    assert response.json() == RESULT
    assert response.headers["content-type"].startswith("application/json")
    assert model.structured_options == [(AfterSalesResult, "json_mode", True)]


# 验证所有声明的请求类别都合法，缺失订单与诉求可返回空值。
@pytest.mark.parametrize("category", ["refund", "return_refund", "exchange", "repair", "logistics", "other", "unknown"])
async def test_accepts_all_declared_categories_and_null_missing_fields(category):
    data = {"order_id": None, "request_type": category, "expected_solution": None}
    async with client_for(StructuredModel(structured_result(data))) as client:
        response = await client.post("/api/extract", json={"text": "没有明确订单"})
    assert response.status_code == 200
    assert response.json() == data


# 验证即使解析器给出合法对象，非法、残缺或带包装的原始 JSON 仍被拒绝。
@pytest.mark.parametrize("raw", [
    '{}', '{"order_id": null, "request_type": "unknown"}',
    '{"order_id": null, "request_type": "unknown", "expected_solution": null, "extra": true}',
    '{"order_id": " ", "request_type": "unknown", "expected_solution": null}',
    '{"order_id": null, "request_type": "unknown", "expected_solution": ""}',
    '{"order_id": null, "request_type": "unsupported", "expected_solution": null}',
    'not JSON SECRET', json.dumps(UNKNOWN)[:-1],
    '```json\n' + json.dumps(UNKNOWN) + '\n```', json.dumps(UNKNOWN) + ' garbage',
    '[]', '{"order_id": 123, "request_type": "unknown", "expected_solution": null}',
])
async def test_rejects_invalid_or_incomplete_raw_even_when_parser_returned_valid_object(raw):
    model = StructuredModel(structured_result(UNKNOWN, raw=raw))
    async with client_for(model) as client:
        response = await client.post("/api/extract", json={"text": TEXT})
    assert response.status_code == 502
    assert response.json() == INVALID
    assert len(model.calls) == 1


# 验证截断、解析错误、解析缺失及原始与解析结果不一致均返回结构化输出错误。
@pytest.mark.parametrize("envelope", [
    structured_result(RESULT, finish_reason="length"),
    structured_result(RESULT, parsing_error=ValueError("SECRET parser details")),
    structured_result(RESULT, parsed=AfterSalesResult.model_validate(UNKNOWN)),
    {"raw": AIMessage(content=json.dumps(RESULT)), "parsed": None, "parsing_error": None},
])
async def test_rejects_truncation_parser_failure_missing_or_inconsistent_parsed(envelope):
    async with client_for(StructuredModel(envelope)) as client:
        response = await client.post("/api/extract", json={"text": TEXT})
    assert response.status_code == 502
    assert response.json() == INVALID


# 验证模型编造的订单号或解决诉求无法通过原文约束。
@pytest.mark.parametrize("field,value", [("order_id", "invented-order"), ("expected_solution", "免费补发")])
async def test_rejects_fields_absent_from_source_description(field, value):
    data = {**RESULT, field: value}
    async with client_for(StructuredModel(structured_result(data))) as client:
        response = await client.post("/api/extract", json={"text": TEXT})
    assert response.status_code == 502
    assert response.json() == INVALID


# 验证模型故障与各类超时映射到对应状态码及安全错误消息。
@pytest.mark.parametrize("failure,status,code,message", [
    (RuntimeError("SECRET provider details"), 502, "upstream_error", "模型服务暂时不可用，请稍后重试。"),
    (TimeoutError("SECRET timeout"), 504, "upstream_timeout", "模型响应超时，请稍后重试。"),
    (httpx.ReadTimeout("SECRET timeout"), 504, "upstream_timeout", "模型响应超时，请稍后重试。"),
    (APITimeoutError(request=httpx.Request("POST", "https://upstream.invalid")), 504, "upstream_timeout", "模型响应超时，请稍后重试。"),
])
async def test_maps_upstream_errors_to_safe_http_response(failure, status, code, message):
    async with client_for(StructuredModel(failure=failure)) as client:
        response = await client.post("/api/extract", json={"text": TEXT})
    assert response.status_code == status
    assert response.json() == {"code": code, "message": message}


# 验证预算不足时在模型调用前拒绝原描述，避免截断后继续抽取。
async def test_budget_rejects_before_invocation_without_truncating_description():
    model = StructuredModel(failure=AssertionError("provider invoked over budget"))
    async with client_for(model, input_token_budget=1) as client:
        response = await client.post("/api/extract", json={"text": TEXT})
    assert response.status_code == 422
    assert response.json() == {"code": "input_too_long", "message": "Input exceeds the context budget."}
    assert model.calls == []


# 验证缺失、空白、超长或额外请求字段在模型调用前返回 422。
@pytest.mark.parametrize("payload", [{}, {"text": " "}, {"text": ""}, {"text": "x" * 20001}, {"text": "hello", "extra": True}])
async def test_invalid_request_rejects_before_invocation(payload):
    model = StructuredModel()
    async with client_for(model) as client:
        response = await client.post("/api/extract", json=payload)
    assert response.status_code == 422
    assert model.calls == []


# 验证抽取保留括号、换行与 JSON 原文，成功或失败均不改变聊天历史。
@pytest.mark.parametrize("failure", [None, RuntimeError("failure")])
async def test_extract_preserves_source_and_independent_chat_repository(failure):
    text = '订单 {ABC-01}\n我想换货，附注 {"keep": true}'
    data = {"order_id": "{ABC-01}", "request_type": "exchange", "expected_solution": "换货"}
    model = StructuredModel(structured_result(data), failure=failure)
    repository = ConversationStore()
    await repository.seed("1", [HumanMessage(content="old"), AIMessage(content="answer")])
    before = repository.snapshot("1")
    async with client_for(model, repository) as client:
        response = await client.post("/api/extract", json={"text": text})
    assert response.status_code == (200 if failure is None else 502)
    assert model.calls[0][-1].content == text
    assert repository.snapshot("1") == before
