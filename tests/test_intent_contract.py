"""意图协议边界：只替换上游网络，真实校验器负责拒绝坏输出。"""
import pytest
from langchain_core.messages import AIMessage

from app.core.errors import ServiceError
from app.workflow.intent import IntentClassifier
from tests.workflow_fakes import ScriptedWorkflowModel


def classifier(body, finish='stop'):
    """以未经修复的原始文本构造受控上游边界。"""
    return IntentClassifier(ScriptedWorkflowModel(intent_replies=[AIMessage(body,
        response_metadata={'finish_reason': finish})]), input_budget=8000, timeout_seconds=1)


@pytest.mark.asyncio
@pytest.mark.parametrize('confidence,effective', [(0.69, '其他'), (0.70, '退款退货'), (1, '退款退货'), (0, '其他')])
async def test_intent_threshold_preserves_raw_label(confidence, effective):
    """阈值前后保留原始标签，避免有效其他覆盖模型审计结果。"""
    result = await classifier('{"intent":"退款退货","confidence":' + str(confidence) + '}').classify('申请退货')
    assert (result.raw_intent, result.intent, result.confidence) == ('退款退货', effective, confidence)


@pytest.mark.asyncio
@pytest.mark.parametrize('body,finish', [
    ('{"intent":"订单"}', 'stop'),
    ('{"intent":"订单","confidence":0.9,"query":"订单"}', 'stop'),
    ('{"intent":"订单","confidence":"0.9"}', 'stop'),
    ('{"intent":"订单","confidence":true}', 'stop'),
    ('{"intent":"订单","confidence":NaN}', 'stop'),
    ('{"intent":"订单","confidence":Infinity}', 'stop'),
    ('{"intent":"订单","confidence":-0.01}', 'stop'),
    ('{"intent":"订单","confidence":1.01}', 'stop'),
    ('{"intent":"订单","confidence":0.9', 'stop'),
    ('{"intent":"订单","confidence":0.9}', 'length'),
    ('{"intent":"订单","confidence":0.9}', None),
])
async def test_intent_exact_fields_and_finite_confidence(body, finish):
    """缺字段、强转、非有限数及截断必须失败，不能变成其他意图。"""
    with pytest.raises(ServiceError) as caught:
        await classifier(body, finish).classify('查询订单1001')
    assert caught.value.code == 'invalid_structured_output'


@pytest.mark.asyncio
@pytest.mark.parametrize('service_name', ['classifier', 'understanding'])
@pytest.mark.parametrize('sdk_error', [False, True])
async def test_control_truncation_is_distinguishable_without_raw_output(service_name, sdk_error):
    """评估能区分截断和普通坏JSON，且异常不携带上游正文。"""
    from openai import LengthFinishReasonError
    from openai.types.chat import ChatCompletion
    from app.workflow.understanding import QueryUnderstanding
    reply = LengthFinishReasonError(completion=ChatCompletion(id='synthetic', model='synthetic',
        object='chat.completion', created=0, choices=[])) if sdk_error else AIMessage('private upstream text',
        response_metadata={'finish_reason': 'length'})
    model = ScriptedWorkflowModel(intent_replies=[reply])
    service = (IntentClassifier if service_name == 'classifier' else QueryUnderstanding)(
        model, input_budget=8000, timeout_seconds=1)
    with pytest.raises(ServiceError) as caught:
        if service_name == 'classifier':
            await service.classify('订单1001')
        else:
            await service.resolve('订单1001', [])
    assert caught.value.code == 'invalid_structured_output'
    assert caught.value.finish_reason == 'length'
    assert 'private upstream text' not in str(caught.value)
