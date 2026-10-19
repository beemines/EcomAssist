"""Explicit local-only transport probe: no LLM, tools, or business data."""
import asyncio
import json
import time
from pathlib import Path
from uuid import uuid4

import pytest
from dotenv import dotenv_values
import httpx


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


async def test_initialized_local_admin_can_sign_in(request):
    if not request.config.getoption('--run-langfuse'):
        pytest.skip('requires explicit --run-langfuse and local CH09 Compose')
    from app.observability.runtime import validate_local_langfuse_url
    root = Path(__file__).resolve().parents[2]
    local = dict(dotenv_values(root / 'runtime/langfuse/local.env'))
    origin = validate_local_langfuse_url(local.get('NEXTAUTH_URL'))
    async with httpx.AsyncClient(base_url=origin, timeout=10, follow_redirects=False) as client:
        # Discover the configured provider rather than guessing a callback URL.
        providers = (await client.get('/api/auth/providers')).json()
        provider = next((value for value in providers.values() if value.get('type') == 'credentials'), None)
        assert provider is not None, 'Local credentials login is not configured'
        callback = provider['callbackUrl']
        assert callback.startswith(origin + '/api/auth/'), 'Refusing nonlocal auth callback'
        csrf = (await client.get('/api/auth/csrf')).json()['csrfToken']
        response = await client.post(callback, data={
            'email': local['LANGFUSE_INIT_USER_EMAIL'],
            'password': local['LANGFUSE_INIT_USER_PASSWORD'],
            'csrfToken': csrf, 'callbackUrl': origin, 'json': 'true'})
        assert response.status_code in (200, 302), 'Local sign-in failed'
        session = (await client.get('/api/auth/session')).json()
        assert session.get('user', {}).get('email') == local['LANGFUSE_INIT_USER_EMAIL']
