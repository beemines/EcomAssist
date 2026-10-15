"""严格扩写的原始 JSON、预算与取消边界；模型只在外部边界替换。"""
import asyncio
import importlib.util
import json
from datetime import date

import httpx
import pytest
from langchain_core.messages import AIMessage

from app.core.errors import InputTooLong, ServiceError
from app.orders.types import OrderSnapshot
from tests.workflow_fakes import ScriptedWorkflowModel


def snapshot():
    """未知商品完好状态的固定演示订单，不补商品质量事实。"""
    return OrderSnapshot(user_id='demo-user', order_id='1001', product_id='p1',
        product_name='星河耳机', model='MH-LP200', category='电子商品', status='已签收',
        amount_cents=29900, signed_at=date(2026, 10, 13), fixture_version='v1')


def expander(content=None, *, finish='stop', budget=8000, usage=True):
    """保留真实扩写和 Schema 校验，只预置外部响应。"""
    assert importlib.util.find_spec('app.workflow.expansion'), 'strict expander is missing'
    from app.workflow.expansion import QueryExpander
    reply = AIMessage(content if content is not None else json.dumps(
        {'queries': ['订单1001能退吗？', 'MH-LP200退货适用条件']}),
        response_metadata={'finish_reason': finish},
        usage_metadata={'input_tokens': 12, 'output_tokens': 8, 'total_tokens': 20} if usage else None)
    model = ScriptedWorkflowModel(intent_replies=[reply])
    return QueryExpander(model, input_budget=budget, timeout_seconds=1), model


async def test_expansion_preserves_question_and_uses_order_facts_with_usage():
    """首条不能改写，订单事实以完整 JSON 提供且费用沿理解器口径。"""
    service, model = expander()
    result = await service.expand('订单1001能退吗？', snapshot())
    assert result == ('订单1001能退吗？', 'MH-LP200退货适用条件')
    request = json.loads(model.intent_inputs[0][-1].content)
    assert request == {'question': '订单1001能退吗？', 'order': snapshot().model_dump(mode='json')}
    assert service.usage == {'actual': 20, 'estimated': 0, 'actual_calls': 1, 'estimated_calls': 0}


@pytest.mark.parametrize('content', [
    '{"standard":"订单1001能退吗？","expansions":[]}',
    '{"queries":["订单1001能退吗？","退货条件"],"reason":"额外字段"}',
    '{"queries":["订单1001能退吗？"]}',
    '{"queries":["订单1001能退吗？","a","b","c"]}',
    '{"queries":["变更问题","退货条件"]}',
    '{"queries":["订单1001能退吗？",5]}',
    '{"queries":["订单1001能退吗？","   "]}',
    '{"queries":["订单1001能退吗？","订单1001能退吗？ "]}',
    '{"queries":["订单1001能退吗？","订单1001 能退吗？"]}',
    '{"queries":["订单1001能退吗？","' + '字' * 513 + '"]}',
    '{"queries":["订单1001能退吗？","退货条件"]',
])
async def test_expansion_wrong_schema_not_degraded(content):
    """错误新旧协议、数量、重复、改写及修复 JSON 都不能偷偷成功。"""
    service, model = expander(content)
    with pytest.raises(ServiceError) as caught:
        await service.expand('订单1001能退吗？', snapshot())
    assert caught.value.code == 'invalid_structured_output' and model.intents == 1


async def test_whitespace_dedup_keeps_two_valid_queries_and_exact_first():
    """归一空白只用于判重，保留原始首条和足够的独立角度。"""
    service, _ = expander(json.dumps({'queries': ['订单1001能退吗？', '退货  条件', '退货 条件']}))
    assert await service.expand('订单1001能退吗？', snapshot()) == ('订单1001能退吗？', '退货  条件')


@pytest.mark.parametrize('finish', ['length', 'content_filter', None])
async def test_expansion_rejects_nonstop(finish):
    """结束状态无效时拒绝解析对象，不能回退。"""
    service, _ = expander(finish=finish)
    with pytest.raises(ServiceError) as caught:
        await service.expand('订单1001能退吗？', snapshot())
    assert caught.value.code == 'invalid_structured_output'


async def test_expansion_estimates_missing_usage_and_resets_per_call():
    """无 usage 时计入完整输出额度，下一次预算拒绝前清零旧费用。"""
    service, model = expander(usage=False)
    await service.expand('订单1001能退吗？', snapshot())
    assert service.usage['estimated'] > 2048 and service.usage['estimated_calls'] == 1
    service.input_budget = 1
    with pytest.raises(InputTooLong):
        await service.expand('订单1001能退吗？', snapshot())
    assert model.intents == 1 and not any(service.usage.values())


@pytest.mark.parametrize('failure,code', [(httpx.ReadTimeout('secret'), 'upstream_timeout'),
                                        (RuntimeError('secret'), 'upstream_error')])
async def test_expansion_transport_failure_never_retries(failure, code):
    """运输故障安全归一，且不重复付费请求。"""
    from app.workflow.expansion import QueryExpander
    model = ScriptedWorkflowModel(intent_replies=[failure])
    with pytest.raises(ServiceError) as caught:
        await QueryExpander(model, input_budget=8000, timeout_seconds=1).expand('能退吗', snapshot())
    assert caught.value.code == code and model.intents == 1 and 'secret' not in str(caught.value)


async def test_expansion_timeout_and_caller_cancellation_stop_model():
    """单次期限与外部取消均终止模型等待，不返回残缺扩写。"""
    from app.workflow.expansion import QueryExpander
    class Waiting:
        """阻塞外部模型入口，以事件定位取消。"""
        def __init__(self):
            """记录请求开始与停止。"""
            self.started, self.stopped = asyncio.Event(), asyncio.Event()
        def with_structured_output(self, schema, **kwargs):
            """保留绑定接口。"""
            return self
        async def ainvoke(self, messages):
            """等待调用方取消。"""
            self.started.set()
            try:
                await asyncio.Event().wait()
            finally:
                self.stopped.set()
    model = Waiting()
    with pytest.raises(ServiceError) as caught:
        await QueryExpander(model, input_budget=8000, timeout_seconds=.01).expand('能退吗', snapshot())
    assert caught.value.code == 'upstream_timeout' and model.stopped.is_set()
    model = Waiting()
    task = asyncio.create_task(QueryExpander(model, input_budget=8000, timeout_seconds=1).expand('能退吗', snapshot()))
    await model.started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert model.stopped.is_set()


@pytest.mark.parametrize('budget,timeout', [(True, 1), (0, 1), (1, True), (1, 0), (1, float('nan'))])
def test_expansion_rejects_invalid_limits(budget, timeout):
    """直接构造也不能绕过有限正预算和期限。"""
    from app.workflow.expansion import QueryExpander
    with pytest.raises(ValueError):
        QueryExpander(ScriptedWorkflowModel(), input_budget=budget, timeout_seconds=timeout)
