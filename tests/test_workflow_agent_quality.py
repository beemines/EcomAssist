"""新证据必须过闸，澄清不能夹带政策或状态，历史不能冒充本轮证据。"""
import json

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.core.errors import ServiceError
from tests.test_evidence import payload
from tests.test_workflow_agent import NOTICE, control, run, setup
from tests.workflow_fakes import workflow_call


@pytest.mark.asyncio
async def test_business_faq_checks_new_evidence():
    """业务补充 FAQ 后必须在第一个正文前评估实际最终编号证据。"""
    context, state = setup([workflow_call('query_faq', {'keyword': '虚构关键词'}), control()],
        question='新买的 MH200 如何操作', intent='售后', answer='操作规则[1]。')
    data = payload(('操作规则',))
    context.faq_repository.retrieve = faq_result(context, data)
    original_stream = context.model.astream
    checked_before_delta = []
    async def guarded_stream(messages, **kwargs):
        """在真实生成边界观测闸门，证明每个正文片段之前质量已检查。"""
        async for chunk in original_stream(messages, **kwargs):
            checked_before_delta.append(bool(context.sufficiency.calls))
            yield chunk
    context.model.astream = guarded_stream
    result, events = await run(context, state)
    assert len(context.sufficiency.calls) >= 1
    assert checked_before_delta and all(checked_before_delta)
    assert context.sufficiency.calls[-1][1].payload['matches'][0]['n'] == 1
    assert context.faq_repository.calls == [('新买的 MH200 如何操作', '新买的 MH200 如何操作', None)]
    assert result['citations'][0]['chunk_id'] == '100'
    assert events[-1]['event'] == 'delta' and events[-1]['data']['text'] == '操作规则[1]。'
    assert 'n' not in json.loads(context.repository.messages[1].content)['matches'][0]


def faq_result(context, data):
    """外部检索替身保留可信关键词及完整原话的观测。"""
    async def retrieve(keyword, *, raw_question, category=None):
        """只有显式检索调用才记录，返回完整检索业务结构。"""
        context.faq_repository.calls.append((keyword, raw_question, category))
        return data
    return retrieve


@pytest.mark.asyncio
async def test_knowledge_does_not_query_faq_twice():
    """强制检索过的知识轮不再向主力模型暴露 FAQ。"""
    context, state = setup([control()], answer='当前规则[1]。')
    state.update(route='knowledge', intent='商品咨询', tool_call_count=1)
    state['messages'] += [workflow_call('query_faq', {'keyword': '订单'}, 'mandatory'),
        ToolMessage(json.dumps(payload(('当前规则',))), tool_call_id='mandatory')]
    state['quality'] = {'useful': True, 'reason': '当前证据已检查', 'response_kind': 'knowledge', 'source': None}
    result, _ = await run(context, state)
    assert 'query_faq' not in {(t['function']['name'] if isinstance(t, dict) else t.name) for t in context.decision_model.bound_tools[0]}
    assert result['tool_call_count'] == 1 and not context.faq_repository.calls
    assert result['citations'][0]['answer'] == '当前规则'


@pytest.mark.asyncio
@pytest.mark.parametrize('tail', ['可以退货', '已发货', '三天到账', '可以退货吗'])
@pytest.mark.parametrize('particle', ['', '呢'])
async def test_clarification_cannot_smuggle_facts(tail, particle):
    """逐句追问守卫拒绝未验证政策/状态/承诺，即使有问号也不放行。"""
    context, state = setup([control('clarification')], question='新买的商品不太会用', intent='售后',
        answer='可以的，你买的是什么商品或型号？具体在哪一步不会操作' + particle + '？' + tail + '。')
    with pytest.raises(ServiceError):
        await run(context, state)
    assert not context.repository.messages and not context.repository.refusals


@pytest.mark.asyncio
async def test_second_turn_cannot_reuse_old_quality_or_citation():
    """完整历史进入 Prompt，但旧质量和引用不能帮助当前空证据回答事实。"""
    context, state = setup([control()], question='另一商品如何用', intent='售后', answer='旧知识[1]。')
    state['messages'] = [HumanMessage('旧问题', id='old'), workflow_call('query_faq', {'keyword': '旧'}, 'old-faq'),
        ToolMessage(json.dumps(payload(('旧知识',))), tool_call_id='old-faq'), AIMessage('旧知识[1]。'), *state['messages']]
    state['quality'] = {'useful': True, 'reason': '旧判断', 'response_kind': 'knowledge', 'source': None}
    with pytest.raises(ServiceError):
        await run(context, state)
    assert context.model.streams == 0
    assert [m.type for m in context.decision_model.tool_inputs[0]][1:] == ['human', 'ai', 'tool', 'ai', 'human']


@pytest.mark.asyncio
async def test_mock_business_answer_must_keep_mock_meaning():
    """服务器补说明后可完成；共享验证器仍拒绝没有说明的模拟事实。"""
    from app.core.answer_validation import validate_business_answer
    from app.core.evidence import EvidencePacket
    context, state = setup([workflow_call(), control()], answer='您的订单已发货。')
    result, events = await run(context, state)
    assert result['final_answer'] == NOTICE + '您的订单已发货。'
    with pytest.raises(ServiceError):
        validate_business_answer('您的订单已发货。', EvidencePacket({}, [], [], None, 'none'), [{'mock': True}])
    assert len(context.repository.messages) == 2


@pytest.mark.asyncio
@pytest.mark.parametrize('content', ['{"reply_mode":"answer","suggested_actions":[],"text":"secret"}',
    '{"reply_mode":"answer","suggested_actions":["delete"]}', '{"reply_mode":"answer"', 'plain answer'])
async def test_control_schema_is_strict_and_not_answer_text(content):
    """非法字段、动作或破损JSON不能降级为最终正文。"""
    context, state = setup([AIMessage(content, response_metadata={'finish_reason': 'stop'})])
    with pytest.raises(ServiceError):
        await run(context, state)
    assert context.model.streams == 0 and not context.repository.messages


@pytest.mark.asyncio
async def test_new_low_score_faq_refuses_before_final_model():
    """新查到的低分资料不能借业务路由生成事实正文。"""
    context, state = setup([workflow_call('query_faq', {'keyword': '新买'})],
        question='新买的 MH200 如何操作', intent='售后')
    context.faq_repository.retrieve = faq_result(context, payload(('低分操作规则',), score=.3))
    result, events = await run(context, state)
    assert context.model.streams == 0 and not context.sufficiency.calls
    assert result['quality']['useful'] is False and result['suggested_actions'] == ['handoff']
    assert '资料不足' in ''.join(e['data']['text'] for e in events if e['event'] == 'delta')


@pytest.mark.asyncio
async def test_faq_service_fault_preserves_paired_error_state():
    """外部检索故障仍保存匹配错误并计数，但不进入低置信或完成路径。"""
    from app.workflow.agent import tool_node
    context, state = setup([workflow_call('query_faq', {'keyword': '新买'})],
        question='新买的 MH200 如何操作', intent='售后')
    async def failed_retrieve(*args, **kwargs):
        """模拟外部检索服务错误，保留执行器错误归一流程。"""
        raise ServiceError('upstream_error', '模型服务暂时不可用，请稍后重试。', 502)
    context.faq_repository.retrieve = failed_retrieve
    # 单节点调用观察生产 tool_node 的回灌状态，避免整体异常掩盖计数丢失。
    from langgraph.runtime import Runtime
    state['selected'] = workflow_call('query_faq', {'keyword': '新买'})
    update = await tool_node(state, Runtime(context=context))
    assert update['tool_call_count'] == 1
    assert update['messages'][-1].status == 'error' and update['messages'][-1].tool_call_id == 'call_1'
    assert update['tool_error']['code'] == 'upstream_error'
    assert len(context.repository.messages) == 2 and not context.repository.refusals
    from app.workflow.agent import finalize_answer
    with pytest.raises(ServiceError):
        await finalize_answer({**state, **update}, Runtime(context=context))
    assert context.model.streams == 0


@pytest.mark.asyncio
@pytest.mark.parametrize('path', ['mandatory_faq', 'logistics'])
async def test_captured_policy_prose_remains_invalid_control_output(path):
    """离线回灌已授权诊断的真实正文，任何阶段都不能把它强转为控制JSON或最终答复。"""
    captured = AIMessage(
        '关于退货政策，简单来说：\n\n'
        '- **无理由退货**：自签收之日起 7 天内，商品完好、不影响二次销售的，支持无理由退货，定制类、生鲜类商品除外 [1][4]。\n'
        '- **运费承担**：无理由退货的退回运费由买家承担；因质量问题、发错货、少发漏发导致的退换货，运费由平台承担 [10]。\n'
        '- **退款时效**：退货商品经平台核验通过后，退款原路退回，到账时效以平台售后规则为准 [8]。\n'
        '- **不支持退货的商品**：定制类、生鲜类、已拆封的猫砂等消耗品，以及标注「不支持无理由退货」的商品，非质量问题不支持退货 [7]。\n\n'
        '如有具体订单需要处理退货，请提供订单号，我可以帮您进一步查询。',
        response_metadata={'finish_reason': 'stop'}, tool_calls=[], invalid_tool_calls=[])
    replies = [captured] if path == 'mandatory_faq' else [workflow_call('query_logistics'), captured]
    context, state = setup(replies, question='退货政策是什么？' if path == 'mandatory_faq' else '订单 A-42 物流到哪了？',
        intent='退款退货' if path == 'mandatory_faq' else '物流')
    if path == 'mandatory_faq':
        state.update(route='knowledge', tool_call_count=1,
            quality={'useful': True, 'reason': '本轮资料已通过闸门', 'response_kind': 'knowledge', 'source': None})
        state['messages'] += [workflow_call('query_faq', {'keyword': '退货政策'}, 'mandatory'),
            ToolMessage(json.dumps(payload(('当前退货规则',))), tool_call_id='mandatory')]
    events = []
    from tests.test_workflow_agent import graph
    with pytest.raises(ServiceError) as error:
        async for event in graph().astream(state, context=context, stream_mode='custom'):
            events.append(event)
    assert error.value.code == 'invalid_structured_output'
    assert context.decision_model.decisions == (1 if path == 'mandatory_faq' else 2)
    assert context.model.streams == 0 and not context.repository.refusals
    assert all(event['event'] != 'delta' for event in events)
    assert [message.type for message in context.repository.messages] == ([] if path == 'mandatory_faq' else ['ai', 'tool'])


@pytest.mark.asyncio
async def test_captured_factual_logistics_still_rejected_under_chosen_clarification():
    """没有可信用户订单锚点的澄清仍不得包含事实，不因模型自行选单绕过守卫。"""
    from tests.test_workflow_agent import graph
    captured = ('您好，为您查询到订单1001的物流信息（此为模拟演示数据，仅供参考）：'
        '包裹目前已揽收，运单号为MOCK11540677，预计2天内送达。'
        '如需了解更多物流详情，建议以实际物流平台信息为准哦～')
    context, state = setup([workflow_call('query_logistics', {'order_id': '1001'}), control('clarification')],
        question='包裹到哪里了？', intent='物流', answer=captured)
    parsed_modes = []
    with pytest.raises(ServiceError) as error:
        async for kind, data in graph().astream(state, context=context, stream_mode=['updates', 'custom']):
            if kind == 'updates' and 'llm_call' in data and 'reply_mode' in data['llm_call']:
                parsed_modes.append(data['llm_call']['reply_mode'])
    assert error.value.code == 'invalid_answer'
    assert parsed_modes == ['clarification']
    assert '回复模式：clarification' in context.model.stream_inputs[0][0].text
    assert [message.type for message in context.repository.messages] == ['ai', 'tool']
    assert context.model.streams == 1 and context.decision_model.decisions == 2
    assert not context.repository.refusals


@pytest.mark.asyncio
async def test_captured_two_step_business_citations_remain_strictly_rejected():
    """两步业务成功后回灌真实伪造引用正文，仍拒绝完成且保留两组审计配对。"""
    from tests.test_workflow_agent import graph
    captured = ('您好，查询结果如下（均为模拟演示数据）：\n\n'
        '- 订单1001状态：已完成，金额58.94元 [1]\n'
        '- 物流情况：已揽收，运单号 MOCK65694130，预计3天送达 [2]\n\n'
        '如需进一步帮助，请告诉我。')
    context, state = setup([
        workflow_call('query_order', {'order_id': '1001'}),
        workflow_call('query_logistics', {'order_id': '1001'}, 'call_2'), control()],
        question='先查订单1001的状态，再按订单查物流', answer=captured)
    events, modes = [], []
    with pytest.raises(ServiceError) as error:
        async for kind, data in graph().astream(state, context=context, stream_mode=['updates', 'custom']):
            if kind == 'custom':
                events.append(data)
            elif 'llm_call' in data and 'reply_mode' in data['llm_call']:
                modes.append(data['llm_call']['reply_mode'])
    assert error.value.code == 'invalid_answer_citations'
    assert modes == ['answer']
    assert [event['data']['citations'] for event in events if event['event'] == 'citations'] == [[]]
    assert ''.join(event['data']['text'] for event in events if event['event'] == 'delta') == NOTICE + captured
    assert all(event['event'] != 'done' for event in events)
    assert [message.type for message in context.repository.messages] == ['ai', 'tool', 'ai', 'tool']
    assert context.model.streams == 1 and context.decision_model.decisions == 3
    assert not context.repository.refusals


@pytest.mark.asyncio
async def test_recorded_step_question_particle_completes_agent_clarification():
    """原样回灌实际缺型号追问，真实Agent必须正常完成且不查询工具或写低置信池。"""
    answer = '可以的，您买的是什么商品或型号？具体在哪一步不会操作呢？'
    context, state = setup([control('clarification')], question='新买的商品不太会用，能帮我看看吗？',
        intent='售后', answer=answer)
    result, events = await run(context, state)
    assert result['final_answer'] == answer
    assert result['reply_mode'] == 'clarification'
    assert result['tool_call_count'] == 0
    assert not context.repository.messages and not context.repository.refusals
    assert events[-1] == {'event': 'delta', 'data': {'text': answer}}
@pytest.mark.asyncio
@pytest.mark.parametrize('business_result', [False, True])
@pytest.mark.parametrize('tail', ['', '可以退货。', '[99]'])
async def test_parent_refund_gate_then_clarification(business_result, tail):
    """真实父图过政策闸后可追问；业务模拟结果不强迫纯追问声明，事实及伪引用仍拒绝。"""
    from langgraph.checkpoint.memory import InMemorySaver
    from app.workflow.agent import build_agent_graph
    from app.workflow.graph import build_workflow_graph
    from tests.test_after_sales_workflow import context as after_sales_context
    decision = control('clarification')
    decision.content = json.dumps({'reply_mode': 'clarification', 'suggested_actions': [],
        'refund_decision': 'ineligible', 'decision_reason': '当前诉求还需确认适用条件'})
    replies = ([workflow_call()] if business_result else []) + [decision]
    context, state = setup(replies, question='订单1001是否符合退货政策',
        intent='退款退货', answer='请提供适用条件。' + tail)
    provided = after_sales_context(data=payload(('当前退货规则',)))
    context.order_provider, context.user_id = provided.order_provider, provided.user_id
    context.expander, context.workflow_retriever = provided.expander, provided.workflow_retriever
    parent = build_workflow_graph(build_agent_graph(), checkpointer=InMemorySaver())
    events = []
    async def consume():
        """消费父子图实际事件，保留根完成与SQL提交边界。"""
        async for namespace, event in parent.astream(state, {'configurable': {'thread_id': 'session'}},
                context=context, stream_mode='custom', subgraphs=True):
            events.append(event)
        return (await parent.aget_state({'configurable': {'thread_id': 'session'}})).values
    if tail:
        with pytest.raises(ServiceError):
            await consume()
        assert not any(m.type == 'ai' and not m.tool_calls for m in context.repository.messages)
    else:
        result = await consume()
        assert result['turn_status'] == 'completed' and result['final_answer'] == '请提供适用条件。'
        assert result['citations'] == [] and result['quality']['response_kind'] == 'clarification'
        assert [e['data']['citations'] for e in events if e['event'] == 'citations'] == [[]]
    assert context.sufficiency.calls
    original = json.loads(context.repository.messages[3].content)
    assert original['matches'][0]['answer'] == '当前退货规则' and 'n' not in original['matches'][0]
