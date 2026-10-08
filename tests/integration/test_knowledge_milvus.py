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


async def test_real_primary_key_upsert_strong_search_and_existing_schema(milvus_collection):
    service = milvus_collection
    index = MilvusIndex(service.uri, collection=service.name, client=service.client)
    await index.ensure_collection()
    first, second = [1.0] + [0.0] * 1023, [0.0, 1.0] + [0.0] * 1022
    assert await index.upsert([(7, first), (9, second)]) == [7, 9]
    assert await index.upsert([(7, second)]) == [7]
    # Fresh adapter verifies metadata returned by the actual installed SDK/service.
    fresh = MilvusIndex(service.uri, collection=service.name, client=service.client)
    hits = await fresh.search(second)
    assert {hit.id for hit in hits} == {7, 9}
    assert all(hit.score == pytest.approx(1.0) for hit in hits)
    rows = await service.client.query(service.name, filter='id >= 0', output_fields=['id'], consistency_level='Strong', timeout=5)
    assert sorted(row['id'] for row in rows) == [7, 9]
    await index.aclose()
    assert await service.client.has_collection(service.name, timeout=5)


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


@pytest.mark.parametrize('failure', ['embed', 'mark', 'cancel'])
async def test_real_mysql_pending_resumes_after_failure_without_duplicate_vectors(knowledge_rows, milvus_collection, failure):
    # Isolate reads to only the fixture-owned rows, preserving any other pending jobs.
    class OwnedRepository(KnowledgeRepository):
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
    def fail_mark(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith('UPDATE KNOWLEDGE_CHUNKS'):
            raise RuntimeError('synthetic transaction failure')
    class FailEmbedder:
        async def embed(self, texts): raise RuntimeError('synthetic embedding interruption')
    class CancelAfterWrite:
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
