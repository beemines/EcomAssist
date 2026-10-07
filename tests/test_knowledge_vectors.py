from copy import deepcopy

import pytest
from pymilvus import DataType

from app.knowledge.types import VectorHit


def index(client, **kwargs):
    try:
        from app.knowledge.vectors import MilvusIndex
    except ImportError:
        pytest.fail('Milvus adapter is missing')
    return MilvusIndex('http://127.0.0.1:19530', client=client, **kwargs)


class SDK:
    def __init__(self, exists=True):
        self.exists = exists
        self.created = None
        self.loaded = False
        self.written = []
        self.closed = False
        self.schema = {'collection_name': 'knowledge', 'auto_id': False, 'enable_dynamic_field': False,
                       'consistency_level': 0, 'consistency_level_name': 'Strong',
                       'fields': [{'name': 'id', 'type': DataType.INT64, 'is_primary': True, 'auto_id': False, 'params': {}},
                                  {'name': 'embedding', 'type': DataType.FLOAT_VECTOR, 'params': {'dim': 1024}}]}
        self.index = {'field_name': 'embedding', 'index_name': 'embedding', 'index_type': 'FLAT', 'metric_type': 'COSINE', 'params': {}, 'state': 'Finished', 'total_rows': 0, 'indexed_rows': 0, 'pending_index_rows': 0}
        self.ack = {'upsert_count': 1, 'ids': [7], 'cost': 0}

    async def has_collection(self, collection_name, **kwargs):
        return self.exists

    async def create_collection(self, collection_name, **kwargs):
        self.exists = True
        self.created = kwargs

    async def describe_collection(self, collection_name, **kwargs):
        return deepcopy(self.schema)

    async def list_indexes(self, collection_name, **kwargs):
        return ['embedding']

    async def describe_index(self, collection_name, index_name, **kwargs):
        return deepcopy(self.index)

    async def load_collection(self, collection_name, **kwargs):
        self.loaded = True

    async def upsert(self, collection_name, data, **kwargs):
        self.written.extend(data)
        assert kwargs['timeout'] == 5
        return self.ack

    async def search(self, collection_name, **kwargs):
        assert kwargs['data'] == [[1.0] * 1024]
        assert kwargs['limit'] == 3
        assert kwargs['anns_field'] == 'embedding'
        assert kwargs['search_params']['metric_type'] == 'COSINE'
        assert kwargs['consistency_level'] == 'Strong'
        assert kwargs['timeout'] == 5
        return [[{'id': 7, 'distance': 0.8, 'entity': {}}]]

    async def close(self):
        self.closed = True


async def test_creates_explicit_schema_flat_cosine_strong_and_preserves_client():
    sdk = SDK(exists=False)
    adapter = index(sdk)
    await adapter.ensure_collection()
    fields = sdk.created['schema'].to_dict()['fields']
    assert [(field['name'], field['type']) for field in fields] == [('id', DataType.INT64), ('embedding', DataType.FLOAT_VECTOR)]
    assert fields[0]['is_primary'] is True and fields[0]['auto_id'] is False
    assert fields[1]['params']['dim'] == 1024
    assert sdk.created['schema'].enable_dynamic_field is False
    assert sdk.created['consistency_level'] == 'Strong'
    assert [parameter.to_dict() for parameter in sdk.created['index_params']] == [{'field_name': 'embedding', 'index_name': 'embedding', 'index_type': 'FLAT', 'metric_type': 'COSINE'}]
    assert sdk.loaded
    await adapter.aclose()
    assert not sdk.closed


@pytest.mark.parametrize('drift', ['auto-id', 'dynamic', 'consistency', 'primary-name', 'primary-type', 'primary-flag', 'dimension', 'vector-name', 'extra-field', 'metric', 'index-type', 'index-field'])
async def test_existing_collection_drift_rejected_before_write(drift):
    sdk = SDK()
    if drift == 'auto-id': sdk.schema['auto_id'] = True
    elif drift == 'dynamic': sdk.schema['enable_dynamic_field'] = True
    elif drift == 'consistency': sdk.schema['consistency_level'] = 2
    elif drift == 'primary-name': sdk.schema['fields'][0]['name'] = 'other'
    elif drift == 'primary-type': sdk.schema['fields'][0]['type'] = DataType.VARCHAR
    elif drift == 'primary-flag': sdk.schema['fields'][0]['is_primary'] = False
    elif drift == 'dimension': sdk.schema['fields'][1]['params']['dim'] = 768
    elif drift == 'vector-name': sdk.schema['fields'][1]['name'] = 'other'
    elif drift == 'extra-field': sdk.schema['fields'].append({'name': 'other', 'type': DataType.INT64, 'params': {}})
    elif drift == 'metric': sdk.index['metric_type'] = 'L2'
    elif drift == 'index-type': sdk.index['index_type'] = 'HNSW'
    elif drift == 'index-field': sdk.index['field_name'] = 'other'
    with pytest.raises(ValueError):
        await index(sdk).upsert([(7, [1.0] * 1024)])
    assert sdk.written == []
    assert not sdk.loaded


async def test_upsert_returns_verified_primary_keys_and_search_hits():
    sdk = SDK()
    adapter = index(sdk)
    assert await adapter.upsert([(7, [1.0] * 1024)]) == [7]
    assert sdk.written == [{'id': 7, 'embedding': [1.0] * 1024}]
    assert await adapter.search([1.0] * 1024) == [VectorHit(7, 0.8)]


async def test_installed_sdk_protobuf_primary_keys_are_normalized_to_list():
    from pymilvus.grpc_gen import schema_pb2
    sdk = SDK()
    sdk.ack['ids'] = schema_pb2.LongArray(data=[7]).data
    result = await index(sdk).upsert([(7, [1.0] * 1024)])
    assert type(result) is list
    assert result == [7]


@pytest.mark.parametrize('ack', [{'upsert_count': 1, 'ids': [8]}, {'upsert_count': 0, 'ids': [7]}, {'upsert_count': 1, 'ids': [True]}, {'upsert_count': 1, 'ids': []}, {'upsert_count': 1}, {'upsert_count': 2, 'ids': [7, 7]}])
async def test_invalid_sdk_ack_rejected(ack):
    sdk = SDK()
    sdk.ack = ack
    with pytest.raises(ValueError):
        await index(sdk).upsert([(7, [1.0] * 1024)])


@pytest.mark.parametrize('rows', [[(9223372036854775808, [1.0] * 1024)], [(True, [1.0] * 1024)], [(7, [1.0] * 1023)], [(7, [float('inf')] * 1024)], [(7, [True] * 1024)], [(7, [1.0] * 1024), (7, [1.0] * 1024)]])
async def test_invalid_input_rejected_before_sdk_write(rows):
    sdk = SDK()
    with pytest.raises(ValueError):
        await index(sdk).upsert(rows)
    assert sdk.written == []


@pytest.mark.parametrize('limit', [0, 4, True, 1.5])
async def test_dense_search_rejects_limit_outside_one_to_three(limit):
    with pytest.raises(ValueError):
        await index(SDK()).search([1.0] * 1024, limit=limit)
