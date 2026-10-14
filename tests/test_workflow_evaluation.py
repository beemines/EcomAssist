"""评估报告不得把未执行、误分类或上游故障计为通过。"""
import importlib.util
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
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
        """边界替身保留一题合法错类，并让后续物流题正确以验证继续测量。"""
        seen.append(question)
        return {'intent': '物流' if question == '查物流' else '订单', 'usage': {'actual_calls': 1, 'estimated_calls': 0}}

    cases = [{'id': 'one', 'question': '订单1001的状态是什么？', 'expected_intent': '订单',
              'expected_route': 'business'},
             {'id': 'social', 'question': '你好', 'expected_intent': '闲聊', 'expected_route': 'social'},
             {'id': 'wrong', 'question': '退货政策是什么？', 'expected_intent': '退款退货', 'expected_route': 'knowledge'},
             {'id': 'after', 'question': '查物流', 'expected_intent': '物流', 'expected_route': 'business'}]
    report = await module.evaluate_intent(cases, classify, execution='controlled')
    assert seen == ['订单1001的状态是什么？', '退货政策是什么？', '查物流']
    assert [row['status'] for row in report['cases']] == ['passed', 'passed', 'misclassified', 'passed']
    assert report['counts']['passed'] == 3
    assert report['counts']['misclassified'] == 1
    assert report['model_calls'] == 3


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
    row = completed_two_tool_row()
    row.update(status=status, model_calls=calls)
    if case_id == 'two-step':
        row['tool_trace'] = [{'name': item['name'], 'tool_call_id': {'query_order': 'order-1', 'query_logistics': 'logistics-1'}[item['name']]} for item in trace]
    else:
        row.update(tool_trace=trace, tool_call_count=0, final_message_id='106',
            sql_messages=[row['sql_messages'][0], row['sql_messages'][-1]])
    assert module.case_outcome(case_id, row) == expected


def test_failed_subgraph_usage_is_not_lost_or_double_counted():
    """失败子图已成功决策仍计入记录账本，父图同一分类成本不能再相加。"""
    module = evaluation()
    assert hasattr(module, 'recorded_usage'), '缺少子图失败账本选择'
    root = {'actual': 300, 'estimated': 0, 'actual_calls': 1, 'estimated_calls': 0}
    child = {'actual': 1100, 'estimated': 0, 'actual_calls': 2, 'estimated_calls': 0}
    assert module.recorded_usage([root, child]) == child


def completed_two_tool_row():
    """手工给出自有当前轮两组标准SQL配对及对应轨迹，不由被测实现推导期望。"""
    return {'status': 'passed', 'browser_status': 'PASS', 'question': '先查订单1001的状态，再按订单查物流',
        'user_message_id': '101', 'final_message_id': '106', 'tool_call_count': 2, 'model_calls': 4,
        'tool_trace': [{'name': 'query_order', 'tool_call_id': 'order-1', 'status': 'success'},
                       {'name': 'query_logistics', 'tool_call_id': 'logistics-1', 'status': 'success'}],
        'sql_messages': [
            {'id': '101', 'role': 'user', 'content': '先查订单1001的状态，再按订单查物流', 'tool_calls': None, 'tool_call_id': None},
            {'id': '102', 'role': 'assistant', 'content': None, 'tool_call_id': None,
             'tool_calls': [{'id': 'order-1', 'type': 'function', 'function': {'name': 'query_order', 'arguments': '{"order_id":"1001"}'}}]},
            {'id': '103', 'role': 'tool', 'content': '{"order_id":"1001","mock":true}', 'tool_calls': None, 'tool_call_id': 'order-1'},
            {'id': '104', 'role': 'assistant', 'content': None, 'tool_call_id': None,
             'tool_calls': [{'id': 'logistics-1', 'type': 'function', 'function': {'name': 'query_logistics', 'arguments': '{"order_id":"1001"}'}}]},
            {'id': '105', 'role': 'tool', 'content': '{"order_id":"1001","mock":true}', 'tool_calls': None, 'tool_call_id': 'logistics-1'},
            {'id': '106', 'role': 'assistant', 'content': '模拟物流进度。', 'tool_calls': None, 'tool_call_id': None}]}


@pytest.mark.parametrize('defect', ['missing-result', 'duplicate-result', 'mismatched-id', 'wrong-name',
    'reversed-pairs', 'reused-call-id', 'count-mismatch', 'wrong-user', 'wrong-final', 'duplicate-message-id'])
def test_completed_trace_cannot_pass_without_exact_owned_sql_pairs(defect):
    """任何缺失、重复、错ID/顺序/计数的SQL都必须推翻表面正确的两步轨迹。"""
    module = evaluation()
    row = completed_two_tool_row()
    if defect == 'missing-result':
        row['sql_messages'].pop(2)
    elif defect == 'duplicate-result':
        row['sql_messages'].insert(3, deepcopy(row['sql_messages'][2]))
    elif defect == 'mismatched-id':
        row['sql_messages'][2]['tool_call_id'] = 'some-other-call'
    elif defect == 'wrong-name':
        row['sql_messages'][1]['tool_calls'][0]['function']['name'] = 'query_product'
    elif defect == 'reversed-pairs':
        row['sql_messages'][1:5] = row['sql_messages'][3:5] + row['sql_messages'][1:3]
        for identifier, message in zip(('102', '103', '104', '105'), row['sql_messages'][1:5]):
            message['id'] = identifier
    elif defect == 'reused-call-id':
        row['sql_messages'][3]['tool_calls'][0]['id'] = row['sql_messages'][4]['tool_call_id'] = 'order-1'
    elif defect == 'count-mismatch':
        row['tool_call_count'] = 1
    elif defect == 'wrong-user':
        row['user_message_id'] = '99'
    elif defect == 'wrong-final':
        row['final_message_id'] = '105'
    else:
        row['sql_messages'][2]['id'] = '102'
    assert module.case_outcome('two-step', row) == 'errors'


def test_owned_sql_validation_ignores_prior_turn_but_checks_current_turn():
    """旧失败轮的孤立审计不污染当前配对，当前轮完整时才能通过。"""
    module = evaluation()
    assert hasattr(module, 'sql_turn_errors'), '缺少自有当前轮SQL配对核验'
    row = completed_two_tool_row()
    row['sql_messages'][:0] = [{'id': '90', 'role': 'user', 'content': '旧失败问题', 'tool_calls': None, 'tool_call_id': None},
        {'id': '91', 'role': 'assistant', 'content': None, 'tool_call_id': None,
         'tool_calls': [{'id': 'old', 'type': 'function', 'function': {'name': 'query_order', 'arguments': '{}'}}]}]
    assert module.sql_turn_errors(row) == []
    assert module.case_outcome('two-step', row) == 'passed'


@pytest.mark.parametrize(('case_id', 'updates'), [
    ('logistics', {'tool_trace': []}),
    ('logistics', {'tool_trace': [{'name': 'query_order'}]}),
    ('usage-help', {'reply_mode': 'answer', 'answer': '抱歉，当前资料不足以可靠回答这个问题。'}),
    ('usage-help', {'reply_mode': 'clarification', 'answer': '请提供订单号。'}),
    ('mh-lp200', {'answer': '容量12L [1]', 'source': 'MH-W60水箱容量3L。'}),
    ('mh-lp200', {'answer': '容量12L [1]', 'source': 'MH-LP100容量12L。'})])
def test_scenario_cannot_pass_without_required_business_or_source_evidence(case_id, updates):
    """物流必须真查物流，缺型号求助应追问型号，12L引用应支持对应商品事实。"""
    module = evaluation()
    row = completed_two_tool_row()
    if case_id == 'logistics':
        has_order = bool(updates['tool_trace'])
        row['sql_messages'] = ([row['sql_messages'][0], *row['sql_messages'][1:3], row['sql_messages'][-1]]
            if has_order else [row['sql_messages'][0], row['sql_messages'][-1]])
        row['tool_call_count'] = int(has_order)
        updates = {**updates, 'tool_trace': [{'name': 'query_order', 'tool_call_id': 'order-1', 'status': 'success'}] if has_order else []}
    elif case_id == 'usage-help':
        row.update(tool_trace=[], tool_call_count=0, sql_messages=[row['sql_messages'][0], row['sql_messages'][-1]])
    row.update(updates)
    if case_id == 'mh-lp200':
        row['citations'] = [{'n': 1, 'question': row['source'], 'answer': row['source'], 'section_path': None}]
    assert module.sql_turn_errors(row) == []
    assert module.case_outcome(case_id, row) == 'errors'


@pytest.mark.parametrize('case_id', ['logistics', 'usage-help', 'mh-lp200'])
def test_required_scenario_evidence_can_pass(case_id):
    """独立有效样例确保加强后的断言仍能接受物流、澄清和对应12L来源。"""
    module = evaluation()
    row = completed_two_tool_row()
    if case_id == 'logistics':
        row['tool_trace'] = row['tool_trace'][1:]
        row['sql_messages'] = [row['sql_messages'][0], *row['sql_messages'][3:]]
        row['tool_call_count'] = 1
    elif case_id == 'usage-help':
        row.update(tool_trace=[], tool_call_count=0, sql_messages=[row['sql_messages'][0], row['sql_messages'][-1]],
            reply_mode='clarification', answer='请问您买的是什么商品或型号，具体在哪一步不会操作？')
    else:
        row.update(answer='MH-LP200猫砂盆容量12L [1]', source='最大猫砂容量12L。', source_identity='MH-LP200商品规格',
            citations=[{'n': 1, 'question': 'MH-LP200商品规格', 'answer': '最大猫砂容量12L。', 'section_path': None}])
    assert module.sql_turn_errors(row) == []
    assert module.case_outcome(case_id, row) == 'passed'


def test_source_must_match_a_citation_actually_used_in_answer():
    """答案虽有12L，另一个未被引用的支持来源不能替代实际错误引用。"""
    module = evaluation()
    row = completed_two_tool_row()
    row.update(answer='MH-LP200容量12L [1]', source='MH-LP200容量12L。',
        citations=[{'n': 1, 'question': 'MH-LP100规格', 'answer': '容量8L。', 'section_path': None},
                   {'n': 2, 'question': 'MH-LP200规格', 'answer': 'MH-LP200容量12L。', 'section_path': None}])
    assert module.sql_turn_errors(row) == []
    assert module.case_outcome('mh-lp200', row) == 'errors'


def test_browser_fixed_scenario_assertions_reject_bad_and_accept_valid_evidence():
    """直接运行浏览器脚本的真实场景断言，受控证据验证拒绝与放行，不发网络。"""
    executable = shutil.which('node') or ('D:/vue/node.exe' if Path('D:/vue/node.exe').is_file() else None)
    if not executable:
        pytest.skip('本机没有Node，不能运行浏览器断言契约')
    code = r'''
const assert = require('node:assert/strict');
const { assertLiveScenario } = require('./scripts/verify-workflow-browser.cjs');
assert.equal(typeof assertLiveScenario, 'function', '缺少可执行的真实场景断言');
assert.throws(() => assertLiveScenario('logistics', {events: []}));
const events = [
 {event:'status',data:{phase:'tool_running',tool_name:'query_logistics',tool_call_id:'log-1',origin:'agent'}},
 {event:'status',data:{phase:'tool_completed',tool_name:'query_logistics',tool_call_id:'log-1',origin:'agent',status:'success'}}];
assert.doesNotThrow(() => assertLiveScenario('logistics', {events}));
assert.throws(() => assertLiveScenario('logistics', {events:[events[1]]}));
assert.throws(() => assertLiveScenario('usage-help', {answer:'抱歉资料不足',tool_badges:[]}));
assert.throws(() => assertLiveScenario('usage-help', {answer:'请提供订单号',tool_badges:[]}));
assert.doesNotThrow(() => assertLiveScenario('usage-help', {answer:'你买的是什么商品型号，在哪一步不会操作？',tool_badges:[]}));
assert.throws(() => assertLiveScenario('mh-lp200', {answer:'容量12L [1]',source:'MH-LP100容量12L'}));
assert.throws(() => assertLiveScenario('mh-lp200', {answer:'容量12L [1]',source:'MH-LP200容量8L'}));
assert.doesNotThrow(() => assertLiveScenario('mh-lp200', {answer:'MH-LP200容量12L [1]',source:'MH-LP200容量12L'}));
console.log('受控场景断言10项通过');
'''
    result = subprocess.run([executable, '-e', code], capture_output=True, text=True, encoding='utf-8', timeout=20)
    assert result.returncode == 0, result.stderr
    assert '受控场景断言10项通过' in result.stdout


def test_later_capacity_citation_can_support_the_answer():
    """首条是介绍、第二条才是被引用容量证据时，报告接受实际打开的第二条。"""
    module = evaluation()
    row = completed_two_tool_row()
    row.update(answer='MH-LP200产品介绍见[1]，猫砂容量12L[2]。', source='最大猫砂容量12L。',
        citations=[{'n': 1, 'question': 'MH-LP200介绍', 'answer': '这是智能猫砂盆。', 'section_path': None},
                   {'n': 2, 'question': 'MH-LP200容量', 'answer': '最大猫砂容量12L。', 'section_path': None}])
    assert module.case_outcome('mh-lp200', row) == 'passed'


def test_later_capacity_citation_browser_click_uses_supporting_source(tmp_path):
    """显式受控Chromium打开真实页面，验证共用点击路径选择后面的容量引用。"""
    if os.environ.get('WORKFLOW_BROWSER_CONTRACT') != '1':
        pytest.skip('显式WORKFLOW_BROWSER_CONTRACT=1运行受控浏览器引用回归')
    executable = shutil.which('node') or ('D:/vue/node.exe' if Path('D:/vue/node.exe').is_file() else None)
    assert executable, '受控浏览器回归需要Node'
    code = r'''
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const assert = require('node:assert/strict');
const {chromium} = require('playwright');
const {openKnowledgeSource, assertLiveScenario} = require('./scripts/verify-workflow-browser.cjs');
// 使用独立回环静态服务器与精确API夹具，所有聊天数据均为受控输入。
async function main() {
  const files = {'/':['index.html','text/html'],'/static/chat.js':['chat.js','text/javascript'],'/static/chat.css':['chat.css','text/css']};
  const server = http.createServer((request,response) => {
    const file = files[new URL(request.url,'http://localhost').pathname];
    if (!file) { response.writeHead(404); response.end(); return; }
    response.writeHead(200,{'Content-Type':file[1]+'; charset=utf-8'});
    response.end(fs.readFileSync(path.join('app','static',file[0])));
  }); // 只提供当前实际页面文件，不访问真实8001/8002服务。
  let browser;
  try {
    await new Promise(resolve => server.listen(0,'127.0.0.1',resolve)); // 只监听自有临时端口。
    browser = await chromium.launch({headless:true, executablePath:process.env.WORKFLOW_CHROMIUM_PATH || chromium.executablePath()});
    const page = await browser.newPage();
    const citations = [
      {n:1,chunk_id:'42',section_path:'产品介绍',question:'MH-LP200介绍',answer:'这是智能猫砂盆。'},
      {n:2,chunk_id:'43',section_path:'商品规格',question:'MH-LP200容量',answer:'最大猫砂容量12L。'},
      {n:3,chunk_id:'44',section_path:'饮水机规格',question:'MH-W60容量',answer:'另一商品容量12L。'}];
    const events = [{event:'citations',data:{citations}},
      {event:'delta',data:{delta:'MH-LP200产品介绍见[1]，猫砂容量12L[2]。'}},
      {event:'done',data:{conversation_id:'1001',message_id:'1002'}}];
    const stream = events.map(event => `event: ${event.event}\ndata: ${JSON.stringify(event.data)}\n\n`).join(''); // 发送真实SSE文本经过页面解析和引用渲染。
    await page.route('**/api/conversations',route => route.fulfill({json:{conversation_id:'1001'}})); // 精确会话夹具。
    await page.route('**/api/chat',route => route.fulfill({contentType:'text/event-stream; charset=utf-8',body:stream})); // 精确聊天夹具，不调用模型。
    await page.goto(`http://127.0.0.1:${server.address().port}/`);
    await page.locator('#message-input').fill('MH-LP200能装多少猫砂？');
    await page.locator('#message-input').press('Enter');
    await page.waitForFunction(() => !document.querySelector('#message-input').disabled); // 等待真实页面消费done和EOF。
    const record = {events,answer:await page.locator('.answer-text').last().innerText()};
    await openKnowledgeSource(page,'mh-lp200',record);
    assert.equal(record.source_title,'知识来源 [2]','必须实际点击后面的容量来源而非介绍[1]');
    assert.equal(record.source,'最大猫砂容量12L。');
    assertLiveScenario('mh-lp200',record);
    await assert.rejects(() => openKnowledgeSource(page,'mh-lp200',{...record,answer:'产品介绍见[1]。'}), /未找到实际被引用/); // 未引用的容量来源不能拿来放行。
    await assert.rejects(() => openKnowledgeSource(page,'mh-lp200',{...record,answer:'另一商品容量12L[3]。'}), /未找到实际被引用/); // 别的商品即使12L也不能替代。
    await page.screenshot({path:process.argv[1],fullPage:true});
    console.log('实际受控点击容量来源[2]通过');
  } finally {
    if (browser) await browser.close();
    server.closeAllConnections();
    await new Promise(resolve => server.close(resolve)); // 只关闭本测试创建的临时服务器。
  }
}
main().catch(error => {console.error(error.stack);process.exitCode=1;}); // 明确报告断言失败并保持非零退出码。
'''
    result = subprocess.run([executable, '-e', code, str(tmp_path / 'later-capacity.png')],
        capture_output=True, text=True, encoding='utf-8', timeout=40)
    assert result.returncode == 0, result.stderr
    assert '实际受控点击容量来源[2]通过' in result.stdout


def test_browser_case_selection_keeps_fixed_denominator_and_supplemental_gate():
    """真实选择器保留固定十项账本，仅执行指定主场景及投诉附加项。"""
    executable = shutil.which('node') or 'D:/vue/node.exe'
    code = r'''
const assert = require('node:assert/strict');
const {selectLiveCases} = require('./scripts/verify-workflow-browser.cjs');
assert.equal(typeof selectLiveCases, 'function', '缺少固定场景选择器');
const chosen = selectLiveCases(['--cases','logistics,two-step,usage-help']);
assert.equal(chosen.length,10);
assert.deepEqual(chosen.filter(row=>row.selected).map(row=>row.name), ['logistics','two-step','usage-help']);
assert.deepEqual(chosen.filter(row=>!row.selected).map(row=>row.name), ['policy','complaint','social','mh-lp200','out-of-library','complaint-ticket-only','restart-offer']);
assert.equal(selectLiveCases([]).filter(row=>row.selected).length,10);
assert.deepEqual(selectLiveCases(['--cases','complaint']).filter(row=>row.selected).map(row=>row.name), ['complaint','complaint-ticket-only','restart-offer']);
for (const args of [['--cases=logistics'],['--cases',''],['--cases'],['--cases','logistics,'],['--cases','logistics,logistics'],['--cases','invented'],['--cases','complaint-ticket-only'],['--cases','logistics','--cases','social']]) {
  assert.throws(()=>selectLiveCases(args), /cases/);
}
'''
    result = subprocess.run([executable, '-e', code], capture_output=True, text=True, encoding='utf-8', timeout=20)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize('selection', ['', 'logistics,logistics', '任意问题', 'restart-offer'])
def test_browser_invalid_cases_fail_before_browser_or_network(selection):
    """无浏览器依赖时仍先报告非法选择，不创建运行目录或触发网络。"""
    executable = shutil.which('node') or 'D:/vue/node.exe'
    result = subprocess.run([executable, 'scripts/verify-workflow-browser.cjs', '--url',
        'http://127.0.0.1:1/', '--mode', 'live', '--cases', selection],
        capture_output=True, text=True, encoding='utf-8', timeout=20)
    assert result.returncode != 0
    assert '--cases' in result.stderr
    assert 'MODE=' not in result.stdout
