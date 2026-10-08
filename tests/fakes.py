import asyncio
import json

from langchain_core.messages import AIMessage, AIMessageChunk

from app.config import Settings


class FAQStub:
    def __init__(self, matches=None, *, failure=None):
        self.matches = matches if matches is not None else []
        self.keywords = []
        self.failure = failure

    async def search(self, keyword, limit=3):
        self.keywords.append(keyword)
        if self.failure is not None:
            raise self.failure
        return self.matches[:limit]


def fake_settings(**overrides):
    return Settings(
        _env_file=None,
        llm_base_url="https://upstream.invalid/v1/",
        llm_model="fake-chat",
        llm_api_key="fake-test-key",
        **overrides,
    )


class StreamingModel:
    """仅替换外部模型流，保留真实消息与事件控制逻辑。"""

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
        self.requests = 0
        self.selected = AIMessage("", response_metadata={"finish_reason": "stop"})

    def bind_tools(self, tools, **kwargs):
        return self

    async def ainvoke(self, messages):
        self.requests += 1
        return self.selected

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
    """替换外部结构化调用，包括包裹原始响应的数据结构。"""

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
    # 产品接口缺失时，应主动报告断言失败而非测试收集错误，
    # 这样首次红灯才能证明功能尚未实现。
    import pytest

    try:
        from app.core.tool_chat import ToolChatService
        from app.api.streaming import ManagedChatResponse
        from app.main import create_app
    except ImportError:
        pytest.fail("HTTP/SSE chat and managed response are not implemented")
    return ToolChatService, ManagedChatResponse, create_app


class ConversationStore:
    """离线持久仓储替身；保留失败审计，但仅完成轮次可回放。"""

    def __init__(self, identifier="1"):
        self.identifier = identifier
        self.users = {identifier: "test"}
        self.ended = set()
        self.rows = {}
        self.commits = 0
        self.fail_final = False

    async def create(self, user_id):
        self.users[self.identifier] = user_id
        return self.identifier

    async def require_open(self, conversation_id):
        from app.core.errors import ServiceError
        from app.repositories.conversations import _conversation_id
        _conversation_id(conversation_id)
        if conversation_id not in self.users:
            raise ServiceError("conversation_not_found", "Conversation does not exist.", 404)
        if conversation_id in self.ended:
            raise ServiceError("conversation_ended", "Conversation has ended.", 409)

    async def load_messages(self, conversation_id):
        return list(self.rows.get(conversation_id, []))

    async def append_message(self, conversation_id, message):
        from app.repositories.records import record_from_message
        rows = self.rows.setdefault(conversation_id, [])
        row = record_from_message(message, identifier=len(rows) + 1)
        if row.role == "assistant" and row.tool_calls is None:
            if self.fail_final:
                raise RuntimeError("SECRET database failure")
            self.commits += 1
        rows.append(row)
        return row.id

    def snapshot(self, conversation_id):
        from app.core.tool_history import completed_turns
        return tuple(message for turn in completed_turns(self.rows.get(conversation_id, [])) for message in turn)

    async def seed(self, conversation_id, messages):
        for message in messages:
            await self.append_message(conversation_id, message)
        self.commits = 0
