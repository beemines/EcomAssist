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
        return ScriptedIntentModel(self)

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

    def __init__(self, model):
        """保留父模型，集中记录意图请求。"""
        self.model = model

    async def ainvoke(self, messages, **kwargs):
        """独立记录并返回意图响应，不消费工具决策。"""
        self.model.intents += 1
        self.model.intent_inputs.append(messages)
        reply = self.model.intent_replies.popleft()
        if isinstance(reply, BaseException):
            raise reply
        return reply


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
