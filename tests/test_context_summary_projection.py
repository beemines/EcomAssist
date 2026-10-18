"""The summary model sees only the same source authority as the validator."""
import json
from dataclasses import asdict, replace

import httpx
import pytest

from app.context.prompts import summary_messages
from app.context.summarizer import _sources, summary_input_tokens
from app.context.tokens import estimate_payload
from app.context.types import FrozenMessage, SummaryBatch
from app.repositories.context import _source_hash


def source_batch(rows):
    rows = tuple(rows)
    return SummaryBatch('72', 643, 1, int(rows[0].id), int(rows[-1].id), rows, _source_hash(rows))


def request(*, content=None, arguments=None):
    calls = [{'id': 'call-1', 'type': 'function', 'function': {
        'name': 'query_order', 'arguments': json.dumps(arguments or {'order_id': 'O-101'})}}]
    return FrozenMessage('645', 'assistant', content, json.dumps(calls), None)


def result(payload, *, call_id='call-1'):
    return FrozenMessage('646', 'tool', json.dumps(payload, ensure_ascii=False), None, call_id)


def packet(source):
    return json.loads(summary_messages(source)[1].content)


async def test_actual_outbound_packet_excludes_assistant_only_prior_facts_and_preserves_raw_batch():
    from app.config import Settings
    from app.context.summarizer import SummaryGenerator
    from app.core.llm import create_model

    source = source_batch([
        FrozenMessage('644', 'user', '联系方式沿用我刚留的那个，未解决的诉求是什么？', None, None),
        request(content='我会用139****9000跟进恒温猫窝。'),
        result({'order_id': 'O-101', 'model': 'MH-BG100', 'status': '待发货', 'mock': True}),
        FrozenMessage('647', 'assistant', '用户此前称恒温猫窝，电话139****9000。', None, None),
    ])
    before = asdict(source)
    sent = []

    async def respond(req):
        sent.append(json.loads(req.content))
        return httpx.Response(200, json={'id': 'fake', 'object': 'chat.completion', 'created': 0,
            'model': 'fake', 'choices': [{'index': 0, 'finish_reason': 'stop', 'message': {
                'role': 'assistant', 'content': json.dumps({'content':
                    '用户追问此前联系方式及未解决诉求；当时模拟订单O-101，MH-BG100待发货。'})}}]})

    config = Settings(_env_file=None, llm_base_url='https://summary.invalid/v1',
                      llm_model='fake', llm_api_key='test-only')
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        await SummaryGenerator(create_model(config, http_async_client=client), config).summarize(source)
    data = json.loads(sent[0]['messages'][1]['content'])
    serialized = json.dumps(data, ensure_ascii=False)
    assert '139****9000' not in serialized
    assert '恒温猫窝' not in serialized
    assert [row['id'] for row in data['source_rows']] == ['644', '645', '646']
    assert data['source_rows'][0]['content'] == source.source_rows[0].content
    assert data['source_rows'][1]['content'] is None
    assert json.loads(data['source_rows'][2]['content'])['model'] == 'MH-BG100'
    assert (data['from_msg_id'], data['upto_msg_id']) == ('644', '647')
    assert asdict(source) == before
    assert source.source_hash == _source_hash(source.source_rows)


@pytest.mark.parametrize('location', ['user', 'tool'])
def test_same_entities_are_preserved_when_present_in_authorized_source(location):
    text = '恒温猫窝，电话139****9000'
    source = source_batch([
        FrozenMessage('644', 'user', text if location == 'user' else '请查进度', None, None),
        request(), result({'order_id': 'O-101', 'product_name': text} if location == 'tool'
                          else {'order_id': 'O-101'}),
    ])
    data = packet(source)
    assert text in json.dumps(data, ensure_ascii=False)
    assert _sources(source) == ([text if location == 'user' else '请查进度'],
        [{'order_id': 'O-101', 'product_name': text}] if location == 'tool' else [{'order_id': 'O-101'}])


@pytest.mark.parametrize('failure', [
    'orphan', 'not_adjacent', 'wrong_id', 'bad_calls_json', 'bad_arguments', 'two_calls',
    'bad_result_json', 'nonobject', 'error_key', 'failed', 'error_status', 'wrong_order',
])
def test_invalid_tool_pairs_are_excluded_from_model_and_validator_authority(failure):
    user = FrozenMessage('644', 'user', '请查进度', None, None)
    req = request()
    res = result({'order_id': 'O-101', 'phone': '18812345678', 'product_name': '不可信商品'})
    rows = [user, req, res]
    if failure == 'orphan':
        rows = [user, res]
    elif failure == 'not_adjacent':
        rows.insert(2, FrozenMessage('645', 'assistant', '打断配对', None, None))
    elif failure == 'wrong_id':
        rows[-1] = replace(res, tool_call_id='other')
    elif failure == 'bad_calls_json':
        rows[1] = replace(req, tool_calls_json='{')
    elif failure in ('bad_arguments', 'two_calls'):
        calls = json.loads(req.tool_calls_json)
        if failure == 'bad_arguments':
            calls[0]['function']['arguments'] = '[]'
        else:
            calls *= 2
        rows[1] = replace(req, tool_calls_json=json.dumps(calls))
    elif failure == 'bad_result_json':
        rows[-1] = replace(res, content='{"phone":"18812345678"')
    elif failure == 'nonobject':
        rows[-1] = replace(res, content='["18812345678"]')
    else:
        fields = {'error_key': {'error': None}, 'failed': {'success': False},
                  'error_status': {'status': 'error'}, 'wrong_order': {'order_id': 'O-999'}}
        rows[-1] = result({**json.loads(res.content), **fields[failure]})
    source = source_batch(rows)
    assert packet(source)['source_rows'] == [asdict(user)]
    assert _sources(source) == (['请查进度'], [])


def test_request_prose_and_untrusted_extra_arguments_cannot_leak_as_facts():
    source = source_batch([
        FrozenMessage('644', 'user', '请查进度', None, None),
        request(content='助手声称电话18812345678',
                arguments={'order_id': 'O-101', 'note': '助手声称电话18812345678'}),
        result({'order_id': 'O-101', 'status': '待发货'}),
    ])
    data = packet(source)
    assert '18812345678' not in json.dumps(data, ensure_ascii=False)
    calls = json.loads(data['source_rows'][1]['tool_calls_json'])
    assert calls[0]['id'] == data['source_rows'][2]['tool_call_id'] == 'call-1'
    assert json.loads(calls[0]['function']['arguments']) == {'order_id': 'O-101'}


@pytest.mark.parametrize('payload,args', [
    ({'order_id': 'O-101', 'success': 0, 'status': 'ERROR'}, {'order_id': 'O-101'}),
    ({'answer': '当时客服时间9:00 至 22:00'}, {'query': '客服时间'}),
])
def test_projection_keeps_exact_existing_success_authority(payload, args):
    source = source_batch([FrozenMessage('644', 'user', '请查进度', None, None),
                           request(arguments=args), result(payload)])
    assert [row['role'] for row in packet(source)['source_rows']] == ['user', 'assistant', 'tool']
    assert _sources(source) == (['请查进度'], [payload])


def test_summary_estimate_counts_exact_projected_packet_and_not_omitted_assistant_text():
    user = FrozenMessage('644', 'user', '请查订单O-101', None, None)
    short = source_batch([user, FrozenMessage('647', 'assistant', '收到', None, None)])
    long = replace(short, source_rows=(user, replace(short.source_rows[1], content='助手旧事实'*1000)))
    assert summary_input_tokens(long) == estimate_payload(summary_messages(long))
    assert summary_input_tokens(long) == summary_input_tokens(short)
