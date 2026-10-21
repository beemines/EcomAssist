"""The side-channel client must never associate an invalid response with a row."""

import asyncio
import json

import httpx
import pytest
from pydantic import ValidationError

from app.topics.client import TopicClient, TopicClientError
from app.topics.types import ClassifyItem, ClassifyRequest, ModelIdentity


def identity():
    return ModelIdentity(model_version='fixture-v1', taxonomy_version='ch10-topics-v1',
        taxonomy_hash='a'*64, cleaning_version='ch10-clean-v1', max_tokens=128)


def reply(items, *, request_id='request-1'):
    return dict(request_id=request_id, identity=identity().model_dump(), items=[dict(
        id=item.id, labels=['物流'], probabilities=[0.7]*17, status='classified',
        model_version=identity().model_version, taxonomy_version=identity().taxonomy_version) for item in items])


async def test_local_round_trip_preserves_bigint_and_request_identity():
    items = [ClassifyItem(id='9007199254740993', text='包裹在哪里?')]
    def handler(request):
        if request.method == 'GET':
            return httpx.Response(200, json=identity().model_dump())
        assert json.loads(request.content)['items'][0]['id'] == '9007199254740993'
        assert '包裹'.encode() in request.content
        assert 'authorization' not in request.headers
        return httpx.Response(200, json=reply(items))
    async with TopicClient('http://127.0.0.1:8103', transport=httpx.MockTransport(handler)) as client:
        assert await client.health() == identity()
        rows = await client.classify(items, identity(), request_id='request-1')
    assert rows[0].id == '9007199254740993'


@pytest.mark.parametrize('change', ['order', 'missing', 'duplicate', 'foreign', 'request_id', 'model', 'taxonomy', 'cleaning'])
async def test_bad_response_identity_rejects_the_entire_batch(change):
    items = [ClassifyItem(id='1', text='包裹?'), ClassifyItem(id='2', text='物流?')]
    body = reply(items)
    if change == 'order':
        body['items'].reverse()
    elif change == 'missing':
        body['items'].pop()
    elif change == 'duplicate':
        body['items'][1]['id'] = '1'
    elif change == 'foreign':
        body['items'][0]['id'] = '3'
    elif change == 'request_id':
        body['request_id'] = 'wrong'
    elif change == 'model':
        body['items'][0]['model_version'] = 'stale-model'
    elif change == 'taxonomy':
        body['identity']['taxonomy_hash'] = 'b'*64
    else:
        body['identity']['cleaning_version'] = 'stale-cleaner'
    async with TopicClient('http://127.0.0.1:8103', transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json=body))) as client:
        with pytest.raises(TopicClientError) as error:
            await client.classify(items, identity(), request_id='request-1')
    assert not error.value.temporary


@pytest.mark.parametrize('bad', [True, float('nan'), float('inf'), -0.1, 1.1, '0.2'])
async def test_nonfinite_or_coerced_probabilities_rejected(bad):
    items = [ClassifyItem(id='1', text='物流?')]
    body = reply(items)
    body['items'][0]['probabilities'][0] = bad
    async with TopicClient('http://127.0.0.1:8103', transport=httpx.MockTransport(
            lambda request: httpx.Response(200, content=json.dumps(body).encode()))) as client:
        with pytest.raises(TopicClientError):
            await client.classify(items, identity(), request_id='request-1')


async def test_input_errors_and_uncertainty_stay_explicit():
    items = [ClassifyItem(id='1', text='物流?'), ClassifyItem(id='2', text='长句')]
    body = reply(items)
    body['items'][0].update(status='needs_review', labels=[])
    body['items'][1].update(status='input_too_long', labels=[], probabilities=None)
    async with TopicClient('http://127.0.0.1:8103', transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json=body))) as client:
        result = await client.classify(items, identity(), request_id='request-1')
    assert result[0].labels == () and result[0].status == 'needs_review'
    assert result[1].probabilities is None and result[1].status == 'input_too_long'


@pytest.mark.parametrize('items', [[], [dict(id=str(i), text='物流?') for i in range(65)],
    [dict(id='1', text=' ')] , [dict(id='1', text='a'*513)], [dict(id=1, text='物流?')],
    [dict(id='1', text='物流?'), dict(id='1', text='退款?')]])
def test_request_bounds_and_duplicate_ids_are_local_errors(items):
    with pytest.raises(ValidationError):
        ClassifyRequest(request_id='request-1', items=items)


@pytest.mark.parametrize('url', ['https://remote.invalid:8103', 'http://127.0.0.1:8103?target=remote',
    'http://user:secret@127.0.0.1:8103', 'http://127.0.0.1:8103/foreign',
    'file:///D:/private', 'http://127.0.0.1:8103#fragment'])
def test_client_cannot_send_pool_text_outside_literal_loopback(url):
    with pytest.raises(ValueError):
        TopicClient(url)


async def test_redirect_is_not_followed_and_network_failure_is_classified():
    count = 0
    def handler(request):
        nonlocal count
        count += 1
        return httpx.Response(307, headers={'location': 'https://remote.invalid/receive'})
    async with TopicClient('http://127.0.0.1:8103', transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(TopicClientError) as error:
            await client.classify([ClassifyItem(id='1', text='物流?')], identity(), request_id='request-1')
    assert count == 1 and not error.value.temporary


async def test_total_timeout_and_busy_do_not_trigger_hidden_retries():
    calls = 0
    async def blocked(request):
        nonlocal calls
        calls += 1
        await asyncio.Event().wait()
    async with TopicClient('http://127.0.0.1:8103', transport=httpx.MockTransport(blocked), timeout_seconds=0.03) as client:
        with pytest.raises(TopicClientError) as error:
            await client.health()
    assert calls == 1 and error.value.temporary
    async with TopicClient('http://127.0.0.1:8103', transport=httpx.MockTransport(
            lambda request: httpx.Response(503, json={'code': 'busy'}))) as client:
        with pytest.raises(TopicClientError) as error:
            await client.health()
    assert error.value.temporary
