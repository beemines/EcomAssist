"""外层分流验证：错误分流会触发不应发生的检索、拒答或动作。"""
import importlib
import json
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, END, StateGraph

from app.workflow.runtime import WorkflowRuntime
from app.workflow.state import WorkflowState, new_turn_state
from tests.workflow_fakes import apply_workflow_update, ScriptedWorkflowModel, workflow_call, workflow_runtime


def implementation(name):
    """缺失实现变为断言 RED，不让导入异常遮蔽任务行为。"""
    try:
        return importlib.import_module('app.workflow.' + name)
    except ImportError:
        pytest.fail('workflow ' + name + ' implementation missing')


def outer_graph():
    """用受控真实子图承接业务；外层节点、边与持久化使用生产实现。"""
    async def agent(state, runtime):
        """只产生受控答案，通过消息表和节点轨迹证明是否进入子图。"""
        return {'final_answer': '受控业务答案', 'reply_mode': 'answer'}
    child = StateGraph(WorkflowState, context_schema=WorkflowRuntime)
    child.add_node('controlled_agent', agent)
    child.add_edge(START, 'controlled_agent')
    child.add_edge('controlled_agent', END)
    return implementation('graph').build_workflow_graph(child.compile(), checkpointer=InMemorySaver())


async def run_outer(context, question='退货政策是什么？'):
    """采集真实父图更新节点，避免生产代码中添加测试专用追踪。"""
    state = new_turn_state(conversation_id='1', user_message_id=7, raw_question=question,
        category='售后', messages=[HumanMessage(question)])
    trace, updates = [], dict(state)
    async for event in outer_graph().astream(state, {'configurable': {'thread_id': '1'}},
        context=context, stream_mode='updates'):
        for name, update in event.items():
            trace.append(name)
            apply_workflow_update(updates, update)
    return trace, updates


def test_all_seven_routes():
    """错把政策或售后分到别的路径会打破七类固定契约。"""
    route_intent = implementation('intent').route_intent
    assert [route_intent(x) for x in ['商品咨询','退款退货','物流','订单','售后','投诉','闲聊']] == [
        'knowledge','after_sales','business','business','after_sales','complaint','social']


def test_greeting_with_order_is_not_social():
    """问候子串命中不能吞掉订单业务。"""
    social_fast_path = implementation('intent').social_fast_path
    assert social_fast_path('你好') and not social_fast_path('你好，订单1001到哪了')


@pytest.mark.asyncio
@pytest.mark.parametrize('intent', ['物流', '订单'])
async def test_business_empty_evidence_bypasses_gate(intent):
    """业务无证据仍进入 Agent，不能被知识闸提前拒答。"""
    context = workflow_runtime(intent=intent)
    trace, state = await run_outer(context, '新买的商品不太会用，能帮我看看吗？')
    assert trace == ['resolve_reference','classify_intent','agent','log_response']
    assert len(context.faq_repository.calls) == len(context.sufficiency.calls) == 0
    assert state['final_answer'] == '受控业务答案' and not context.repository.refusals


@pytest.mark.asyncio
async def test_complaint_has_two_options_no_tools():
    """投诉只安抚和建议；自动调用任何工具或工单都会破坏此行为。"""
    context = workflow_runtime(intent='投诉')
    trace, state = await run_outer(context, '我要投诉订单1001一直不发货')
    assert trace == ['resolve_reference','classify_intent','complaint_response','log_response']
    assert state['suggested_actions'] == ['handoff','create_ticket']
    assert not context.faq_repository.calls and len(context.repository.messages) == 1
    assert context.repository.messages[0].tool_calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize('question', ['你好', '谢谢', '再见'])
async def test_social_whole_turn_uses_no_model(question):
    """明确整句闲聊不调用分类或 Agent，固定话术仍提交数据库。"""
    context = workflow_runtime()
    trace, state = await run_outer(context, question)
    assert trace == ['resolve_reference','classify_intent','social_response','log_response']
    assert context.model.intents == context.model.decisions == context.model.streams == 0
    assert state['final_answer'] == '您好，我是 MewHelp 智能客服，可以帮您查询订单、物流以及商品和售后问题。'


@pytest.mark.asyncio
@pytest.mark.parametrize('label,confidence', [('其他', 0.95), ('退款退货', 0.69)])
async def test_other_is_fixed_exit_without_retrieval_or_actions(label, confidence):
    """未知诉求和低置信度不查工具、不进入知识不足池，只提交澄清提示。"""
    context = workflow_runtime()
    context.intent_model = ScriptedWorkflowModel(intent_replies=[AIMessage(json.dumps(
        {'intent': label, 'confidence': confidence}), response_metadata={'finish_reason': 'stop'})])
    trace, state = await run_outer(context, '蓝色星期八能替我给月亮签收吗？')
    assert trace == ['resolve_reference','classify_intent','other_response','log_response']
    assert state['intent'] == '其他' and state['route'] == 'other'
    assert state['final_answer'] and state['suggested_actions'] == []
    assert not context.faq_repository.calls and not context.sufficiency.calls
    assert not context.repository.refusals and len(context.repository.messages) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize('body,finish', [(' {"intent":"未知"}', 'stop'),
    ('{"intent":"订单","extra":1}', 'stop'), ('{"intent":"订单"', 'stop'),
    ('{"intent":"订单"}', 'length'), ('{"intent":"订单"}', None)])
async def test_classifier_rejects_illegal_json_and_finish(body, finish):
    """非法上游输出必须服务错误，不能降级成另一类意图。"""
    classifier = implementation('intent').IntentClassifier
    from app.core.errors import ServiceError
    model = ScriptedWorkflowModel(intent_replies=[AIMessage(body, response_metadata={'finish_reason': finish})])
    with pytest.raises(ServiceError) as caught:
        await classifier(model, input_budget=8000, timeout_seconds=1).classify('订单1001')
    assert caught.value.code == 'invalid_structured_output'


@pytest.mark.asyncio
async def test_classifier_rejects_tool_output_without_routing():
    """带工具申请的分类响应不成为合法意图，即使 JSON 文本看似有效。"""
    classifier = implementation('intent').IntentClassifier
    from app.core.errors import ServiceError
    reply = workflow_call()
    reply.content = '{"intent":"订单"}'
    reply.response_metadata['finish_reason'] = 'stop'
    model = ScriptedWorkflowModel(intent_replies=[reply])
    with pytest.raises(ServiceError) as caught:
        await classifier(model, input_budget=8000, timeout_seconds=1).classify('订单1001')
    assert caught.value.code == 'invalid_structured_output'


@pytest.mark.asyncio
async def test_classifier_preserves_original_and_records_actual_usage():
    """分类输入原样透传，合法 usage 优先于最大输出估算。"""
    classifier = implementation('intent').IntentClassifier
    reply = AIMessage('{"intent":"售后","confidence":0.95}', response_metadata={'finish_reason': 'stop'},
        usage_metadata={'input_tokens': 12, 'output_tokens': 8, 'total_tokens': 20})
    model = ScriptedWorkflowModel(intent_replies=[reply])
    service = classifier(model, input_budget=8000, timeout_seconds=1)
    question = '  新买的商品不太会用\n能帮我看看吗？  '
    result = await service.classify(question)
    assert result.intent == result.raw_intent == '售后' and result.confidence == 0.95
    assert model.intent_inputs[0][-1].content == question
    assert service.usage == {'actual': 20, 'estimated': 0, 'actual_calls': 1, 'estimated_calls': 0}


def test_new_turn_drops_previous_evidence():
    """新输入不会复用旧证据、动作、终态或计数。"""
    old = new_turn_state(conversation_id='1', user_message_id=7, raw_question='旧问题', category=None,
        messages=[HumanMessage('旧问题')])
    old.update(evidence_payload={'matches': [1]}, suggested_actions=['create_ticket'], final_answer='旧答复',
        final_message_id='8', tool_call_count=4, decision_count=5, turn_status='completed')
    new = new_turn_state(conversation_id='1', user_message_id=9, raw_question='新问题', category=None,
        messages=[HumanMessage('新问题')])
    assert new['evidence_payload'] == {} and new['suggested_actions'] == []
    assert new['final_answer'] is new['final_message_id'] is None
    assert new['tool_call_count'] == new['decision_count'] == 0 and new['turn_status'] == 'pending'


def test_intent_cases_have_unique_ids_and_all_buckets():
    """离线只验证标注覆盖，不用关键词替代真实模型质量评测。"""
    path = Path(__file__).parents[1] / 'evals/workflow_intent_cases.jsonl'
    assert path.exists(), 'intent validation cases missing'
    cases = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
    assert len({case['id'] for case in cases}) == len(cases) >= 24
    for intent in ['商品咨询','退款退货','物流','订单','售后','投诉','闲聊']:
        assert sum(case['expected_intent'] == intent for case in cases) >= 3
    for case in cases:
        expected = 'after_sales' if case['expected_intent'] in ('退款退货', '售后') else case['expected_route']
        assert implementation('intent').route_intent(case['expected_intent']) == expected
    assert any(case['should_clarify'] and case['expected_intent'] == '售后' for case in cases)
