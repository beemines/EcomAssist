"""验证评估器不会用金标补失败历史或隐藏真实分母。"""
import json
import pytest

from langchain_core.messages import AIMessage

from evals.evaluate_intent_routing import evaluate, score


# 七份保存报告中的全部六种实际消解输出；不读取未跟踪的运行文件。
OBSERVED_RESOLUTIONS = [
    ('dialogue-1-2', '订单1001的MH-LP200能退货吗'),
    ('dialogue-1-3', '订单1001的物流现在到哪里了？'),
    ('dialogue-3-3', '订单1002能退吗'),
    ('dialogue-5-2', '订单1001申请退货'),
    ('dialogue-5-3', '请查订单1001的配送进度。'),
    ('dialogue-6-2', '订单1002的明辉饮水机MH-WD100的保修期限是多久？'),
]


def resolution_checks(identifier, query):
    """使用真实固定题和来源事实核验完整评分路径。"""
    from evals.evaluate_intent_routing import CASES, fixture_messages
    case = next(json.loads(line) for line in CASES.read_text(encoding='utf-8').splitlines()
                if json.loads(line)['id'] == identifier)
    return score(case, {'resolved_question': query, 'intent': case['expected_intent'],
                        'route': case['expected_route']}, fixture_messages(case.get('history_fixture', [])))


@pytest.mark.parametrize('identifier,query', OBSERVED_RESOLUTIONS + [
    ('dialogue-1-2', '请问订单1001能不能申请退货？'),
    ('dialogue-3-3', '订单1002的明辉饮水机MH-WD100能退货么？'),
    ('dialogue-1-3', '请问订单1001的物流目前到哪儿了？'),
    ('dialogue-5-2', '请为订单1001申请退货。'),
    ('dialogue-5-3', '查询订单1001的配送进度'),
    ('dialogue-6-2', 'MH-WD100的保修期有多长时间？'),
    ('dialogue-6-2', '订单1002的保修期限是多少年？'),
])
def test_whole_request_accepts_observed_resolutions_and_legitimate_aliases(identifier, query):
    """全部实际成功输出及有限同义表达仍通过实体与请求双重核验。"""
    assert all(resolution_checks(identifier, query).values())


@pytest.mark.parametrize('identifier,query', [
    ('dialogue-5-2', '订单1001无需申请退货。'),
    ('dialogue-5-3', '后天请查订单1001的配送进度。'),
])
def test_whole_request_rejects_actual_review_counterexamples(identifier, query):
    """真实审查反例实体和路由正确，但请求极性或时间改变必须失败。"""
    checks = resolution_checks(identifier, query)
    assert checks['entity_preservation'] and checks['intent'] and checks['route']
    assert checks['resolvable'] is False


@pytest.mark.parametrize('negation', ['无需', '无须', '不用', '不必'])
@pytest.mark.parametrize('template', ['订单1001{word}申请退货。', '{word}为订单1001申请退货。',
                                      '订单1001申请退货，{word}办理。'])
def test_whole_request_rejects_changed_polarity(negation, template):
    """否定出现在主语前后或追加分句均不能靠合法请求尾部蒙混通过。"""
    assert not resolution_checks('dialogue-5-2', template.format(word=negation))['resolvable']


@pytest.mark.parametrize('identifier,query', OBSERVED_RESOLUTIONS)
@pytest.mark.parametrize('when', ['明天', '后天'])
@pytest.mark.parametrize('position', ['prefix', 'suffix'])
def test_whole_request_rejects_new_time_anywhere(identifier, query, when, position):
    """固定六题任何前后附加时间都改变原请求，不能只检查局部词组。"""
    changed = when + query if position == 'prefix' else query.rstrip('。？?') + '，' + when
    assert not resolution_checks(identifier, changed)['resolvable']


@pytest.mark.parametrize('identifier,query', [
    ('dialogue-5-2', '订单1001已经退款，申请退货。'),
    ('dialogue-5-2', '取消订单1001申请退货。'),
    ('dialogue-5-2', '订单1001申请退款。'),
    ('dialogue-5-2', '订单1001可以申请退货。'),
    ('dialogue-5-2', '订单1001能申请退货吗？'),
    ('dialogue-5-3', '订单1001已签收，请查订单1001的配送进度。'),
    ('dialogue-5-3', '不要查询订单1001的配送进度。'),
    ('dialogue-5-3', '请修改订单1001的配送进度。'),
    ('dialogue-1-2', '订单1001能退货。'),
    ('dialogue-1-3', '订单1001的物流到哪里了？'),
    ('dialogue-6-2', '订单1002无须保修，保修期限是多久？'),
    ('dialogue-6-2', '订单1002的保修期限是三年。'),
    ('dialogue-6-2', '订单1002的维修期限是多久？'),
    ('dialogue-6-2', '据说订单1002的保修期限是多久？'),
])
def test_whole_request_rejects_conclusions_changed_actions_and_unsupported_wording(identifier, query):
    """固定语法保守拒绝结论、改动作及未支持措辞，不冒充通用语义判官。"""
    assert not resolution_checks(identifier, query)['resolvable']


@pytest.mark.parametrize('identifier,query,valid', [
    ('dialogue-6-2', '订单1002的保修期限是多久？', True),
    ('dialogue-6-2', 'MH-WD100的保修期限是多久？', True),
    ('dialogue-6-2', '订单1002的容量是多少？', False),
    ('dialogue-6-2', '订单1002没有保修。', False),
    ('dialogue-1-2', 'MH-LP200能退货吗？', False),
    ('dialogue-1-2', '订单1001不能退货。', False),
    ('dialogue-1-3', '订单1001的物流昨天到哪里了？', False),
    ('dialogue-5-2', '订单1001不申请退货。', False),
])
def test_resolution_preserves_request_semantics(identifier, query, valid):
    """同实体不同动作/否定/时间或伪造结论不能算消解成功。"""
    from evals.evaluate_intent_routing import CASES, fixture_messages
    case = next(json.loads(line) for line in CASES.read_text(encoding='utf-8').splitlines() if json.loads(line)['id'] == identifier)
    checks = score(case, {'resolved_question': query, 'intent': case['expected_intent'], 'route': case['expected_route']},
        fixture_messages(case.get('history_fixture', [])))
    assert checks['resolvable'] is valid


async def test_evaluation_retains_safe_sdk_finish_diagnostic():
    """SDK直接抛截断时无raw响应，也必须保存白名单finish_reason。"""
    from openai import LengthFinishReasonError
    from openai.types.chat import ChatCompletion
    from tests.workflow_fakes import ScriptedWorkflowModel
    failure = LengthFinishReasonError(completion=ChatCompletion(id='test', model='test', object='chat.completion', created=0, choices=[]))
    report = await evaluate(split='acceptance', live=True, case_id='dialogue-1-1',
        model=ScriptedWorkflowModel(intent_replies=[failure]))
    row = report['results'][0]
    assert row['finish_reason'] == 'length' and row['model_calls'] == 1
    assert row['raw_outputs'][0]['raw'] is None


class ScriptedModel:
    """仅替换收费网络边界，真实理解/分类解析与计数保留。"""
    def __init__(self, outputs):
        self.outputs, self.calls = iter(outputs), []

    def with_structured_output(self, schema, **kwargs):
        """按实际结构化接口保留原响应与解析错误。"""
        parent = self
        class Bound:
            async def ainvoke(self, messages):
                """记录真正传入模型的消息。"""
                parent.calls.append(messages)
                value = next(parent.outputs)
                raw = AIMessage(json.dumps(value, ensure_ascii=False), response_metadata={'finish_reason': 'stop'},
                                usage_metadata={'input_tokens': 10, 'output_tokens': 5, 'total_tokens': 15})
                try:
                    parsed = schema.model_validate(value)
                    return {'raw': raw, 'parsed': parsed, 'parsing_error': None}
                except ValueError as exc:
                    return {'raw': raw, 'parsed': None, 'parsing_error': exc}
        return Bound()


async def test_default_evaluation_makes_zero_calls():
    """缺少live时不进入模型边界且完整报告未执行。"""
    model = ScriptedModel([])
    report = await evaluate(split='acceptance', model=model)
    assert report['counts'] == {'total': 16, 'passed': 0, 'failed': 0, 'blocked': 0, 'not_executed': 16}
    assert report['model_calls'] == 0 and not model.calls


async def test_protocol_error_stops_paid_continuation():
    """理解协议错后不调用分类或同对话后续轮。"""
    model = ScriptedModel([{'query': '订单1001的物流到哪里了？', 'extra': True}])
    report = await evaluate(split='acceptance', live=True, model=model, case_id='dialogue-1-1')
    assert report['model_calls'] == 1
    assert report['results'][0]['status'] == 'failed'
    assert report['results'][1]['status'] == 'not_executed'


async def test_bad_turn_not_removed_from_denominator():
    """定点失败保留整个split的16轮分母。"""
    report = await evaluate(split='acceptance', live=True, model=ScriptedModel([{}]), case_id='dialogue-1-1')
    assert report['counts']['total'] == 16 and report['counts']['failed'] == 1
    assert report['counts']['not_executed'] == 15


async def test_previous_turn_failure_does_not_inject_gold_history():
    """失败先行轮不会借history_fixture继续同对话收费。"""
    outputs = [{}] * 100
    report = await evaluate(split='acceptance', live=True, model=ScriptedModel(outputs))
    dependent = report['results'][1]
    assert dependent['status'] == 'blocked' and dependent['model_calls'] == 0
    assert dependent['history'] == []
    assert report['model_calls'] == 4


async def test_entity_passthrough_and_ambiguity_metrics_keep_failures():
    """完整问句被改写会失败，即使意图分类正确。"""
    model = ScriptedModel([{'query': '订单1001物流？'}, {'intent': '物流', 'confidence': .99}])
    report = await evaluate(split='acceptance', live=True, model=model, case_id='dialogue-1-1')
    assert report['metrics']['full_passthrough']['passed'] == 0
    assert report['metrics']['intent']['passed'] == 1
    assert report['counts']['passed'] == 0
    assert report['metrics']['ambiguity_zero_guess']['total'] == 1


async def test_point_recheck_never_replays_prerequisites():
    """缺少有效旧输出时定点后续轮blocked，无自动付费前序重放。"""
    report = await evaluate(split='acceptance', live=True, model=ScriptedModel([]), case_id='dialogue-1-2')
    assert report['model_calls'] == 0 and report['results'][1]['status'] == 'blocked'


async def test_chat_missing_sql_root_evidence_never_passes():
    """浏览器PASS文字本身不能替代SQL/根状态证据。"""
    report = await evaluate(mode='chat', split='acceptance', live=True,
                            evidence={'mode': 'live', 'results': [{'status': 'PASS'}]})
    assert report['model_calls'] == 0 and report['counts']['passed'] == 0
    assert report['full_chain']['passed'] == 0


def test_product_only_resolution_does_not_require_unasked_order_number():
    """知识问句消解成已知型号即可，不能因没加订单号误判。"""
    case = {'query': '这台设备的保修期限是多久？', 'expected_query': 'MH-WD100的保修期限是多久？',
            'expected_intent': '商品咨询', 'expected_route': 'knowledge', 'resolvable': True, 'antecedent': '1002'}
    row = {'resolved_question': 'MH-WD100的保修期限是多久？', 'intent': '商品咨询', 'route': 'knowledge'}
    assert score(case, row, [])['resolvable'] is True


def test_resolution_accepts_source_order_but_rejects_alternative_entities():
    """唯一来源订单也可消解，但错误旧单或不同型号不能借OR分支通过。"""
    case = {'query': '这台设备的保修期限是多久？', 'expected_query': 'MH-WD100的保修期限是多久？',
            'expected_intent': '商品咨询', 'expected_route': 'knowledge', 'resolvable': True, 'antecedent': '1002'}
    for query, expected in [('订单1002的保修期限是多久？', True), ('订单1001的保修期限是多久？', False),
                            ('订单1002的MH-LP200的保修期限是多久？', False)]:
        row = {'resolved_question': query, 'intent': '商品咨询', 'route': 'knowledge'}
        assert score(case, row, [])['resolvable'] is expected


@pytest.mark.parametrize('mutation,allowed', [('prompt_hash', True), ('sample_hash', False), ('model', False), ('failed', False)])
async def test_point_history_reuse_preserves_provenance_and_rejects_invalid_sources(mutation, allowed):
    """定点只复用同题库同模型有效观测，Prompt变更需明示来源而不重付前序。"""
    previous = await evaluate(split='acceptance', live=True, case_id='dialogue-1-1',
        model=ScriptedModel([{'query': '订单1001的物流到哪里了？'}, {'intent': '物流', 'confidence': .99}]))
    if mutation == 'failed':
        previous['results'][0]['status'] = 'failed'
    else:
        previous[mutation] = 'old-version'
    model = ScriptedModel([{'query': '订单1001的MH-LP200能退货吗？'}, {'intent': '退款退货', 'confidence': .98}])
    report = await evaluate(split='acceptance', live=True, case_id='dialogue-1-2', previous=previous, model=model)
    assert report['model_calls'] == (2 if allowed else 0)
    assert report['results'][1]['status'] == ('passed' if allowed else 'blocked')
    if allowed:
        assert report['results'][0]['source_prompt_hash'] == 'old-version'
        assert report['results'][0]['source_report_hash']
        assert '订单1001的物流到哪里了？' in [m.content for m in model.calls[0]]


async def test_chat_flags_without_local_storage_verification_cannot_pass(tmp_path):
    """导入必须重新核验SQL/原根，不能只信JSON里的两个true标志。"""
    screenshot = tmp_path / 'actual.png'
    screenshot.write_bytes(b'placeholder')
    evidence = {'mode': 'live', 'results': [{'name': 'policy-no-picker', 'case_id': 'dialogue-1-1', 'status': 'PASS',
        'requests': [{'method': 'POST'}], 'screenshot': str(screenshot), 'conversation_id': '1',
        'sql_evidence': {'verified': True, 'conversation_id': '1', 'assistant_message_id': '2'},
        'root_evidence': {'durable': True, 'conversation_id': '1', 'assistant_message_id': '2'}}]}
    report = await evaluate(mode='chat', split='acceptance', live=True, evidence=evidence)
    assert report['counts']['passed'] == 0
    assert report['full_chain'] == {'passed': 0, 'total': 8, 'not_executed': 7}

