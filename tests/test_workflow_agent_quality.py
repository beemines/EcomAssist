"""新证据必须过闸，澄清不能夹带政策或状态，历史不能冒充本轮证据。"""
import json

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.core.errors import ServiceError
from tests.test_evidence import payload
from tests.test_workflow_agent import control, run, setup
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
    assert 'query_faq' not in {t.name for t in context.decision_model.bound_tools[0]}
    assert result['tool_call_count'] == 1 and not context.faq_repository.calls
    assert result['citations'][0]['answer'] == '当前规则'


@pytest.mark.asyncio
@pytest.mark.parametrize('tail', ['可以退货', '已发货', '三天到账', '可以退货吗'])
async def test_clarification_cannot_smuggle_facts(tail):
    """逐句追问守卫拒绝未验证政策/状态/承诺，即使有问号也不放行。"""
    context, state = setup([control('clarification')], question='新买的商品不太会用', intent='售后',
        answer='可以的，你买的是什么商品或型号？具体在哪一步不会操作？' + tail + '。')
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
    """模拟工具结果不能被模型表述为真实订单已发货。"""
    context, state = setup([workflow_call(), control()], answer='您的订单已发货。')
    with pytest.raises(ServiceError):
        await run(context, state)
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
