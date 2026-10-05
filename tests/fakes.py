import asyncio
import json

from langchain_core.messages import AIMessage, AIMessageChunk

from app.config import Settings


def fake_settings(**overrides):
    return Settings(
        _env_file=None,
        llm_base_url="https://upstream.invalid/v1/",
        llm_model="fake-chat",
        llm_api_key="fake-test-key",
        **overrides,
    )


class StreamingModel:
    """Replace only the external stream; retain real messages and event gating."""

    def __init__(self, chunks=None, *, failure=None, gate_at=None):
        self.chunks = chunks if chunks is not None else [
            AIMessageChunk(content="你好"),
            AIMessageChunk(content="", response_metadata={"finish_reason": "stop"}),
        ]
        self.failure = failure
        self.gate_at = gate_at
        self.gate = asyncio.Event()
        self.waiting = asyncio.Event()
        self.started = asyncio.Event()
        self.closed = asyncio.Event()
        self.eof = asyncio.Event()
        self.calls = []

    def with_structured_output(self, schema, *, method, include_raw):
        return StructuredModel()

    async def astream(self, messages):
        self.calls.append(messages)
        self.started.set()
        try:
            for index, chunk in enumerate(self.chunks):
                if index == self.gate_at:
                    self.waiting.set()
                    await self.gate.wait()
                yield chunk
            if self.gate_at == len(self.chunks):
                self.waiting.set()
                await self.gate.wait()
            if self.failure is not None:
                raise self.failure
            self.eof.set()
        finally:
            self.closed.set()


class StructuredModel(StreamingModel):
    """Replace the external structured invocation, including its raw envelope."""

    def __init__(self, result=None, *, failure=None):
        super().__init__()
        self.result = result
        self.failure = failure
        self.structured_options = []

    def with_structured_output(self, schema, *, method, include_raw):
        self.structured_options.append((schema, method, include_raw))
        return self

    async def ainvoke(self, messages):
        self.calls.append(messages)
        if self.failure is not None:
            raise self.failure
        return self.result


def structured_result(data, *, raw=None, parsed=None, parsing_error=None, finish_reason="stop"):
    from app.schemas.extract import AfterSalesResult

    return {
        "raw": AIMessage(
            content=json.dumps(data, ensure_ascii=False) if raw is None else raw,
            response_metadata={"finish_reason": finish_reason},
        ),
        "parsed": AfterSalesResult.model_validate(data) if parsed is None else parsed,
        "parsing_error": parsing_error,
    }


def decode_sse(text):
    events = []
    for frame in text.strip().split("\n\n"):
        lines = frame.splitlines()
        events.append((lines[0].removeprefix("event: "), json.loads(lines[1].removeprefix("data: "))))
    return events


def implementations():
    # Missing production APIs must report an intentional assertion, not a
    # collection error, so the first RED proves the feature is absent.
    import pytest

    try:
        from app.core.chat import ChatService
        from app.api.streaming import ManagedChatResponse
        from app.main import create_app
    except ImportError:
        pytest.fail("HTTP/SSE chat and managed response are not implemented")
    return ChatService, ManagedChatResponse, create_app
