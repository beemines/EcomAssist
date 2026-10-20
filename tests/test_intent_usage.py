from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest


def root(trace_id='t1', *, intent='物流', purpose='chat', closed=True, replay=False):
    return {'id': 'root-' + trace_id, 'trace_id': trace_id, 'type': 'SPAN',
            'end_time': '2026-10-19T00:00:01Z' if closed else None,
            'metadata': {'intent': intent, 'purpose': purpose, 'replay': replay,
                         'ch09_execution': True, 'outcome': 'success' if closed else None}}


def generation(identifier, usage=None, **extra):
    return {'id': identifier, 'trace_id': 't1', 'type': 'GENERATION',
            'usage_details': usage, 'metadata': {}, **extra}


def test_preclassification_generations_belong_to_final_intent():
    from app.observability.intent_usage import summarize_intent_usage
    early = generation('g1', {'input': 10, 'output': 2})
    later = generation('g2', {'input': 3, 'output': 1})
    parent = {'id': 'parent', 'trace_id': 't1', 'type': 'SPAN',
              'usage_details': {'total': 99999}}
    [row] = summarize_intent_usage([root()], [early, later, early, parent])
    assert row['intent'] == '物流'
    assert row['actual_tokens'] == 16
    assert row['input_tokens'] == 13
    assert row['output_tokens'] == 3
    assert row['model_calls'] == 2 and row['requests'] == 1
    assert row['currency_cost'] is None


def test_missing_usage_is_not_zero_and_estimates_are_separate():
    from app.observability.intent_usage import summarize_intent_usage
    rows = [generation('g1'), generation('g2', {'input': 4, 'output': 3},
        metadata={'usage_source': 'estimated'})]
    [row] = summarize_intent_usage([root()], rows)
    assert row['unknown_calls'] == 1 and row['estimated_calls'] == 1
    assert row['estimated_tokens'] == 7
    assert row['actual_tokens'] is None


def test_actual_scope_excludes_fixture_and_unmarked_roots_from_request_average():
    from app.observability.intent_usage import summarize_intent_usage
    roots=[root('actual'),root('fixture'),root('legacy')]
    roots[0]['metadata']['source_kind']='actual'
    roots[1]['metadata']['source_kind']='fixture'
    observations=[generation('a',{'input':10,'output':2},trace_id='actual'),
        generation('f',{'total':10000},trace_id='fixture'),generation('l',{'total':100},trace_id='legacy')]
    [row]=summarize_intent_usage(roots,observations,source_scope='actual')
    assert row['requests']==1 and row['actual_tokens']==12 and row['average_tokens']==12


def test_replay_and_in_progress_are_excluded_and_background_is_separate():
    from app.observability.intent_usage import summarize_intent_usage
    roots = [root(), root('t2', purpose='flywheel'), root('t3', closed=False), root('t4', replay=True)]
    generations = [generation('g1', {'input': 1, 'output': 1}),
        generation('g2', {'total': 5}, trace_id='t2'),
        generation('g3', {'total': 1000}, trace_id='t3'),
        generation('g4', {'total': 1000}, trace_id='t4')]
    rows = summarize_intent_usage(roots, generations)
    assert {(r['purpose'], r['actual_tokens']) for r in rows} == {('chat', 2), ('flywheel', 5)}


async def test_repeated_cursor_reports_incomplete_instead_of_looping():
    from app.observability.intent_usage import IntentUsageReader

    class RepeatingAPI:
        calls = 0

        def get_many(self, **kwargs):
            self.calls += 1
            return SimpleNamespace(data=[root()], meta=SimpleNamespace(cursor='same', has_more=True))

    api = RepeatingAPI()
    client = SimpleNamespace(api=SimpleNamespace(observations=api))
    now = datetime.now(timezone.utc)
    result = await IntentUsageReader(client).read(now - timedelta(days=1), now)
    assert result['complete'] is False
    assert result['reason'] == 'pagination_incomplete'
    assert api.calls <= 3
    assert result['rows'] == []


async def test_reader_deduplicates_and_caches_without_hiding_unavailability():
    from app.observability.intent_usage import IntentUsageReader

    class API:
        calls = 0

        def get_many(self, **kwargs):
            self.calls += 1
            data = [root()] if kwargs.get('name') == 'ch09.execution' else [generation('g1', {'total': 7})]
            return SimpleNamespace(data=data, meta=SimpleNamespace(cursor=None, has_more=False))

    api = API()
    reader = IntentUsageReader(SimpleNamespace(api=SimpleNamespace(observations=api)))
    now = datetime.now(timezone.utc)
    first = await reader.read(now - timedelta(days=1), now)
    second = await reader.read(now - timedelta(days=1), now)
    assert first['complete'] and second['rows'][0]['actual_tokens'] == 7
    assert api.calls == 2
    unavailable = await IntentUsageReader(None).read(now - timedelta(days=1), now)
    assert unavailable['complete'] is False and unavailable['rows'] == []


@pytest.mark.parametrize('days,aware', [(91, True), (1, False), (-1, True)])
async def test_time_range_is_bounded_and_timezone_required(days, aware):
    from app.observability.intent_usage import IntentUsageReader
    now = datetime.now(timezone.utc) if aware else datetime.now()
    with pytest.raises(ValueError):
        await IntentUsageReader(None).read(now - timedelta(days=days), now)


@pytest.mark.parametrize('value', [float('nan'), float('inf'), True, -1, '9'])
def test_invalid_usage_is_reported_unknown_instead_of_breaking_statistics(value):
    from app.observability.intent_usage import summarize_intent_usage
    [row] = summarize_intent_usage([root()], [generation('bad', {'total': value})])
    assert row['unknown_calls'] == 1 and row['actual_tokens'] is None


async def test_api_returns_explicit_unavailable_and_rejects_naive_range():
    import httpx
    from fastapi import FastAPI
    from app.api.observability import router
    app = FastAPI()
    app.include_router(router)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://127.0.0.1:8006') as client:
        response = await client.get('/api/observability/intent-usage')
        assert response.status_code == 200 and response.json()['complete'] is False
        assert response.json()['reason'] == 'langfuse_unavailable'
        response = await client.get('/api/observability/intent-usage', params={
            'from_time': '2026-10-18T00:00:00', 'to_time': '2026-10-19T00:00:00'})
        assert response.status_code == 422
