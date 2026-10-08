# 真实 Milvus 集成测试，覆盖集合契约、主键写入、检索及 MySQL 待向量化恢复。
import asyncio

import pytest
from pymilvus import AsyncMilvusClient, DataType
from sqlalchemy import event, select

from app.db.models import KnowledgeChunk
from app.knowledge.types import ChunkDraft
from app.knowledge.vectorization import PendingVectorizer
from app.knowledge.vectors import MilvusIndex
from app.repositories.knowledge import KnowledgeRepository
from tests.ch03_fakes import RecordingEmbedder


# 验证真实 Milvus 按主键覆盖写入、强一致检索与既有结构复查，并保留外部客户端所有权。
async def test_real_primary_key_upsert_strong_search_and_existing_schema(milvus_collection):
    service = milvus_collection
    index = MilvusIndex(service.uri, collection=service.name, client=service.client)
    await index.ensure_collection()
    first, second = [1.0] + [0.0] * 1023, [0.0, 1.0] + [0.0] * 1022
    assert await index.upsert([(7, first), (9, second)]) == [7, 9]
    assert await index.upsert([(7, second)]) == [7]
    # 用新建适配器核验当前 SDK 和服务真实返回的集合元数据。
    fresh = MilvusIndex(service.uri, collection=service.name, client=service.client)
    hits = await fresh.search(second)
    assert {hit.id for hit in hits} == {7, 9}
    assert all(hit.score == pytest.approx(1.0) for hit in hits)
    rows = await service.client.query(service.name, filter='id >= 0', output_fields=['id'], consistency_level='Strong', timeout=5)
    assert sorted(row['id'] for row in rows) == [7, 9]
    await index.aclose()
    assert await service.client.has_collection(service.name, timeout=5)


# 验证维度、度量、索引、自动主键、动态字段或一致性配置漂移被拒绝。
@pytest.mark.parametrize('drift', ['dimension', 'metric', 'index', 'auto-id', 'dynamic', 'consistency'])
async def test_real_schema_drift_is_rejected(milvus_collection, drift):
    service = milvus_collection
    schema = AsyncMilvusClient.create_schema(auto_id=drift == 'auto-id', enable_dynamic_field=drift == 'dynamic')
    schema.add_field('id', DataType.INT64, is_primary=True, auto_id=drift == 'auto-id')
    schema.add_field('embedding', DataType.FLOAT_VECTOR, dim=768 if drift == 'dimension' else 1024)
    params = AsyncMilvusClient.prepare_index_params()
    params.add_index('embedding', index_name='embedding', index_type='HNSW' if drift == 'index' else 'FLAT', metric_type='L2' if drift == 'metric' else 'COSINE')
    await service.client.create_collection(service.name, schema=schema, index_params=params, consistency_level='Bounded' if drift == 'consistency' else 'Strong', timeout=5)
    with pytest.raises(ValueError):
        await MilvusIndex(service.uri, collection=service.name, client=service.client).ensure_collection()


# 验证嵌入失败、完成提交失败或向量写后取消后可恢复，且不会生成重复向量。
@pytest.mark.parametrize('failure', ['embed', 'mark', 'cancel'])
async def test_real_mysql_pending_resumes_after_failure_without_duplicate_vectors(knowledge_rows, milvus_collection, failure):
    # 读取范围只包含夹具自己的记录，保留其他任务尚待向量化的数据。
    class OwnedRepository(KnowledgeRepository):
        # 仅读取本 fixture 标记的待处理行，防止恢复测试消费其他待向量化任务。
        async def pending(self, limit=20):
            async with self.database.session() as session:
                rows = (await session.scalars(select(KnowledgeChunk).where(KnowledgeChunk.category == knowledge_rows.token, KnowledgeChunk.vectorize_status == 'pending').order_by(KnowledgeChunk.id).limit(limit))).all()
                from app.repositories.knowledge import _record
                return [_record(row) for row in rows]
    repo = OwnedRepository(knowledge_rows.database)
    ids = await repo.add_chunks([ChunkDraft(knowledge_rows.token, '合成测试配送费用', '合成测试配送8元。')])
    service = milvus_collection
    index = MilvusIndex(service.uri, collection=service.name, client=service.client)
    embedder = RecordingEmbedder()
    engine = knowledge_rows.database.engine.sync_engine
    # 在更新知识完成状态前注入事务故障，以检验向量已写入但 SQL 未提交时的恢复。
    def fail_mark(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith('UPDATE KNOWLEDGE_CHUNKS'):
            raise RuntimeError('synthetic transaction failure')
    class FailEmbedder:
        # 直接抛出嵌入故障，模拟向量写入前被中断的处理批次。
        async def embed(self, texts): raise RuntimeError('synthetic embedding interruption')
    class CancelAfterWrite:
        # 先写入真实向量再传播取消，模拟向量与 SQL 完成状态之间的中断边界。
        async def upsert(self, rows):
            await index.upsert(rows)
            raise asyncio.CancelledError()
    if failure == 'mark': event.listen(engine, 'before_cursor_execute', fail_mark)
    try:
        with pytest.raises(asyncio.CancelledError if failure == 'cancel' else RuntimeError):
            await PendingVectorizer(repo, FailEmbedder() if failure == 'embed' else embedder, CancelAfterWrite() if failure == 'cancel' else index).run()
    finally:
        if failure == 'mark': event.remove(engine, 'before_cursor_execute', fail_mark)
    assert await repo.get_done(ids) == []
    assert await PendingVectorizer(repo, embedder, index).run() == 1
    assert [(row.id, row.vector_id) for row in await repo.get_done(ids)] == [(ids[0], str(ids[0]))]
    assert await PendingVectorizer(repo, embedder, index).run() == 0
    rows = await service.client.query(service.name, filter='id >= 0', output_fields=['id'], consistency_level='Strong', timeout=5)
    assert rows == [{'id': ids[0]}]
