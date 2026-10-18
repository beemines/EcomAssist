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
async def test_actual_http_request_has_512_reserve_json_mode_trusted_source_and_no_retry(limit_field):
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
    assert len(data['source_rows']) == 1
    assert data['source_rows'][0]['role'] == 'user'
    assert data['source_rows'][0]['content'] == '订单 O-101 的包裹未找到'
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


@pytest.mark.parametrize('answer', ['您好！有什么可以帮您的吗？',
                                   '您好！我是客服小助手，可以为您解答问题。',
                                   '欢迎咨询，我能为您提供什么帮助？'])
def test_greeting_with_help_boilerplate_accepts_empty_summary(answer):
    from app.context.summarizer import validate_summary
    assert validate_summary('', batch('你好', answer)) == ''


@pytest.mark.parametrize('source', [
    batch('你好，请查订单 O-101 的物流。', '您好！有什么可以帮您的吗？'),
    batch('你好', '您好！有什么可以帮您的吗？', {'order_id':'O-101','status':'运输中','mock':True}),
    batch('你好', '查询失败。', {'order_id':'O-101','error':'not_found'}),
])
def test_greeting_cannot_erase_user_business_or_tool_history(source):
    from app.context.summarizer import validate_summary
    with pytest.raises(ValueError):
        validate_summary('', source)


def test_independently_specified_orders_in_same_request_are_not_ambiguous():
    from app.context.summarizer import validate_summary
    source = batch('请查订单 O-101 的物流；另外订单 O-202 我要申请退款。', '会分别核实。')
    summary = '用户查询订单 O-101 的物流，另希望针对订单 O-202 申请退款；两项诉求分别对应已明确的订单，物流和退款均尚无处理结果。'
    assert validate_summary(summary, source) == summary


def test_separate_clear_complete_turns_can_share_summary_without_invented_uncertainty():
    from app.context.summarizer import validate_summary
    first = batch('请查订单 O-101 的物流。', '等待物流结果。')
    second = batch('订单 O-202 我要申请退款。', '还未提交申请。', start=3)
    rows = first.source_rows + second.source_rows
    combined = replace(first, source_rows=rows, upto_msg_id=4, source_hash=_source_hash(rows))
    summary = '用户先查询订单 O-101 的物流，后希望针对订单 O-202 申请退款；这两项诉求各有明确订单，尚无处理结果。'
    assert validate_summary(summary, combined) == summary


@pytest.mark.parametrize('user', [
    '订单 O-101 和 O-202 都买过，帮我看看那个到哪里了。',
    '订单 O-101 和 O-202 我还没区分，想查其中一单的物流。',
    '请查订单 O-101 和 O-202 中的一单，还没有明确具体是哪单。',
])
def test_actual_unresolved_order_reference_cannot_be_summarized_as_distinguished(user):
    from app.context.summarizer import validate_summary
    with pytest.raises(ValueError):
        validate_summary('用户已明确分别查询订单 O-101 和订单 O-202 的物流。', batch(user, '请确认要查哪一单。'))


def order_sequence(*turns):
    first = batch(*turns[0])
    rows = first.source_rows
    for index, turn in enumerate(turns[1:], start=1):
        rows += batch(*turn, start=2*index+1).source_rows
    return replace(first, source_rows=rows, upto_msg_id=len(rows), source_hash=_source_hash(rows))


def test_cross_turn_unresolved_reference_cannot_select_an_order():
    from app.context.summarizer import validate_summary
    source = order_sequence(('订单 O-101 和 O-202 都买过。', '请问需要查询哪一单？'),
                            ('帮我看看那个到哪里了。', '请确认具体订单。'))
    with pytest.raises(ValueError):
        validate_summary('用户查询订单 O-101 的物流，订单 O-202 是其另一笔订单。', source)
    faithful = '用户提到订单 O-101 和 O-202，随后询问那个订单的物流，但仍未明确是哪一单，待确认具体订单。'
    assert validate_summary(faithful, source) == faithful


@pytest.mark.parametrize('followup', [None, '我也买过订单 O-101。', '可能是订单 O-101，我还不确定是哪单。'])
def test_clarification_remains_pending_until_an_explicit_user_selection(followup):
    from app.context.summarizer import validate_summary
    turns = [('订单 O-101 和 O-202 都买过。', '请问需要查询哪一单？')]
    if followup:
        turns.append((followup, '请确认具体订单。'))
    with pytest.raises(ValueError):
        validate_summary('用户查询订单 O-101 的物流，订单 O-202 是其另一笔订单。', order_sequence(*turns))


@pytest.mark.parametrize('followup', [
    '可能就是订单 O-101。', '可能就是订单O-101。', '也许就是订单 O-101。', '大概就是订单 O-101。',
    '可能就是订单编号 O-101。', '可能就是订单号为 O-101。', '可能是订单：O-101。',
    '好像就是订单 O-101。', '应该就是订单 O-101。', '或许就是订单 O-101。',
    '估计就是订单 O-101。', '似乎就是订单 O-101。', '我猜就是订单 O-101。',
    '就是订单 O-101 吧。', '可能是最开始那个订单，请查物流。',
])
def test_tentative_selection_keeps_identity_pending_until_later_confirmation(followup):
    from app.context.summarizer import validate_summary
    turns = [('订单 O-101 和 O-202 都买过，帮我看看那个到哪里了。', '请确认具体订单。'),
             (followup, '请确认具体订单。')]
    candidate = '用户查询订单 O-101 的物流，订单 O-202 是其另一笔订单。'
    with pytest.raises(ValueError, match='unresolved identity'):
        validate_summary(candidate, order_sequence(*turns))
    faithful = '用户提到订单 O-101 和 O-202，希望查询物流，具体订单仍待确认。'
    assert validate_summary(faithful, order_sequence(*turns)) == faithful
    turns.append(('我确认就是订单 O-101，请查这单物流。', '会按您确认的订单核实。'))
    assert validate_summary(candidate, order_sequence(*turns)) == candidate


@pytest.mark.parametrize('confirmation', [
    '我确认就是订单 O-101，请查吧。',
    '我选订单 O-101，请查物流，可能明天到。',
    '我选订单 O-101，请查物流，可能是运输延误。',
])
def test_definite_identity_selection_allows_politeness_and_shipping_uncertainty(confirmation):
    from app.context.summarizer import validate_summary
    source = order_sequence(('订单 O-101 和 O-202 都买过，帮我看看那个到哪里了。', '请确认具体订单。'),
                            (confirmation, '会按您确认的订单核实。'))
    candidate = '用户提及订单 O-101 和 O-202，随后确认查询订单 O-101 的物流，尚无查询结果。'
    assert validate_summary(candidate, source) == candidate


@pytest.mark.parametrize('confirmation', [
    '我选订单 O-101，请查物流，可能是订单还没发货。',
    '我选订单 O-101，请查物流，也许是订单在等揽收。',
    '我选订单 O-101，请查物流，大概就是订单物流更新慢了。',
    '我选订单 O-101，请查物流，应该是订单信息还没更新。',
])
def test_order_state_uncertainty_does_not_veto_explicit_identity_selection(confirmation):
    from app.context.summarizer import validate_summary
    source = order_sequence(('订单 O-101 和 O-202 都买过，帮我看看那个到哪里了。', '请确认具体订单。'),
                            (confirmation, '会按您确认的订单核实。'))
    candidate = '用户提及订单 O-101 和 O-202，随后确认查询订单 O-101 的物流，尚无查询结果。'
    assert validate_summary(candidate, source) == candidate


@pytest.mark.parametrize('first_user', ['订单 O-101 和 O-202 都买过。',
                                      '订单 O-101 和 O-202 都买过，帮我看看那个到哪里了。'])
def test_later_explicit_selection_resolves_earlier_uncertainty(first_user):
    from app.context.summarizer import validate_summary
    source = order_sequence((first_user, '请问需要查询哪一单？'),
                            ('帮我看看那个到哪里了。', '请确认具体订单。'),
                            ('我选订单 O-202，请查这单物流。', '会按您选定的订单核实。'))
    summary = '用户提过订单 O-101 和 O-202，后来明确选择订单 O-202 查询物流，尚无查询结果。'
    assert validate_summary(summary, source) == summary


@pytest.mark.parametrize('reference', ['最开始那个订单', '第一笔订单'])
def test_explicit_positional_reference_does_not_invent_ambiguity(reference):
    from app.context.summarizer import validate_summary
    source = order_sequence(('订单 O-101 和 O-202 都买过，帮我看看那个到哪里了。', '请确认具体订单。'),
                            (f'我说的是{reference}，请查物流。', '会核实其物流。'))
    summary = '用户提及订单 O-101 和 O-202，随后明确要查最开始的订单 O-101 的物流；尚无查询结果。'
    assert validate_summary(summary, source) == summary


def test_reference_after_distinct_clear_turns_uses_recent_narrowed_scope():
    from app.context.summarizer import validate_summary
    source = order_sequence(('请查订单 O-101 的物流。', '会核实。'),
                            ('订单 O-202 我要申请退款。', '尚无处理结果。'),
                            ('那个订单的退款怎么样了？', '需要查询进度。'))
    summary = '用户先查订单 O-101 的物流，后询问订单 O-202 的退款申请及进度，尚无处理结果。'
    assert validate_summary(summary, source) == summary


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
