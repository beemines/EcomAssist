"""在线链路回归：仅替换外部传输，保留严格解析、消费降级与安全错误。"""
import asyncio
import json
import logging

import httpx
from langchain_core.exceptions import OutputParserException
from langchain_core.tools import tool
from pydantic import ValidationError
import pytest

from app.core.errors import InputTooLong, ServiceError
from app.core.llm import create_model, model_with_output_budget
from app.retrieval.query import QueryPlanner
from app.tools.executor import ToolExecutor
from app.tools.types import ToolCall
from tests.fakes import ConversationStore, FAQStub, fake_settings
from tests.test_evidence import build
from tests.test_retrieval_service import service_parts


QUESTION = 'MH-W40只买一台，金额199元，未拆封且不接受换货可以退吗？'
PRIVATE = 'sk-private-key request-body-private'


@pytest.mark.parametrize('effort,evaluation', [(None, 'low'), ('low', None), ('low', 'max')])
@pytest.mark.parametrize('field', ['max_tokens', 'max_completion_tokens'])
async def test_online_owner_sends_own_effort_and_keeps_budgets_independent(monkeypatch, effort, evaluation, field):
    """漏接在线配置或借用评估配置会在真实SDK三阶段请求中暴露。"""
    import app.main as main
    assert 'online_reasoning_effort' in type(fake_settings()).model_fields, 'online effort configuration missing'
    settings = fake_settings(ONLINE_REASONING_EFFORT=effort,
        rag_evaluation_reasoning_effort=evaluation, llm_token_limit_field=field)
    requests = []

    def respond(request):
        body = json.loads(request.content)
        requests.append(body)
        prompt = body['messages'][0]['content']
        content = ('{"standard":"邮费？","expansions":[]}' if '只整理本轮原话' in prompt else
            '{"useful":true,"reason":"覆盖","response_kind":"knowledge"}'
            if '直接判断当前证据' in prompt else '答案')
        return httpx.Response(200, json=dict(id='offline', object='chat.completion', created=0,
            model='fake-chat', choices=[dict(index=0, finish_reason='stop',
                message=dict(role='assistant', content=content))]))

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as http:
        def owned_model(configuration, **kwargs):
            return create_model(configuration, http_async_client=http, **kwargs)
        monkeypatch.setattr(main, 'create_model', owned_model)
        app = main.create_app(settings, repository=ConversationStore(), faq_repository=FAQStub())
        async with app.router.lifespan_context(app):
            model = app.state.chat_service.model
            await QueryPlanner(model_with_output_budget(model, settings, 2048), 8000).plan('邮费？')
            await app.state.chat_service.sufficiency_service.check('邮费？', build())
            await model.ainvoke('final')
            assert [body[field] for body in requests] == [2048, 2048, 512]
            assert all(body.get('reasoning_effort') == effort for body in requests)
            assert all(('reasoning_effort' in body) == (effort is not None) for body in requests)
            assert model.max_retries == 0 and model.request_timeout == 60
            assert app.state.rag_evaluation_settings.rag_evaluation_reasoning_effort == evaluation
            assert settings.online_reasoning_effort == effort


@pytest.mark.parametrize('value', ['', ' ', True, False, 1, 'medium', 'high', 'max', 'unknown'])
def test_online_effort_rejects_values_other_than_low(value):
    """空白与未授权努力等级不得偷偷改成线上低思考。"""
    with pytest.raises(ValidationError):
        fake_settings(ONLINE_REASONING_EFFORT=value)


@pytest.mark.parametrize('content,finish', [
    ('[{"standard":"错误型号","expansions":[]}]', 'stop'),
    ('{"answer":{"standard":"错误型号","expansions":[]}}', 'stop'),
    ('{"standard":"错误型号","expansions":[]', 'stop'),
    ('{"standard":"错误型号","expansions":"退款"}', 'stop'),
    ('{"standard":"错误型号","expansions":[]}', 'length'),
    ('{"standard":"错误型号","expansions":[]}', 'content_filter'),
])
async def test_invalid_sdk_rewrite_falls_back_to_full_original_once(content, finish, caplog):
    """结构错误必须一次改写后用完整型号、金额和否定条件检索，不解包猜字段。"""
    requests = []
    def respond(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, json=dict(id='offline', object='chat.completion', created=0,
            model='fake-chat', choices=[dict(index=0, finish_reason=finish,
                message=dict(role='assistant', content=content))]))
    settings = fake_settings()
    service, _, _, embedder, index, _, _ = service_parts()
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as http:
        model = create_model(settings, http_async_client=http)
        service.planner = QueryPlanner(model_with_output_budget(model, settings, 2048), 8000)
        try:
            with caplog.at_level(logging.WARNING):
                bundle = await service.retrieve(QUESTION)
            assert bundle.query.standard == QUESTION and bundle.query.expansions == []
            assert embedder.texts == [QUESTION] and index.calls[0][1] == QUESTION
            assert len(requests) == 1 and requests[0]['messages'][-1]['content'] == QUESTION
            assert requests[0]['max_tokens'] == 2048
            messages = [record.getMessage() for record in caplog.records if record.name == 'app.retrieval.service']
            assert messages == ['stage=rewrite code=invalid_structured_output type=ServiceError status=degraded']
            assert all(record.exc_info is None for record in caplog.records)
        finally:
            model.root_client.close()


@pytest.mark.parametrize('failure', ['timeout', 'upstream', 'input', 'unknown', 'cancel',
    'invalid_timeout', 'invalid_input', 'invalid_unknown', 'invalid_cancel', 'invalid_context',
    'invalid_store', 'invalid_auth', 'invalid_http_timeout'])
async def test_non_structural_rewrite_failures_never_fall_back(failure, caplog):
    """宽泛捕获或忽略异常链会误触发检索，并泄露异常正文到日志。"""
    errors = dict(timeout=TimeoutError(PRIVATE), upstream=ServiceError('upstream_error', PRIVATE, 502),
        input=InputTooLong(), unknown=RuntimeError(PRIVATE), cancel=asyncio.CancelledError(PRIVATE))
    from app.rag_evaluation.store import StoreError
    errors.update(store=StoreError(PRIVATE), auth=ServiceError('authentication_error', PRIVATE, 401),
        http_timeout=httpx.ReadTimeout(PRIVATE))
    if failure.startswith('invalid_'):
        error = ServiceError('invalid_structured_output', PRIVATE, 502)
        underlying = errors['unknown' if failure == 'invalid_context' else failure.removeprefix('invalid_')]
        if failure == 'invalid_context':
            error.__context__ = underlying
        else:
            error.__cause__ = underlying
    else:
        error = errors[failure]
    service, _, repo, embedder, index, _, reranker = service_parts()
    calls = []
    class FailingPlanner:
        async def plan(self, raw_question):
            calls.append(raw_question)
            raise error
    service.planner = FailingPlanner()
    with caplog.at_level(logging.WARNING), pytest.raises(BaseException) as raised:
        await service.retrieve(QUESTION)
    assert raised.value is error or isinstance(raised.value, asyncio.CancelledError)
    assert calls == [QUESTION] and embedder.texts == index.calls == repo.calls == reranker.calls == []
    assert PRIVATE not in caplog.text and QUESTION not in caplog.text
    assert all(record.exc_info is None for record in caplog.records)


async def test_known_parser_cause_still_allows_original_query_fallback():
    """已知解析错误链不得被未知故障保护误拒绝。"""
    service, _, _, embedder, _, _, _ = service_parts()
    class ParserFailure:
        async def plan(self, question):
            parser = OutputParserException(PRIVATE)
            parser.__cause__ = json.JSONDecodeError(PRIVATE, '', 0)
            raise ServiceError('invalid_structured_output', PRIVATE, 502) from parser
    service.planner = ParserFailure()
    bundle = await service.retrieve(QUESTION)
    assert bundle.query.standard == QUESTION and embedder.texts == [QUESTION]


@pytest.mark.parametrize('invalid', [False, True])
async def test_planner_response_after_existing_deadline_never_enters_retrieval(invalid):
    """下层吞掉deadline取消后返回时，既有改写期限仍不得被成功或降级绕过。"""
    from langchain_core.messages import AIMessage
    service, _, repo, embedder, index, _, reranker = service_parts()
    calls = []
    class LateModel:
        def with_structured_output(self, schema, **kwargs):
            self.schema = schema
            return self
        async def ainvoke(self, messages):
            calls.append(messages)
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                content = '{"answer":{}}' if invalid else '{"standard":"邮费？","expansions":[]}'
                return dict(raw=AIMessage(content, response_metadata={'finish_reason': 'stop'}),
                    parsed=None if invalid else self.schema.model_validate_json(content), parsing_error=None)
    service.planner = QueryPlanner(LateModel(), 8000, timeout=.01)
    with pytest.raises(ServiceError) as raised:
        await service.retrieve(QUESTION)
    assert raised.value.code == 'upstream_timeout'
    assert len(calls) == 1 and embedder.texts == index.calls == repo.calls == reranker.calls == []


async def test_swallowed_caller_cancellation_cannot_become_success():
    """下层正常返回不代表取消已消失；取消任务必须停止全部检索依赖。"""
    from app.retrieval.types import QueryPlan
    service, _, repo, embedder, index, _, reranker = service_parts()
    entered = asyncio.Event()
    class SwallowCancellation:
        async def plan(self, question):
            entered.set()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                return QueryPlan(standard=question, expansions=[])
    service.planner = SwallowCancellation()
    task = asyncio.create_task(service.retrieve(QUESTION))
    await entered.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert embedder.texts == index.calls == repo.calls == reranker.calls == []


async def test_real_planner_deadline_is_timeout_not_caller_cancellation():
    """asyncio期限包装包含内部CancelledError，但不能误认为调用方取消。"""
    service, _, repo, embedder, index, _, reranker = service_parts()
    class WaitingModel:
        def with_structured_output(self, schema, **kwargs):
            return self
        async def ainvoke(self, messages):
            await asyncio.sleep(1)
    service.planner = QueryPlanner(WaitingModel(), 8000, timeout=.01)
    with pytest.raises(ServiceError) as raised:
        await service.retrieve(QUESTION)
    assert raised.value.code == 'upstream_timeout'
    assert embedder.texts == index.calls == repo.calls == reranker.calls == []


@pytest.mark.parametrize('code,message', [
    ('upstream_timeout', '模型响应超时，请稍后重试。'),
    ('upstream_error', '模型服务暂时不可用，请稍后重试。'),
    ('invalid_structured_output', '模型返回的结构化结果无效，请稍后重试。'),
    ('input_too_long', 'Input exceeds the context budget.'),
    ('private_arbitrary_code', '工具执行失败。'),
])
async def test_tools_preserve_safe_whitelisted_failure_codes(code, message, caplog):
    """折叠合法错误会失去可诊断分类；回显任意message/code会泄露请求正文。"""
    calls = []
    @tool
    async def query_faq(keyword: str) -> dict:
        """模拟知识链路服务错误。"""
        calls.append(keyword)
        raise ServiceError(code, PRIVATE, 502)
    with caplog.at_level(logging.WARNING):
        outcome = await ToolExecutor(max_retries=0).execute(
            ToolCall('faq', 'query_faq', {'keyword': QUESTION}), {'query_faq': query_faq})
    expected = code if code != 'private_arbitrary_code' else 'tool_execution_error'
    assert outcome.content == {'error': {'code': expected, 'message': message}}
    assert outcome.status == 'error' and outcome.attempts == 1 and calls == [QUESTION]
    assert [record.getMessage() for record in caplog.records if record.name == 'app.tools.executor'] == [
        f'stage=tool code={expected} type=ServiceError']
    assert PRIVATE not in caplog.text and QUESTION not in caplog.text and 'private_arbitrary_code' not in caplog.text
    assert all(record.exc_info is None for record in caplog.records)
