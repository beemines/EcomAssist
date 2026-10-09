# 云端重排的真实 HTTP 边界测试，权威正文保留在调用方输入中。
import asyncio
import importlib
import json

import httpx
import pytest

from tests.fakes import fake_settings


def reranker(client=None, **overrides):
    try:
        adapter = importlib.import_module('app.retrieval.rerank').SiliconFlowReranker
    except ImportError:
        pytest.fail('cloud reranker is missing')
    config = {'siliconflow_api_key': 'synthetic-key', **overrides}
    return adapter(fake_settings(**config), http_client=client)


def payload(results):
    return {'id': 'synthetic-rerank', 'results': results,
            'meta': {'tokens': {'input_tokens': 3, 'output_tokens': 0}, 'billed_units': {'search_units': 1}}}


async def test_fixed_model_request_and_sorted_stable_index_results():
    def handle(request):
        assert str(request.url) == 'https://api.siliconflow.cn/v1/rerank'
        assert json.loads(request.content) == {'model': 'BAAI/bge-reranker-v2-m3', 'query': '退货',
            'documents': ['权威甲', '权威乙', '权威丙'], 'top_n': 10, 'return_documents': False}
        assert request.extensions['timeout']['read'] == 20
        return httpx.Response(200, json=payload([
            {'index': 2, 'relevance_score': .8, 'document': {'text': '不可信替换'}},
            {'index': 0, 'relevance_score': .9}, {'index': 1, 'relevance_score': .8}]))
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        worker = reranker(client)
        hits = await worker.rank('退货', ['权威甲', '权威乙', '权威丙'])
        assert [(hit.index, hit.score) for hit in hits] == [(0, .9), (2, .8), (1, .8)]
        await worker.aclose()
        assert not client.is_closed


@pytest.mark.parametrize('results', [
    [{'index': 0, 'relevance_score': .5}, {'index': 0, 'relevance_score': .6}],
    [{'index': 2, 'relevance_score': .5}], [{'index': -1, 'relevance_score': .5}],
    [{'index': True, 'relevance_score': .5}], [{'index': '0', 'relevance_score': .5}],
    *[[{'index': 0, 'relevance_score': score}] for score in (True, '0.5', float('nan'), float('inf'))],
    [{}], None, ['invalid'],
])
async def test_rejects_invalid_index_or_score_before_returning_any_hits(results):
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request:
            httpx.Response(200, content=json.dumps(payload(results))))) as client:
        with pytest.raises(ValueError):
            await reranker(client).rank('退货', ['甲', '乙'])


async def test_limits_valid_results_to_requested_top_n():
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request:
            httpx.Response(200, json=payload([{'index': 0, 'relevance_score': .1}, {'index': 1, 'relevance_score': .9}])))) as client:
        assert [(h.index, h.score) for h in await reranker(client).rank('问', ['甲', '乙'], top_n=1)] == [(1, .9)]


async def test_http_failure_propagates_without_retry():
    requests = []
    def handle(request):
        requests.append(request)
        return httpx.Response(429)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        with pytest.raises(httpx.HTTPStatusError):
            await reranker(client).rank('问', ['甲'])
    assert len(requests) == 1


async def test_cancel_propagates_and_transport_is_cancelled():
    started, cancelled = asyncio.Event(), asyncio.Event()
    async def handle(request):
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        task = asyncio.create_task(reranker(client).rank('问', ['甲']))
        await started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert cancelled.is_set()


async def test_closes_owned_client():
    worker = reranker()
    await worker.aclose()
    assert worker._client.is_closed


async def test_outer_deadline_cancels_slow_transport_once():
    requests, cancelled = [], asyncio.Event()
    async def handle(request):
        requests.append(request)
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        with pytest.raises(TimeoutError):
            await reranker(client, rerank_timeout_seconds=.01).rank('问', ['甲'])
        assert cancelled.is_set() and len(requests) == 1


@pytest.mark.parametrize('query,docs,top_n', [(' ', ['甲'], 1), ('问', [''], 1),
                                          ('问', ['甲'], True), ('问', ['甲'], 0)])
async def test_invalid_inputs_do_not_reach_http(query, docs, top_n):
    def forbidden(request):
        pytest.fail('invalid input must fail before HTTP')
    async with httpx.AsyncClient(transport=httpx.MockTransport(forbidden)) as client:
        with pytest.raises(ValueError):
            await reranker(client).rank(query, docs, top_n=top_n)


async def test_missing_key_and_empty_batch_do_not_reach_http():
    def forbidden(request):
        pytest.fail('empty or missing-key request must not reach HTTP')
    async with httpx.AsyncClient(transport=httpx.MockTransport(forbidden)) as client:
        worker = reranker(client, siliconflow_api_key=None)
        assert await worker.rank('问', []) == []
        with pytest.raises(ValueError, match='SILICONFLOW_API_KEY'):
            await worker.rank('问', ['甲'])
