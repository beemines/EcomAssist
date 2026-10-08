from langchain_core.messages import AIMessage, AIMessageChunk

from app.core.conversation_locks import ConversationLocks
from app.repositories.records import record_from_message
from app.tools.registry import build_registry
from app.tools.types import ToolOutcome
from tests.fakes import fake_settings


# 构造带工具名称、参数、调用编号和结束原因的模型选择响应。
def selected_call(name="query_order", args=None, identifier="call_1", reason="tool_calls"):
    return AIMessage("", tool_calls=[{"name": name, "args": args if args is not None else {"order_id": "A-42"}, "id": identifier}], response_metadata={"finish_reason": reason})


class ToolModel:
    # 配置工具选择与最终回复片段，并初始化绑定和请求计数。
    def __init__(self, selected=None, chunks=None):
        self.selected = selected if selected is not None else selected_call()
        self.chunks = chunks if chunks is not None else [AIMessageChunk("模拟订单已完成。"), AIMessageChunk("", response_metadata={"finish_reason": "stop"})]
        self.selection_requests = self.final_stream_requests = self.bind_requests = 0
        self.final_input = None
        self.bind_options = None
        self.closed = False

    # 记录绑定选项和次数，以验证工具调用模式及单次绑定行为。
    def bind_tools(self, tools, **kwargs):
        self.bind_requests += 1
        self.bind_options = kwargs
        return self

    # 返回预设工具选择，或抛出异常以模拟选择阶段的模型故障。
    async def ainvoke(self, messages):
        self.selection_requests += 1
        if isinstance(self.selected, BaseException):
            raise self.selected
        return self.selected

    # 记录最终输入并依次输出预设片段，支持中途异常且始终标记流已关闭。
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
    # 准备消息审计行、提交顺序和按消息角色触发的落库故障。
    def __init__(self, trace=None, fail_role=None, rows=None):
        self.trace = trace if trace is not None else []
        self.rows = rows if rows is not None else []
        self.fail_role = fail_role

    # 复用真实编号校验，避免仓储替身绕过会话格式约束。
    async def require_open(self, conversation_id):
        from app.repositories.conversations import _conversation_id
        _conversation_id(conversation_id)

    # 返回预置审计行的副本，用于历史恢复测试。
    async def load_messages(self, conversation_id):
        return list(self.rows)

    # 按角色模拟提交故障并记录提交顺序，以核对工具轮次的持久化边界。
    async def append_message(self, conversation_id, message):
        row = record_from_message(message, identifier=101 + len(self.rows))
        final = row.role == "assistant" and not row.tool_calls
        if self.fail_role == ("final" if final else row.role):
            raise RuntimeError("secret database failure")
        self.rows.append(row)
        self.trace.append("commit_final" if final else "commit_" + row.role)
        return row.id


class ControlledExecutor:
    # 预设工具执行结果并初始化执行次数。
    def __init__(self, outcome=None):
        self.calls = 0
        self.outcome = outcome or ToolOutcome({"mock": True, "status": "已完成"}, "success", 1)

    # 记录执行次数并返回固定结果，使聊天服务测试只关注工具编排。
    async def execute(self, call, registry):
        self.calls += 1
        return self.outcome


class FAQ:
    # 为邮费或退货关键词提供固定 FAQ，其余关键词返回空结果。
    async def search(self, keyword, limit):
        if keyword == '邮费':
            return [{'id': 7, 'question': '标准配送费用', 'answer': '合成演示8元，商品实付满99元包邮。', 'category': '合成演示'}]
        return [{"id": 8, "question": "如何退货", "answer": "请联系商家确认。", "category": "合成演示"}] if keyword == "退货" else []


class Tickets:
    # 返回固定工单编号和待处理状态，避免访问真实工单仓储。
    async def create(self, **kwargs):
        return {"ticket_no": "T-test", "status": "待处理"}


# 组装真实工具聊天服务与离线依赖，并允许覆盖模型、仓储、执行器和预算。
def setup_service(*, model=None, repository=None, executor=None, budget=8000):
    from app.core.tool_chat import ToolChatService
    contexts = []
    # 记录每轮工具上下文并用 FAQ 与工单替身创建工具注册表。
    def factory(context):
        contexts.append(context)
        return build_registry(FAQ(), Tickets(), context)
    settings = fake_settings().model_copy(update={"tool_input_token_budget": budget})
    repository = repository or ToolRepository()
    model = model or ToolModel()
    executor = executor or ControlledExecutor()
    service = ToolChatService(model, repository, factory, ConversationLocks(), settings, executor=executor)
    return service, model, repository, executor, contexts


# 收集流事件及可选顺序记录，并确保结束或异常时释放会话锁。
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
