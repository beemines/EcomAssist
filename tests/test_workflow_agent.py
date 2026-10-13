"""主力子图离线行为：顺序执行、不可见控制和唯一最终生成。"""
import importlib
import json
from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, ToolMessage

from app.core.errors import ServiceError
from app.tools.business import query_order, query_logistics, query_product, contextual_tools
from app.tools.executor import ToolExecutor
from app.tools.types import ToolContext
from app.workflow.state import new_turn_state
from tests.workflow_fakes import ScriptedWorkflowModel, workflow_call, workflow_runtime


def control(mode='answer', actions=()):
    """生成独立控制响应，确保正文只能来自最终流。"""
    return AIMessage(json.dumps({'reply_mode': mode, 'suggested_actions': list(actions)}),
        response_metadata={'finish_reason': 'stop'})


def graph():
    """缺少生产图时以行为 RED 断言失败，不制造收集错误。"""
    try:
        module = importlib.import_module('app.workflow.agent')
    except ImportError:
        pytest.fail('bounded workflow agent implementation missing')
    return module.build_agent_graph()


def setup(replies, *, question='订单 A-42 的状态和物流', intent='订单', answer='模拟查询：订单待发货，物流运输中。', chunks=None):
    """只替换模型和数据库边界，保留真实工具注册与执行器。"""
    context = workflow_runtime(intent=intent)
    context.model = ScriptedWorkflowModel(final_chunks=chunks if chunks is not None else [
        AIMessageChunk(answer), AIMessageChunk('', response_metadata={'finish_reason': 'stop'})])
    context.decision_model = ScriptedWorkflowModel(replies)
    tools = [query_order, query_logistics, query_product, *contextual_tools(
        context.faq_repository, SimpleNamespace(),
        ToolContext('session', 1, question))]
    context.registry = {tool.name: tool for tool in tools}
    context.executor = ToolExecutor(overrides={'query_faq': (90, 0)})
    state = new_turn_state(conversation_id='session', user_message_id=1, raw_question=question,
        category=None, messages=[HumanMessage(question)])
    state.update(intent=intent, route='business')
    return context, state


async def run(context, state):
    """从真实图 custom/updates 获取输出状态及前端可消费事件。"""
    events, result = [], dict(state)
    async for kind, data in graph().astream(state, context=context,
            config={'recursion_limit': 32}, stream_mode=['custom', 'updates']):
        if kind == 'custom':
            events.append(data)
        else:
            for update in data.values():
                result.update(update)
    return result, events


@pytest.mark.asyncio
async def test_agent_two_sequential_tools():
    """省略回灌或并行工具会破坏实际顺序、配对和 SQL 审计。"""
    context, state = setup([workflow_call(), workflow_call('query_logistics', identifier='call_2'), control()])
    result, events = await run(context, state)
    assert [step['name'] for step in result['tool_trace']] == ['query_order', 'query_logistics']
    assert result['tool_call_count'] == 2 and context.model.streams == 1
    assert [m.type for m in context.repository.messages] == ['ai', 'tool', 'ai', 'tool']
    assert all(m.id for m in result['messages'][1:])
    assert [m.tool_call_id for m in result['messages'] if isinstance(m, ToolMessage)] == ['call_1', 'call_2']
    assert all(option['parallel_tool_calls'] is False for option in context.decision_model.bind_options)
    assert [(e['data']['status'], e['data']['tool']) for e in events if e['event'] == 'status'] == [
        ('running', 'query_order'), ('completed', 'query_order'), ('running', 'query_logistics'), ('completed', 'query_logistics')]


@pytest.mark.asyncio
async def test_final_stream_hides_control_json():
    """错误流出决策正文会被实际 text 字段和最终内容断言发现。"""
    context, state = setup([workflow_call(), control(actions=['handoff', 'handoff'])])
    result, events = await run(context, state)
    deltas = [e['data']['text'] for e in events if e['event'] == 'delta']
    assert deltas and ''.join(deltas) == result['final_answer']
    assert all('reply_mode' not in text for text in deltas)
    assert result['suggested_actions'] == ['handoff']
    assert not any('reply_mode' in str(m.content) for m in context.repository.messages)


@pytest.mark.asyncio
async def test_ticket_never_in_bound_tools():
    """模型可见注册表错误暴露写工具时，本轮实际绑定即失败。"""
    context, state = setup([control('clarification')], answer='请提供订单号。')
    await run(context, state)
    assert context.decision_model.bound_tools
    assert 'create_ticket' not in {t.name for t in context.decision_model.bound_tools[0]}


@pytest.mark.asyncio
async def test_forged_ticket_call_is_rejected_before_executor_or_sql():
    """模型伪造未绑定工单申请也不能触发执行器、SQL写入或最终生成。"""
    context, state = setup([workflow_call('create_ticket',
        {'description': '伪造模型工单', 'ticket_type': '售后'})])
    assert 'create_ticket' in context.registry
    executed = []
    original_execute = context.executor.execute
    async def observed_execute(call, registry):
        """保留真实执行器，仅记录是否越过工具申请执行边界。"""
        executed.append(call.name)
        return await original_execute(call, registry)
    context.executor.execute = observed_execute
    with pytest.raises(ServiceError) as error:
        await run(context, state)
    assert error.value.code == 'upstream_error'
    assert executed == [] and not context.repository.messages
    assert context.decision_model.decisions == 1 and context.model.streams == 0


@pytest.mark.asyncio
async def test_usage_help_asks_for_product():
    """已购商品缺型号的使用求助只追问，不错误写低置信池。"""
    context, state = setup([control('clarification')], question='新买的商品不太会用，能帮我看看吗', intent='售后',
        answer='可以的，你买的是什么商品或型号？具体在哪一步不会操作？')
    result, events = await run(context, state)
    assert result['reply_mode'] == 'clarification' and not context.repository.refusals
    assert '商品' in result['final_answer'] and '型号' in result['final_answer']
    assert result['tool_call_count'] == 0 and not context.sufficiency.calls
    assert len([e for e in events if e['event'] == 'delta']) == 1


@pytest.mark.asyncio
async def test_parent_commits_final_once_after_child_validation():
    """实际父子图只提交一个最终答复，工具配对保留相邻关系。"""
    from langgraph.checkpoint.memory import InMemorySaver
    from app.workflow.graph import build_workflow_graph
    context, state = setup([workflow_call(), control()])
    context.intent_model = ScriptedWorkflowModel(intent_replies=[AIMessage('{"intent":"订单"}',
        response_metadata={'finish_reason': 'stop'})])
    parent = build_workflow_graph(graph(), checkpointer=InMemorySaver())
    result = await parent.ainvoke(state, context=context, config={'configurable': {'thread_id': 'parent-child'}})
    assert result['turn_status'] == 'completed'
    assert [m.type for m in context.repository.messages] == ['ai', 'tool', 'ai']
    assert context.repository.messages[-1].content == result['final_answer']
    assert result['messages'][-1].id == result['final_message_id']
