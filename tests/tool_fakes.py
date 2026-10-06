from langchain_core.messages import AIMessage, AIMessageChunk

from app.core.conversation_locks import ConversationLocks
from app.repositories.records import record_from_message
from app.tools.registry import build_registry
from app.tools.types import ToolOutcome
from tests.fakes import fake_settings


def selected_call(name="query_order", args=None, identifier="call_1", reason="tool_calls"):
    return AIMessage("", tool_calls=[{"name": name, "args": args if args is not None else {"order_id": "A-42"}, "id": identifier}], response_metadata={"finish_reason": reason})


class ToolModel:
    def __init__(self, selected=None, chunks=None):
        self.selected = selected if selected is not None else selected_call()
        self.chunks = chunks if chunks is not None else [AIMessageChunk("模拟订单已完成。"), AIMessageChunk("", response_metadata={"finish_reason": "stop"})]
        self.selection_requests = self.final_stream_requests = self.bind_requests = 0
        self.final_input = None
        self.bind_options = None
        self.closed = False

    def bind_tools(self, tools, **kwargs):
        self.bind_requests += 1
        self.bind_options = kwargs
        return self

    async def ainvoke(self, messages):
        self.selection_requests += 1
        if isinstance(self.selected, BaseException):
            raise self.selected
        return self.selected

    async def astream(self, messages):
        self.final_stream_requests += 1
        self.final_input = messages
        try:
            for chunk in self.chunks:
                if isinstance(chunk, BaseException):
                    raise chunk
                yield chunk
        finally:
            self.closed = True


class ToolRepository:
    def __init__(self, trace=None, fail_role=None, rows=None):
        self.trace = trace if trace is not None else []
        self.rows = rows if rows is not None else []
        self.fail_role = fail_role

    async def require_open(self, conversation_id):
        from app.repositories.conversations import _conversation_id
        _conversation_id(conversation_id)

    async def load_messages(self, conversation_id):
        return list(self.rows)

    async def append_message(self, conversation_id, message):
        row = record_from_message(message, identifier=101 + len(self.rows))
        final = row.role == "assistant" and not row.tool_calls
        if self.fail_role == ("final" if final else row.role):
            raise RuntimeError("secret database failure")
        self.rows.append(row)
        self.trace.append("commit_final" if final else "commit_" + row.role)
        return row.id


class ControlledExecutor:
    def __init__(self, outcome=None):
        self.calls = 0
        self.outcome = outcome or ToolOutcome({"mock": True, "status": "已完成"}, "success", 1)

    async def execute(self, call, registry):
        self.calls += 1
        return self.outcome


class FAQ:
    async def search(self, keyword, limit):
        return [{"question": "如何退货", "answer": "请联系商家确认。"}] if keyword == "退货" else []


class Tickets:
    async def create(self, **kwargs):
        return {"ticket_no": "T-test", "status": "待处理"}


def setup_service(*, model=None, repository=None, executor=None, budget=8000):
    from app.core.tool_chat import ToolChatService
    contexts = []
    def factory(context):
        contexts.append(context)
        return build_registry(FAQ(), Tickets(), context)
    settings = fake_settings().model_copy(update={"tool_input_token_budget": budget})
    repository = repository or ToolRepository()
    model = model or ToolModel()
    executor = executor or ControlledExecutor()
    service = ToolChatService(model, repository, factory, ConversationLocks(), settings, executor=executor)
    return service, model, repository, executor, contexts


async def collect(service, prepared, trace=None):
    events = []
    try:
        async for event in service.stream(prepared):
            events.append(event)
            if trace is not None:
                trace.append(event.event)
    finally:
        service.release(prepared)
    return events
