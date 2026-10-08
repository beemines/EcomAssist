from copy import deepcopy

import pytest
from pymilvus import DataType

from app.knowledge.types import VectorHit


# 构造注入 SDK 客户端的真实 Milvus 适配器，避免连接外部服务。
def index(client, **kwargs):
    try:
        from app.knowledge.vectors import MilvusIndex
    except ImportError:
        pytest.fail('Milvus adapter is missing')
    return MilvusIndex('http://127.0.0.1:19530', client=client, **kwargs)


class SDK:
    # 准备集合与索引元数据、写入确认和资源状态，供结构漂移与协议测试修改。
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

    # 返回预设集合是否存在，以覆盖新建与已有集合路径。
    async def has_collection(self, collection_name, **kwargs):
        return self.exists

    # 记录集合创建参数，并将集合标记为存在。
    async def create_collection(self, collection_name, **kwargs):
        self.exists = True
        self.created = kwargs

    # 返回集合元数据副本，避免适配器修改替身的原始结构。
    async def describe_collection(self, collection_name, **kwargs):
        return deepcopy(self.schema)

    # 返回固定嵌入索引名，供既有集合校验使用。
    async def list_indexes(self, collection_name, **kwargs):
        return ['embedding']

    # 返回索引元数据副本，供度量、类型和字段漂移检查。
    async def describe_index(self, collection_name, index_name, **kwargs):
        return deepcopy(self.index)

    # 记录集合加载状态，验证只有结构校验通过后才加载。
    async def load_collection(self, collection_name, **kwargs):
        self.loaded = True

    # 记录写入数据、核对超时并返回可配置的主键确认。
    async def upsert(self, collection_name, data, **kwargs):
        self.written.extend(data)
        assert kwargs['timeout'] == 5
        return self.ack

    # 核对查询向量、数量、字段、度量和强一致参数，返回固定命中。
    async def search(self, collection_name, **kwargs):
        assert kwargs['data'] == [[1.0] * 1024]
        assert kwargs['limit'] == 3
        assert kwargs['anns_field'] == 'embedding'
        assert kwargs['search_params']['metric_type'] == 'COSINE'
        assert kwargs['consistency_level'] == 'Strong'
        assert kwargs['timeout'] == 5
        return [[{'id': 7, 'distance': 0.8, 'entity': {}}]]

    # 记录 SDK 客户端关闭状态，用于核对注入资源所有权。
    async def close(self):
        self.closed = True


# 验证新集合显式采用 INT64 主键、1024 维向量、FLAT COSINE 和强一致，并保留外部客户端。
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


# 验证已有集合或索引结构漂移在加载与向量写入前被拒绝。
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


# 验证写入只包含主键与向量，确认编号正确且检索结果转换为命中对象。
async def test_upsert_returns_verified_primary_keys_and_search_hits():
    sdk = SDK()
    adapter = index(sdk)
    assert await adapter.upsert([(7, [1.0] * 1024)]) == [7]
    assert sdk.written == [{'id': 7, 'embedding': [1.0] * 1024}]
    assert await adapter.search([1.0] * 1024) == [VectorHit(7, 0.8)]


# 验证已安装 SDK 的 protobuf 主键序列被规范化为普通列表。
async def test_installed_sdk_protobuf_primary_keys_are_normalized_to_list():
    from pymilvus.grpc_gen import schema_pb2
    sdk = SDK()
    sdk.ack['ids'] = schema_pb2.LongArray(data=[7]).data
    result = await index(sdk).upsert([(7, [1.0] * 1024)])
    assert type(result) is list
    assert result == [7]


# 验证 SDK 返回错误编号、数量、布尔主键、缺失或重复确认时拒绝接受写入结果。
@pytest.mark.parametrize('ack', [{'upsert_count': 1, 'ids': [8]}, {'upsert_count': 0, 'ids': [7]}, {'upsert_count': 1, 'ids': [True]}, {'upsert_count': 1, 'ids': []}, {'upsert_count': 1}, {'upsert_count': 2, 'ids': [7, 7]}])
async def test_invalid_sdk_ack_rejected(ack):
    sdk = SDK()
    sdk.ack = ack
    with pytest.raises(ValueError):
        await index(sdk).upsert([(7, [1.0] * 1024)])


# 验证越界或布尔主键、非法维度数值及重复编号在 SDK 写入前被拒绝。
@pytest.mark.parametrize('rows', [[(9223372036854775808, [1.0] * 1024)], [(True, [1.0] * 1024)], [(7, [1.0] * 1023)], [(7, [float('inf')] * 1024)], [(7, [True] * 1024)], [(7, [1.0] * 1024), (7, [1.0] * 1024)]])
async def test_invalid_input_rejected_before_sdk_write(rows):
    sdk = SDK()
    with pytest.raises(ValueError):
        await index(sdk).upsert(rows)
    assert sdk.written == []


# 验证稠密检索数量只接受一到三的整数，拒绝越界、布尔与小数。
@pytest.mark.parametrize('limit', [0, 4, True, 1.5])
async def test_dense_search_rejects_limit_outside_one_to_three(limit):
    with pytest.raises(ValueError):
        await index(SDK()).search([1.0] * 1024, limit=limit)
