"""PyMilvus 3.0.2 adapter with an explicit, verified dense collection."""

import math
from collections.abc import Sequence

from pymilvus import AsyncMilvusClient, DataType

from app.knowledge.embeddings import validate_vector
from app.knowledge.types import VectorHit, validate_id


def validate_acknowledged_ids(actual: list[int], expected: list[int]) -> None:
    if not isinstance(actual, list):
        raise ValueError('vector upsert did not return primary keys')
    for identifier in actual:
        validate_id(identifier)
    if len(actual) != len(expected) or len(set(actual)) != len(actual) or set(actual) != set(expected):
        raise ValueError('vector upsert primary keys differ from requested ids')


class MilvusIndex:
    def __init__(self, uri: str, *, collection: str = 'knowledge', client=None, timeout: float = 5):
        if isinstance(timeout, bool) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError('Milvus timeout must be positive and finite')
        self.collection = collection
        self.timeout = timeout
        self._owns_client = client is None
        # Installed 3.0.2 constructor is lazy; no synchronous network I/O here.
        self._client = client if client is not None else AsyncMilvusClient(uri=uri, timeout=timeout)
        self._ready = False

    async def ensure_collection(self) -> None:
        client = self._client
        if not await client.has_collection(self.collection, timeout=self.timeout):
            schema = AsyncMilvusClient.create_schema(auto_id=False, enable_dynamic_field=False)
            schema.add_field('id', DataType.INT64, is_primary=True, auto_id=False)
            schema.add_field('embedding', DataType.FLOAT_VECTOR, dim=1024)
            indexes = AsyncMilvusClient.prepare_index_params()
            indexes.add_index(field_name='embedding', index_name='embedding', index_type='FLAT', metric_type='COSINE', params={})
            await client.create_collection(self.collection, schema=schema, index_params=indexes,
                                           consistency_level='Strong', timeout=self.timeout)
        description = await client.describe_collection(self.collection, timeout=self.timeout)
        fields = description.get('fields', [])
        by_name = {field.get('name'): field for field in fields}
        primary, vector = by_name.get('id', {}), by_name.get('embedding', {})
        if (len(fields) != 2 or set(by_name) != {'id', 'embedding'}
                or description.get('auto_id') is not False
                or description.get('enable_dynamic_field') is not False
                or description.get('consistency_level') != 0
                or primary.get('type') != DataType.INT64
                or primary.get('is_primary') is not True
                or primary.get('auto_id', False) is not False
                or vector.get('type') != DataType.FLOAT_VECTOR
                or str(vector.get('params', {}).get('dim')) != '1024'):
            raise ValueError('existing Milvus collection schema differs from dense knowledge schema')
        index_names = await client.list_indexes(self.collection, timeout=self.timeout)
        if len(index_names) != 1:
            raise ValueError('dense knowledge requires one FLAT COSINE index')
        index = await client.describe_index(self.collection, index_names[0], timeout=self.timeout)
        if not isinstance(index, dict) or any(index.get(key) != value for key, value in {
            'field_name': 'embedding', 'index_type': 'FLAT', 'metric_type': 'COSINE',
        }.items()):
            raise ValueError('existing Milvus index differs from FLAT COSINE')
        await client.load_collection(self.collection, timeout=self.timeout)
        self._ready = True

    async def upsert(self, rows: list[tuple[int, list[float]]]) -> list[int]:
        identifiers, data = [], []
        for identifier, vector in rows:
            validate_id(identifier)
            identifiers.append(identifier)
            data.append({'id': identifier, 'embedding': validate_vector(vector)})
        if len(set(identifiers)) != len(identifiers):
            raise ValueError('duplicate vector primary keys')
        if not rows:
            return []
        if not self._ready:
            await self.ensure_collection()
        result = await self._client.upsert(self.collection, data=data, timeout=self.timeout)
        if not isinstance(result, dict) or type(result.get('upsert_count')) is not int or result['upsert_count'] != len(rows):
            raise ValueError('vector upsert count differs from requested rows')
        actual = result.get('ids')
        # 3.0.2 exposes protobuf RepeatedScalarContainer, which is a Sequence.
        if not isinstance(actual, Sequence) or isinstance(actual, (str, bytes)):
            raise ValueError('vector upsert did not return primary keys')
        actual = list(actual)
        validate_acknowledged_ids(actual, identifiers)
        return actual

    async def search(self, vector: list[float], limit: int = 3) -> list[VectorHit]:
        vector = validate_vector(vector)
        if type(limit) is not int or not 1 <= limit <= 3:
            raise ValueError('dense search limit must be between 1 and 3')
        if not self._ready:
            await self.ensure_collection()
        result = await self._client.search(self.collection, data=[vector], limit=limit, anns_field='embedding',
                                           search_params={'metric_type': 'COSINE', 'params': {}},
                                           consistency_level='Strong', timeout=self.timeout)
        if not isinstance(result, list) or len(result) != 1 or not isinstance(result[0], list) or len(result[0]) > limit:
            raise ValueError('invalid vector search response')
        hits = []
        for item in result[0]:
            identifier = item.get('id')
            score = item.get('distance')
            validate_id(identifier)
            if type(score) not in (int, float) or not math.isfinite(score):
                raise ValueError('invalid vector search score')
            hits.append(VectorHit(identifier, float(score)))
        return hits

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.close()
