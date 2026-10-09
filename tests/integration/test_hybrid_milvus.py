# 真实 Milvus 验收中文 analyzer、TEXT/BM25、分类型号检索与读回确认。
import pytest
from pymilvus import DataType


# 五字段、双索引与中文型号检索必须在夹具拥有的唯一集合中真实通过。
async def test_real_bm25_model_search_stays_inside_category(milvus_collection):
    from app.retrieval.milvus import HybridMilvusIndex
    from app.retrieval.types import IndexedChunk
    service = milvus_collection
    index = HybridMilvusIndex(service.uri, collection=service.name, client=service.client)
    await index.ensure_collection()
    description = await service.client.describe_collection(service.name)
    fields = {field['name']: field for field in description['fields']}
    assert set(fields) == {'id', 'embedding', 'text', 'category', 'sparse'}
    assert fields['text']['type'] == DataType.TEXT
    assert description['consistency_level'] == 0
    analyzed = await service.client.run_analyzer('索尼 WH-1000XM5 主动降噪耳机', collection_name=service.name, field_name='text')
    assert {'索尼', '主动', '降噪', '耳机', 'XM5'} <= set(analyzed.tokens)
    vector = [0.1] * 1024
    rows = [IndexedChunk(7, vector, '索尼 WH-1000XM5 耳机支持主动降噪和蓝牙连接。', '耳机'),
            IndexedChunk(9, vector, '索尼 WH-1000XM4 耳机续航三十小时。', '耳机'),
            IndexedChunk(11, vector, 'WH-1000XM5 手机保护壳库存充足。', '手机')]
    assert set(await index.upsert(rows)) == {7, 9, 11}
    await index.verify_rows(rows)
    assert await index.all_ids() == {7, 9, 11}
    for strategy in ('bm25', 'hybrid', 'dense'):
        hits = await index.recall(vector, 'WH-1000XM5 降噪', strategy=strategy, category='耳机')
        ids = [hit.id for hit in hits]
        assert 7 in ids[:10] and set(ids) <= {7, 9}
    assert 11 in [hit.id for hit in await index.recall(None, 'WH-1000XM5', strategy='bm25')]
    replacement = IndexedChunk(7, [0.2] * 1024, '索尼 WH-1000XM5 可开启降噪。', '耳机')
    assert await index.upsert([replacement]) == [7]
    await index.verify_rows([replacement])
    assert await index.all_ids() == {7, 9, 11}
    # 重新创建适配器必须核验真实服务器元数据而非只信第一次创建。
    fresh = HybridMilvusIndex(service.uri, collection=service.name, client=service.client)
    await fresh.ensure_collection()
    await fresh.aclose()
    assert await service.client.has_collection(service.name)


# 255 个四字节 Unicode 分类必须完整写入和过滤，TEXT 还须承载超过 VARCHAR 上限的正文。
async def test_real_category_character_limit_and_long_text_roundtrip(milvus_collection):
    from app.retrieval.milvus import HybridMilvusIndex
    from app.retrieval.types import IndexedChunk
    service = milvus_collection
    index = HybridMilvusIndex(service.uri, collection=service.name, client=service.client)
    category = '😀' * 255
    row = IndexedChunk(17, [0.1] * 1024, '中文降噪知识。' * 4000, category)
    assert len(row.text.encode('utf-8')) > 65535
    assert await index.upsert([row]) == [17]
    await index.verify_rows([row])
    assert [hit.id for hit in await index.recall(None, '降噪', strategy='bm25', category=category)] == [17]
    with pytest.raises(ValueError):
        IndexedChunk(19, [0.1] * 1024, '正文', '😀' * 256)


# 已有旧稠密结构必须报错且保留集合，避免破坏既有评估索引。
async def test_real_legacy_schema_rejected_without_drop(milvus_collection):
    from app.knowledge.vectors import MilvusIndex
    from app.retrieval.milvus import HybridMilvusIndex
    service = milvus_collection
    await MilvusIndex(service.uri, collection=service.name, client=service.client).ensure_collection()
    with pytest.raises(ValueError):
        await HybridMilvusIndex(service.uri, collection=service.name, client=service.client).ensure_collection()
    assert await service.client.has_collection(service.name)
