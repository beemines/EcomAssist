"""Join generation usage to final execution intent; never add parent totals."""
from __future__ import annotations

import asyncio
import copy
import math
import time
from collections.abc import Sequence
from datetime import datetime, timedelta,timezone


def _tokens(usage):
    if not isinstance(usage, dict):
        return None
    for value in usage.values():
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or value < 0 or int(value) != value):
            return None
    total = usage.get('total')
    if total is None:
        if usage.get('input') is None or usage.get('output') is None:
            return None
        total = usage['input'] + usage['output']
    return int(total), usage.get('input'), usage.get('output')


def summarize_intent_usage(roots: Sequence[dict], observations: Sequence[dict], *, estimate_prices=True,source_scope='all') -> list[dict]:
    if source_scope not in ('all','actual'): raise ValueError('Unknown source scope')
    by_trace, groups = {}, {}
    coverage={}
    for root in roots:
        meta = root.get('metadata') or {}
        trace_id = root.get('trace_id')
        if (not trace_id or not meta.get('ch09_execution') or not root.get('end_time')
                or not meta.get('outcome') or meta.get('replay')):
            continue
        if trace_id in by_trace:
            continue
        if source_scope=='actual' and meta.get('source_kind')!='actual': continue
        key = ('fixture' if meta.get('source_kind')=='fixture' else meta.get('purpose', 'chat'), meta.get('intent') or '未识别')
        by_trace[trace_id] = key
        coverage[trace_id]={'calls':0,'actual':0}
        row = groups.setdefault(key, {'purpose': key[0], 'intent': key[1], 'requests': 0,
            'model_calls': 0, 'actual_calls': 0, 'estimated_calls': 0, 'unknown_calls': 0,
            'input_tokens': None, 'output_tokens': None, 'actual_tokens': None,
            'estimated_tokens': None, 'currency_cost': None,'cost_currency':'USD',
            'estimated_cost_cny':None,'priced_calls':0,'unpriced_calls':0,'unknown_cost_calls':0})
        row['requests'] += 1
    seen = set()
    for observation in observations:
        identifier, trace_id = observation.get('id'), observation.get('trace_id')
        if (observation.get('type') != 'GENERATION' or not identifier or identifier in seen
                or trace_id not in by_trace):
            continue
        seen.add(identifier)
        row = groups[by_trace[trace_id]]
        covered=coverage[trace_id]
        covered['calls']+=1
        row['model_calls'] += 1
        details=observation.get('cost_details') or {}
        cost=details.get('total',observation.get('total_cost'))
        if type(cost) in (int,float) and math.isfinite(cost) and cost>=0:
            row['currency_cost']=(row['currency_cost'] or 0)+cost
        else: row['unknown_cost_calls']+=1
        from app.observability.pricing import estimate_cost
        price=estimate_cost(observation.get('model'),observation.get('usage_details')) if estimate_prices else None
        if price and (observation.get('metadata') or {}).get('usage_source')!='estimated':
            row['estimated_cost_cny']=(row['estimated_cost_cny'] or 0)+price['cost_cny']
            row['priced_calls']+=1
        else: row['unpriced_calls']+=1
        tokens = _tokens(observation.get('usage_details'))
        if tokens is None:
            row['unknown_calls'] += 1
            continue
        total, input_tokens, output_tokens = tokens
        meta = observation.get('metadata') or {}
        if meta.get('usage_source') == 'estimated':
            row['estimated_calls'] += 1
            row['estimated_tokens'] = (row['estimated_tokens'] or 0) + total
        else:
            covered['actual']+=1
            row['actual_calls'] += 1
            row['actual_tokens'] = (row['actual_tokens'] or 0) + total
            for field, value in (('input_tokens', input_tokens), ('output_tokens', output_tokens)):
                if value is not None:
                    row[field] = (row[field] or 0) + int(value)
    result=[groups[key] for key in sorted(groups)]
    totals={purpose:sum(row['actual_tokens'] or 0 for row in result if row['purpose']==purpose)
        for purpose,_ in groups}
    for row in result:
        key=(row['purpose'],row['intent'])
        row['complete_requests']=sum(by_trace[trace_id]==key and value['calls']>0 and value['calls']==value['actual']
            for trace_id,value in coverage.items())
    complete={purpose:all(row['complete_requests']==row['requests'] for row in result if row['purpose']==purpose)
        for purpose,_ in groups}
    for row in result:
        row['average_tokens']=row['actual_tokens']/row['requests'] if row['actual_tokens'] is not None and row['complete_requests']==row['requests'] else None
        denominator=totals[row['purpose']]
        row['token_share']=row['actual_tokens']/denominator if row['actual_tokens'] is not None and denominator and complete[row['purpose']] else None
    return result


def _dict(value):
    if isinstance(value, dict):
        return value
    return value.model_dump(mode='python')


class _IncompletePagination(Exception):
    pass


class IntentUsageReader:
    def __init__(self, client, *, clock=time.monotonic, max_pages=100,estimate_prices=False):
        self.client = client
        self.estimate_prices=estimate_prices
        self.clock, self.max_pages = clock, max_pages
        self._cache = {}
        self._lock = asyncio.Lock()

    async def read(self, from_time, to_time, *, force_refresh=False,source_scope='all'):
        if source_scope not in ('all','actual'): raise ValueError('Unknown source scope')
        if (not isinstance(from_time, datetime) or not isinstance(to_time, datetime)
                or from_time.utcoffset() is None or to_time.utcoffset() is None
                or not timedelta(0) < to_time - from_time <= timedelta(days=90)):
            raise ValueError('An aware positive time range of at most 90 days is required')
        if self.client is None:
            return {'complete': False, 'reason': 'langfuse_unavailable', 'rows': []}
        key = (from_time.isoformat(), to_time.isoformat(),source_scope)
        async with self._lock:
            cached = self._cache.get(key)
            if cached and not force_refresh and self.clock() - cached[0] < 60:
                return copy.deepcopy(cached[1])
            try:
                roots = await self._pages(from_time, to_time, name='ch09.execution', type='SPAN')
                generations = await self._pages(from_time, to_time, type='GENERATION')
                result = {'complete': True, 'reason': None,
                    'from_time': key[0], 'to_time': key[1],'source_scope':source_scope,
                    'in_progress': sum(1 for root in roots if not root.get('end_time')),
                    'computed_at':datetime.now(timezone.utc).isoformat(),
                    'rows': summarize_intent_usage(roots, generations,estimate_prices=self.estimate_prices,source_scope=source_scope)}
                from app.observability.pricing import PRICE_VERSION,PRICE_SOURCE
                result['pricing']={'kind':'tariff_estimate','currency':'CNY','version':PRICE_VERSION,
                    'source':PRICE_SOURCE,'enabled':self.estimate_prices}
            except _IncompletePagination:
                return {'complete': False, 'reason': 'pagination_incomplete', 'rows': []}
            except Exception:
                return {'complete': False, 'reason': 'langfuse_unavailable', 'rows': []}
            self._cache = {k: v for k, v in self._cache.items() if self.clock() - v[0] < 60}
            if len(self._cache) >= 32:
                self._cache.pop(next(iter(self._cache)))
            self._cache[key] = (self.clock(), copy.deepcopy(result))
            return result

    async def _pages(self, start, end, **filters):
        cursor, seen, records = None, set(), {}
        for _ in range(self.max_pages):
            page = await asyncio.to_thread(self.client.api.observations.get_many,
                fields='core,basic,metadata,usage,model',
                expand_metadata='intent,purpose,replay,outcome,ch09_execution,source_kind',
                from_start_time=start, to_start_time=end, limit=1000, cursor=cursor,
                request_options={'timeout_in_seconds': 5, 'max_retries': 0}, **filters)
            for raw in page.data:
                record = _dict(raw)
                if record.get('id'):
                    records[record['id']] = record
            meta = page.meta
            cursor = meta.get('cursor') if isinstance(meta, dict) else meta.cursor
            if not cursor:
                return list(records.values())
            if cursor in seen:
                raise _IncompletePagination
            seen.add(cursor)
        raise _IncompletePagination
