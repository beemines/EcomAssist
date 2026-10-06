import json

import httpx
import pytest
from langchain_core.messages import HumanMessage, SystemMessage
from openai import RateLimitError

from app.config import Settings
from app.schemas.extract import AfterSalesResult


@pytest.fixture(params=["max_tokens", "max_completion_tokens"])
def settings(request):
    return Settings(
        _env_file=None,
        llm_base_url="https://upstream.invalid/custom/v1/",
        llm_model="gpt-5.4-custom",
        llm_api_key="fake-test-key",
        llm_token_limit_field=request.param,
        max_output_tokens=137,
        llm_timeout_seconds=7.5,
    )


def factory():
    try:
        from app.core.llm import create_model
    except ImportError:
        pytest.fail("The unified model factory is not implemented")
    return create_model


def check_request(request, settings):
    assert str(request.url) == "https://upstream.invalid/custom/v1/chat/completions"
    payload = json.loads(request.content)
    assert payload[settings.llm_token_limit_field] == 137
    other_field = (
        "max_completion_tokens"
        if settings.llm_token_limit_field == "max_tokens"
        else "max_tokens"
    )
    assert other_field not in payload
    assert payload["model"] == "gpt-5.4-custom"
    assert "tools" not in payload
    assert "tool_choice" not in payload
    assert "stream_options" not in payload
    assert "extra_body" not in payload
    assert request.extensions["timeout"] == {
        "connect": 7.5, "read": 7.5, "write": 7.5, "pool": 7.5,
    }
    assert request.headers["authorization"] == "Bearer fake-test-key"
    return payload


async def test_stream_uses_configured_chat_completions_payload(settings):
    requests = []

    def respond(request):
        requests.append(request)
        payload = check_request(request, settings)
        assert payload["stream"] is True
        assert "response_format" not in payload
        assert payload["messages"] == [{"role": "user", "content": "你好"}]
        chunks = [
            {"id": "chatcmpl-test", "object": "chat.completion.chunk", "created": 1,
             "model": settings.llm_model,
             "choices": [{"index": 0, "delta": {"role": "assistant", "content": "您好"},
                          "finish_reason": None}]},
            {"id": "chatcmpl-test", "object": "chat.completion.chunk", "created": 1,
             "model": settings.llm_model,
             "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]},
        ]
        body = "".join(f"data: {json.dumps(chunk)}\n\n" for chunk in chunks)
        return httpx.Response(200, text=body + "data: [DONE]\n\n",
                              headers={"content-type": "text/event-stream"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        model = factory()(settings, http_async_client=client)
        chunks = [chunk async for chunk in model.astream([HumanMessage("你好")])]
    assert "".join(chunk.content for chunk in chunks) == "您好"
    assert len(requests) == 1


async def test_extract_uses_json_mode_and_preserves_original_description(settings):
    try:
        from app.core.prompts import build_extract_messages
    except ImportError:
        pytest.fail("The extraction prompt builder is not implemented")
    text = '订单 A-42\n请保留 {original} 和 "引号"，我要退货退款。'
    messages = build_extract_messages(text)
    assert len(messages) == 2
    assert isinstance(messages[0], SystemMessage)
    assert isinstance(messages[1], HumanMessage)
    assert messages[1].content == text
    assert text not in messages[0].content
    requests = []

    def respond(request):
        requests.append(request)
        payload = check_request(request, settings)
        assert payload["stream"] is False
        assert payload["response_format"] == {"type": "json_object"}
        assert payload["messages"][1] == {"role": "user", "content": text}
        return httpx.Response(200, json={
            "id": "chatcmpl-test", "object": "chat.completion", "created": 1,
            "model": settings.llm_model,
            "choices": [{"index": 0, "finish_reason": "stop", "message": {
                "role": "assistant", "content": json.dumps({
                    "order_id": "A-42", "request_type": "return_refund",
                    "expected_solution": "退货退款",
                }), "refusal": None,
            }}],
            "usage": {"prompt_tokens": 12, "completion_tokens": 20, "total_tokens": 32},
        })

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        model = factory()(settings, http_async_client=client)
        result = await model.with_structured_output(
            AfterSalesResult, method="json_mode",
        ).ainvoke(messages)
    assert result == AfterSalesResult(
        order_id="A-42", request_type="return_refund", expected_solution="退货退款",
    )
    assert len(requests) == 1


async def test_factory_does_not_retry_upstream_failure(settings):
    requests = []

    def respond(request):
        requests.append(request)
        check_request(request, settings)
        return httpx.Response(429, json={"error": {
            "message": "test rate limit", "type": "rate_limit_error",
            "param": None, "code": "rate_limit_exceeded",
        }})

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        model = factory()(settings, http_async_client=client)
        with pytest.raises(RateLimitError):
            await model.ainvoke([HumanMessage("你好")])
    assert len(requests) == 1
