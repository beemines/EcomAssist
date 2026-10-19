import asyncio
import json
from types import SimpleNamespace
from uuid import uuid4

import pytest


@pytest.fixture
def local_exporter():
    from langfuse import Langfuse
    from app.observability.tracing import create_callback_handler
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from app.observability.runtime import LangfuseRuntime
    exporter = InMemorySpanExporter()
    public_key = 'pk-test-' + uuid4().hex
    client = Langfuse(public_key=public_key, secret_key='unused',
        base_url='http://127.0.0.1:1', tracer_provider=TracerProvider(), span_exporter=exporter)
    yield LangfuseRuntime(client=client, handler=create_callback_handler(public_key=public_key)), exporter
    client.shutdown()


def identity(conv='1', turn='2', **extra):
    from app.observability.tracing import ExecutionIdentity
    return ExecutionIdentity(conv, turn, uuid4().hex, 'chat', **extra)


def metadata(span, key):
    raw = span.attributes.get('langfuse.observation.metadata.' + key)
    return json.loads(raw) if raw is not None else None


async def test_concurrent_execution_scopes_do_not_cross_sessions(local_exporter):
    from app.observability.tracing import begin_execution, current_execution, operation
    runtime, exporter = local_exporter

    async def one(conv, intent):
        with begin_execution(runtime, identity(conv)) as trace:
            trace.set_intent(intent, .9, 'business')
            await asyncio.sleep(0)
            assert current_execution().identity.conversation_id == conv
            with operation('query_order', input={'order_id': conv}, metadata={'observation_type': 'tool'}) as step:
                step.update(output={'status': '已付款'})
            trace.finish('success')

    await asyncio.gather(one('1', '物流'), one('2', '订单'))
    runtime.client.flush()
    spans = exporter.get_finished_spans()
    roots = [span for span in spans if span.name == 'ch09.execution']
    assert len(roots) == 2
    assert {span.attributes['session.id'] for span in roots} == {'1', '2'}
    by_trace = {span.context.trace_id: metadata(span, 'intent') for span in roots}
    assert set(by_trace.values()) == {'物流', '订单'}
    assert all(span.context.trace_id in by_trace for span in spans)
    assert current_execution() is None


def test_resume_has_same_logical_turn_but_new_trace(local_exporter):
    from app.observability.tracing import begin_execution
    runtime, exporter = local_exporter
    for result in ('paused', 'success'):
        with begin_execution(runtime, identity()) as trace:
            trace.set_intent('工单', 1, 'business')
            trace.finish(result)
    runtime.client.flush()
    roots = [span for span in exporter.get_finished_spans() if span.name == 'ch09.execution']
    assert len({span.context.trace_id for span in roots}) == 2
    assert {metadata(span, 'logical_turn_id') for span in roots} == {'1:2'}
    assert {metadata(span, 'outcome') for span in roots} == {'paused', 'success'}


def test_background_execution_does_not_inherit_active_chat_trace(local_exporter):
    from app.observability.tracing import begin_execution, ExecutionIdentity
    runtime, exporter = local_exporter
    with begin_execution(runtime, identity()):
        with begin_execution(runtime, ExecutionIdentity('1', '2', uuid4().hex, 'summary')):
            pass
    runtime.client.flush()
    roots = [span for span in exporter.get_finished_spans() if span.name == 'ch09.execution']
    assert len({span.context.trace_id for span in roots}) == 2
    assert {metadata(span, 'purpose') for span in roots} == {'chat', 'summary'}


def test_replay_does_not_create_new_observations(local_exporter):
    from app.observability.tracing import begin_execution, operation
    runtime, exporter = local_exporter
    with begin_execution(runtime, identity(replay=True)):
        with operation('read_saved_result', input={}, metadata={}):
            pass
    runtime.client.flush()
    assert exporter.get_finished_spans() == ()


async def test_cancellation_finishes_root_without_leaking_context(local_exporter):
    from app.observability.tracing import begin_execution, current_execution
    runtime, exporter = local_exporter
    ready = asyncio.Event()

    async def execute():
        with begin_execution(runtime, identity()):
            ready.set()
            await asyncio.Event().wait()

    task = asyncio.create_task(execute())
    await ready.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    runtime.client.flush()
    [span] = exporter.get_finished_spans()
    assert metadata(span, 'outcome') == 'cancelled'
    assert current_execution() is None


def test_tracking_error_does_not_change_business_result_or_leak_key(caplog):
    from app.observability.tracing import begin_execution, operation

    class BrokenClient:
        def start_as_current_observation(self, **kwargs):
            raise RuntimeError('sk-secret')

    runtime = SimpleNamespace(client=BrokenClient())
    with begin_execution(runtime, identity()) as trace:
        trace.set_intent('物流', .9, 'business')
        with operation('read', input={}, metadata={}):
            result = 'business answer'
        trace.finish('success')
    assert result == 'business answer'
    assert 'sk-secret' not in caplog.text


def test_operation_does_not_suppress_business_error(local_exporter):
    from app.observability.tracing import begin_execution, operation
    runtime, exporter = local_exporter
    with pytest.raises(ValueError, match='business failed'):
        with begin_execution(runtime, identity()):
            with operation('read', input={}, metadata={}):
                raise ValueError('business failed')
    runtime.client.flush()
    roots = [span for span in exporter.get_finished_spans() if span.name == 'ch09.execution']
    assert metadata(roots[0], 'outcome') == 'error'


async def test_actual_workflow_records_nodes_and_final_intent(tmp_path, local_exporter, caplog):
    from app.main import create_app
    from tests.fakes import FAQStub, fake_settings, decode_sse
    from tests.test_workflow_api import Store, request
    from tests.workflow_fakes import ScriptedWorkflowModel
    runtime, exporter = local_exporter
    store = Store()
    from pydantic import SecretStr
    settings = fake_settings(workflow_checkpoint_path=tmp_path / 'trace.sqlite').model_copy(
        update={'llm_api_key': SecretStr('sensitive-trace-sentinel')})
    app = create_app(settings, model=ScriptedWorkflowModel(), repository=store,
        faq_repository=FAQStub(), quality_repository=store, observability_runtime=runtime)
    async with app.router.lifespan_context(app):
        frames = decode_sse((await request(app, '你好')).text)
        assert frames[-1][0] == 'done'
    runtime.client.flush()
    spans = exporter.get_finished_spans()
    [root] = [span for span in spans if span.name == 'ch09.execution']
    assert metadata(root, 'intent') == '闲聊' and metadata(root, 'outcome') == 'success'
    assert {'resolve_reference', 'classify_intent', 'social_response', 'log_response'} <= {span.name for span in spans}
    assert 'sensitive-trace-sentinel' not in str([dict(span.attributes) for span in spans])
    assert 'stage=close degraded' not in caplog.text


async def test_deterministic_retrieval_has_original_results_in_child_span(tmp_path, local_exporter):
    from tests.test_workflow_api import workflow_app, request, intent
    from tests.workflow_fakes import ScriptedWorkflowModel
    from tests.fakes import decode_sse
    runtime, exporter = local_exporter
    model = ScriptedWorkflowModel(intent_replies=[intent('商品咨询')])
    async with workflow_app(tmp_path, model=model, observability_runtime=runtime) as app:
        frames = decode_sse((await request(app, '运费多少')).text)
    assert frames[-1][0] == 'done'
    runtime.client.flush()
    spans = exporter.get_finished_spans()
    [retrieval] = [span for span in spans if span.name == 'knowledge.retrieve']
    payload = json.loads(retrieval.attributes['langfuse.observation.output'])
    assert isinstance(payload['evidence'], dict)
    assert 'matches' in payload['evidence']


async def test_summary_generation_has_separate_purpose_and_model_observation(local_exporter):
    import httpx
    from app.core.llm import create_model
    from app.context.summarizer import SummaryGenerator
    from app.observability.tracing import begin_execution
    from tests.test_context_summarizer import batch, settings
    runtime, exporter = local_exporter

    async def response(request):
        return httpx.Response(200, json={'id': 'summary-offline', 'object': 'chat.completion',
            'created': 0, 'model': 'fake', 'usage': {'prompt_tokens': 10, 'completion_tokens': 3, 'total_tokens': 13},
            'choices': [{'index': 0, 'message': {'role': 'assistant',
                'content': '{"content":"订单 O-101 的包裹未找到。"}'}, 'finish_reason': 'stop'}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(response)) as http:
        config = settings()
        model = create_model(config, http_async_client=http)
        try:
            generator = SummaryGenerator(model, config, observability=runtime)
            with begin_execution(runtime, identity()):
                assert await generator.summarize(batch()) == '订单 O-101 的包裹未找到。'
        finally:
            model.root_client.close()
            await model.root_async_client.close()
    runtime.client.flush()
    spans = exporter.get_finished_spans()
    roots = [span for span in spans if span.name == 'ch09.execution']
    assert len({span.context.trace_id for span in roots}) == 2
    [summary] = [span for span in roots if metadata(span, 'purpose') == 'summary']
    generations = [span for span in spans if span.attributes.get('langfuse.observation.type') == 'generation']
    assert len(generations) == 1 and generations[0].context.trace_id == summary.context.trace_id


async def test_model_callback_observes_intent_updated_from_another_task(local_exporter):
    import httpx
    from app.core.llm import create_model
    from app.observability.tracing import begin_execution
    from tests.test_context_summarizer import settings
    from langchain_core.messages import HumanMessage
    runtime, exporter = local_exporter

    async def response(request):
        return httpx.Response(200, json={'id': 'callback-offline', 'object': 'chat.completion',
            'created': 0, 'model': 'fake', 'usage': {'prompt_tokens': 2, 'completion_tokens': 1, 'total_tokens': 3},
            'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': 'ok'}, 'finish_reason': 'stop'}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(response)) as http:
        model = create_model(settings(), http_async_client=http)
        try:
            with begin_execution(runtime, identity()) as trace:
                async def classify():
                    trace.set_intent('物流', .9, 'business')
                await asyncio.create_task(classify())
                await model.ainvoke([HumanMessage('probe')], config={'callbacks': [runtime.handler]})
        finally:
            model.root_client.close()
            await model.root_async_client.close()
    runtime.client.flush()
    [generation] = [span for span in exporter.get_finished_spans()
        if span.attributes.get('langfuse.observation.type') == 'generation']
    assert metadata(generation, 'intent') == '物流'


async def test_rank_trace_keeps_recall_score_separate_from_rerank(local_exporter):
    from app.observability.tracing import begin_execution
    from app.knowledge.types import ChunkRecord, VectorHit
    from app.retrieval.types import RerankHit
    from tests.test_retrieval_service import service_parts
    runtime, exporter = local_exporter
    row = ChunkRecord('售后', '退货问题', '原始政策条文', id=7, vectorize_status='done')
    service, *_ = service_parts([VectorHit(7, .8)], [row], [RerankHit(index=0, score=.12)])
    with begin_execution(runtime, identity()):
        await service.retrieve('这个能退吗', category='售后')
    runtime.client.flush()
    [rank] = [span for span in exporter.get_finished_spans() if span.name == 'retrieval.rank']
    payload = json.loads(rank.attributes['langfuse.observation.output'])
    assert payload['candidate_score_kind'] == 'rrf'
    assert payload['candidates'] == [{'id': '7', 'rank': 1, 'score': .8}]
    assert payload['evidence']['matches'][0]['score_kind'] == 'rerank'
    assert payload['evidence']['matches'][0]['score'] == .12
    assert payload['evidence']['matches'][0]['answer'] == '原始政策条文'


async def test_failed_tool_is_visible_as_error_without_raising_into_chat(local_exporter):
    from app.observability.tracing import begin_execution
    from app.tools.executor import ToolExecutor
    from app.tools.types import ToolCall
    runtime, exporter = local_exporter
    with begin_execution(runtime, identity()):
        outcome = await ToolExecutor().execute(ToolCall('call-1', 'missing_tool', {}), {})
    assert outcome.status == 'error'
    runtime.client.flush()
    [tool] = [span for span in exporter.get_finished_spans() if span.name == 'tool.execute.missing_tool']
    assert tool.attributes['langfuse.observation.level'] == 'ERROR'
    payload = json.loads(tool.attributes['langfuse.observation.output'])
    assert payload['attempts'] == 0 and payload['result']['error']['code'] == 'unknown_tool'
