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


# 加载实际查询理解类，缺失接口时给出明确失败而非隐式跳过。
def planner_type():
    try:
        return importlib.import_module('app.retrieval.query').QueryPlanner
    except ImportError:
        pytest.fail('query planner is missing')


# 用完整 Chat Completions 回包驱动实际 JSON 解析器，避免测试替身替我们修补原文。
async def query(raw, content, *, finish='stop', budget=10000):
    requests = []
    # 捕获真实模型请求体并提供完整Chat Completions回包，驱动SDK原始解析。
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


# 核对单轮JSON请求、合法查询计划、约束保留及确定性同义表达。
async def test_single_turn_json_request_and_valid_query_plan():
    result, requests = await query('退货咋办', '{"standard":"退货如何办理？","expansions":["退货 申请流程"]}')
    assert result.standard == '退货如何办理？'
    assert result.expansions == ['退货 申请流程']
    assert len(requests) == 1
    assert requests[0]['response_format'] == {'type': 'json_object'}
    assert requests[0]['max_tokens'] == 512
    assert requests[0]['messages'][-1] == {'role': 'user', 'content': '退货咋办'}


# 正向语义断言能发现只返回合法原话、却未完成口语归一或同义扩展的退化。
@pytest.mark.parametrize('raw,standard,expansions,want_standard,want_expansion', [
    ('物流咋查啊', '物流如何查询？', ['快递查询方法'], '物流如何查询？', '快递查询方法'),
    ('退款咋办', '退钱如何办理？', ['退钱申请流程'], '退款如何办理？', '退钱申请流程'),
    ('退钱咋办', '退款如何办理？', ['退钱办理流程'], '退款如何办理？', '退钱办理流程'),
])
async def test_safe_colloquial_rewrite_and_retrieval_synonym_are_preserved(raw, standard, expansions, want_standard, want_expansion):
    result, _ = await query(raw, json.dumps({'standard': standard, 'expansions': expansions}))
    assert result.standard == want_standard
    assert want_expansion in result.expansions


# 模型原样复述已知口语时仍执行安全归一化和同义扩展。
@pytest.mark.parametrize('raw,want_standard,want_expansion', [
    ('物流咋查啊', '物流如何查询？', '快递如何查询？'),
    ('退款咋办', '退款如何办理？', '退钱如何办理？'),
    ('退钱咋办', '退款如何办理？', '退钱如何办理？'),
])
async def test_valid_model_echo_still_normalizes_known_phrase_and_generates_synonym(raw, want_standard, want_expansion):
    result, requests = await query(raw, json.dumps({'standard': raw, 'expansions': []}))
    assert result.standard == want_standard and result.standard != raw
    assert want_expansion in result.expansions
    assert requests[0]['messages'][-1]['content'] == raw


# 全角或异文数字与型号冲突时保留完整原话，不悄然改变业务限制。
@pytest.mark.parametrize('raw,standard', [
    ('满２９９元免运费吗？', '满１９９元免运费吗？'),
    ('星河 ＡＣ－１２ 如何查询？', '星河 ＡＣ－１３ 如何查询？'),
    ('星河 ＡＢ 耳机？', '星河 ＣＤ 耳机？'),
    ('满٢٩٩元免运费吗？', '满١٩٩元免运费吗？'),
])
async def test_unicode_numeric_and_model_anchor_conflicts_preserve_original(raw, standard):
    result, _ = await query(raw, json.dumps({'standard': standard, 'expansions': [standard]}))
    assert result.standard == raw
    assert result.expansions == []


# 未知品牌或意图漂移不得进入安全同义路径，防止改写篡改查询。
@pytest.mark.parametrize('raw,standard,expansion', [
    ('退钱牌耳机退款咋办', '退款牌耳机退钱如何办理？', '退钱申请流程'),
    ('星河耳机退款咋办', '星河耳机退钱如何办理？', '星河耳机退钱申请流程'),
    ('退款咋办', '退款如何办理？', '退货申请流程'),
    ('退款咋办', '退款怎么查询？', '退款查询流程'),
])
async def test_unknown_identity_or_changed_intent_cannot_enter_safe_synonym_path(raw, standard, expansion):
    result, _ = await query(raw, json.dumps({'standard': standard, 'expansions': [expansion]}))
    if raw != '退款咋办' or standard == '退款怎么查询？':
        assert result.standard == raw and result.expansions == []
    else:
        assert expansion not in result.expansions


# 原始JSON不合法、超限、额外字段或非stop均拒绝，不能靠解析结果修补。
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


# 型号、价格、否定和售后条件冲突的标准问法应回退本轮原话。
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


# 冲突的扩展词不能替换原话中的商品身份与限制条件。
async def test_conflicting_expansions_cannot_replace_query_constraints():
    raw = '不要换货，星河 AC-12 购买7天内只退款'
    result, _ = await query(raw, json.dumps({'standard': raw, 'expansions': ['星河 AC-13 换货', '超过7天 换货']}))
    assert result.standard == raw
    assert result.expansions == []


# 改写及扩展不得引入用户未提供的新品牌。
@pytest.mark.parametrize('standard,expansions', [
    ('星河退货如何办理？', ['退货流程']),
    ('退货如何办理？', ['星河退货流程']),
])
async def test_new_brand_cannot_enter_standard_or_expansions(standard, expansions):
    result, _ = await query('退货咋办', json.dumps({'standard': standard, 'expansions': expansions}))
    assert '星河' not in result.standard
    assert all('星河' not in text for text in result.expansions)


# 解析对象与未改动原始JSON不一致时拒绝，防止中间层修补掩盖非法结果。
async def test_parsed_result_must_match_untouched_raw_json():
    from app.retrieval.types import QueryPlan
    class Model:
        # 返回受控结构化模型绑定，专门模拟解析结果与原文不一致。
        def with_structured_output(self, schema, **kwargs):
            return self
        # 提供标准问法不同的原文及解析对象，暴露严格一致性保护。
        async def ainvoke(self, messages):
            return {'raw': AIMessage('{"standard":"退货","expansions":[]}', response_metadata={'finish_reason': 'stop'}),
                    'parsed': QueryPlan(standard='退款', expansions=[]), 'parsing_error': None}
    with pytest.raises(ServiceError) as caught:
        await planner_type()(Model(), 10000).plan('退货')
    assert caught.value.code == 'invalid_structured_output'


# 模型传输错误只返回安全错误码且不重试，不能泄漏供应商异常详情。
@pytest.mark.parametrize('failure,code', [(httpx.ReadTimeout('synthetic'), 'upstream_timeout'),
                                        (RuntimeError('private detail'), 'upstream_error')])
async def test_model_transport_errors_are_sanitized_and_not_retried(failure, code):
    class Model:
        calls = 0
        # 保留结构化绑定接口，让传输故障由真实planner处理。
        def with_structured_output(self, schema, **kwargs):
            return self
        # 只计一次实际调用后抛指定异常，检测隐藏重试和错误清洗。
        async def ainvoke(self, messages):
            self.calls += 1
            raise failure
    model = Model()
    with pytest.raises(ServiceError) as caught:
        await planner_type()(model, 10000).plan('退货')
    assert caught.value.code == code and model.calls == 1
    assert 'private detail' not in str(caught.value)


# 直接构造planner也须拒绝布尔、非正和非有限期限。
@pytest.mark.parametrize('timeout', [True, 0, float('inf'), float('nan')])
def test_direct_planner_timeout_validation(timeout):
    with pytest.raises(ValueError):
        planner_type()(WaitingModel(), 10000, timeout=timeout)


# 必需输入预算不足时在发送模型请求前拒绝。
async def test_budget_rejects_before_model_request():
    with pytest.raises(InputTooLong):
        await query('问' * 200, '{"standard":"问","expansions":[]}', budget=1)


class WaitingModel:
    # 建立进入、取消信号及调用计数，精确定位外层期限和取消行为。
    def __init__(self):
        self.started = asyncio.Event()
        self.cancelled = asyncio.Event()
        self.calls = 0

    # 核对planner明确使用json_mode和原始回包，保持线上结构化契约。
    def with_structured_output(self, schema, *, method, include_raw):
        assert (method, include_raw) == ('json_mode', True)
        return self

    # 永久等待并在退出时置取消信号，验证超时真实终止模型等待。
    async def ainvoke(self, messages):
        self.calls += 1
        self.started.set()
        try:
            await asyncio.Event().wait()
        finally:
            self.cancelled.set()


# 外层期限取消唯一模型请求，安全返回超时且无重试。
async def test_outer_deadline_cancels_model_without_retry():
    model = WaitingModel()
    with pytest.raises(ServiceError) as caught:
        await planner_type()(model, 10000, timeout=0.01).plan('售后？')
    assert caught.value.code == 'upstream_timeout'
    assert model.cancelled.is_set() and model.calls == 1


# 调用方在模型已进入后取消，异常须向外传播并终止等待。
async def test_caller_cancellation_propagates():
    model = WaitingModel()
    task = asyncio.create_task(planner_type()(model, 10000).plan('售后？'))
    await model.started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert model.cancelled.is_set() and model.calls == 1


# 检索配置拒绝非法期限、布尔分数和替代模型，防止默默放宽约束。
@pytest.mark.parametrize('field,value', [
    ('query_timeout_seconds', True), ('query_timeout_seconds', 0),
    ('query_timeout_seconds', float('nan')), ('rerank_timeout_seconds', False),
    ('rerank_timeout_seconds', float('inf')), ('rerank_min_score', True),
    ('rerank_min_score', float('nan')), ('rerank_model', 'other'),
])
def test_invalid_new_retrieval_settings_are_rejected(field, value):
    with pytest.raises(ValidationError):
        fake_settings(**{field: value})


# 校准前允许缺门槛的合法配置，校准运行才能采集真实样本。
def test_calibration_can_load_settings_without_threshold():
    assert fake_settings(rerank_min_score=None).rerank_min_score is None
