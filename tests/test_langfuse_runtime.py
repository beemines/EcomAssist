import asyncio
import time

import pytest
from pydantic import ValidationError

from app.config import Settings


def settings(**overrides):
    return Settings(_env_file=None, LLM_BASE_URL='https://example.test/v1',
                    LLM_MODEL='demo', LLM_API_KEY='model-secret', **overrides)


@pytest.mark.parametrize('value', [
    'https://cloud.langfuse.com', '', 'http://127.0.0.1.evil.test:3000',
    'http://user:secret@127.0.0.1:3000', 'http://127.0.0.1:3000/path',
    'http://127.0.0.1:3000?secret=yes', 'http://localhost:3000/#fragment',
])
def test_rejects_cloud_destination(value):
    from app.observability.runtime import validate_local_langfuse_url
    with pytest.raises(ValueError) as error:
        validate_local_langfuse_url(value)
    assert 'secret' not in str(error.value)


@pytest.mark.parametrize('value', ['http://127.0.0.1:3000', 'http://localhost:3010'])
def test_accepts_explicit_local_destination(value):
    from app.observability.runtime import validate_local_langfuse_url
    assert validate_local_langfuse_url(value) == value


def test_enabled_tracking_requires_explicit_base_url_without_leaking_keys():
    with pytest.raises(ValidationError) as error:
        settings(LANGFUSE_ENABLED=True, LANGFUSE_PUBLIC_KEY='pk-secret',
                 LANGFUSE_SECRET_KEY='sk-secret')
    assert 'sk-secret' not in str(error.value)
    assert 'pk-secret' not in str(error.value)
    assert 'LANGFUSE_BASE_URL' in str(error.value)
    assert 'extra_forbidden' not in str(error.value)


def test_disabled_tracking_has_no_client_or_handler():
    from app.observability.runtime import LangfuseRuntime
    runtime = LangfuseRuntime.from_settings(settings())
    assert runtime.handler is None
    assert runtime.client is None


async def test_close_failure_is_safe_idempotent_and_does_not_log_secret(caplog):
    from app.observability.runtime import LangfuseRuntime

    class BrokenExporter:
        calls = 0

        def flush(self):
            self.calls += 1
            raise RuntimeError('sk-secret in provider error')

        def shutdown(self):
            self.calls += 1

    client = BrokenExporter()
    runtime = LangfuseRuntime(client=client)
    await runtime.close()
    await runtime.close()
    assert client.calls == 2
    assert 'sk-secret' not in caplog.text


async def test_close_has_bounded_latency_even_when_exporter_blocks():
    from app.observability.runtime import LangfuseRuntime

    class SlowExporter:
        def flush(self):
            time.sleep(0.15)

        def shutdown(self):
            pass

    runtime = LangfuseRuntime(client=SlowExporter())
    started = time.monotonic()
    await asyncio.wait_for(runtime.close(timeout_seconds=0.01), timeout=0.08)
    assert time.monotonic() - started < 0.08


def test_sdk_construction_error_fails_open_without_logging_secret(caplog):
    from app.observability.runtime import LangfuseRuntime

    def broken_factory(**kwargs):
        raise RuntimeError('sk-secret connection failed')

    runtime = LangfuseRuntime.from_settings(settings(
        LANGFUSE_ENABLED=True, LANGFUSE_BASE_URL='http://127.0.0.1:3000',
        LANGFUSE_PUBLIC_KEY='pk-secret', LANGFUSE_SECRET_KEY='sk-secret'),
        client_factory=broken_factory)
    assert runtime.handler is None
    assert 'sk-secret' not in caplog.text
