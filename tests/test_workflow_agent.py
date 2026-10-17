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
from tests.workflow_fakes import apply_workflow_update, ScriptedWorkflowModel, workflow_call, workflow_runtime

NOTICE = '本轮订单、物流等业务信息为模拟演示数据，仅供参考。\n\n'

def control(mode='answer', actions=()):
    """生成独立控制响应，确保正文只能来自最终流。"""
    return AIMessage(json.dumps({'reply_mode': mode, 'suggested_actions': list(actions),
                                'refund_decision': None, 'decision_reason': None}),
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
                apply_workflow_update(result, update)
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
    context, state = setup([control('clarification')], question='查订单', answer='请提供订单号。')
    await run(context, state)
    assert context.decision_model.bound_tools
    assert 'create_ticket' not in {(t['function']['name'] if isinstance(t, dict) else t.name) for t in context.decision_model.bound_tools[0]}


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
    context.intent_model = ScriptedWorkflowModel(intent_replies=[AIMessage('{"intent":"订单","confidence":0.95}',
        response_metadata={'finish_reason': 'stop'})])
    parent = build_workflow_graph(graph(), checkpointer=InMemorySaver())
    result = await parent.ainvoke(state, context=context, config={'configurable': {'thread_id': 'parent-child'}})
    assert result['turn_status'] == 'completed'
    assert [m.type for m in context.repository.messages] == ['ai', 'tool', 'ai']
    assert context.repository.messages[-1].content == result['final_answer']
    assert result['messages'][-1].id == result['final_message_id']


@pytest.mark.asyncio
@pytest.mark.parametrize('path', ['mandatory_faq', 'logistics'])
async def test_actual_model_inputs_separate_decision_and_final_phase(path):
    """强制检索后及物流回灌后的实际决策输入不得混入最终正文阶段指令。"""
    from tests.test_evidence import payload
    if path == 'mandatory_faq':
        context, state = setup([control()], question='退货政策是什么？', intent='退款退货', answer='当前退货规则[1]。')
        state.update(route='knowledge', tool_call_count=1,
            quality={'useful': True, 'reason': '本轮资料已通过闸门', 'response_kind': 'knowledge', 'source': None})
        state['messages'] += [workflow_call('query_faq', {'keyword': '退货政策'}, 'mandatory'),
            ToolMessage(json.dumps(payload(('当前退货规则',))), tool_call_id='mandatory')]
    else:
        context, state = setup([workflow_call('query_logistics'), control()],
            question='订单 A-42 物流到哪了？', intent='物流', answer='模拟物流查询：运输中。')
    result, _ = await run(context, state)
    assert len(context.decision_model.tool_inputs) == (1 if path == 'mandatory_faq' else 2)
    for messages in context.decision_model.tool_inputs:
        system = messages[0].text
        assert '不需要继续读取时正文只输出严格JSON' in system
        assert '需要进一步读取时申请一个业务读取工具' in system
        assert '申请一个业务读取工具，正文必须为空' in system
        assert '不输出控制 JSON' not in system, 'decision request contains final-only no-JSON instruction'
        assert '不申请工具' not in system, 'decision request forbids its own read-tool phase'
        assert '最终回复只输出给用户看的简短中文正文' not in system
        assert '只依据本轮编号证据和本轮工具结果' in system
        assert '历史不能充当新证据' in system
        assert 'mock=true' in system
    final_system = context.model.stream_inputs[0][0].text
    assert '最终回复只输出给用户看的简短中文正文，不输出控制 JSON，不申请工具' in final_system
    assert '不需要工具时只输出严格 JSON' not in final_system
    assert '知识事实必须引用当前证据 [n]' in final_system
    assert 'mock=true' in final_system and '模拟' in final_system and '演示' in final_system
    assert '澄清只询问必要信息，不包含政策、状态、期限或承诺' in final_system
    assert '转人工、创建工单仅为用户可确认的建议，不声称已执行' in final_system
    assert result['final_answer'] == ('当前退货规则[1]。' if path == 'mandatory_faq' else NOTICE + '模拟物流查询：运输中。')


@pytest.mark.asyncio
@pytest.mark.parametrize('question,intent,mode,tool,answer', [
    pytest.param('订单1001的包裹到哪里了？', '物流', 'answer', 'query_logistics',
        '模拟物流查询：包裹已揽收。', id='successful_mock_logistics_is_answer'),
    pytest.param('新买的商品不太会用，能帮我看看吗', '售后', 'clarification', None,
        '可以的，你买的是什么商品或型号？具体在哪一步不会操作？', id='missing_product_model_is_clarification'),
])
async def test_annotated_reply_modes_have_explicit_meaning_in_actual_model_inputs(question, intent, mode, tool, answer):
    """独立标注的模拟结果/缺型号样例在实际两阶段输入中有明确且一致的模式语义。"""
    import re
    from app.workflow.agent import AgentControl
    replies = [control(mode)] if tool is None else [workflow_call(tool, {'order_id': '1001'}), control(mode)]
    context, state = setup(replies, question=question, intent=intent, answer=answer)
    result, _ = await run(context, state)
    decision_system = context.decision_model.tool_inputs[-1][0].text
    assert 'answer：本轮读取结果或编号证据足以回应当前问题' in decision_system
    assert '解释已有工具结果属于 answer' in decision_system
    assert 'mock=true 的结果在保留模拟说明后仍可选择 answer' in decision_system
    assert 'clarification：仅用于追问用户尚未提供的必要信息' in decision_system
    # 实际发送的每个JSON示例都必须被正式控制Schema接受，不能写伪enum字面量。
    examples = [AgentControl.model_validate(json.loads(text)) for text in re.findall(r'\{[^{}]*\}', decision_system)]
    assert examples and {example.reply_mode for example in examples} == {'answer', 'clarification'}
    annotated_examples = {}
    for line in decision_system.splitlines():
        if line.startswith('示例：') and '{' in line:
            annotated_examples[line.split('→')[0]] = AgentControl.model_validate_json(line[line.index('{'):].rstrip('。'))
    assert any('订单1001的包裹到哪里了？' in label and example.reply_mode == 'answer'
        for label, example in annotated_examples.items())
    assert any('尚未提供商品或型号' in label and example.reply_mode == 'clarification'
        for label, example in annotated_examples.items())
    final_system = context.model.stream_inputs[0][0].text
    attachment = next(json.loads(m.content)['data'] for m in context.model.stream_inputs[0]
                      if isinstance(m, HumanMessage) and m.content.startswith('{"kind":"context_data"'))
    assert attachment['reply_mode'] == mode
    assert 'answer直接依据当前结果或编号证据回答' in final_system
    assert 'clarification只询问缺少的必要用户信息，不复述业务事实' in final_system
    assert result['reply_mode'] == mode and result['final_answer'] == (NOTICE + answer if tool else answer)


@pytest.mark.asyncio
@pytest.mark.parametrize('path', ['business_without_faq', 'mixed_faq', 'numbered_faq'])
async def test_final_model_input_distinguishes_business_results_from_faq_citation_sources(path):
    """真实最终输入必须限定 FAQ 的 n 为引用来源，同时保留无引用业务及混合知识回答。"""
    from tests.test_evidence import payload
    from tests.test_workflow_agent_quality import faq_result
    business = path != 'numbered_faq'
    has_faq = path != 'business_without_faq'
    replies = [workflow_call(), workflow_call('query_logistics', identifier='call_2')] if business else []
    if business and has_faq:
        replies.append(workflow_call('query_faq', {'keyword': '退货政策'}, 'faq'))
    answer = ('模拟查询：订单及物流查询已返回。' if business else '') + ('退货规则乙[2]。' if has_faq else '')
    context, state = setup([*replies, control()], question='订单 A-42 的状态、物流和退货政策', answer=answer)
    context.faq_repository.retrieve = faq_result(context, payload(('退货规则甲', '退货规则乙', '退货规则丙')))
    if not business:
        state.update(route='knowledge', intent='退款退货', tool_call_count=1,
            quality={'useful': True, 'reason': '本轮资料已通过闸门', 'response_kind': 'knowledge', 'source': None})
        state['messages'] += [workflow_call('query_faq', {'keyword': '退货政策'}, 'faq'),
            ToolMessage(json.dumps(payload(('退货规则甲', '退货规则乙', '退货规则丙'))), tool_call_id='faq')]
    result, _ = await run(context, state)
    final_messages = context.model.stream_inputs[0]
    system = final_messages[0].text
    assert '只有当前轮 FAQ 证据 matches 中实际存在的 n 字段才可作为 [n] 引用号' in system
    assert '订单、物流、商品等业务工具结果没有 FAQ 引用号' in system
    assert '不得把工具调用顺序、结果位置、调用 ID 或业务编号编造成引用号' in system
    assert '没有带 n 的 FAQ 证据时，直接用普通正文说明已有业务结果，不添加 [n]' in system
    assert '混合业务与 FAQ 时，仅为 FAQ 知识事实标注其实际 n' in system
    assert 'mock=true' in system and '模拟' in system
    shown = [json.loads(message.content) for message in final_messages if isinstance(message, ToolMessage)]
    business_payloads = [data for data in shown if 'evidence_in_attachment' not in data]
    assert len(business_payloads) == (2 if business else 0)
    assert all('n' not in data and data['mock'] is True for data in business_payloads)
    attachment = next(json.loads(m.content)['data'] for m in final_messages
                      if isinstance(m, HumanMessage) and m.content.startswith('{"kind":"context_data"'))
    numbered = attachment['evidence'].get('matches', [])
    assert all('matches' not in data for data in shown)
    assert [item['n'] for item in numbered] == ([1, 3, 2] if has_faq else [])
    assert [item['n'] for item in result['citations']] == ([1, 3, 2] if has_faq else [])
    assert result['final_answer'] == (NOTICE + answer if business else answer) and context.model.streams == 1
