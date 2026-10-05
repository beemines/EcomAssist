import json

import httpx
import pytest
from langchain_core.messages import AIMessage, HumanMessage

from app.core.llm import create_model
from app.core.memory import SessionStore
from app.main import create_app
from tests.fakes import decode_sse, fake_settings


@pytest.mark.parametrize("reasons, done_marker, terminal", [
    pytest.param([], False, "incomplete", id="missing-reason-eof-synthetic-last"),
    pytest.param([], True, "incomplete", id="done-marker-without-public-reason"),
    pytest.param(["stop"], False, "done", id="normal-stop-eof-synthetic-last"),
    pytest.param(["stop"], True, "done", id="normal-stop-done-marker"),
    pytest.param(["stop", None], False, "done", id="normal-stop-retained-through-empty-final"),
    pytest.param(["content_filter"], True, "incomplete", id="content-filter"),
    pytest.param(["tool_calls"], True, "incomplete", id="tool-calls"),
    pytest.param(["unexpected"], True, "incomplete", id="unknown-reason"),
    pytest.param(["stop", "content_filter"], True, "incomplete", id="stop-then-abnormal"),
    pytest.param(["content_filter", "stop"], True, "incomplete", id="abnormal-then-stop"),
    pytest.param(["length", "stop"], True, "length", id="length-cannot-be-overridden"),
])
async def test_factory_stream_requires_normal_completion_before_history_commit(
    reasons, done_marker, terminal,
):
    """Catch accepting public EOF/synthetic last or abnormal reasons as success."""
    settings = fake_settings()
    memory = SessionStore()
    lease = memory.acquire("same")
    memory.commit(lease, [HumanMessage(content="old"), AIMessage(content="answer")])
    memory.release(lease)
    requests = []

    def respond(request):
        requests.append(request)
        assert str(request.url) == "https://upstream.invalid/v1/chat/completions"
        payload = json.loads(request.content)
        assert payload["stream"] is True
        assert payload["messages"][1:] == [
            {"role": "user", "content": "old"},
            {"role": "assistant", "content": "answer"},
            {"role": "user", "content": "new"},
        ]
        choices = [{"delta": {"role": "assistant", "content": "partial answer"},
                    "finish_reason": None}]
        choices.extend({"delta": {}, "finish_reason": reason} for reason in reasons)
        body = "".join("data: " + json.dumps({
            "id": "chatcmpl-test", "object": "chat.completion.chunk", "created": 1,
            "model": settings.llm_model, "choices": [{"index": 0, **choice}],
        }) + "\n\n" for choice in choices)
        if done_marker:
            body += "data: [DONE]\n\n"
        return httpx.Response(200, text=body, headers={"content-type": "text/event-stream"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond), trust_env=False) as upstream:
        model = create_model(settings, http_async_client=upstream)
        try:
            app = create_app(settings, model=model, memory=memory)
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app), base_url="http://test", trust_env=False,
            ) as client:
                response = await client.post("/api/chat", json={"session_id": "same", "message": "new"})
        finally:
            await model.root_async_client.close()
            model.root_client.close()

    assert response.status_code == 200
    events = decode_sse(response.text)
    expected_terminal = (
        ("done", {"session_id": "same"}) if terminal == "done" else
        ("error", {"code": "upstream_error", "message": (
            "模型回复被截断，请检查输出上限。" if terminal == "length" else
            "模型回复未正常完成，请稍后重试。"
        )})
    )
    assert events == [("delta", {"delta": "partial answer"}), expected_terminal]
    assert [item.content for item in memory.snapshot("same")] == (
        ["old", "answer", "new", "partial answer"] if terminal == "done" else ["old", "answer"]
    )
    assert len(requests) == 1
    memory.release(memory.acquire("same"))
