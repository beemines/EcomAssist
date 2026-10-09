# 原生 TEXT/chinese/BM25 与固定 BGE-M3 向量索引；正文权威源仍是 MySQL。
import asyncio
import json
import math
from collections.abc import Sequence
from functools import wraps
from typing import Literal

from pymilvus import AnnSearchRequest, AsyncMilvusClient, DataType, Function, FunctionType, RRFRanker

from app.knowledge.embeddings import validate_vector
from app.knowledge.types import VectorHit, validate_id
from app.knowledge.vectors import validate_acknowledged_ids
from app.retrieval.types import IndexedChunk, validate_category


# 为整个逻辑操作设置一次期限，嵌套调用不能延长外层预算，取消直接传播。
def _bounded(operation):
    # 保留公开方法签名与说明，并用取消感知期限限制包括初始化在内的全部 RPC。
    @wraps(operation)
    async def bounded(self, *args, **kwargs):
        async with asyncio.timeout(self.timeout):
            return await operation(self, *args, **kwargs)
    return bounded


class HybridMilvusIndex:
    # 校验超时并记录客户端所有权，内部客户端延迟连接且不设置会触发 SDK 重试的数值期限。
    def __init__(self, uri: str, *, collection: str = 'knowledge_hybrid', client=None, timeout: float = 5):
        if isinstance(timeout, bool) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError('Milvus timeout must be positive and finite')
        self.collection = collection
        self.timeout = timeout
        self._owns_client = client is None
        self._client = client if client is not None else AsyncMilvusClient(uri=uri, timeout=None)
        self._ready = False

    # 禁用 SDK RPC 与限流重试；upsert 固有的最多一次同主键 Schema 刷新重放为已批准例外。
    async def _call(self, method: str, *args, **kwargs):
        return await getattr(self._client, method)(
            *args, timeout=None, retry_times=0, retry_on_rate_limit=False, **kwargs,
        )

    # 离线可创建集合；在线只核验既有结构，缺集合时在任何 DDL 前拒绝。
    @_bounded
    async def ensure_collection(self, *, create_if_missing: bool = True) -> None:
        self._ready = False
        if not await self._call('has_collection', self.collection):
            if not create_if_missing:
                raise ValueError('hybrid knowledge collection is missing; explicit initialization required')
            schema = AsyncMilvusClient.create_schema(auto_id=False, enable_dynamic_field=False)
            schema.add_field('id', DataType.INT64, is_primary=True, auto_id=False)
            schema.add_field('embedding', DataType.FLOAT_VECTOR, dim=1024)
            schema.add_field('text', DataType.TEXT, enable_analyzer=True, analyzer_params={'type': 'chinese'})
            # VARCHAR 使用字节上限，1020 字节能容纳业务允许的 255 个 Unicode 字符。
            schema.add_field('category', DataType.VARCHAR, max_length=1020)
            schema.add_field('sparse', DataType.SPARSE_FLOAT_VECTOR)
            schema.add_function(Function(name='text_bm25', function_type=FunctionType.BM25,
                                         input_field_names=['text'], output_field_names=['sparse']))
            # 分开调用防止 SDK 创建集合的嵌套索引与加载丢失零重试参数。
            await self._call('create_collection', self.collection, schema=schema, consistency_level='Strong')
            indexes = AsyncMilvusClient.prepare_index_params()
            indexes.add_index('embedding', index_name='embedding', index_type='FLAT', metric_type='COSINE', params={})
            indexes.add_index('sparse', index_name='sparse', index_type='SPARSE_INVERTED_INDEX', metric_type='BM25',
                              params={'inverted_index_algo': 'DAAT_MAXSCORE', 'bm25_k1': 1.2, 'bm25_b': 0.75})
            await self._call('create_index', self.collection, index_params=indexes)
        description = await self._call('describe_collection', self.collection)
        self._verify_schema(description)
        names = await self._call('list_indexes', self.collection)
        if not isinstance(names, list) or len(names) != 2:
            raise ValueError('hybrid knowledge requires exactly two vector indexes')
        indexes = [await self._call('describe_index', self.collection, name) for name in names]
        self._verify_indexes(indexes)
        await self._call('load_collection', self.collection)
        self._ready = True

    # 校验真实 SDK 集合描述的五字段、中文 analyzer、BM25 函数与 Strong 一致性。
    @staticmethod
    def _verify_schema(description: dict) -> None:
        if not isinstance(description, dict):
            raise ValueError('invalid hybrid collection description')
        fields = description.get('fields', [])
        by_name = {field.get('name'): field for field in fields}
        primary, dense = by_name.get('id', {}), by_name.get('embedding', {})
        text, category, sparse = by_name.get('text', {}), by_name.get('category', {}), by_name.get('sparse', {})
        text_params = text.get('params', {})
        analyzer = text_params.get('analyzer_params')
        if isinstance(analyzer, str):
            try:
                analyzer = json.loads(analyzer)
            except (TypeError, ValueError):
                analyzer = None
        functions = description.get('functions', [])
        valid_function = (len(functions) == 1 and functions[0].get('type') == FunctionType.BM25
                          and list(functions[0].get('input_field_names', [])) == ['text']
                          and list(functions[0].get('output_field_names', [])) == ['sparse']
                          and functions[0].get('params', {}) == {})
        if (len(fields) != 5 or set(by_name) != {'id', 'embedding', 'text', 'category', 'sparse'}
                or description.get('auto_id') is not False or description.get('enable_dynamic_field') is not False
                or description.get('consistency_level') != 0
                or primary.get('type') != DataType.INT64 or primary.get('is_primary') is not True
                or primary.get('auto_id', False) is not False
                or dense.get('type') != DataType.FLOAT_VECTOR or str(dense.get('params', {}).get('dim')) != '1024'
                or text.get('type') != DataType.TEXT or text_params.get('enable_analyzer') not in (True, 'true')
                or analyzer != {'type': 'chinese'}
                or category.get('type') != DataType.VARCHAR or str(category.get('params', {}).get('max_length')) != '1020'
                or sparse.get('type') != DataType.SPARSE_FLOAT_VECTOR or not valid_function
                or any(field.get('nullable', False) for field in fields)):
            raise ValueError('existing Milvus collection schema differs from hybrid knowledge schema')

    # 按字段匹配真实索引描述，并要求稠密余弦精确索引与固定 BM25 参数。
    @staticmethod
    def _verify_indexes(indexes: list[dict]) -> None:
        by_field = {index.get('field_name'): index for index in indexes if isinstance(index, dict)}
        dense, sparse = by_field.get('embedding', {}), by_field.get('sparse', {})
        if (set(by_field) != {'embedding', 'sparse'}
                or dense.get('index_type') != 'FLAT' or dense.get('metric_type') != 'COSINE'
                or sparse.get('index_type') != 'SPARSE_INVERTED_INDEX' or sparse.get('metric_type') != 'BM25'
                or sparse.get('inverted_index_algo') != 'DAAT_MAXSCORE'
                or str(sparse.get('bm25_k1')) != '1.2' or str(sparse.get('bm25_b')) != '0.75'):
            raise ValueError('existing Milvus indexes differ from hybrid knowledge indexes')

    # 校验全部字段与重复主键后幂等覆盖，计数和确认主键完全匹配才返回成功。
    @_bounded
    async def upsert(self, rows: list[IndexedChunk]) -> list[int]:
        rows = self._validate_rows(rows)
        if not rows:
            return []
        if not self._ready:
            await self.ensure_collection()
        identifiers = [row.id for row in rows]
        data = [{'id': row.id, 'embedding': row.embedding, 'text': row.text, 'category': row.category} for row in rows]
        result = await self._call('upsert', self.collection, data=data)
        if not isinstance(result, dict) or type(result.get('upsert_count')) is not int or result['upsert_count'] != len(rows):
            raise ValueError('hybrid upsert count differs from requested rows')
        actual = result.get('ids')
        if not isinstance(actual, Sequence) or isinstance(actual, (str, bytes)):
            raise ValueError('hybrid upsert did not return primary keys')
        actual = list(actual)
        validate_acknowledged_ids(actual, identifiers)
        return actual

    # 重建数据契约以防可变向量在创建行后发生非法变化，并拒绝重复主键。
    @staticmethod
    def _validate_rows(rows: list[IndexedChunk]) -> list[IndexedChunk]:
        if not isinstance(rows, list) or any(not isinstance(row, IndexedChunk) for row in rows):
            raise ValueError('hybrid rows must be IndexedChunk instances')
        result = [IndexedChunk(row.id, row.embedding, row.text, row.category) for row in rows]
        if len({row.id for row in result}) != len(result):
            raise ValueError('duplicate hybrid primary keys')
        return result

    # 用 Strong 一致性读回源字段，按请求顺序返回实际存在的行并拒绝异常或重复主键。
    @_bounded
    async def get_rows(self, ids: list[int]) -> list[IndexedChunk]:
        if not isinstance(ids, list):
            raise ValueError('hybrid ids must be a list')
        for identifier in ids:
            validate_id(identifier)
        if len(set(ids)) != len(ids):
            raise ValueError('duplicate hybrid primary keys')
        if not ids:
            return []
        if not self._ready:
            await self.ensure_collection()
        result = await self._call('get', self.collection, ids=ids, output_fields=['id', 'embedding', 'text', 'category'],
                                  consistency_level='Strong')
        if not isinstance(result, list):
            raise ValueError('invalid hybrid row response')
        by_id = {}
        for item in result:
            if not isinstance(item, dict):
                raise ValueError('invalid hybrid row response')
            row = IndexedChunk(item.get('id'), item.get('embedding'), item.get('text'), item.get('category'))
            if row.id not in ids or row.id in by_id:
                raise ValueError('hybrid row response has unexpected or duplicate id')
            by_id[row.id] = row
        return [by_id[identifier] for identifier in ids if identifier in by_id]

    # 正文和分类精确一致，向量使用 float32 明确误差容差，缺行或漂移均拒绝确认。
    @_bounded
    async def verify_rows(self, rows: list[IndexedChunk]) -> None:
        rows = self._validate_rows(rows)
        actual = await self.get_rows([row.id for row in rows])
        if len(actual) != len(rows):
            raise ValueError('hybrid verification has missing rows')
        for expected, observed in zip(rows, actual):
            if (expected.text != observed.text or expected.category != observed.category
                    or any(not math.isclose(want, got, rel_tol=1e-6, abs_tol=1e-7)
                           for want, got in zip(expected.embedding, observed.embedding))):
                raise ValueError('hybrid verification differs from requested fields')

    # 显式按 id 升序进行 keyset 分页，避免默认无序或 offset 窗口上限导致漏行。
    @_bounded
    async def all_ids(self) -> set[int]:
        if not self._ready:
            await self.ensure_collection()
        result, last_id = set(), 0
        while True:
            page = await self._call('query', self.collection, filter='id > {last_id}', filter_params={'last_id': last_id},
                                    output_fields=['id'], order_by=['id:asc'], limit=1000, consistency_level='Strong')
            if not isinstance(page, list) or len(page) > 1000:
                raise ValueError('invalid hybrid primary key page')
            if not page:
                return result
            for row in page:
                identifier = row.get('id') if isinstance(row, dict) else None
                validate_id(identifier)
                if identifier <= last_id:
                    raise ValueError('hybrid primary key page is not strictly ascending')
                result.add(identifier)
                last_id = identifier

    # 按固定策略召回最多五十候选，分类表达式始终参数化并在每条搜索路径提前过滤。
    @_bounded
    async def recall(self, vector: list[float] | None, text: str | None, *,
                     strategy: Literal['dense', 'bm25', 'hybrid'], category: str | None = None) -> list[VectorHit]:
        if strategy not in ('dense', 'bm25', 'hybrid'):
            raise ValueError('invalid hybrid retrieval strategy')
        if strategy in ('dense', 'hybrid'):
            vector = validate_vector(vector)
        if strategy in ('bm25', 'hybrid') and (not isinstance(text, str) or not text.strip()):
            raise ValueError('BM25 query must be nonempty text')
        validate_category(category)
        if not self._ready:
            await self.ensure_collection()
        expression = {} if category is None else {'expr': 'category == {category}', 'expr_params': {'category': category}}
        dense_params, sparse_params = {'metric_type': 'COSINE', 'params': {}}, {'metric_type': 'BM25', 'params': {}}
        if strategy == 'hybrid':
            requests = [AnnSearchRequest([vector], 'embedding', dense_params, 50, **expression),
                        AnnSearchRequest([text], 'sparse', sparse_params, 50, **expression)]
            result = await self._call('hybrid_search', self.collection, reqs=requests, ranker=RRFRanker(k=60),
                                      limit=50, consistency_level='Strong')
        else:
            filters = {} if category is None else {'filter': 'category == {category}', 'filter_params': {'category': category}}
            result = await self._call('search', self.collection,
                                      data=[vector] if strategy == 'dense' else [text],
                                      anns_field='embedding' if strategy == 'dense' else 'sparse', limit=50,
                                      search_params=dense_params if strategy == 'dense' else sparse_params,
                                      consistency_level='Strong', **filters)
        if not isinstance(result, list) or len(result) != 1 or not isinstance(result[0], list) or len(result[0]) > 50:
            raise ValueError('invalid hybrid search response')
        hits, ids = [], set()
        for item in result[0]:
            if not isinstance(item, dict):
                raise ValueError('invalid hybrid search hit')
            identifier, score = item.get('id'), item.get('distance')
            validate_id(identifier)
            if identifier in ids or type(score) not in (int, float) or not math.isfinite(score):
                raise ValueError('invalid or duplicate hybrid search hit')
            ids.add(identifier)
            hits.append(VectorHit(identifier, float(score)))
        return hits

    # 仅关闭本适配器创建的客户端，外部客户端的生命周期归调用方所有。
    @_bounded
    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.close()
