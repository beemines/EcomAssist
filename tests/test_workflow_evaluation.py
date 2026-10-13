"""评估报告不得把未执行、误分类或上游故障计为通过。"""
import importlib.util
import json
import subprocess
import sys

import pytest


def evaluation():
    """明确断言验收模块存在，再加载待验证的报告行为。"""
    assert importlib.util.find_spec('evals.evaluate_workflow') is not None, '缺少有界验收模块'
    from evals import evaluate_workflow
    return evaluate_workflow


def test_default_cli_never_calls_model(tmp_path):
    """默认CLI无配置仍能输出未执行报告，防止悄悄发起收费调用。"""
    evaluation()
    output = tmp_path / 'report.json'
    result = subprocess.run([sys.executable, '-m', 'evals.evaluate_workflow', '--mode', 'intent',
        '--output', str(output)], capture_output=True, text=True, encoding='utf-8', timeout=20)
    assert result.returncode == 0, result.stderr
    report = json.loads(output.read_text(encoding='utf-8'))
    assert report['execution'] == 'controlled'
    assert report['counts'] == {'total': 24, 'attempted': 0, 'passed': 0, 'misclassified': 0,
        'refused': 0, 'errors': 0, 'timeouts': 0, 'truncated': 0, 'not_executed': 24}


async def test_intent_records_original_inputs_and_one_call_per_non_social_case():
    """分类报告只传原问题，问候零调用，错类不会成为通过。"""
    module = evaluation()
    seen = []

    async def classify(question):
        """边界替身只记录真实输入并给出固定合法错类。"""
        seen.append(question)
        return {'intent': '订单', 'usage': {'actual_calls': 1, 'estimated_calls': 0}}

    cases = [{'id': 'one', 'question': '订单1001的状态是什么？', 'expected_intent': '订单',
              'expected_route': 'business'},
             {'id': 'social', 'question': '你好', 'expected_intent': '闲聊', 'expected_route': 'social'},
             {'id': 'wrong', 'question': '退货政策是什么？', 'expected_intent': '退款退货', 'expected_route': 'knowledge'},
             {'id': 'after', 'question': '查物流', 'expected_intent': '物流', 'expected_route': 'business'}]
    report = await module.evaluate_intent(cases, classify, execution='controlled')
    assert seen == ['订单1001的状态是什么？', '退货政策是什么？']
    assert [row['status'] for row in report['cases']] == ['passed', 'passed', 'misclassified', 'not_executed']
    assert report['counts']['passed'] == 2
    assert report['counts']['misclassified'] == 1
    assert report['model_calls'] == 2


@pytest.mark.parametrize(('failure', 'status'), [(TimeoutError(), 'timeouts'),
    (RuntimeError('bad upstream'), 'errors')])
async def test_first_intent_error_stops_remaining_calls(failure, status):
    """首次上游异常停止收费，后续题仍保留未执行分母。"""
    module = evaluation()
    seen = []

    async def classify(question):
        """模拟不可避免的外部模型异常，禁止验收层隐式重试。"""
        seen.append(question)
        raise failure

    cases = module.load_intent_cases()[:2]
    report = await module.evaluate_intent(cases, classify, execution='controlled')
    assert len(seen) == 1
    assert report['counts'][status] == 1
    assert report['counts']['passed'] == 0
    assert report['counts']['not_executed'] == 1


def test_chat_requires_legal_done_and_keeps_refusal_distinct():
    """断流、错误、超时和截断不得当拒答或通过；拒答只看已完成质量快照。"""
    module = evaluation()
    done = {'event': 'done', 'data': {'conversation_id': '1', 'message_id': '2'}}
    assert module.chat_outcome([], {}) == 'truncated'
    assert module.chat_outcome([{'event': 'error', 'data': {'code': 'upstream_timeout'}}], {}) == 'timeouts'
    assert module.chat_outcome([{'event': 'error', 'data': {'code': 'invalid_model_output'}}], {}) == 'errors'
    assert module.chat_outcome([done], {'turn_status': 'completed', 'quality': {'useful': False}}) == 'refused'
    assert module.chat_outcome([done], {'turn_status': 'running'}) == 'errors'
    assert module.chat_outcome([done], {'turn_status': 'completed', 'quality': {}}) == 'passed'


def test_all_fixed_cases_remain_in_default_chat_denominator():
    """固定场景未执行保留分母，报告标题必须显式声明受控模式。"""
    module = evaluation()
    report = module.unexecuted_report('chat')
    assert '受控' in report['title']
    assert report['counts']['total'] == report['counts']['not_executed'] == 8
    assert report['counts']['passed'] == 0
    assert report['model_calls'] == 0


@pytest.mark.parametrize(('case_id', 'status', 'calls', 'trace', 'expected'), [
    ('social', 'passed', 1, [], 'errors'),
    ('out-of-library', 'passed', 1, [], 'errors'),
    ('policy', 'refused', 1, [], 'refused'),
    ('two-step', 'passed', 4, [{'name': 'query_logistics'}, {'name': 'query_order'}], 'errors'),
    ('two-step', 'passed', 4, [{'name': 'query_order'}, {'name': 'query_logistics'}], 'passed')])
def test_case_contract_rejects_wrong_live_behavior(case_id, status, calls, trace, expected):
    """零模型闲聊、库外拒答和两步顺序为实际约束，不能只凭HTTP200通过。"""
    module = evaluation()
    assert hasattr(module, 'case_outcome'), '缺少真实场景语义校验'
    row = {'status': status, 'model_calls': calls, 'tool_trace': trace, 'browser_status': 'PASS'}
    assert module.case_outcome(case_id, row) == expected


def test_failed_subgraph_usage_is_not_lost_or_double_counted():
    """失败子图已成功决策仍计入记录账本，父图同一分类成本不能再相加。"""
    module = evaluation()
    assert hasattr(module, 'recorded_usage'), '缺少子图失败账本选择'
    root = {'actual': 300, 'estimated': 0, 'actual_calls': 1, 'estimated_calls': 0}
    child = {'actual': 1100, 'estimated': 0, 'actual_calls': 2, 'estimated_calls': 0}
    assert module.recorded_usage([root, child]) == child
