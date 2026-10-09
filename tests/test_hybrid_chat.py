# 混合知识聊天契约：真实质量服务配合可控外部模型，不请求云端。
import asyncio
import json

import pytest
from langchain_core.messages import AIMessage, AIMessageChunk
from pydantic import ValidationError

from app.core.answer_validation import REFUSAL_TEXT
from app.core.sufficiency import SufficiencyService
from app.schemas.chat import ChatRequest
from app.tools.executor import ToolExecutor
from app.tools.types import ToolCall, ToolContext, ToolOutcome
from tests.fakes import AssessmentModel, fake_settings
from tests.tool_fakes import ControlledExecutor, ToolModel, ToolRepository, collect, selected_call, setup_service


class QualityStore:
    # 模拟原子边界，失败时不追加助手和池记录。
    def __init__(self, repository, fail=False):
        self.repository, self.fail, self.pool = repository, fail, []

    # 原子拒答返回当前真实消息编号，测试核对 done 使用该编号。
    async def commit_refusal(self, conversation_id, answer, **kwargs):
        if self.fail:
            raise RuntimeError('controlled transaction failure')
        identifier = await self.repository.append_message(conversation_id, answer)
        self.pool.append(kwargs)
        return identifier


# 独立手写四条相关度，期望展示序 1、3、4、2 而不是重新编号。
def payload():
    return {'found': True, 'matches': [
        {'id': 9007199254740993 + n, 'question': f'规则{n}', 'answer': f'答案{n}',
         'score': score, 'score_kind': 'rerank', 'section_path': f'章节{n}'}
        for n, score in enumerate([.9, .8, .7, .6])],
        'retrieval': {'strategy': 'hybrid_rerank', 'candidate_count': 4, 'match_count': 4}}


# 组装真实聊天和充分性服务，仅替代外部工具结果和模型响应。
def hybrid_service(*, useful=True, no_tool=False, chunks=None, failure=None, fail_commit=False, budget=8000):
    selected = AIMessage('', response_metadata={'finish_reason': 'stop'}) if no_tool else selected_call('query_faq', {'keyword': '退货'})
    model = ToolModel(selected, chunks or [AIMessageChunk('答案0[1]。', response_metadata={'finish_reason': 'stop'})])
    service, _, repository, executor, contexts = setup_service(model=model, executor=ControlledExecutor(ToolOutcome(payload(), 'success', 1)), budget=budget)
    quality = QualityStore(repository, fail_commit)
    assessment = SufficiencyService(AssessmentModel(useful, failure=failure), input_budget=budget, minimum_rerank_score=.5)
    # 先断言公开接口，RED 不以意外 TypeError 或缺失 import 冒充行为失败。
    import inspect
    assert 'sufficiency_service' in inspect.signature(type(service)).parameters, 'chat quality dependencies are missing'
    service = type(service)(model, repository, service.registry_factory, service.locks, service.settings,
                           executor=executor, sufficiency_service=assessment, quality_repository=quality)
    return service, model, repository, quality, contexts


# 若引用先后顺序、持久 payload 或 done 主键偏离本轮真实输入，本测试失败。
async def test_citations_precede_deltas_and_done_follows_actual_commit():
    service, model, repository, quality, contexts = hybrid_service()
    trace = repository.trace
    events = await collect(service, await service.prepare('9007199254740993', '退货规则', category='售后'), trace)
    names = [event.event for event in events]
    assert names.index('citations') < names.index('delta') < names.index('done')
    assert trace.index('commit_final') < trace.index('done')
    citations = next(event.data['citations'] for event in events if event.event == 'citations')
    assert [item['n'] for item in citations] == [1, 3, 4, 2]
    assert [item['chunk_id'] for item in citations] == ['9007199254740993', '9007199254740995', '9007199254740996', '9007199254740994']
    saved = next(row.content for row in repository.rows if row.role == 'tool')
    assert saved == model.final_input[-1].content
    assert [item['n'] for item in json.loads(saved)['matches']] == [1, 3, 4, 2]
    assert events[-1].data == {'conversation_id': '9007199254740993', 'message_id': str(repository.rows[-1].id)}
    assert contexts[-1].category == '售后' and quality.pool == []


# 缺证据和合法 false 都必须固定拒答，不能让自由模型生成拒答或入池两次。
@pytest.mark.parametrize('no_tool', [False, True])
async def test_insufficient_is_fixed_atomic_refusal_without_free_generation(no_tool):
    service, model, repository, quality, _ = hybrid_service(useful=False, no_tool=no_tool)
    events = await collect(service, await service.prepare('42', '退货规则'))
    assert ''.join(event.data['delta'] for event in events if event.event == 'delta') == REFUSAL_TEXT
    assert model.final_stream_requests == 0
    assert len(quality.pool) == 1 and repository.rows[-1].content == REFUSAL_TEXT
    assert events[-1].data['message_id'] == str(repository.rows[-1].id)


# 非法引用、非 stop 和再次工具申请都不能形成完整回答或问题池。
@pytest.mark.parametrize('chunks', [
    [AIMessageChunk('答案[99]', response_metadata={'finish_reason': 'stop'})],
    [AIMessageChunk('答案[1]', response_metadata={'finish_reason': 'length'})],
    [AIMessageChunk('答案[1]', tool_call_chunks=[{'name': 'query_faq', 'args': '{}', 'id': 'again', 'index': 0}], response_metadata={'finish_reason': 'stop'})],
])
async def test_invalid_final_never_commits_answer_or_pool(chunks):
    service, _, repository, quality, _ = hybrid_service(chunks=chunks)
    events = await collect(service, await service.prepare('42', '退货规则'))
    assert events[-1].event == 'error' and quality.pool == []
    assert not any(row.role == 'assistant' and not row.tool_calls for row in repository.rows)


# 自评外部故障以及提交失败必须可见 error，不能成功或记录低置信池。
@pytest.mark.parametrize('failure,fail_commit', [(TimeoutError(), False), (RuntimeError('provider'), False), (None, True)])
async def test_failures_have_no_success_or_pool(failure, fail_commit):
    service, _, repository, quality, _ = hybrid_service(useful=False, failure=failure, fail_commit=fail_commit)
    events = await collect(service, await service.prepare('42', '退货规则'))
    assert events[-1].event == 'error' and quality.pool == []
    assert not any(row.role == 'assistant' and not row.tool_calls for row in repository.rows)


# FAQ 错误停止本轮，其他业务工具错误仍保留旧正常回答路线。
async def test_faq_failure_never_enters_free_answer():
    service, model, repository, quality, _ = hybrid_service()
    service.executor.outcome = ToolOutcome({'error': {'code': 'tool_timeout', 'message': '超时'}}, 'error', 1)
    events = await collect(service, await service.prepare('42', '退货规则'))
    assert events[-1].event == 'error' and model.final_stream_requests == 0 and quality.pool == []


# 无工具问候仍核验最终非事实输出，不允许绕过自评附加商家政策。
async def test_no_tool_social_answer_cannot_add_unverified_policy():
    service, model, repository, quality, _ = hybrid_service(no_tool=True,
        chunks=[AIMessageChunk('您好，七天内都能退货。', response_metadata={'finish_reason': 'stop'})])
    service.sufficiency_service = SufficiencyService(AssessmentModel(kind='social'), input_budget=8000, minimum_rerank_score=.5)
    events = await collect(service, await service.prepare('42', '你好'))
    assert events[-1].data['code'] == 'invalid_answer' and quality.pool == []
    assert model.final_stream_requests == 1 and len(repository.rows) == 1


# 四个业务工具沿用已有证据和正常流，不调用知识自评或发送伪造引用。
@pytest.mark.parametrize('name,args', [('query_order', {'order_id': 'A-42'}), ('query_product', {'product_id': 'P7'}),
                                     ('query_logistics', {'order_id': 'A-42'}), ('create_ticket', {'description': '需要人工', 'ticket_type': '咨询'})])
async def test_business_tools_preserve_normal_flow_without_fake_knowledge(name, args):
    service, model, repository, quality, _ = hybrid_service()
    model.selected = selected_call(name, args)
    model.chunks = [AIMessageChunk('模拟业务结果。', response_metadata={'finish_reason': 'stop'})]
    service.executor.outcome = ToolOutcome({'mock': True, 'status': '演示'}, 'success', 1)
    service.sufficiency_service = SufficiencyService(AssessmentModel(failure=AssertionError('business must not self-check')),
                                                   input_budget=8000, minimum_rerank_score=.5)
    events = await collect(service, await service.prepare('42', '查订单 A-42'))
    assert events[-1].event == 'done' and quality.pool == []
    assert not any(event.event == 'citations' or event.data.get('phase') == 'checking' for event in events)
    assert json.loads(model.final_input[-1].content) == {'mock': True, 'status': '演示'}


# 单轮总预算覆盖选择阶段，且取消向外传播，不伪装知识不足。
async def test_total_deadline_and_cancellation_never_commit():
    service, model, repository, quality, _ = hybrid_service()
    started = asyncio.Event()
    # 外部模型永久等待，以可观测事件定位总期限。
    async def wait(messages):
        started.set()
        await asyncio.Event().wait()
    model.ainvoke = wait
    service.settings = service.settings.model_copy(update={'chat_timeout_seconds': .02})
    events = await collect(service, await service.prepare('42', '退货规则'))
    assert events[-1].data['code'] == 'upstream_timeout' and quality.pool == []
    assert not any(row.role == 'assistant' and not row.tool_calls for row in repository.rows)
    service.settings = service.settings.model_copy(update={'chat_timeout_seconds': 2})
    started.clear()
    task = asyncio.create_task(collect(service, await service.prepare('42', '退货规则')))
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert quality.pool == []
    assert not any(row.role == 'assistant' and not row.tool_calls for row in repository.rows)
    # 取消后同一会话可立即重新占用，凭证由collect的finally归还。
    prepared = await service.prepare('42', '退货规则')
    service.release(prepared)


# category 在 HTTP 边界严格校验，不接受数字、空白或超长过滤值。
@pytest.mark.parametrize('category', [123, True, '', ' ', '中' * 256])
def test_category_is_strict_bounded_text(category):
    with pytest.raises(ValidationError):
        ChatRequest(conversation_id='9007199254740993', message='退货规则', category=category)


# HTTP 分类和巨大整数身份原样保留，不经过浮点归一化。
def test_valid_category_and_identity_remain_exact_strings():
    request = ChatRequest(conversation_id='18446744073709551615', message='退货规则', category='中' * 255)
    assert request.conversation_id == '18446744073709551615' and request.category == '中' * 255


# 配置不能扩大线上总期限或 FAQ 期限，也不能把布尔值当秒数。
@pytest.mark.parametrize('field,value', [('chat_timeout_seconds', 241), ('faq_timeout_seconds', 91),
                                      ('chat_timeout_seconds', True), ('faq_timeout_seconds', True)])
def test_online_deadline_config_cannot_exceed_hard_limits(field, value):
    with pytest.raises(ValidationError):
        fake_settings(**{field: value})


# 模型选择必须看到知识查询边界，不能以模拟商品库存替代售后知识。
async def test_selection_prompt_requires_faq_for_policy_and_model_knowledge():
    from app.core.prompts import build_tool_chat_system_prompt
    prompt = build_tool_chat_system_prompt()
    assert '商家政策、FAQ、商品型号参数和售后条件必须选择 query_faq' in prompt
    assert 'query_product 仅查询模拟价格和库存' in prompt


# 模型仅看到 keyword，完整原话和分类由可信工具闭包传给检索。
async def test_faq_trusts_request_context_and_hides_category():
    from app.tools.registry import build_registry
    from tests.tool_fakes import Tickets
    calls = []
    class FAQ:
        # 接收完整原话与分类；测试断言真实工具调用的数据边界。
        async def retrieve(self, keyword, **kwargs):
            calls.append((keyword, kwargs))
            return payload()
    import inspect
    assert 'category' in inspect.signature(ToolContext).parameters, 'trusted category is missing'
    registry = build_registry(FAQ(), Tickets(), ToolContext('42', 101, '商品X9退货规则', '售后'))
    assert set(registry['query_faq'].tool_call_schema.model_json_schema()['properties']) == {'keyword'}
    outcome = await ToolExecutor().execute(ToolCall('faq', 'query_faq', {'keyword': '退货'}), registry)
    assert outcome.status == 'success'
    assert calls == [('退货', {'raw_question': '商品X9退货规则', 'category': '售后'})]


# FAQ 零重试覆盖原默认重试策略，失败没有第二次真实调用。
async def test_faq_timeout_override_has_zero_retries():
    from langchain_core.tools import tool
    calls = []
    # 阻塞外部依赖，核对 deadline 取消执行且不重试。
    @tool
    async def query_faq(keyword: str) -> dict:
        """测试 FAQ 超时。"""
        calls.append(keyword)
        await asyncio.Event().wait()
    import inspect
    assert 'overrides' in inspect.signature(ToolExecutor).parameters, 'per-tool deadlines are missing'
    outcome = await ToolExecutor(.01, 1, overrides={'query_faq': (.02, 0)}).execute(ToolCall('faq', 'query_faq', {'keyword': '退货'}), {'query_faq': query_faq})
    assert outcome.status == 'error' and outcome.attempts == 1 and calls == ['退货']


# 非法自评 JSON 与超预算证据都走故障，不得记录低置信池。
@pytest.mark.parametrize('case', ['invalid_assessment', 'evidence_budget'])
async def test_invalid_assessment_or_evidence_budget_has_no_pool(case):
    service, model, repository, quality, _ = hybrid_service()
    if case == 'invalid_assessment':
        assessment = AssessmentModel()
        assessment.data['useful'] = 'false'
        service.sufficiency_service = SufficiencyService(assessment, input_budget=8000, minimum_rerank_score=.5)
    else:
        content = payload()
        for item in content['matches']:
            item['answer'] = '中' * 25000
        service.executor.outcome = ToolOutcome(content, 'success', 1)
    events = await collect(service, await service.prepare('42', '退货规则'))
    assert events[-1].event == 'error' and quality.pool == [] and model.final_stream_requests == 0
    assert events[-1].data['code'] == ('invalid_structured_output' if case == 'invalid_assessment' else 'input_too_long')
    assert not any(row.role == 'assistant' and not row.tool_calls for row in repository.rows)


# 固定拒答已发送但客户端取消时，不得开启原子提交或留下问题池。
async def test_cancel_after_refusal_delta_prevents_atomic_commit():
    service, model, repository, quality, _ = hybrid_service(useful=False)
    prepared = await service.prepare('42', '退货规则')
    events = service.stream(prepared)
    try:
        async for event in events:
            if event.event == 'delta':
                break
    finally:
        await events.aclose()
        service.release(prepared)
    assert quality.pool == [] and model.final_stream_requests == 0
    assert not any(row.role == 'assistant' and not row.tool_calls for row in repository.rows)


# 真实回环 TCP + 独立 MySQL：中文按单字节解码，首增量在末片段放行前到达。
@pytest.mark.parametrize('refuse', [False, True])
async def test_real_tcp_utf8_terminal_and_actual_mysql_commit(mysql_database, refuse):
    import codecs
    import httpx
    from sqlalchemy import text
    from uuid import uuid4
    from app.main import create_app
    from app.repositories.conversations import ConversationRepository
    from app.quality.repository import QualityRepository
    from tests.fakes import StreamingModel
    from tests.test_network_stream import local_server

    repository = ConversationRepository(mysql_database)
    conversation_id = await repository.create('task7_tcp_' + uuid4().hex)
    model = StreamingModel([AIMessageChunk('中文答案'), AIMessageChunk('[1]。'),
                            AIMessageChunk('', response_metadata={'finish_reason': 'stop'})], gate_at=1)
    model.selected = selected_call('query_faq', {'keyword': '退货'})
    class FAQ:
        # 固定受控知识证据，不连接嵌入、重排或云端模型。
        async def retrieve(self, *args, **kwargs):
            return payload()
    sufficiency = SufficiencyService(AssessmentModel(useful=not refuse), input_budget=8000, minimum_rerank_score=.5)
    app = create_app(fake_settings(), model=model, database=mysql_database, repository=repository,
        faq_repository=FAQ(), sufficiency_service=sufficiency, quality_repository=QualityRepository(mysql_database))
    try:
        async with local_server(app) as url, httpx.AsyncClient(base_url=url, trust_env=False) as client:
            async with client.stream('POST', '/api/chat', json={'conversation_id': conversation_id, 'message': '退货规则', 'category': '售后'}) as response:
                assert response.status_code == 200
                decoder = codecs.getincrementaldecoder('utf-8')()
                frames, pending = [], ''
                async for octet in response.aiter_bytes(chunk_size=1):
                    pending += decoder.decode(octet)
                    if pending.endswith('\n\n'):
                        event, data = pending.strip().split('\n', 1)
                        frames.append((event.removeprefix('event: '), json.loads(data.removeprefix('data: '))))
                        pending = ''
                        if frames[-1][0] == 'delta' and not refuse and not model.gate.is_set():
                            assert frames[-1][1]['delta'] == '中文答案'
                            await asyncio.wait_for(model.waiting.wait(), 2)
                            assert not model.eof.is_set()
                            rows = await repository.load_messages(conversation_id)
                            assert not any(row.role == 'assistant' and not row.tool_calls for row in rows)
                            model.gate.set()
                assert decoder.decode(b'', final=True) == '' and pending == ''
                names = [event for event, _ in frames]
                assert names.index('citations') < names.index('delta') < names.index('done')
                assert names.count('done') == 1 and names[-1] == 'done' and 'error' not in names
        rows = await repository.load_messages(conversation_id)
        assert frames[-1][1] == {'conversation_id': conversation_id, 'message_id': str(rows[-1].id)}
        assert rows[-1].content == (REFUSAL_TEXT if refuse else '中文答案[1]。')
        async with mysql_database.session() as session:
            count = await session.scalar(text('SELECT COUNT(*) FROM low_confidence_questions WHERE conversation_id=:id'), {'id': int(conversation_id)})
        assert count == (1 if refuse else 0)
        assert not refuse or model.calls == []
    finally:
        # 仅清理本测试新建会话，绝不读取或修改业务库与他人历史。
        async with mysql_database.session() as session, session.begin():
            for table in ('low_confidence_questions', 'messages', 'conversations'):
                column = 'id' if table == 'conversations' else 'conversation_id'
                await session.execute(text(f'DELETE FROM {table} WHERE {column}=:id'), {'id': int(conversation_id)})
