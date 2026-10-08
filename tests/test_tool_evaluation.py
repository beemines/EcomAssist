import importlib
import json
from pathlib import Path

import httpx
import pytest
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, ToolMessage

from tests.fakes import FAQStub, ConversationStore, StreamingModel, fake_settings
from tests.test_smoke import frame


# 加载工具评测模块，缺失实现时报告明确测试失败。
def implementation():
    try:
        return importlib.import_module('evals.evaluate_tools')
    except ModuleNotFoundError:
        pytest.fail('tool evaluation implementation is missing')


CASES = [json.loads(line) for line in Path('evals/tool_cases.jsonl').read_text(encoding='utf-8').splitlines()]
SHIPPING_MATCH = {'id': 7, 'question': '标准配送费用', 'answer': '合成演示8元，满99元包邮。', 'category': '合成演示'}


# 预置匹配审计并运行真实工具评测，支持参数、结果、答案或 SSE 协议故障注入。
async def run_case(case, *, mode='good', args=None, result=None, answer=None):
    module = implementation()
    repo = ConversationStore('9007199254741099')
    identifier = repo.identifier
    call = {'id': 'call-1', 'name': case['expected_tool'], 'args': args or case['expected_args']}
    answer = answer if answer is not None else case['controlled_answer']
    default_result = {'found': True, 'matches': [SHIPPING_MATCH]} if case['expected_found'] else {'found': False, 'matches': []}
    await repo.seed(identifier, [HumanMessage(case['message']), AIMessage('', tool_calls=[call]),
        ToolMessage(json.dumps(result if result is not None else default_result), tool_call_id='call-1'), AIMessage(answer)])
    requests = []

    # 模拟会话创建与聊天 SSE，并按场景制造缺完成、错编号、非法 JSON 或 UTF-8 等故障。
    def handler(request):
        requests.append(request.url.path)
        if request.url.path == '/api/conversations':
            return httpx.Response(200, json={'conversation_id': identifier})
        data = frame('status', {'phase': 'selecting'}) + frame('delta', {'delta': answer[:2]}) + frame('delta', {'delta': answer[2:]})
        data += frame('done', {'conversation_id': identifier})
        if mode == 'incomplete':
            data = data[:data.rfind(b'event: done')]
        elif mode == 'wrong_identity':
            data = data[:data.rfind(b'event: done')] + frame('done', {'conversation_id': 9007199254741099})
        elif mode == 'bad_json':
            data = b'event: delta\ndata: {broken}\n\n'
        elif mode == 'bad_utf8':
            data = b'event: delta\ndata: \xff\n\n'
        elif mode == 'error':
            data = frame('error', {'code': 'upstream_error', 'message': 'SECRET'})
        return httpx.Response(200, headers={'content-type': 'text/event-stream'}, content=data)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        report = await module.evaluate_tools(client, 'http://app.invalid', [case], repository=repo)
    assert 'SECRET' not in json.dumps(report.cases)
    return report, repo, requests


# 验证首样本协议失败后停止其余七个样本，保留未执行标记。
async def test_compatibility_failure_stops_remaining_cases():
    module = implementation()
    requests = []
    # 返回合法会话与安全待处理的流错误，构造首样本兼容性失败。
    def handler(request):
        requests.append(request.url.path)
        if request.url.path == '/api/conversations':
            return httpx.Response(200, json={'conversation_id': '1'})
        return httpx.Response(200, headers={'content-type': 'text/event-stream'}, content=frame('error', {'code': 'upstream_error', 'message': 'SECRET'}))
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        report = await module.evaluate_tools(client, 'http://app.invalid', CASES, repository=ConversationStore())
    assert report.attempted == 1
    assert report.not_attempted == 7
    assert len(requests) == 2
    assert all(c['error_code'] == 'not_attempted' for c in report.cases[1:])


# 验证预期 FAQ 命中的实际参数与知识结果通过工具评测，同时仍待人工回答复核。
async def test_expected_faq_hit_is_success():
    report, _, _ = await run_case(CASES[4])
    case = report.cases[0]
    assert case['passed'] is True
    assert case['actual_found'] is True
    assert case['matches'] == [SHIPPING_MATCH]
    assert case['actual_args'] == {'keyword': '邮费'}
    assert case['human_answer_review'] == 'pending'


# 验证答案同义表达不会被当作工具失败，字面短语未匹配仍交由人工复核。
async def test_faq_hit_synonym_is_not_a_tool_failure():
    report, _, _ = await run_case(CASES[4], answer='演示配送需八元，商品实付达到九十九元可免邮。')
    assert report.cases[0]['passed'] is True
    assert report.cases[0]['answer_phrase_match'] is False
    assert report.cases[0]['human_answer_review'] == 'pending'


# 验证缺失完成帧的聊天流不能通过评测。
async def test_incomplete_stream_is_not_pass():
    report, _, _ = await run_case(CASES[4], mode='incomplete')
    case = report.cases[0]
    assert case['passed'] is False


# 验证非法 JSON、数值会话编号、错误 UTF-8 或错误事件均判协议失败。
@pytest.mark.parametrize('mode', ['bad_json', 'wrong_identity', 'bad_utf8', 'error'])
async def test_malformed_protocol_cannot_pass(mode):
    report, _, _ = await run_case(CASES[4], mode=mode)
    assert report.cases[0]['passed'] is False


# 验证实际审计参数偏离预期工具参数时评测失败，并保留真实参数。
async def test_audit_must_match_actual_arguments_and_tool_identity():
    report, _, _ = await run_case(CASES[4], args={'keyword': '运费'})
    assert report.cases[0]['passed'] is False
    assert report.cases[0]['actual_args'] == {'keyword': '运费'}


# 验证持久审计含多个工具调用时不能通过单调用验收。
async def test_multiple_persisted_tool_calls_cannot_pass():
    report, repo, _ = await run_case(CASES[4])
    from dataclasses import replace
    repo.rows[repo.identifier][1] = replace(repo.rows[repo.identifier][1], tool_calls=repo.rows[repo.identifier][1].tool_calls * 2)
    assert implementation().audit_messages(repo.rows[repo.identifier], CASES[4], report.cases[0]['stream'])['passed'] is False


# 验证最终回答缺失时判失败，但报告仍保留已执行工具、参数与 FAQ 命中。
async def test_failed_final_answer_retains_actual_tool_audit():
    report, repo, _ = await run_case(CASES[4])
    rows = repo.rows[repo.identifier][:-1]
    audit = implementation().audit_messages(rows, CASES[4], report.cases[0]['stream'])
    assert audit['passed'] is False
    assert audit['actual_tool'] == 'query_faq'
    assert audit['actual_args'] == {'keyword': '邮费'}
    assert audit['actual_found'] is True
    assert audit['matches'] == [SHIPPING_MATCH]


# 验证工具评测可运行真实应用链路，并依据已提交审计核对模拟物流结果。
async def test_evaluation_uses_application_chain_and_committed_audit():
    from app.main import create_app
    case = CASES[0]
    model = StreamingModel([AIMessageChunk(content='模拟物流'), AIMessageChunk(content='仅供演示'), AIMessageChunk(content='', response_metadata={'finish_reason': 'stop'})])
    model.selected = AIMessage('', tool_calls=[{'id': 'logistics-1', 'name': 'query_logistics', 'args': {'order_id': 'A-42'}}], response_metadata={'finish_reason': 'tool_calls'})
    repo = ConversationStore()
    app = create_app(fake_settings(), faq_repository=FAQStub(), model=model, repository=repo)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app)) as client:
        report = await implementation().evaluate_tools(client, 'http://test', [case], repository=repo)
    assert report.cases[0]['passed'] is True
    assert report.cases[0]['tool_result']['order_id'] == 'A-42'
    assert report.cases[0]['tool_result']['mock'] is True
    assert repo.commits == 1
