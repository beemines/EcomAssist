"""Explicit local-only transport probe: no LLM, tools, or business data."""
import asyncio
import json
import time
from pathlib import Path
from uuid import uuid4

import pytest
from dotenv import dotenv_values


async def test_local_span_is_exported_and_read_back(request):
    if not request.config.getoption('--run-langfuse'):
        pytest.skip('requires explicit --run-langfuse and local CH09 Compose')
    from app.config import Settings
    from app.observability.runtime import LangfuseRuntime

    root = Path(__file__).resolve().parents[2]
    sdk_file = root / 'runtime/langfuse/sdk.env'
    if not sdk_file.exists():
        pytest.fail('Run local_stack prepare/up first', pytrace=False)
    sdk = dict(dotenv_values(sdk_file))
    settings = Settings(_env_file=None, LLM_BASE_URL='https://unused.test/v1',
                        LLM_MODEL='unused', LLM_API_KEY='unused', **sdk)
    runtime = LangfuseRuntime.from_settings(settings)
    assert runtime.client is not None and runtime.handler is not None
    marker = 'ch09-transport-' + uuid4().hex
    try:
        with runtime.client.start_as_current_observation(
            name=marker, input={'message': '本地非模型连通性验证'},
            metadata={'purpose': 'transport_test'},
        ) as span:
            trace_id = span.trace_id
            span.update(output={'ok': True})
        await asyncio.to_thread(runtime.client.flush)
        deadline = time.monotonic() + 60
        found = None
        while time.monotonic() < deadline:
            page = await asyncio.to_thread(runtime.client.api.observations.get_many,
                trace_id=trace_id, fields='core,basic,io,metadata', limit=20)
            found = next((row for row in page.data if row.name == marker), None)
            if found:
                break
            await asyncio.sleep(2)
        assert found is not None, 'Local span was not readable before deadline'
        raw_input = json.loads(found.input) if isinstance(found.input, str) else found.input
        raw_output = json.loads(found.output) if isinstance(found.output, str) else found.output
        assert raw_input == {'message': '本地非模型连通性验证'}
        assert raw_output == {'ok': True}
        assert found.type == 'SPAN'
    finally:
        await runtime.close()
