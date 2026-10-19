"""Own one optional, local-only SDK client; no per-request flush."""
from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

if TYPE_CHECKING:
    from app.config import Settings

logger = logging.getLogger(__name__)


def validate_local_langfuse_url(value: str | None) -> str:
    error = 'LANGFUSE_BASE_URL must be an explicit loopback HTTP(S) origin with port'
    if not isinstance(value, str) or not value:
        raise ValueError(error)
    try:
        parsed = urlsplit(value)
        valid = (parsed.scheme in ('http', 'https')
                 and parsed.hostname in ('127.0.0.1', 'localhost', '::1')
                 and parsed.port is not None and 1 <= parsed.port <= 65535
                 and parsed.username is None and parsed.password is None
                 and not parsed.path and not parsed.query and not parsed.fragment
                 and value == f'{parsed.scheme}://{parsed.netloc}')
    except ValueError:
        valid = False
    if not valid:
        raise ValueError(error)
    return value


class LangfuseRuntime:
    def __init__(self, *, client=None, handler=None):
        self.client, self.handler = client, handler
        self._closed = False

    @classmethod
    def from_settings(cls, settings: Settings, *, client_factory=None, handler_factory=None):
        if not settings.langfuse_enabled:
            return cls()
        base_url = validate_local_langfuse_url(settings.langfuse_base_url)
        public_key = settings.langfuse_public_key.get_secret_value()
        client = None
        try:
            if client_factory is None:
                from langfuse import Langfuse
                from opentelemetry.sdk.trace import TracerProvider
                client_factory = Langfuse
                # Explicit provider prevents unrelated global exporters joining local traces.
                extra = {'tracer_provider': TracerProvider()}
            else:
                extra = {}
            client = client_factory(public_key=public_key,
                secret_key=settings.langfuse_secret_key.get_secret_value(),
                base_url=base_url, timeout=2, debug=False, flush_at=32,
                flush_interval=1, environment='ch09-local', **extra)
            if handler_factory is None:
                from langfuse.langchain import CallbackHandler
                handler_factory = CallbackHandler
            return cls(client=client, handler=handler_factory(public_key=public_key))
        except Exception as exc:
            # Provider exceptions can contain credentials; log only a fixed stage and type.
            logger.warning('langfuse init degraded error_type=%s', type(exc).__name__)
            return cls(client=client)

    async def close(self, timeout_seconds=5):
        if self._closed:
            return
        self._closed = True
        if self.client is None:
            return

        def finish():
            try:
                self.client.flush()
            except Exception as exc:
                logger.warning('langfuse flush degraded error_type=%s', type(exc).__name__)
            finally:
                try:
                    self.client.shutdown()
                except Exception as exc:
                    logger.warning('langfuse shutdown degraded error_type=%s', type(exc).__name__)

        try:
            await asyncio.wait_for(asyncio.to_thread(finish), timeout=timeout_seconds)
        except TimeoutError:
            logger.warning('langfuse close deadline reached')
