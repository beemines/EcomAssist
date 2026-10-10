"""受控 HTTP 原文经过真实解析器，验证共同门槛和联合裁判边界。"""

import asyncio
import importlib
import json
from dataclasses import asdict
from pathlib import Path

import httpx
import pytest
from langchain_core.messages import AIMessage

from app.core.evidence import Citation
from app.core.llm import create_model
from app.core.sufficiency import SufficiencyService
from app.rag_evaluation.contracts import AnswerPoint
from tests.fakes import fake_settings
from tests.test_evidence import build, payload
from tests.test_rag_metrics import record

POINTS = (AnswerPoint('p1', '未拆封七天内可退货', '未拆封', ('一周内可退',)),)
CITATIONS = (Citation(1, '1', '退货', '什么条件可退？', '未拆封七天内可退货。'),)
VALID = {'points': [{'point_id': 'p1', 'covered': True, 'reason': '完整表达条件及期限'}],
         'claims': [{'claim': '未拆封七天内可退货', 'supported': True, 'reason': '引用1直接支持'}]}
LABELED = json.loads((Path(__file__).resolve().parents[1] /
    'docs/validation/joint-generation-v2.1-labeled.json').read_text(encoding='utf-8'))


def judgment_api():
    """缺失实现变成明确断言失败，避免收集异常代替功能红灯。"""
    assert importlib.util.find_spec('app.rag_evaluation.judgment'), '联合裁判尚未实现'
    return importlib.import_module('app.rag_evaluation.judgment')


async def run_judge(content=None, *, finish='stop', question='退货条件？',
                    answer='未拆封七天内可退货', citations=CITATIONS, points=POINTS,
                    budget=16000, limit_field='max_tokens'):
    """仅替换外部 HTTP，保留已安装 LangChain 的完整 raw/parsed 管线。"""
    api = judgment_api()
    requests = []
    raw = json.dumps(VALID, ensure_ascii=False) if content is None else content

    def handle(request):
        """记录实际请求并提供含停止原因的完整 Chat Completions 合成回包。"""
        requests.append(json.loads(request.content))
        return httpx.Response(200, json={'id': 'synthetic', 'object': 'chat.completion', 'created': 0,
            'model': 'fake-chat', 'choices': [{'index': 0, 'finish_reason': finish,
                'message': {'role': 'assistant', 'content': raw}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as http:
        model = create_model(fake_settings(llm_token_limit_field=limit_field, max_output_tokens=2048), http_async_client=http)
        try:
            result = await api.GenerationJudge(model, input_budget=budget).judge(question, answer, citations, points)
            return result, requests
        finally:
            await model.root_async_client.close()
            model.root_client.close()


@pytest.mark.parametrize('strategy', ['dense', 'bm25', 'hybrid', 'hybrid_rerank'])
async def test_content_ablation_all_strategies_share_gate(strategy):
    """恢复按重排分拒答的评估分支会使同内容低分四路得到不公平结果。"""
    from tests.fakes import AssessmentModel
    packet = build(payload(('完整规则',), strategy=strategy, score=.001))
    decision = await SufficiencyService(AssessmentModel(), input_budget=10000,
        minimum_rerank_score=None, mode='content_ablation').check('退货条件？', packet)
    assert (decision.useful, decision.source) == (True, None)
    if strategy == 'hybrid_rerank':
        online = await SufficiencyService(AssessmentModel(), input_budget=10000,
            minimum_rerank_score=.5).check('退货条件？', packet)
        assert (online.useful, online.source) == (False, 'retrieval_low_conf')


@pytest.mark.parametrize('kind', ['knowledge', 'social', 'clarification'])
async def test_empty_or_knowledge_question_cannot_bypass_gate(kind):
    """删除空证据或安全问法检查会放行模型伪造的社交/澄清分类。"""
    from tests.fakes import AssessmentModel
    result = await SufficiencyService(AssessmentModel(kind=kind), input_budget=10000,
        minimum_rerank_score=None, mode='content_ablation').check(
            'AC-12拆封后七天内能退吗？', build(payload(())))
    assert (result.useful, result.response_kind, result.source) == (False, 'knowledge', 'retrieval_low_conf')


@pytest.mark.parametrize('limit_field', ['max_tokens', 'max_completion_tokens'])
async def test_valid_judge_preserves_leaf_answer_actual_evidence_and_output_budget(limit_field):
    """错误预算、添加会话或删去证据将破坏裁判收到的实际边界。"""
    result, requests = await run_judge(limit_field=limit_field)
    assert result.points[0].covered and result.claims[0].supported and result.finish_reason == 'stop'
    assert len(requests) == 1 and requests[0][limit_field] == 2048
    assert requests[0]['response_format'] == {'type': 'json_object'}
    body = json.loads(requests[0]['messages'][-1]['content'])
    assert body == {'question': '退货条件？', 'final_answer': '未拆封七天内可退货',
                    'coverage_rubric': [dict(asdict(POINTS[0]), aliases=['一周内可退'])],
                    'supporting_evidence': [asdict(CITATIONS[0])]}
    assert result.prompt_version and result.raw_response == json.dumps(VALID, ensure_ascii=False)


@pytest.mark.parametrize('content,finish', [
    ('{"points":[],"claims":[]}', 'stop'),
    (json.dumps(dict(VALID, points=VALID['points'] * 2)), 'stop'),
    (json.dumps(VALID).replace('true', '"true"', 1), 'stop'),
    (json.dumps(VALID), 'length'), (json.dumps(VALID), None),
    (json.dumps(VALID).replace('p1', 'p2'), 'stop'),
    (json.dumps(VALID, ensure_ascii=False).replace('完整表达条件及期限', '   '), 'stop'),
    (json.dumps(VALID)[:-1], 'stop'),
    (json.dumps(dict(VALID, extra=1)), 'stop'),
])
async def test_judge_rejects_missing_duplicate_point_string_bool_and_nonstop(content, finish):
    """松散 Schema 或只信 parsed 会接受缺号、重复号、伪布尔及修复后的原文。"""
    api = judgment_api()
    with pytest.raises(api.JudgeError) as caught:
        await run_judge(content, finish=finish)
    assert caught.value.code == 'judge_error'
    assert caught.value.raw_response == content and caught.value.prompt_version
    assert caught.value.finish_reason == (finish or 'unknown')


async def test_gold_fact_is_not_faithfulness_evidence():
    """金标只进入覆盖区；受控 unsupported 判定不能被覆盖成功改成 supported。"""
    response = dict(VALID, claims=[{'claim': '未拆封七天内可退货', 'supported': False, 'reason': '实际证据没有退货规则'}])
    evidence = (Citation(1, '1', None, '营业时间？', '九点营业。'),)
    result, requests = await run_judge(json.dumps(response, ensure_ascii=False), citations=evidence)
    body = json.loads(requests[0]['messages'][-1]['content'])
    assert body['supporting_evidence'] == [asdict(evidence[0])]
    assert result.points[0].covered and not result.claims[0].supported


async def test_zero_claims_not_perfect_faithfulness():
    """纯拒答返回空断言，在真实报告计分中忠实度必须为 N/A 而非满分。"""
    from app.rag_evaluation.report import case_metrics
    data = {'points': [{'point_id': 'p1', 'covered': False, 'reason': '纯拒答没有覆盖事实'}], 'claims': []}
    result, _ = await run_judge(json.dumps(data, ensure_ascii=False), answer='现有证据不足，无法回答。')
    scores = case_metrics(record(answer='现有证据不足，无法回答。', refused=True,
        point_verdicts=[asdict(v) for v in result.points], claim_verdicts=[asdict(v) for v in result.claims]))
    assert scores['answer_point_coverage'] == 0. and scores['faithfulness'] is None


class WaitingJudgeModel:
    """隔离会收费的模型调用，保留应用超时取消与调用次数。"""
    def __init__(self):
        """创建生命周期信号，允许测试等待真实调用进入后再取消。"""
        self.calls = 0
        self.started, self.cancelled = asyncio.Event(), asyncio.Event()

    def with_structured_output(self, schema, *, method, include_raw):
        """明确要求受测组件选择项目兼容 JSON 模式并保留原文。"""
        assert (method, include_raw) == ('json_mode', True)
        return self

    async def ainvoke(self, messages):
        """等待到应用取消，不能自动返回虚假的成功判定。"""
        self.calls += 1
        self.started.set()
        try:
            await asyncio.Event().wait()
        finally:
            self.cancelled.set()


async def test_judge_timeout_and_cancellation_do_not_retry():
    """删除外层期限或吞掉调用方取消都会使错误判定或后台费用失控。"""
    api = judgment_api()
    model = WaitingJudgeModel()
    with pytest.raises(api.JudgeError):
        await api.GenerationJudge(model, input_budget=16000, timeout=.01).judge('问', '答', CITATIONS, POINTS)
    assert model.calls == 1 and model.cancelled.is_set()
    other = WaitingJudgeModel()
    task = asyncio.create_task(api.GenerationJudge(other, input_budget=16000).judge('问', '答', CITATIONS, POINTS))
    await other.started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert other.calls == 1 and other.cancelled.is_set()


@pytest.mark.parametrize('part', ['answer', 'citation', 'point', 'prompt'])
async def test_judge_budget_counts_complete_actual_input_before_model(part):
    """只算问题或截断金标/证据将漏过完整裁判输入超限。"""
    api = judgment_api()
    model = WaitingJudgeModel()
    answer = '大' * 6000 if part == 'answer' else '答'
    citations = (Citation(1, '1', None, '问', '大' * 6000),) if part == 'citation' else CITATIONS
    points = (AnswerPoint('p1', '大' * 6000, None, ()),) if part == 'point' else POINTS
    with pytest.raises(api.JudgeError):
        await api.GenerationJudge(model, input_budget=1 if part == 'prompt' else 16000).judge('问', answer, citations, points)
    assert model.calls == 0


@pytest.mark.parametrize('sample', LABELED['cases'], ids=[case['label'] for case in LABELED['cases']])
async def test_labeled_prompt_samples_accept_controlled_raw_verdicts(sample):
    """人工样例只验证完整raw协议可消费，不把合成判定冒充真实模型语义能力。"""
    points = tuple(AnswerPoint(item['point_id'], item['text'], item['condition'], tuple(item['aliases']))
                   for item in sample['points'])
    citations = tuple(Citation(**item) for item in sample['citations'])
    result, requests = await run_judge(json.dumps(sample['expected'], ensure_ascii=False),
        question=sample['question'], answer=sample['answer'], citations=citations, points=points)
    assert [asdict(item) for item in result.points] == sample['expected']['points']
    assert [asdict(item) for item in result.claims] == sample['expected']['claims']
    assert result.prompt_version == LABELED['prompt_version']
    assert json.loads(requests[0]['messages'][-1]['content'])['supporting_evidence'] == sample['citations']


async def test_raw_string_boolean_cannot_hide_behind_coerced_parsed_result():
    """即使注入 parsed 已把伪布尔转成 true，原文严格验证仍必须拒绝。"""
    api = judgment_api()

    class CoercedModel:
        """模拟不可信外部解析器已转换布尔值的实际raw/parsed冲突。"""
        def with_structured_output(self, schema, *, method, include_raw):
            """保存真实裁判 Schema，以合法 parsed 孤立测试原文拒绝。"""
            self.schema = schema
            return self

        async def ainvoke(self, messages):
            """原文伪布尔与合法 parsed 同时提供，错误不能被后者掩盖。"""
            return {'raw': AIMessage(json.dumps(VALID).replace('true', '"true"'),
                        response_metadata={'finish_reason': 'stop'}),
                    'parsed': self.schema.model_validate(VALID), 'parsing_error': None}

    with pytest.raises(api.JudgeError):
        await api.GenerationJudge(CoercedModel(), 16000).judge('问', '答', CITATIONS, POINTS)


async def test_judge_failure_audit_is_bounded_and_contains_no_request_exception():
    """任意异常不泄漏请求信息；超长非法原文仅保留有界私有片段。"""
    api = judgment_api()
    text = 'x' * 20000
    with pytest.raises(api.JudgeError) as caught:
        await run_judge(text)
    assert caught.value.raw_response == 'x' * 16384
    assert caught.value.finish_reason == 'stop'

    class FailingModel(WaitingJudgeModel):
        """仅替换外部调用的异常，检查公开错误与SDK异常隔离。"""
        async def ainvoke(self, messages):
            """合成含敏感请求文本的异常，不访问真实凭据或网络。"""
            self.calls += 1
            raise RuntimeError('PRIVATE REQUEST TOKEN')

    model = FailingModel()
    with pytest.raises(api.JudgeError) as failure:
        await api.GenerationJudge(model, 16000).judge('问', '答', CITATIONS, POINTS)
    assert str(failure.value) == '联合裁判执行失败' and failure.value.raw_response == ''
    assert model.calls == 1 and failure.value.__suppress_context__
