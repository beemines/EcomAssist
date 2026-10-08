import json

import httpx
import pytest
from pydantic import ValidationError

from app.config import Settings
from app.knowledge.types import ChunkDraft, embedding_text


def embedder(settings, client):
    try:
        from app.knowledge.embeddings import SiliconFlowEmbedder
    except ImportError:
        pytest.fail('cloud embedder is missing')
    return SiliconFlowEmbedder(settings, http_client=client)


def settings(**kwargs):
    values = dict(llm_base_url='https://example.test', llm_model='test', llm_api_key='placeholder', siliconflow_api_key='synthetic-key')
    values.update(kwargs)
    return Settings(_env_file=None, **values)


def payload(entries):
    return {'model': 'BAAI/bge-m3', 'data': entries, 'usage': {'prompt_tokens': 1, 'total_tokens': 1}}


async def test_posts_only_three_fields_and_restores_out_of_order_batch():
    draft = ChunkDraft('运费', '配送费用', '标准配送8元。', section_path='private/path', content_type='faq', is_key_clause=True)
    assert embedding_text(draft) == 'category: 运费\nquestions: 配送费用\nanswer: 标准配送8元。'
    def handle(request):
        assert str(request.url) == 'https://api.siliconflow.cn/v1/embeddings'
        assert json.loads(request.content) == {'model': 'BAAI/bge-m3', 'input': ['category: 运费\nquestions: 配送费用\nanswer: 标准配送8元。', 'second'], 'encoding_format': 'float'}
        assert request.headers['Authorization'] == 'Bearer synthetic-key'
        assert request.extensions['timeout']['read'] == 20
        return httpx.Response(200, json=payload([{'object': 'embedding', 'index': 1, 'embedding': [2.0] * 1024}, {'object': 'embedding', 'index': 0, 'embedding': [1.0] * 1024}]))
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        worker = embedder(settings(), client)
        assert await worker.embed([embedding_text(draft), 'second']) == [[1.0] * 1024, [2.0] * 1024]
        await worker.aclose()
        assert not client.is_closed


@pytest.mark.parametrize('entries', [
    [{'index': 0, 'embedding': [1.0] * 1024}, {'index': 0, 'embedding': [1.0] * 1024}],
    [{'embedding': [1.0] * 1024}, {'index': 1, 'embedding': [1.0] * 1024}],
    [{'index': 0, 'embedding': [1.0] * 1024}],
    [{'index': True, 'embedding': [1.0] * 1024}, {'index': 0, 'embedding': [1.0] * 1024}],
    [{'index': 0, 'embedding': [1.0] * 1023}, {'index': 1, 'embedding': [1.0] * 1024}],
    *[[{'index': 0, 'embedding': [bad] + [0.0] * 1023}, {'index': 1, 'embedding': [1.0] * 1024}] for bad in (True, '1', float('nan'), float('inf'), -float('inf'))],
], ids=['duplicate', 'missing-index', 'wrong-count', 'bool-index', 'dimension', 'bool', 'text', 'nan', 'inf', 'neg-inf'])
async def test_rejects_malformed_cloud_vectors(entries):
    # Bytes allow deliberately invalid NaN/Infinity wire values through the decoder.
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, content=json.dumps(payload(entries))))) as client:
        with pytest.raises(ValueError):
            await embedder(settings(), client).embed(['first', 'second'])


async def test_missing_key_fails_before_http_and_no_retry_on_service_error():
    def forbidden(request):
        pytest.fail('missing key must not reach HTTP')
    async with httpx.AsyncClient(transport=httpx.MockTransport(forbidden)) as client:
        with pytest.raises(ValueError, match='SILICONFLOW_API_KEY'):
            await embedder(settings(siliconflow_api_key=None), client).embed(['text'])


async def test_service_error_is_propagated_without_retry():
    requests = []
    def handle(request):
        requests.append(request)
        return httpx.Response(429)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        with pytest.raises(httpx.HTTPStatusError):
            await embedder(settings(), client).embed(['text'])
    assert len(requests) == 1


@pytest.mark.parametrize('kwargs', [{'embedding_model': 'other'}, {'embedding_timeout_seconds': 0}, {'milvus_timeout_seconds': float('inf')}])
def test_fixed_model_and_finite_timeouts_rejected(kwargs):
    with pytest.raises(ValidationError):
        settings(**kwargs)


def test_embedding_settings_accept_explicit_endpoint_and_timeouts():
    config = settings(embedding_model='BAAI/bge-m3', embedding_timeout_seconds=12, milvus_uri='http://127.0.0.1:19530', milvus_timeout_seconds=3)
    assert config.embedding_model == 'BAAI/bge-m3'
    assert config.embedding_timeout_seconds == 12
    assert config.milvus_timeout_seconds == 3
    assert str(config.milvus_uri).rstrip('/') == 'http://127.0.0.1:19530'


async def test_closes_owned_http_client():
    from app.knowledge.embeddings import SiliconFlowEmbedder
    worker = SiliconFlowEmbedder(settings())
    await worker.aclose()
    assert worker._client.is_closed
