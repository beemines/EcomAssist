# 基础聊天测试替身与 SSE 解析辅助，提供可控的模型、会话仓储和固定结果。
import asyncio
import json

from langchain_core.messages import AIMessage, AIMessageChunk

from app.config import Settings


class FAQStub:
    # 配置 FAQ 命中结果或检索异常，并保留查询关键词供断言。
    def __init__(self, matches=None, *, failure=None):
        self.matches = matches if matches is not None else []
        self.keywords = []
        self.failure = failure

    # 记录关键词，按数量返回预设 FAQ，或抛出预设故障验证错误处理。
    async def search(self, keyword, limit=3):
        self.keywords.append(keyword)
        if self.failure is not None:
            raise self.failure
        return self.matches[:limit]


# 构造禁用环境文件且使用虚假模型凭据的设置，允许测试覆盖指定字段。
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

    # 配置流片段、故障与阻塞位置，并创建启动、等待、结束和关闭信号供生命周期测试同步。
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

    # 让工具绑定沿用当前替身，以保留同一组响应和调用状态。
    def bind_tools(self, tools, **kwargs):
        return self

    # 记录非流式请求次数，并返回预设的模型选择响应。
    async def ainvoke(self, messages):
        self.requests += 1
        return self.selected

    # 返回结构化模型替身，替代真实的结构化输出请求。
    def with_structured_output(self, schema, *, method, include_raw):
        return StructuredModel()

    # 在指定片段处阻塞以模拟慢流或断连，支持尾部故障，并通过信号区分正常结束与资源关闭。
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

    # 配置结构化结果或异常，并记录结构化输出选项。
    def __init__(self, result=None, *, failure=None):
        super().__init__()
        self.result = result
        self.failure = failure
        self.structured_options = []

    # 保存输出模式与模式对象，便于验证结构化调用参数。
    def with_structured_output(self, schema, *, method, include_raw):
        self.structured_options.append((schema, method, include_raw))
        return self

    # 记录输入消息并返回预设结构化结果，或抛出预设上游异常。
    async def ainvoke(self, messages):
        self.calls.append(messages)
        if self.failure is not None:
            raise self.failure
        return self.result


# 构造同时包含原始响应、解析结果和解析错误的模型返回包。
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


# 将完整 SSE 文本拆成事件名和 JSON 数据，便于核对事件顺序与载荷。
def decode_sse(text):
    events = []
    for frame in text.strip().split("\n\n"):
        lines = frame.splitlines()
        events.append((lines[0].removeprefix("event: "), json.loads(lines[1].removeprefix("data: "))))
    return events


# 加载真实聊天服务、响应和应用入口，使缺失接口表现为清晰的测试断言失败。
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

    # 初始化离线会话、审计记录与最终落库故障开关。
    def __init__(self, identifier="1"):
        self.identifier = identifier
        self.users = {identifier: "test"}
        self.ended = set()
        self.rows = {}
        self.commits = 0
        self.fail_final = False

    # 记录新会话所属用户，并返回预设会话编号。
    async def create(self, user_id):
        self.users[self.identifier] = user_id
        return self.identifier

    # 校验会话编号格式，并模拟不存在或已结束会话的服务错误。
    async def require_open(self, conversation_id):
        from app.core.errors import ServiceError
        from app.repositories.conversations import _conversation_id
        _conversation_id(conversation_id)
        if conversation_id not in self.users:
            raise ServiceError("conversation_not_found", "Conversation does not exist.", 404)
        if conversation_id in self.ended:
            raise ServiceError("conversation_ended", "Conversation has ended.", 409)

    # 返回会话审计消息的副本，供历史恢复流程读取。
    async def load_messages(self, conversation_id):
        return list(self.rows.get(conversation_id, []))

    # 保存消息审计记录并统计最终回复提交，支持在最终落库处注入数据库故障。
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

    # 从审计行中筛选完整轮次，供测试核对可回放的历史。
    def snapshot(self, conversation_id):
        from app.core.tool_history import completed_turns
        return tuple(message for turn in completed_turns(self.rows.get(conversation_id, [])) for message in turn)

    # 预置会话消息并重置提交计数，避免准备数据影响后续断言。
    async def seed(self, conversation_id, messages):
        for message in messages:
            await self.append_message(conversation_id, message)
        self.commits = 0
