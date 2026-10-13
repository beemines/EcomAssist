"""Workflow 专用离线模型，不改变旧聊天替身的含义。"""
from collections import deque

from langchain_core.messages import AIMessage, AIMessageChunk


class ScriptedWorkflowModel:
    """独立记录意图、决策和最终流，并支持阻塞和异常。"""

    def __init__(self, replies=(), *, final_chunks=None, intent_replies=(), block=None):
        """保存受控响应队列；阻塞事件用于取消验证。"""
        self.replies, self.intent_replies = deque(replies), deque(intent_replies)
        self.final_chunks = final_chunks if final_chunks is not None else [
            AIMessageChunk('受控物流答案'), AIMessageChunk('', response_metadata={'finish_reason': 'stop'})]
        self.block = block
        self.intent_inputs, self.tool_inputs, self.stream_inputs = [], [], []
        self.bind_options, self.bound_tools = [], []
        self.decisions = self.intents = self.streams = 0
        self.closed = False

    def bind_tools(self, tools, **kwargs):
        """只记录工具绑定，后续请求仍由明确的决策队列提供。"""
        self.bound_tools.append(list(tools))
        self.bind_options.append(kwargs)
        return self

    def with_structured_output(self, schema, **kwargs):
        """用独立入口包装意图调用，避免与工具决策混用计数。"""
        return ScriptedIntentModel(self, schema)

    async def ainvoke(self, messages, **kwargs):
        """记录完整决策输入并返回下一条预置响应或故障。"""
        self.decisions += 1
        self.tool_inputs.append([message.model_copy(deep=True) for message in messages])
        if self.block is not None:
            await self.block.wait()
        reply = self.replies.popleft()
        if isinstance(reply, BaseException):
            raise reply
        return reply

    async def astream(self, messages, **kwargs):
        """记录最终输入，逐片输出并在取消或异常后标记关闭。"""
        self.streams += 1
        self.stream_inputs.append([message.model_copy(deep=True) for message in messages])
        try:
            if self.block is not None:
                await self.block.wait()
            for chunk in self.final_chunks:
                if isinstance(chunk, BaseException):
                    raise chunk
                yield chunk
        finally:
            self.closed = True


class ScriptedIntentModel:
    """只消费意图队列的结构化包装。"""

    def __init__(self, model, schema):
        """保留父模型，集中记录意图请求。"""
        self.model = model
        self.schema = schema

    async def ainvoke(self, messages, **kwargs):
        """独立记录并返回意图响应，不消费工具决策。"""
        self.model.intents += 1
        self.model.intent_inputs.append(messages)
        reply = self.model.intent_replies.popleft()
        if isinstance(reply, BaseException):
            raise reply
        if isinstance(reply, AIMessage):
            try:
                parsed = self.schema.model_validate_json(reply.text)
                error = None
            except Exception as exc:
                parsed, error = None, exc
            return {'raw': reply, 'parsed': parsed, 'parsing_error': error}
        return reply


class WorkflowRepository:
    """离线保留真实消息内容和提交身份，不连接数据库。"""

    def __init__(self):
        """初始化审计消息及拒答数据。"""
        self.messages, self.refusals = [], []

    async def append_message(self, conversation_id, message):
        """保存深拷贝，使展示侧变更不能改写已提交审计。"""
        self.messages.append(message.model_copy(deep=True))
        return 100 + len(self.messages)

    async def commit_refusal(self, conversation_id, answer, **kwargs):
        """同时保存拒答及问题来源，镜像质量仓储原子接口。"""
        self.refusals.append({'conversation_id': conversation_id, **kwargs})
        return await self.append_message(conversation_id, answer)


def workflow_runtime(*, intent='商品咨询', payload=None, useful=True, error=None):
    """组装只替换外部模型及数据库边界的完整运行依赖。"""
    import json
    import time
    from types import SimpleNamespace
    from app.core.sufficiency import QualityDecision
    from app.workflow.runtime import WorkflowRuntime

    class FAQ:
        """记录检索可信入参并返回完整载荷。"""
        def __init__(self):
            """初始化受控检索调用记录。"""
            self.calls = []

        async def retrieve(self, keyword, *, raw_question, category=None):
            """故障与空命中分开，使故障不能冒充低置信度。"""
            self.calls.append((keyword, raw_question, category))
            if error:
                raise error
            return payload if payload is not None else {'found': False, 'matches': [],
                'retrieval': {'strategy': 'hybrid_rerank', 'match_count': 0}}

    class Sufficiency:
        """离线内容评估，只计达标后调用。"""
        def __init__(self):
            """初始化自评调用记录。"""
            self.calls = []

        async def check(self, raw_question, evidence):
            """记录原话及实际证据并返回受控合法判定。"""
            self.calls.append((raw_question, evidence))
            return QualityDecision(useful=useful, reason='离线内容判定',
                response_kind='knowledge', source=None if useful else 'self_check')

    repository = WorkflowRepository()
    model = ScriptedWorkflowModel(intent_replies=[AIMessage(json.dumps({'intent': intent}, ensure_ascii=False),
        response_metadata={'finish_reason': 'stop'})])
    settings = SimpleNamespace(tool_input_token_budget=8000, llm_timeout_seconds=60,
        faq_timeout_seconds=90, rerank_min_score=.5, intent_max_output_tokens=2048)
    return WorkflowRuntime(model, model, model, repository, FAQ(), Sufficiency(), repository,
        {}, None, settings, time.monotonic() + 240)


def workflow_call(name='query_order', args=None, identifier='call_1'):
    """构造包含真实 Chat Completions 镜像的单工具申请。"""
    import json
    args = {'order_id': 'A-42'} if args is None else args
    return AIMessage('', tool_calls=[{'id': identifier, 'name': name, 'args': args}],
        additional_kwargs={'tool_calls': [{'id': identifier, 'type': 'function', 'function': {
            'name': name, 'arguments': json.dumps(args, ensure_ascii=False)}}]},
        response_metadata={'finish_reason': 'tool_calls'})


def workflow_stop():
    """构造正常结束的无工具决策。"""
    return AIMessage('受控物流答案', response_metadata={'finish_reason': 'stop'})
