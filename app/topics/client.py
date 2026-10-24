"""A bounded local inference client; no model runtime or teacher is imported."""

import asyncio
import json
import math
from urllib.parse import urlsplit

import httpx

from app.topics.types import ClassifyRequest, ClassifyResponse, ModelIdentity


class TopicClientError(RuntimeError):
    def __init__(self, code: str, *, temporary: bool = False):
        self.code, self.temporary = code, temporary
        super().__init__(code)


def _local_url(url):
    if type(url) is not str:
        raise ValueError('Topic service URL must be text')
    parsed = urlsplit(url)
    if (parsed.scheme != 'http' or parsed.hostname not in ('127.0.0.1', '::1', 'localhost')
            or parsed.username is not None or parsed.password is not None or parsed.path not in ('', '/')
            or parsed.query or parsed.fragment or parsed.port is None or not 0 < parsed.port <= 65535):
        raise ValueError('Topic service requires an explicit loopback HTTP URL and port')
    host = '[::1]' if parsed.hostname == '::1' else '127.0.0.1'
    return f'http://{host}:{parsed.port}'


def _json_unique(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate response JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs)


class TopicClient:
    def __init__(self, service_url: str, *, transport=None, timeout_seconds=60):
        self.service_url = _local_url(service_url)
        if (type(timeout_seconds) not in (int, float) or not math.isfinite(timeout_seconds)
                or not 0 < timeout_seconds <= 300):
            raise ValueError('Invalid local inference total timeout')
        self.timeout_seconds = timeout_seconds
        self._http = httpx.AsyncClient(transport=transport or httpx.AsyncHTTPTransport(retries=0),
            trust_env=False, follow_redirects=False, timeout=httpx.Timeout(timeout_seconds, connect=min(5, timeout_seconds)))

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.aclose()

    async def aclose(self):
        await self._http.aclose()

    async def _request(self, method, path, payload=None):
        content = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8') if payload is not None else None
        try:
            async with asyncio.timeout(self.timeout_seconds):
                async with self._http.stream(method, self.service_url + path, content=content,
                        headers={'Content-Type': 'application/json'} if payload is not None else {}) as response:
                    if response.status_code != 200:
                        raise TopicClientError('topic_http_failure', temporary=response.status_code in (429, 500, 502, 503, 504))
                    body = bytearray()
                    async for chunk in response.aiter_bytes():
                        body.extend(chunk)
                        if len(body) > 512 * 1024:
                            raise TopicClientError('topic_response_too_large')
            return _json_unique(bytes(body))
        except (TimeoutError, httpx.TransportError):
            raise TopicClientError('topic_network_failure', temporary=True) from None
        except (ValueError, UnicodeDecodeError):
            raise TopicClientError('topic_response_invalid') from None

    async def health(self) -> ModelIdentity:
        body = await self._request('GET', '/health')
        try:
            return ModelIdentity.model_validate(body)
        except ValueError:
            raise TopicClientError('topic_identity_invalid') from None

    async def classify(self, items, expected: ModelIdentity, *, request_id: str):
        request = ClassifyRequest(request_id=request_id, items=items)
        expected = ModelIdentity.model_validate(expected.model_dump())
        body = await self._request('POST', '/classify', request.model_dump(mode='json'))
        try:
            result = ClassifyResponse.model_validate(body)
        except ValueError:
            raise TopicClientError('topic_prediction_invalid') from None
        if (result.identity != expected or result.request_id != request.request_id
                or tuple(item.id for item in result.items) != tuple(item.id for item in request.items)):
            raise TopicClientError('topic_response_identity_mismatch')
        return result.items
