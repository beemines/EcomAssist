import importlib
import json
from pathlib import Path

import httpx
import pytest
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, ToolMessage

from tests.fakes import FAQStub, ConversationStore, StreamingModel, fake_settings
from tests.test_smoke import frame


def implementation():
    try:
        return importlib.import_module('evals.evaluate_tools')
    except ModuleNotFoundError:
        pytest.fail('tool evaluation implementation is missing')


CASES = [json.loads(line) for line in Path('evals/tool_cases.jsonl').read_text(encoding='utf-8').splitlines()]


async def run_case(case, *, mode='good', args=None, result=None, answer=None):
    module = implementation()
    repo = ConversationStore('9007199254741099')
    identifier = repo.identifier
    call = {'id': 'call-1', 'name': case['expected_tool'], 'args': args or case['expected_args']}
    answer = answer if answer is not None else case['controlled_answer']
    await repo.seed(identifier, [HumanMessage(case['message']), AIMessage('', tool_calls=[call]),
        ToolMessage(json.dumps(result if result is not None else {'found': False, 'matches': []}), tool_call_id='call-1'), AIMessage(answer)])
    requests = []

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


async def test_compatibility_failure_stops_remaining_cases():
    module = implementation()
    requests = []
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


async def test_expected_faq_miss_is_success():
    report, _, _ = await run_case(CASES[4])
    case = report.cases[0]
    assert case['passed'] is True
    assert case['actual_found'] is False
    assert case['matches'] == []
    assert case['actual_args'] == {'keyword': '邮费'}
    assert case['human_answer_review'] == 'pending'


async def test_faq_miss_synonym_is_not_a_tool_failure():
    report, _, _ = await run_case(CASES[4], answer='没有查到关于邮费的说明，请人工客服确认。')
    assert report.cases[0]['passed'] is True
    assert report.cases[0]['answer_phrase_match'] is False
    assert report.cases[0]['human_answer_review'] == 'pending'


async def test_incomplete_stream_is_not_pass():
    report, _, _ = await run_case(CASES[4], mode='incomplete')
    case = report.cases[0]
    assert case['passed'] is False


@pytest.mark.parametrize('mode', ['bad_json', 'wrong_identity', 'bad_utf8', 'error'])
async def test_malformed_protocol_cannot_pass(mode):
    report, _, _ = await run_case(CASES[4], mode=mode)
    assert report.cases[0]['passed'] is False


async def test_audit_must_match_actual_arguments_and_tool_identity():
    report, _, _ = await run_case(CASES[4], args={'keyword': '运费'})
    assert report.cases[0]['passed'] is False
    assert report.cases[0]['actual_args'] == {'keyword': '运费'}


async def test_multiple_persisted_tool_calls_cannot_pass():
    report, repo, _ = await run_case(CASES[4])
    from dataclasses import replace
    repo.rows[repo.identifier][1] = replace(repo.rows[repo.identifier][1], tool_calls=repo.rows[repo.identifier][1].tool_calls * 2)
    assert implementation().audit_messages(repo.rows[repo.identifier], CASES[4], report.cases[0]['stream'])['passed'] is False


async def test_failed_final_answer_retains_actual_tool_audit():
    report, repo, _ = await run_case(CASES[4])
    rows = repo.rows[repo.identifier][:-1]
    audit = implementation().audit_messages(rows, CASES[4], report.cases[0]['stream'])
    assert audit['passed'] is False
    assert audit['actual_tool'] == 'query_faq'
    assert audit['actual_args'] == {'keyword': '邮费'}
    assert audit['actual_found'] is False
    assert audit['matches'] == []


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
