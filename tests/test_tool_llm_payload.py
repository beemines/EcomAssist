import json

import httpx

from app.core.llm import create_model
from tests.tool_fakes import collect, setup_service
from tests.fakes import fake_settings


# 验证真实模型协议先绑定五个工具做单调用选择，再以匹配结果发起无工具最终流。
async def test_real_model_wire_selects_five_tools_then_streams_without_tools():
    payloads = []
    settings = fake_settings()
    # 核对选择与最终请求的协议字段和调用编号，并返回合成工具调用及正常流片段。
    def respond(request):
        assert str(request.url).endswith("/chat/completions")
        payload = json.loads(request.content)
        payloads.append(payload)
        if len(payloads) == 1:
            assert payload["stream"] is False
            assert {tool["function"]["name"] for tool in payload["tools"]} == {"query_order", "query_product", "query_logistics", "query_faq", "create_ticket"}
            assert payload["tool_choice"] == "auto" and payload["parallel_tool_calls"] is False
            assert "tool_call_id" not in payload["tools"][-1]["function"]["parameters"]["properties"]
            return httpx.Response(200, json={"id": "chatcmpl-test", "object": "chat.completion", "created": 1, "model": settings.llm_model,
                "choices": [{"index": 0, "finish_reason": "tool_calls", "message": {"role": "assistant", "content": None, "tool_calls": [{"id": "call-wire", "type": "function", "function": {"name": "query_order", "arguments": '{"order_id":"A-42"}'}}]}}]})
        assert payload["stream"] is True and "tools" not in payload and "tool_choice" not in payload
        request_message, result_message = payload["messages"][-2:]
        assert request_message["tool_calls"][0]["id"] == result_message["tool_call_id"] == "call-wire"
        assert json.loads(result_message["content"])["mock"] is True
        chunks = [{"id": "chatcmpl-test", "object": "chat.completion.chunk", "created": 1, "model": settings.llm_model,
            "choices": [{"index": 0, "delta": delta, "finish_reason": reason}]} for delta, reason in [({"role": "assistant", "content": "模拟订单已完成。"}, None), ({}, "stop")]]
        return httpx.Response(200, text="".join("data: " + json.dumps(chunk) + "\n\n" for chunk in chunks) + "data: [DONE]\n\n", headers={"content-type": "text/event-stream"})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond), trust_env=False) as client:
        model = create_model(settings, http_async_client=client)
        assert model.max_retries == 0 and model.use_responses_api is False
        service, _, _, _, _ = setup_service(model=model)
        try:
            events = await collect(service, await service.prepare("42", "查订单 A-42"))
        finally:
            await model.root_async_client.close()
            model.root_client.close()
    assert len(payloads) == 2 and events[-1].event == "done"
