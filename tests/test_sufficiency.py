# 真实 LangChain JSON 解析器与 HTTP 合成响应覆盖充分性判定及错误关闭。
import asyncio
import importlib
import json

import httpx
import pytest
from pydantic import ValidationError

from app.core.errors import InputTooLong, ServiceError
from app.core.llm import create_model
from tests.fakes import fake_settings
from tests.test_evidence import build, payload


# 缺失模块时返回明确失败，避免收集错误掩盖行为 RED。
def service_type():
    try:
        return importlib.import_module('app.core.sufficiency').SufficiencyService
    except ImportError:
        pytest.fail('sufficiency service is missing')


# 使用真实结构化输出管线；仅隔离外部 HTTP 与付费模型。
async def check(question='如何退货？', *, data=None, content=None, finish='stop', threshold=.5, budget=10000):
    requests = []
    if content is None:
        content = '{"useful":true,"reason":"条件齐全","response_kind":"knowledge"}'
    # 返回完整合成HTTP回包，保留真实模型解析流程。
    def handle(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, json={'id': 'synthetic', 'object': 'chat.completion', 'created': 0,
            'model': 'fake-chat', 'choices': [{'index': 0, 'finish_reason': finish,
                'message': {'role': 'assistant', 'content': content}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as http:
        model = create_model(fake_settings(), http_async_client=http)
        try:
            result = await service_type()(model, input_budget=budget, minimum_rerank_score=threshold).check(
                question, data if data is not None else build())
            return result, requests
        finally:
            await model.root_async_client.close()
            model.root_client.close()


# 真实解析器验证显式JSON模式、512输出上限及只读本轮输入。
async def test_valid_self_check_uses_json_mode_current_question_and_current_evidence_only():
    decision, requests = await check()
    assert (decision.useful, decision.response_kind, decision.source) == (True, 'knowledge', None)
    assert len(requests) == 1 and requests[0]['response_format'] == {'type': 'json_object'}
    assert requests[0]['max_tokens'] == 512
    body = json.loads(requests[0]['messages'][-1]['content'])
    assert body['question'] == '如何退货？' and body['evidence']['matches'][0]['answer'] == '规则甲'


@pytest.mark.parametrize('data', [lambda: build(payload(())), lambda: build(payload(score=.1))])
# 模型自评true不能跳过空知识和低重排分的硬门槛。
async def test_self_approved_empty_and_low_score_knowledge_forced_refusal(data):
    decision, _ = await check(data=data())
    assert (decision.useful, decision.source, decision.response_kind) == (False, 'retrieval_low_conf', 'knowledge')


@pytest.mark.parametrize('strategy', ['dense', 'bm25', 'hybrid'])
# 稠密/BM25/RRF基线走内容自评，不能把原始分数当置信概率。
async def test_baselines_use_content_check_without_treating_rank_score_as_probability(strategy):
    decision, _ = await check(data=build(payload(strategy=strategy, score=.001)), threshold=None)
    assert decision.useful and decision.source is None


# hybrid_rerank缺校准阈值时在模型请求前拒绝。
async def test_missing_hybrid_threshold_blocks_before_online_model_request():
    with pytest.raises(ValueError, match='threshold'):
        await check(threshold=None)


# 合法的模型false才产生self_check拒答来源。
async def test_model_false_is_a_valid_self_check_refusal():
    decision, _ = await check(content='{"useful":false,"reason":"缺少关键条件","response_kind":"knowledge"}')
    assert (decision.useful, decision.source) == (False, 'self_check')


@pytest.mark.parametrize('kind', ['social', 'clarification'])
# 完整业务事实问句不能用错误分类绕开知识证据。
async def test_business_fact_question_cannot_be_relabeled_to_skip_evidence(kind):
    decision, _ = await check('拆封商品可以七天无理由退货吗？', data=build(payload(())),
        content=json.dumps({'useful': True, 'reason': '随便答', 'response_kind': kind}))
    assert not decision.useful and decision.response_kind == 'knowledge'


# 未选工具的纯问候仍要调用自评，但无需知识引用。
async def test_no_tool_question_still_judged_and_greeting_can_be_social():
    from langchain_core.messages import HumanMessage, SystemMessage
    from app.core.evidence import build_evidence
    packet = build_evidence(system=SystemMessage('系统'), turns=[], current=HumanMessage('你好'),
                            request=None, payload=None, budget=1000)
    decision, requests = await check('你好', data=packet, threshold=None,
        content='{"useful":true,"reason":"问候","response_kind":"social"}')
    assert decision.useful and decision.response_kind == 'social' and len(requests) == 1


# 无工具的事实问题也必须自评，知识为空不能借工具选择结果直接生成事实。
async def test_no_tool_factual_question_is_still_judged_and_refused():
    from langchain_core.messages import HumanMessage, SystemMessage
    from app.core.evidence import build_evidence
    packet = build_evidence(system=SystemMessage('系统'), turns=[], current=HumanMessage('星河AC-12保修多久？'),
                            request=None, payload=None, budget=1000)
    decision, requests = await check('星河AC-12保修多久？', data=packet, threshold=None)
    assert (decision.useful, decision.source) == (False, 'retrieval_low_conf') and len(requests) == 1


# 缺订单号或条件的真实业务主题仍可仅追问；带明确条件或 SKU 的事实问法必须走知识。
@pytest.mark.parametrize('question,kind,want_useful,want_kind', [
    ('我的订单到哪了？', 'clarification', True, 'clarification'),
    ('可以退货吗？', 'clarification', True, 'clarification'),
    ('谢谢您！', 'social', True, 'social'),
    ('星河AC-12未拆封5天能退吗？', 'clarification', False, 'knowledge'),
    ('谢谢！星河AC-12运费多少？', 'social', False, 'knowledge'),
])
async def test_nonfactual_question_boundary_preserves_legitimate_clarification(question, kind, want_useful, want_kind):
    result, _ = await check(question, data=build(payload(())),
                           content=json.dumps({'useful': True, 'reason': '仅追问', 'response_kind': kind}))
    assert (result.useful, result.response_kind) == (want_useful, want_kind)


@pytest.mark.parametrize('content,finish', [
    ('{"useful":true,"reason":"足够","response_kind":"knowledge"', 'stop'),
    ('{"useful":true,"reason":"足够","response_kind":"knowledge","extra":1}', 'stop'),
    ('{"useful":"true","reason":"足够","response_kind":"knowledge"}', 'stop'),
    ('{"useful":true,"reason":" ","response_kind":"knowledge"}', 'stop'),
    ('{"useful":true,"reason":"足够","response_kind":"knowledge"}', 'length'),
    ('{"useful":true,"reason":"足够","response_kind":"knowledge"}', 'content_filter'),
    ('{"useful":true,"reason":"足够","response_kind":"knowledge"}', None),
])
# 非法原始JSON、额外键、类型错误及非stop结束必须保持错误语义。
async def test_invalid_raw_or_nonstop_is_error_never_valid_refusal(content, finish):
    with pytest.raises(ServiceError) as caught:
        await check(content=content, finish=finish)
    assert caught.value.code == 'invalid_structured_output'


# 阻塞外部调用可观察期限、取消和不重试，不持有真实客户端。
class WaitingModel:
    # 初始化可观察调用与取消信号。
    def __init__(self):
        self.started, self.cancelled = asyncio.Event(), asyncio.Event()
        self.calls = 0

    # 模拟已绑定 Schema 的外部模型，接口必须明确指定 JSON 模式与原文。
    def with_structured_output(self, schema, *, method, include_raw):
        assert (method, include_raw) == ('json_mode', True)
        return self

    # 等待直到取消，以验证应用绝对期限。
    async def ainvoke(self, messages):
        self.calls += 1
        self.started.set()
        try:
            await asyncio.Event().wait()
        finally:
            self.cancelled.set()


# 外层期限取消模型且不重试，不能把超时当拒答。
async def test_timeout_is_error_without_retry():
    model = WaitingModel()
    with pytest.raises(ServiceError) as caught:
        await service_type()(model, input_budget=10000, timeout=.01, minimum_rerank_score=.5).check('退货？', build())
    assert caught.value.code == 'upstream_timeout' and model.cancelled.is_set() and model.calls == 1


# 自评输入超预算必须在外部调用前拒绝。
async def test_budget_rejection_happens_before_model():
    model = WaitingModel()
    with pytest.raises(InputTooLong):
        await service_type()(model, input_budget=1, minimum_rerank_score=.5).check('退货？', build())
    assert model.calls == 0


# 调用方取消必须传播，不能变成拒答或偷偷继续第二次调用。
async def test_caller_cancellation_propagates_without_retry():
    model = WaitingModel()
    task = asyncio.create_task(service_type()(model, input_budget=10000, minimum_rerank_score=.5).check('退货？', build()))
    await model.started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert model.cancelled.is_set() and model.calls == 1


# 人工制造原文与 parsed 不同，确保合法 Schema 仍不能掩盖解析篡改。
async def test_raw_and_parsed_disagreement_is_error():
    from langchain_core.messages import AIMessage

    class DisagreeingModel:
        # 获取生产 Schema 构造真实 parsed，不自行替代校验行为。
        def with_structured_output(self, schema, *, method, include_raw):
            self.schema = schema
            return self

        # 返回两份各自合法但互相冲突的结果。
        async def ainvoke(self, messages):
            return {'raw': AIMessage('{"useful":false,"reason":"不足","response_kind":"knowledge"}',
                                     response_metadata={'finish_reason': 'stop'}),
                    'parsed': self.schema(useful=True, reason='足够', response_kind='knowledge'), 'parsing_error': None}

    with pytest.raises(ServiceError) as caught:
        await service_type()(DisagreeingModel(), input_budget=10000, minimum_rerank_score=.5).check('退货？', build())
    assert caught.value.code == 'invalid_structured_output'


@pytest.mark.parametrize('value', [True, 0, float('nan'), float('inf')])
# 时间配置拒绝布尔值、零、NaN及无穷大。
def test_sufficiency_timeout_configuration_rejects_invalid_numbers(value):
    with pytest.raises(ValidationError):
        fake_settings(sufficiency_timeout_seconds=value)


# 合法配置确实可被在线服务消费，避免仅靠 unknown-field 报错产生假阳性。
def test_valid_sufficiency_settings_used_by_service():
    settings = fake_settings(sufficiency_timeout_seconds=12.5)
    service = service_type()(WaitingModel(), input_budget=10000,
                            timeout=settings.sufficiency_timeout_seconds, minimum_rerank_score=None)
    assert service.timeout == 12.5 and fake_settings().sufficiency_timeout_seconds == 20
