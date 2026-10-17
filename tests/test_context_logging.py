"""Actual UTF-8 JSON body records remain independent of metadata audit."""
import json

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from app.context.view import compose_call
from tests.test_context_view import snapshot


def test_logger_records_complete_packet_without_client_credentials(tmp_path):
    from app.context.logging import ContextLogger
    path = tmp_path / 'log' / 'app.log'
    logger = ContextLogger(path)
    frozen = snapshot()
    long_result = json.dumps({'order_id': 'A-1', 'description': '完整工具正文' * 100}, ensure_ascii=False)
    packet = compose_call(frozen, system=SystemMessage('系统'), current=HumanMessage('订单 A-1'),
        attachment={'summary_note': '全文摘要\n第二行'}, tools=[], output_tokens=512,
        pending=[AIMessage('', tool_calls=[{'id': 'read1', 'name': 'query_order', 'args': {'order_id': 'A-1'}}]),
                 ToolMessage(long_result, tool_call_id='read1')])
    logger.history(frozen, consumer='prepare', packet=None, sent=False)
    logger.model(packet, conversation_id='42', user_message_id='99', phase='decision', call_index=1)
    logger.close()
    raw = path.read_text(encoding='utf-8')
    records = [json.loads(line) for line in raw.splitlines()]
    assert records[0]['event'] == 'history_ctx' and records[0]['sent'] is False
    assert records[1]['messages'][-1] == {'role': 'tool', 'content': long_result, 'tool_call_id': 'read1'}
    assert records[1]['messages'][0] == {'role': 'system', 'content': '系统'}
    assert '全文摘要' in records[1]['messages'][2]['content']
    assert 'Authorization' not in raw and 'runtime-secret' not in raw


async def test_summary_logs_the_body_before_failed_invocation(tmp_path):
    import pytest
    from app.context.summarizer import SummaryGenerator
    from app.context.logging import ContextLogger
    from tests.test_context_summarizer import settings, batch

    class Failed:
        def bind(self, **kwargs):
            return self
        async def ainvoke(self, messages):
            records = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
            assert records[-1]['phase'] == 'summary'
            assert records[-1]['messages'][1]['content'] == messages[1].content
            raise RuntimeError('upstream failure runtime-secret Authorization')
    path = tmp_path / 'app.log'
    logger = ContextLogger(path)
    generator = SummaryGenerator(Failed(), settings(), context_logger=logger)
    with pytest.raises(RuntimeError):
        await generator.summarize(batch())
    logger.close()
    assert 'runtime-secret' not in path.read_text(encoding='utf-8')


async def test_actual_http_summary_payload_matches_log_without_runtime_authorization(tmp_path):
    import httpx
    import pytest
    from app.core.llm import create_model
    from app.context.summarizer import SummaryGenerator
    from app.context.logging import ContextLogger
    from tests.test_context_summarizer import settings, batch
    path = tmp_path / 'app.log'
    requests = []
    def respond(request):
        requests.append(json.loads(request.content))
        assert request.headers['Authorization'] == 'Bearer test-only'
        return httpx.Response(500, json={'error': {'message': 'controlled'}})
    logger = ContextLogger(path)
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        model = create_model(settings(), http_async_client=client)
        try:
            with pytest.raises(Exception):
                await SummaryGenerator(model, settings(), context_logger=logger).summarize(
                    batch(tool={'order_id': 'O-101', 'model': 'M-1', 'mock': True, 'details': '全文工具 JSON' * 100}))
        finally:
            await model.root_async_client.close()
            model.root_client.close()
    logger.close()
    records = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
    assert len(requests) == len(records) == 1
    assert records[0]['messages'] == requests[0]['messages']
    assert records[0]['output_tokens'] == requests[0]['max_tokens'] == 512
    raw = path.read_text(encoding='utf-8')
    assert 'Authorization' not in raw and 'test-only' not in raw


async def test_cancelled_understanding_retains_sent_body_and_single_usage(tmp_path):
    import asyncio
    import pytest
    from app.context.logging import ContextLogger
    from app.workflow.understanding import QueryUnderstanding
    entered = asyncio.Event()
    class Blocked:
        def with_structured_output(self, *args, **kwargs):
            return self
        async def ainvoke(self, messages):
            entered.set()
            await asyncio.Event().wait()
    path = tmp_path / 'app.log'
    logger = ContextLogger(path)
    service = QueryUnderstanding(Blocked(), input_budget=8000, timeout_seconds=20)
    task = asyncio.create_task(service.resolve('订单 A-1', [], snapshot=snapshot(), context_logger=logger))
    await asyncio.wait_for(entered.wait(), 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    logger.close()
    events = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
    assert [row['event'] for row in events] == ['history_ctx', 'model_ctx', 'token_calibration']
    assert events[2]['prompt_tokens'] is None and events[2]['absolute_error'] is None
    assert events[2]['relative_error'] is None and events[2]['calibrated'] is False
    assert events[1]['messages'][-2]['content'] == '订单 A-1'
    assert service.usage['estimated_calls'] == 1 and service.usage['actual_calls'] == 0
