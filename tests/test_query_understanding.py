# 查询理解协议测试：真实 LangChain 解析器与原始 HTTP 回包共同覆盖失败关闭。
import asyncio
import importlib
import json

import httpx
import pytest
from langchain_core.messages import AIMessage
from pydantic import ValidationError

from app.core.errors import InputTooLong, ServiceError
from app.core.llm import create_model
from tests.fakes import fake_settings


def planner_type():
    try:
        return importlib.import_module('app.retrieval.query').QueryPlanner
    except ImportError:
        pytest.fail('query planner is missing')


# 用完整 Chat Completions 回包驱动实际 JSON 解析器，避免测试替身替我们修补原文。
async def query(raw, content, *, finish='stop', budget=10000):
    requests = []
    def handle(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, json={
            'id': 'synthetic', 'object': 'chat.completion', 'created': 0, 'model': 'fake-chat',
            'choices': [{'index': 0, 'finish_reason': finish,
                         'message': {'role': 'assistant', 'content': content}}],
        })
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as http:
        model = create_model(fake_settings(), http_async_client=http)
        try:
            result = await planner_type()(model, budget).plan(raw)
            return result, requests
        finally:
            model.client._client.close()


async def test_single_turn_json_request_and_valid_query_plan():
    result, requests = await query('退货咋办', '{"standard":"退货如何办理？","expansions":["退货 申请流程"]}')
    assert result.standard == '退货如何办理？'
    assert result.expansions == ['退货 申请流程']
    assert len(requests) == 1
    assert requests[0]['response_format'] == {'type': 'json_object'}
    assert requests[0]['max_tokens'] == 512
    assert requests[0]['messages'][-1] == {'role': 'user', 'content': '退货咋办'}


@pytest.mark.parametrize('content,finish', [
    ('{"standard":"售后？","expansions":[]', 'stop'),
    ('{"standard":"售后？","expansions":[],"answer":"可以退款"}', 'stop'),
    ('{"standard":"售后？","expansions":[]}', 'length'),
    ('{"standard":"售后？","expansions":[]}', 'content_filter'),
    ('{"standard":"售后？","expansions":[]}', None),
    ('{"standard":123,"expansions":[]}', 'stop'),
    ('{"standard":"售后？","expansions":["1","2","3","4","5"]}', 'stop'),
    (json.dumps({'standard': '问' * 513, 'expansions': []}), 'stop'),
    (json.dumps({'standard': '问', 'expansions': ['词' * 65]}), 'stop'),
    ('{"standard":"   ","expansions":[]}', 'stop'),
])
async def test_rejects_unmodified_raw_schema_errors_and_nonstop(content, finish):
    with pytest.raises(ServiceError) as caught:
        await query('售后？', content, finish=finish)
    assert caught.value.code == 'invalid_structured_output'


@pytest.mark.parametrize('raw,standard', [
    ('星河 AC-12 的退货条件？', '星河 AC-13 的退货条件？'),
    ('满299元才免运费吗？', '满199元才免运费吗？'),
    ('不要换货，只要退款', '换货流程是什么？'),
    ('未拆封而且购买7天内能退款吗？', '商品拆封后能退款吗？'),
    ('星河 AC-12 能退吗？', '远山 AC-12 能退吗？'),
    ('可以退货吗？', '不可以退货吗？'),
    ('星河耳机怎么退货？', '远山耳机怎么退货？'),
])
async def test_conflicting_rewrite_preserves_original_question(raw, standard):
    result, _ = await query(raw, json.dumps({'standard': standard, 'expansions': ['售后 退款']}))
    assert result.standard == raw
    assert len(result.expansions) <= 4


async def test_conflicting_expansions_cannot_replace_query_constraints():
    raw = '不要换货，星河 AC-12 购买7天内只退款'
    result, _ = await query(raw, json.dumps({'standard': raw, 'expansions': ['星河 AC-13 换货', '超过7天 换货']}))
    assert result.standard == raw
    assert result.expansions == []


@pytest.mark.parametrize('standard,expansions', [
    ('星河退货如何办理？', ['退货流程']),
    ('退货如何办理？', ['星河退货流程']),
])
async def test_new_brand_cannot_enter_standard_or_expansions(standard, expansions):
    result, _ = await query('退货咋办', json.dumps({'standard': standard, 'expansions': expansions}))
    assert '星河' not in result.standard
    assert all('星河' not in text for text in result.expansions)


async def test_parsed_result_must_match_untouched_raw_json():
    from app.retrieval.types import QueryPlan
    class Model:
        def with_structured_output(self, schema, **kwargs):
            return self
        async def ainvoke(self, messages):
            return {'raw': AIMessage('{"standard":"退货","expansions":[]}', response_metadata={'finish_reason': 'stop'}),
                    'parsed': QueryPlan(standard='退款', expansions=[]), 'parsing_error': None}
    with pytest.raises(ServiceError) as caught:
        await planner_type()(Model(), 10000).plan('退货')
    assert caught.value.code == 'invalid_structured_output'


@pytest.mark.parametrize('failure,code', [(httpx.ReadTimeout('synthetic'), 'upstream_timeout'),
                                        (RuntimeError('private detail'), 'upstream_error')])
async def test_model_transport_errors_are_sanitized_and_not_retried(failure, code):
    class Model:
        calls = 0
        def with_structured_output(self, schema, **kwargs):
            return self
        async def ainvoke(self, messages):
            self.calls += 1
            raise failure
    model = Model()
    with pytest.raises(ServiceError) as caught:
        await planner_type()(model, 10000).plan('退货')
    assert caught.value.code == code and model.calls == 1
    assert 'private detail' not in str(caught.value)


@pytest.mark.parametrize('timeout', [True, 0, float('inf'), float('nan')])
def test_direct_planner_timeout_validation(timeout):
    with pytest.raises(ValueError):
        planner_type()(WaitingModel(), 10000, timeout=timeout)


async def test_budget_rejects_before_model_request():
    with pytest.raises(InputTooLong):
        await query('问' * 200, '{"standard":"问","expansions":[]}', budget=1)


class WaitingModel:
    def __init__(self):
        self.started = asyncio.Event()
        self.cancelled = asyncio.Event()
        self.calls = 0

    def with_structured_output(self, schema, *, method, include_raw):
        assert (method, include_raw) == ('json_mode', True)
        return self

    async def ainvoke(self, messages):
        self.calls += 1
        self.started.set()
        try:
            await asyncio.Event().wait()
        finally:
            self.cancelled.set()


async def test_outer_deadline_cancels_model_without_retry():
    model = WaitingModel()
    with pytest.raises(ServiceError) as caught:
        await planner_type()(model, 10000, timeout=0.01).plan('售后？')
    assert caught.value.code == 'upstream_timeout'
    assert model.cancelled.is_set() and model.calls == 1


async def test_caller_cancellation_propagates():
    model = WaitingModel()
    task = asyncio.create_task(planner_type()(model, 10000).plan('售后？'))
    await model.started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert model.cancelled.is_set() and model.calls == 1


@pytest.mark.parametrize('field,value', [
    ('query_timeout_seconds', True), ('query_timeout_seconds', 0),
    ('query_timeout_seconds', float('nan')), ('rerank_timeout_seconds', False),
    ('rerank_timeout_seconds', float('inf')), ('rerank_min_score', True),
    ('rerank_min_score', float('nan')), ('rerank_model', 'other'),
])
def test_invalid_new_retrieval_settings_are_rejected(field, value):
    with pytest.raises(ValidationError):
        fake_settings(**{field: value})


def test_calibration_can_load_settings_without_threshold():
    assert fake_settings().rerank_min_score is None
