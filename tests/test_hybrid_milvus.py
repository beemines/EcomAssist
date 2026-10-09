# 原生混合索引的边界行为测试：分类前过滤、确认校验、分页和取消均不依赖网络。
import asyncio
import json
from copy import deepcopy
from types import SimpleNamespace

import grpc
import pytest
from pymilvus import DataType, FunctionType
from pymilvus.decorators import retry_on_rpc_failure
from pymilvus.exceptions import MilvusException


# 延迟加载待实现接口，使 RED 以缺少实现的测试失败呈现。
def implementation():
    from app.retrieval.milvus import HybridMilvusIndex
    from app.retrieval.types import IndexedChunk
    return HybridMilvusIndex, IndexedChunk


# 使用有效确定性向量，避免请求模型服务。
def vector():
    return [1.0] + [0.0] * 1023


class SearchClient:
    # 保存发送到 SDK 的真实请求对象，回包结构与真实 SDK 搜索一致。
    def __init__(self):
        self.calls = []

    # 捕获混合调用参数并返回一个合法主键命中。
    async def hybrid_search(self, *args, **kwargs):
        self.calls.append(('hybrid', args, kwargs))
        return [[{'id': 7, 'distance': 0.032786883413791656, 'entity': {}}]]

    # 捕获单路调用参数并返回合法主键与分数。
    async def search(self, *args, **kwargs):
        self.calls.append(('single', args, kwargs))
        return [[{'id': 7, 'distance': 1.0, 'entity': {}}]]


# 分类必须对两路使用相同参数化表达式和 Top-50，融合采用固定 RRF。
async def test_hybrid_requests_use_equal_prefilters_and_limits():
    Index, _ = implementation()
    client = SearchClient()
    index = Index('unused', client=client)
    index._ready = True
    hits = await index.recall(vector(), 'WH-1000XM5', strategy='hybrid', category='耳机')
    assert [(h.id, h.score) for h in hits] == [(7, pytest.approx(0.0327868834))]
    _, _, options = client.calls[0]
    dense, sparse = options['reqs']
    assert dense.limit == sparse.limit == options['limit'] == 50
    assert dense.expr == sparse.expr == 'category == {category}'
    assert dense.expr_params == sparse.expr_params == {'category': '耳机'}
    assert dense.anns_field == 'embedding' and sparse.anns_field == 'sparse'
    assert dense.data == [vector()] and sparse.data == ['WH-1000XM5']
    assert options['ranker'].dict() == {'strategy': 'rrf', 'params': {'k': 60}}
    assert options['consistency_level'] == 'Strong'


# 单路有分类时执行等值前过滤，无分类时省略筛选表达式。
@pytest.mark.parametrize('strategy,field,data', [('dense', 'embedding', [vector()]), ('bm25', 'sparse', ['型号'])])
@pytest.mark.parametrize('category', [None, '耳机" or id > 0'])
async def test_single_recall_prefilter_is_parameterized_or_absent(strategy, field, data, category):
    Index, _ = implementation()
    client = SearchClient()
    index = Index('unused', client=client)
    index._ready = True
    await index.recall(vector(), '型号', strategy=strategy, category=category)
    options = client.calls[0][2]
    assert options['anns_field'] == field and options['data'] == data and options['limit'] == 50
    if category is None:
        assert 'filter' not in options and 'filter_params' not in options
    else:
        assert options['filter'] == 'category == {category}'
        assert options['filter_params'] == {'category': category}


# 混合无分类请求不能意外筛掉合法候选。
async def test_hybrid_without_category_has_no_expression():
    Index, _ = implementation()
    client = SearchClient()
    index = Index('unused', client=client)
    index._ready = True
    await index.recall(vector(), '型号', strategy='hybrid')
    assert all(request.expr is None and request.expr_params in (None, {}) for request in client.calls[0][2]['reqs'])


# 请求数据错误必须在网络调用前被拒绝。
@pytest.mark.parametrize('dense,text,strategy,category', [
    (None, '型号', 'dense', None), (vector(), None, 'bm25', None),
    ([1.0], '型号', 'hybrid', None), (vector(), ' ', 'hybrid', None),
    (vector(), '型号', 'other', None), (vector(), '型号', 'dense', '耳' * 256),
])
async def test_invalid_recall_is_rejected_before_io(dense, text, strategy, category):
    Index, _ = implementation()
    client = SearchClient()
    index = Index('unused', client=client)
    with pytest.raises(ValueError):
        await index.recall(dense, text, strategy=strategy, category=category)
    assert client.calls == []


# 入库数据契约复用正 INT64、1024 维有限向量与分类字符上限。
@pytest.mark.parametrize('identifier,dense,text,category', [
    (True, vector(), '正文', '耳机'), (0, vector(), '正文', '耳机'),
    (7, [float('nan')] * 1024, '正文', '耳机'), (7, [1.0], '正文', '耳机'),
    (7, vector(), None, '耳机'), (7, vector(), '正文', '耳' * 256),
])
def test_indexed_chunk_rejects_invalid_fields(identifier, dense, text, category):
    _, Chunk = implementation()
    with pytest.raises(ValueError):
        Chunk(identifier, dense, text, category)


class RowClient:
    # 保存入库及读回测试所需的受控外部状态。
    def __init__(self, result=None, rows=None):
        self.result = result
        self.rows = rows or []
        self.calls = []

    # 捕获全字段写入并返回指定的服务端确认。
    async def upsert(self, *args, **kwargs):
        self.calls.append(('upsert', kwargs))
        return self.result

    # 按真实 SDK 行结构返回受控结果。
    async def get(self, *args, **kwargs):
        self.calls.append(('get', kwargs))
        return self.rows


# 重复主键必须被拒绝，以免批次确认掩盖覆盖丢失。
async def test_duplicate_ids_rejected_before_write():
    Index, Chunk = implementation()
    client = RowClient()
    index = Index('unused', client=client)
    with pytest.raises(ValueError):
        await index.upsert([Chunk(7, vector(), '正文', '耳机')] * 2)
    assert client.calls == []


# 写入必须发送所有源字段并核验计数及主键，而不是只相信成功状态。
@pytest.mark.parametrize('result', [
    {'upsert_count': 0, 'ids': [7]}, {'upsert_count': 1, 'ids': [8]},
    {'upsert_count': True, 'ids': [7]}, {'upsert_count': 1, 'ids': [True]},
    {'upsert_count': 1},
])
async def test_wrong_upsert_acknowledgement_rejected(result):
    Index, Chunk = implementation()
    client = RowClient(result=result)
    index = Index('unused', client=client)
    index._ready = True
    with pytest.raises(ValueError):
        await index.upsert([Chunk(7, vector(), '正文', '耳机')])
    assert client.calls[0][1]['data'] == [{'id': 7, 'embedding': vector(), 'text': '正文', 'category': '耳机'}]


# 主键读回顺序应依请求还原，允许缺失但拒绝未请求、重复与非法字段。
async def test_get_rows_preserves_requested_order():
    Index, Chunk = implementation()
    client = RowClient(rows=[{'id': 9, 'embedding': vector(), 'text': '乙', 'category': '耳机'},
                             {'id': 7, 'embedding': vector(), 'text': '甲', 'category': '耳机'}])
    index = Index('unused', client=client)
    index._ready = True
    assert await index.get_rows([7, 8, 9]) == [Chunk(7, vector(), '甲', '耳机'), Chunk(9, vector(), '乙', '耳机')]


# 核验允许明确 float32 误差，同时必须发现正文、分类、向量或缺行变化。
@pytest.mark.parametrize('change', ['float32', 'text', 'category', 'embedding', 'missing'])
async def test_verify_rows_uses_tolerance_and_exact_text(change):
    Index, Chunk = implementation()
    row = {'id': 7, 'embedding': [0.1] * 1024, 'text': '正文', 'category': '耳机'}
    expected = Chunk(7, [0.1] * 1024, '正文', '耳机')
    if change == 'float32': row['embedding'] = [0.10000000149011612] * 1024
    elif change == 'embedding': row['embedding'][0] = 0.11
    elif change != 'missing': row[change] = '漂移'
    index = Index('unused', client=RowClient(rows=[] if change == 'missing' else [row]))
    index._ready = True
    if change == 'float32':
        await index.verify_rows([expected])
    else:
        with pytest.raises(ValueError):
            await index.verify_rows([expected])


class PageClient:
    # 提供超过 Milvus offset 窗口的乱序全集，排序仅在适配器显式请求时生效。
    def __init__(self):
        self.ids = list(range(17001, 0, -1))
        self.calls = []

    # 执行游标筛选及排序，缺少排序会模拟 Milvus 默认未指定顺序导致的漏行。
    async def query(self, *args, **kwargs):
        self.calls.append(kwargs)
        cursor = kwargs['filter_params']['last_id']
        ids = [i for i in self.ids if i > cursor]
        if kwargs.get('order_by') == ['id:asc']:
            ids.sort()
        return [{'id': i} for i in ids[:kwargs['limit']]]


# 全量主键读取必须跨越 offset 上限，不能依赖默认顺序或一次查询。
async def test_all_ids_uses_sorted_keyset_pages_beyond_offset_window():
    Index, _ = implementation()
    client = PageClient()
    index = Index('unused', client=client)
    index._ready = True
    assert await index.all_ids() == set(range(1, 17002))
    assert all(call['filter'] == 'id > {last_id}' and 'offset' not in call for call in client.calls)
    assert all(call['consistency_level'] == 'Strong' for call in client.calls)


class Unavailable(grpc.RpcError):
    # 模拟可重试 RPC 故障，促使真实 SDK 装饰器暴露重试行为。
    def code(self):
        return grpc.StatusCode.UNAVAILABLE

    # 返回不含凭据的错误详情。
    def details(self):
        return 'synthetic unavailable'


class FailingClient:
    # 记录真实 SDK 重试装饰器调用底层操作的次数与取消状态。
    def __init__(self, slow=False):
        self.attempts = 0
        self.slow = slow
        self.cancelled = False
        self.options = None

    # 复用已安装 SDK 的真实重试装饰器，不能用接受任意参数的假重试代替。
    @retry_on_rpc_failure()
    async def search(self, *args, **kwargs):
        self.attempts += 1
        self.options = kwargs
        if self.slow:
            try:
                await asyncio.Event().wait()
            finally:
                self.cancelled = True
        raise Unavailable()


# 一次可重试 RPC 失败必须立即传播，不能因数值 timeout 被 SDK 隐藏重试。
async def test_retryable_rpc_error_is_attempted_once():
    Index, _ = implementation()
    client = FailingClient()
    index = Index('unused', client=client, timeout=0.1)
    index._ready = True
    with pytest.raises(MilvusException):
        await index.recall(vector(), None, strategy='dense')
    assert client.attempts == 1
    assert client.options['timeout'] is None and client.options['retry_times'] == 0


# 外层期限必须取消挂起调用并传播 TimeoutError。
async def test_deadline_cancels_hanging_rpc():
    Index, _ = implementation()
    client = FailingClient(slow=True)
    index = Index('unused', client=client, timeout=0.02)
    index._ready = True
    with pytest.raises(TimeoutError):
        await index.recall(vector(), None, strategy='dense')
    assert client.attempts == 1 and client.cancelled


# 外部客户端生命周期由调用方持有。
async def test_external_client_is_not_closed():
    Index, _ = implementation()
    client = SimpleNamespace()
    await Index('unused', client=client).aclose()


# 内部创建的 SDK 客户端必须被关闭，避免应用关停时遗留连接。
async def test_owned_client_is_closed(monkeypatch):
    Index, _ = implementation()
    import app.retrieval.milvus as module
    closed = []
    # 仅替代客户端构造边界，关闭与归属分支仍由真实适配器执行。
    async def close():
        closed.append(True)
    client = SimpleNamespace(close=close)
    monkeypatch.setattr(module, 'AsyncMilvusClient', lambda **kwargs: client)
    await Index('unused').aclose()
    assert closed == [True]


# 空批次与空读回应短路，不能因无数据创建集合。
async def test_empty_batches_do_not_access_client():
    Index, _ = implementation()
    index = Index('unused', client=SimpleNamespace())
    assert await index.upsert([]) == []
    assert await index.get_rows([]) == []
    await index.verify_rows([])


# 合法写入接受回包乱序，但返回真实服务端确认的主键。
async def test_upsert_accepts_reordered_complete_acknowledgement():
    Index, Chunk = implementation()
    client = RowClient(result={'upsert_count': 2, 'ids': [9, 7]})
    index = Index('unused', client=client)
    index._ready = True
    assert await index.upsert([Chunk(7, vector(), '甲', '耳机'), Chunk(9, vector(), '乙', '耳机')]) == [9, 7]


# 读回越界、重复及非法数据必须被拒绝，避免确认错误记录。
@pytest.mark.parametrize('rows', [
    [{'id': 8, 'embedding': vector(), 'text': '甲', 'category': '耳机'}],
    [{'id': 7, 'embedding': vector(), 'text': '甲', 'category': '耳机'}] * 2,
    [{'id': 7, 'embedding': [1.0], 'text': '甲', 'category': '耳机'}],
    [{'id': 7, 'embedding': vector(), 'text': None, 'category': '耳机'}],
    None,
])
async def test_get_rows_rejects_invalid_response(rows):
    Index, _ = implementation()
    client = RowClient()
    client.rows = rows
    index = Index('unused', client=client)
    index._ready = True
    with pytest.raises(ValueError):
        await index.get_rows([7])


# 非法检索回包不能成为合法证据主键或超过候选上限。
@pytest.mark.parametrize('response', [
    [], [[{'id': True, 'distance': 1.0, 'entity': {}}]],
    [[{'id': 7, 'distance': float('nan'), 'entity': {}}]],
    [[{'id': 7, 'distance': True, 'entity': {}}]],
    [[{'id': 7, 'distance': 1.0, 'entity': {}}] * 2],
    [[{'id': i, 'distance': 1.0, 'entity': {}} for i in range(1, 52)]],
])
async def test_recall_rejects_malformed_hits(response):
    Index, _ = implementation()
    # 仅替换网络响应，实际适配器解析与校验保持运行。
    async def search(*args, **kwargs):
        return response
    index = Index('unused', client=SimpleNamespace(search=search))
    index._ready = True
    with pytest.raises(ValueError):
        await index.recall(vector(), None, strategy='dense')


# 无效超时必须在创建 SDK 客户端之前失败。
@pytest.mark.parametrize('timeout', [0, -1, True, float('inf'), float('nan')])
def test_timeout_must_be_positive_finite(timeout):
    Index, _ = implementation()
    with pytest.raises(ValueError):
        Index('unused', client=SimpleNamespace(), timeout=timeout)


# 完整复刻 StorageV3 探针观察到的 SDK 描述形状；元数据值使用固定非生产标识。
def collection_description():
    return {
        'collection_name': 'owned', 'auto_id': False, 'num_shards': 1, 'description': '',
        'fields': [
            {'field_id': 100, 'name': 'id', 'description': '', 'type': DataType.INT64, 'params': {}, 'is_primary': True},
            {'field_id': 101, 'name': 'embedding', 'description': '', 'type': DataType.FLOAT_VECTOR, 'params': {'dim': 1024}},
            {'field_id': 102, 'name': 'text', 'description': '', 'type': DataType.TEXT,
             'params': {'enable_analyzer': 'true', 'analyzer_params': '{"type":"chinese"}'}},
            {'field_id': 103, 'name': 'category', 'description': '', 'type': DataType.VARCHAR, 'params': {'max_length': 1020}},
            {'field_id': 104, 'name': 'sparse', 'description': '', 'type': DataType.SPARSE_FLOAT_VECTOR,
             'params': {}, 'is_function_output': True},
        ],
        'functions': [{'name': 'text_bm25', 'id': 100, 'description': '', 'type': FunctionType.BM25, 'params': {},
                       'input_field_names': ['text'], 'input_field_ids': [102],
                       'output_field_names': ['sparse'], 'output_field_ids': [104]}],
        'aliases': [], 'collection_id': 1000, 'consistency_level': 0, 'consistency_level_name': 'Strong',
        'properties': {'timezone': 'UTC', 'namespace.sharding.enabled': 'false', 'max_field_id': '104'},
        'num_partitions': 1, 'enable_dynamic_field': False, 'enable_namespace': False,
        'schema_version': 0, 'created_timestamp': 1000, 'update_timestamp': 1000,
    }


class SchemaClient:
    # 完整复刻探针的两索引回包，并记录适配器发出的结构与 RPC 选项。
    def __init__(self, *, exists=True, delay=0):
        self.exists, self.delay = exists, delay
        self.description = collection_description()
        self.indexes = [
            {'metric_type': 'COSINE', 'index_type': 'FLAT', 'field_name': 'embedding', 'index_name': 'embedding',
             'total_rows': 0, 'indexed_rows': 0, 'pending_index_rows': 0, 'state': 'Finished'},
            {'inverted_index_algo': 'DAAT_MAXSCORE', 'bm25_k1': '1.2', 'bm25_b': '0.75', 'metric_type': 'BM25',
             'index_type': 'SPARSE_INVERTED_INDEX', 'field_name': 'sparse', 'index_name': 'sparse',
             'total_rows': 0, 'indexed_rows': 0, 'pending_index_rows': 0, 'state': 'Finished'},
        ]
        self.calls = []

    # 仅替代外部 RPC，保留真实适配器集合创建、元数据解析与期限逻辑。
    def __getattr__(self, method):
        # 提供元数据与创建响应，并使挂起网络行为可受外层取消。
        async def call(*args, **kwargs):
            self.calls.append((method, args, kwargs))
            await asyncio.sleep(self.delay)
            if method == 'has_collection': return self.exists
            if method == 'describe_collection': return deepcopy(self.description)
            if method == 'list_indexes': return [index['index_name'] for index in self.indexes]
            if method == 'describe_index': return deepcopy(next(index for index in self.indexes if index['index_name'] == args[1]))
            if method == 'search': return [[]]
        return call


# 新集合真实 schema 对象与两索引必须分别发送，且每次 RPC 都禁用可配置重试。
async def test_create_collection_emits_native_schema_indexes_and_zero_retry_options():
    Index, _ = implementation()
    client = SchemaClient(exists=False)
    await Index('unused', client=client).ensure_collection()
    calls = {method: options for method, _, options in client.calls if method in ('create_collection', 'create_index')}
    schema = calls['create_collection']['schema'].to_dict()
    fields = {field['name']: field for field in schema['fields']}
    assert set(fields) == {'id', 'embedding', 'text', 'category', 'sparse'}
    assert fields['text']['type'] == DataType.TEXT
    assert fields['text']['params']['enable_analyzer'] is True
    assert json.loads(fields['text']['params']['analyzer_params']) == {'type': 'chinese'}
    assert fields['category']['params']['max_length'] == 1020
    assert fields['embedding']['params']['dim'] == 1024
    assert schema['functions'][0]['type'] == FunctionType.BM25
    assert schema['functions'][0]['input_field_names'] == ['text']
    assert schema['functions'][0]['output_field_names'] == ['sparse']
    assert calls['create_collection']['consistency_level'] == 'Strong'
    assert 'index_params' not in calls['create_collection']
    configs = [index.to_dict() for index in calls['create_index']['index_params']]
    assert configs == [
        {'field_name': 'embedding', 'index_name': 'embedding', 'index_type': 'FLAT', 'metric_type': 'COSINE'},
        {'field_name': 'sparse', 'index_name': 'sparse', 'index_type': 'SPARSE_INVERTED_INDEX', 'metric_type': 'BM25',
         'inverted_index_algo': 'DAAT_MAXSCORE', 'bm25_k1': 1.2, 'bm25_b': 0.75},
    ]
    assert all(options['timeout'] is None and options['retry_times'] == 0 and options['retry_on_rate_limit'] is False
               for _, _, options in client.calls)


# 枚举实际元数据漂移，拒绝初始化且不得 drop、重建或加载不匹配集合。
@pytest.mark.parametrize('drift', ['field', 'dimension', 'text-type', 'analyzer', 'category', 'function',
                                   'dynamic', 'consistency', 'auto-id', 'metric', 'sparse-algo', 'k1', 'b'])
async def test_schema_or_index_drift_rejected_without_destructive_repair(drift):
    Index, _ = implementation()
    client = SchemaClient()
    fields = {field['name']: field for field in client.description['fields']}
    if drift == 'field': client.description['fields'].pop()
    elif drift == 'dimension': fields['embedding']['params']['dim'] = 768
    elif drift == 'text-type': fields['text']['type'] = DataType.VARCHAR
    elif drift == 'analyzer': fields['text']['params']['analyzer_params'] = '{"type":"english"}'
    elif drift == 'category': fields['category']['params']['max_length'] = 255
    elif drift == 'function': client.description['functions'][0]['input_field_names'] = ['category']
    elif drift == 'dynamic': client.description['enable_dynamic_field'] = True
    elif drift == 'consistency': client.description['consistency_level'] = 2
    elif drift == 'auto-id': client.description['auto_id'] = True
    elif drift == 'metric': client.indexes[0]['metric_type'] = 'L2'
    elif drift == 'sparse-algo': client.indexes[1]['inverted_index_algo'] = 'DAAT_WAND'
    elif drift == 'k1': client.indexes[1]['bm25_k1'] = '1.5'
    elif drift == 'b': client.indexes[1]['bm25_b'] = '0.5'
    index = Index('unused', client=client)
    with pytest.raises(ValueError):
        await index.ensure_collection()
    assert not index._ready
    assert not {'drop_collection', 'create_collection', 'create_index', 'load_collection'} & {method for method, _, _ in client.calls}


# 初始化与召回共享同一期限，不能每次 RPC 或嵌套初始化续期。
async def test_recall_deadline_includes_initialization_without_renewal():
    Index, _ = implementation()
    client = SchemaClient(delay=0.01)
    index = Index('unused', client=client, timeout=0.035)
    with pytest.raises(TimeoutError):
        await index.recall(vector(), None, strategy='dense')
    assert 'search' not in [method for method, _, _ in client.calls]


# 主动取消不能被适配器转成空命中或吞掉，挂起调用必须已取消。
async def test_external_cancellation_propagates_to_rpc():
    Index, _ = implementation()
    client = FailingClient(slow=True)
    index = Index('unused', client=client)
    index._ready = True
    task = asyncio.create_task(index.recall(vector(), None, strategy='dense'))
    while client.attempts == 0:
        await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert client.cancelled and client.attempts == 1


@pytest.mark.parametrize('category', ['', ' \t', 7, True, '中' * 256])
async def test_invalid_category_cannot_reach_index_initialization_or_search(category):
    """分类早拒必须发生在集合初始化与任何搜索前，避免无效筛选误算未命中。"""
    Index, _ = implementation()
    client = SearchClient()
    index = Index('unused', client=client)
    async def forbidden_initialization(*args, **kwargs):
        """无效分类不得触发初始化查询，显式定位错误边界。"""
        pytest.fail('invalid category reached index initialization')
    client.has_collection = forbidden_initialization
    with pytest.raises(ValueError):
        await index.recall(vector(), '问题', strategy='hybrid', category=category)
    assert client.calls == []
