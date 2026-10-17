"""Offline annotations and strict protocol checks, never a live model evaluation."""
import asyncio
import json
from dataclasses import replace
from pathlib import Path

import httpx
import pytest
from langchain_core.messages import AIMessage

from app.config import Settings
from app.context.types import FrozenMessage, SummaryBatch
from app.repositories.context import _source_hash


CASES = json.loads((Path(__file__).parent / 'fixtures/context/summary_cases.json').read_text(encoding='utf-8'))


def settings(**changes):
    return Settings(_env_file=None, llm_base_url='https://summary.invalid/v1', llm_model='fake',
                    llm_api_key='test-only', **changes)


def batch(user='订单 O-101 的包裹未找到', assistant='仍需核实。', tool=None, *, conversation_id='1', start=1):
    rows = [FrozenMessage(str(start), 'user', user, None, None)]
    if tool is not None:
        calls = [{'id': 'call-1', 'type': 'function', 'function': {
            'name': 'query_order', 'arguments': json.dumps({'order_id': tool.get('order_id', 'O-101')})}}]
        rows.extend([FrozenMessage(str(start+1), 'assistant', None, json.dumps(calls), None),
                     FrozenMessage(str(start+2), 'tool', json.dumps(tool, ensure_ascii=False), None, 'call-1')])
    rows.append(FrozenMessage(str(start+len(rows)), 'assistant', assistant, None, None))
    frozen = tuple(rows)
    return SummaryBatch(conversation_id, None, 0, start, int(rows[-1].id), frozen, _source_hash(frozen))


class ReplyModel:
    def __init__(self, content, *, reason='stop', additional=None):
        self.reply = AIMessage(content, response_metadata={'finish_reason': reason}, additional_kwargs=additional or {})
        self.calls = []

    def bind(self, **kwargs):
        self.options = kwargs
        return self

    async def ainvoke(self, messages):
        self.calls.append(messages)
        return self.reply


@pytest.mark.parametrize('case', CASES, ids=lambda case: case['id'])
def test_annotated_examples_and_counterexamples(case):
    from app.context.summarizer import validate_summary
    source = batch(case['user'], case['assistant'], case.get('tool'))
    assert validate_summary(case['summary'], source) == case['summary']
    assert all(fact in case['summary'] for fact in case['must_keep'])
    assert all(fact not in case['summary'] for fact in case['forbidden'])
    with pytest.raises(ValueError):
        validate_summary(case['bad'], source)


@pytest.mark.parametrize('content,reason,additional', [
    ('not json', 'stop', {}), ('{"content":"订单 O-101 的包裹未找到","extra":1}', 'stop', {}),
    ('{"content":1}', 'stop', {}), ('{"content":"","content":"订单 O-101 的包裹未找到"}', 'stop', {}),
    ('{"content":"订单 O-101 的包裹未找到"}', 'length', {}),
    ('{"content":"订单 O-101 的包裹未找到"}', None, {}),
    ('{"content":"订单 O-101 的包裹未找到"}', 'stop', {'tool_calls':[{'id':'x','type':'function','function':{'name':'x','arguments':'{}'}}]}),
    ('{"content":"订单 O-101 的包裹未找到"}', 'stop', {'refusal':'refused'}),
    (json.dumps({'content': '甲'*201}), 'stop', {}),
    ('{"content":"订单 O-999 的包裹未找到"}', 'stop', {}), ('{"content":""}', 'stop', {}),
    ('{"content":"订单 O-101 的包裹未找到[1]"}', 'stop', {}),
])
async def test_rejects_protocol_length_entities_and_references(content, reason, additional):
    from app.context.summarizer import SummaryGenerator
    model = ReplyModel(content, reason=reason, additional=additional)
    with pytest.raises(ValueError):
        await SummaryGenerator(model, settings()).summarize(batch())
    assert len(model.calls) == 1  # No paid retry after invalid output.


def test_entities_from_assistant_failed_or_unpaired_tools_are_not_trusted():
    from app.context.summarizer import validate_summary
    sources = [batch('你好', '订单 O-999 已发货'),
               batch('请查进度', '收到', {'order_id':'O-999','error':'missing'}),
               batch('请查进度', '收到', {'order_id':'O-999','success':False}),
               batch('请查进度', '收到', {'order_id':'O-999','status':'error'})]
    good = batch('请查进度', '收到', {'order_id':'O-999','status':'运输中'})
    sources.append(replace(good, source_rows=tuple(replace(row, tool_call_id='wrong') if row.role=='tool' else row for row in good.source_rows)))
    for source in sources:
        with pytest.raises(ValueError):
            validate_summary('订单 O-999 当时运输中。', source)


@pytest.mark.parametrize('limit_field', ['max_tokens', 'max_completion_tokens'])
async def test_actual_http_request_has_512_reserve_json_mode_raw_source_and_no_retry(limit_field):
    from app.context.summarizer import SummaryGenerator
    from app.core.llm import create_model
    requests = []
    async def respond(request):
        payload = json.loads(request.content)
        requests.append(payload)
        return httpx.Response(200, json={'id':'fake','object':'chat.completion','created':0,'model':'fake',
            'choices':[{'index':0,'message':{'role':'assistant','content':'{"content":"订单 O-101 的包裹未找到。"}'},'finish_reason':'stop'}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        config = settings(max_output_tokens=7, llm_token_limit_field=limit_field)
        generator = SummaryGenerator(create_model(config, http_async_client=client), config)
        assert await generator.summarize(batch(assistant='原文'*100)) == '订单 O-101 的包裹未找到。'
    assert len(requests) == 1
    sent = requests[0]
    assert sent.get('max_tokens', sent.get('max_completion_tokens')) == 512
    assert sent['response_format'] == {'type':'json_object'}
    assert 'tools' not in sent
    data = json.loads(sent['messages'][1]['content'])
    assert data['source_rows'][-1]['content'] == '原文'*100
    assert 'summaries' not in data


async def test_http_failure_is_one_call_without_sdk_retry():
    from app.context.summarizer import SummaryGenerator
    from app.core.llm import create_model
    from openai import InternalServerError
    requests = []
    async def respond(request):
        requests.append(request)
        return httpx.Response(500, json={'error': {'message':'controlled failure','type':'server_error'}})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        config = settings()
        with pytest.raises(InternalServerError):
            await SummaryGenerator(create_model(config, http_async_client=client), config).summarize(batch())
    assert len(requests) == 1


@pytest.mark.parametrize('user,summary', [
    ('订单 O-1 已申请退款，但尚未退款。', '订单 O-1 尚未退款。'),
    ('订单 O-1 打开了退款表单，又取消了表单，没有提交。', '订单 O-1 取消了表单，没有提交。'),
    ('不是订单 O-1，我换成订单 O-2。', '不是订单 O-2，改查订单 O-1。'),
    ('订单 O-1 未找到包裹。', '订单 O-1 未找到包裹，但订单 O-1 已收到。'),
])
def test_known_action_stages_and_direction_must_not_be_lost(user, summary):
    from app.context.summarizer import validate_summary
    with pytest.raises(ValueError):
        validate_summary(summary, batch(user, '等待核实。'))


async def test_full_wrappers_output_safety_and_timeout_are_enforced():
    from app.context.summarizer import SummaryGenerator
    model = ReplyModel('{"content":"订单 O-101 的包裹未找到。"}')
    with pytest.raises(ValueError, match='window'):
        await SummaryGenerator(model, settings(model_context_window=800)).summarize(batch())
    assert not model.calls
    entered, cancelled = asyncio.Event(), asyncio.Event()
    class Blocked(ReplyModel):
        async def ainvoke(self, messages):
            entered.set()
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()
    with pytest.raises(TimeoutError):
        await SummaryGenerator(Blocked(''), settings(llm_timeout_seconds=0.01)).summarize(batch())
    assert entered.is_set() and cancelled.is_set()
