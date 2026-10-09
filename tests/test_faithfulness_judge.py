import importlib
import json
import httpx
import pytest
from app.core.llm import create_model
from app.core.evidence import Citation
from app.core.errors import ServiceError, InputTooLong
from tests.fakes import fake_settings


async def judge(content, *, budget=16000, finish='stop'):
    """返回预设裁判结论或模拟非法上游，隔离付费请求。"""
    try:
        cls = importlib.import_module('evals.faithfulness').FaithfulnessJudge
    except ImportError:
        pytest.fail('faithfulness judge is missing')
    def handle(request):
        """模拟完整上游HTTP响应，保留真实请求序列化和结构化解析。"""
        return httpx.Response(200, json={'id': 'synthetic', 'object': 'chat.completion', 'created': 0,
            'model': 'fake-chat', 'choices': [{'index': 0, 'finish_reason': finish,
                'message': {'role': 'assistant', 'content': content}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as http:
        model = create_model(fake_settings(), http_async_client=http)
        try:
            return await cls(model, input_budget=budget).judge('邮费？', '邮费8元[1]。',
                [Citation(1, '10', '配送', '邮费？', '邮费8元。')])
        finally:
            await model.root_async_client.close()
            model.root_client.close()


async def test_supported_and_unsupported_claims_have_fractional_score():
    """验证逐断言支持比例，合法角标不能替代证据支持判定。"""
    result = await judge(json.dumps({'claims': [{'claim': '邮费8元', 'support': True, 'reason': '证据1'},
                                               {'claim': '明天到货', 'support': False, 'reason': '无依据'}]}))
    assert result['score'] == .5 and result['claims'][1]['support'] is False


async def test_refusal_without_claims_is_not_perfect_faithfulness():
    """验证无事实断言忠实度不适用，不伪装成百分百。"""
    assert (await judge('{"claims":[]}'))['score'] is None


@pytest.mark.parametrize('content,finish', [('{"claims":[]', 'stop'), ('{"claims":[],"score":1}', 'stop'),
    ('{"claims":[{"claim":"x","support":"false","reason":"x"}]}', 'stop'), ('{"claims":[]}', 'length')])
async def test_judge_invalid_raw_json_and_finish_are_errors(content, finish):
    """验证原始坏JSON、额外字段、错误类型和截断全部关闭裁判结果。"""
    with pytest.raises(ServiceError):
        await judge(content, finish=finish)


async def test_budget_is_enforced_before_judging():
    """验证输入预算超限在发送裁判请求前失败。"""
    with pytest.raises(InputTooLong):
        await judge('{"claims":[]}', budget=1)
