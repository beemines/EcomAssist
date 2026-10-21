"""Actual local Langfuse + LangGraph/SQLite; all paid boundaries remain offline."""
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
import time

import pytest
from dotenv import dotenv_values


async def test_workflow_trace_and_intent_usage_are_readable_locally(tmp_path, request):
    if not request.config.getoption('--run-langfuse'):
        pytest.skip('requires --run-langfuse and the local CH09 stack')
    from app.config import Settings
    from app.observability.runtime import LangfuseRuntime
    from app.observability.intent_usage import IntentUsageReader
    from tests.test_workflow_api import workflow_app, request as chat_request, intent
    from tests.workflow_fakes import ScriptedWorkflowModel
    from tests.fakes import decode_sse
    from langfuse import Langfuse
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    root = Path(__file__).resolve().parents[2]
    sdk = dict(dotenv_values(root / 'runtime/langfuse/sdk.env'))
    settings = Settings(_env_file=None, LLM_BASE_URL='https://unused.test/v1',
                        LLM_MODEL='unused', LLM_API_KEY='unused', **sdk)
    probe = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(probe))
    runtime = LangfuseRuntime.from_settings(settings,
        client_factory=lambda **kwargs: Langfuse(**kwargs, tracer_provider=provider))
    assert runtime.client is not None and runtime.handler is not None
    start = datetime.now(timezone.utc)
    try:
        async with workflow_app(tmp_path, model=ScriptedWorkflowModel(intent_replies=[intent('商品咨询')]),
                                observability_runtime=runtime) as app:
            frames = decode_sse((await chat_request(app, '运费多少')).text)
            assert frames[-1][0] == 'done'
        trace_id = runtime.handler.last_trace_id
        assert trace_id, 'Workflow callbacks did not report a trace ID'
        await asyncio.to_thread(runtime.client.flush)
        deadline = time.monotonic() + 60
        rows = []
        while time.monotonic() < deadline:
            page = await asyncio.to_thread(runtime.client.api.observations.get_many,
                trace_id=trace_id, fields='core,basic,io,metadata,usage', limit=1000)
            rows = page.data
            if {'ch09.execution', 'knowledge.retrieve', 'log_response'} <= {row.name for row in rows}:
                break
            await asyncio.sleep(2)
        assert {'ch09.execution', 'classify_intent', 'knowledge.retrieve', 'confidence_gate',
                'log_response'} <= {row.name for row in rows}
        [execution] = [row for row in rows if row.name == 'ch09.execution']
        diagnostic = [{ 'name': span.name,
            'dimensions': {key: value for key, value in span.attributes.items()
                if key.endswith('.intent') or key.endswith('.outcome') or key.endswith('.route')}}
            for span in probe.get_finished_spans() if span.name in ('ch09.execution', 'LangGraph', 'classify_intent')]
        if execution.metadata['intent'] != '商品咨询':
            print(json.dumps({'exported': diagnostic, 'read_back': {
                'intent': execution.metadata.get('intent'), 'outcome': execution.metadata.get('outcome')}}, ensure_ascii=False))
        assert execution.metadata['intent'] == '商品咨询', diagnostic
        assert execution.metadata['outcome'] == 'success'
        result = await IntentUsageReader(runtime.client).read(start, datetime.now(timezone.utc))
        assert result['complete'] is True
        [intent_row] = [row for row in result['rows'] if row['intent'] == '商品咨询']
        # Scripted model intentionally emits no real generation usage; no fabricated bill.
        assert intent_row['requests'] >= 1 and intent_row['model_calls'] == 0
        assert intent_row['actual_tokens'] is None
    finally:
        await runtime.close()
