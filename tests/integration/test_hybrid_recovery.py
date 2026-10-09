# 真实 3308/MySQL 与随机 Milvus 集合验证重建、读回及只中断本测试启动的进程。
import asyncio
import json
import sys
import textwrap

import pytest
from sqlalchemy import select

from app.db.models import KnowledgeChunk
from app.knowledge.locking import job_lock
from app.knowledge.types import ChunkDraft
from app.repositories.knowledge import KnowledgeRepository
from app.retrieval.milvus import HybridMilvusIndex
from app.retrieval.types import IndexedChunk
from tests.test_hybrid_jobs import Embedder, jobs


class OwnedRepository(KnowledgeRepository):
    # 仅运行本测试刚创建的记录；底层仍执行产品的真实 MySQL 分页。
    def __init__(self, database, ids):
        super().__init__(database)
        self.ids = ids

    async def done_page(self, *, after_id=0, limit=20):
        return [row for row in await super().done_page(after_id=max(after_id, min(self.ids) - 1), limit=limit)
                if row.id in self.ids]

    async def pending(self, limit=20):
        return [row for row in await super().pending(10000) if row.id in self.ids][:limit]


async def states(database, ids):
    async with database.session() as session:
        rows = (await session.execute(select(KnowledgeChunk.id, KnowledgeChunk.vectorize_status,
            KnowledgeChunk.vector_id).where(KnowledgeChunk.id.in_(ids)).order_by(KnowledgeChunk.id))).all()
    return [tuple(row) for row in rows]


async def test_real_done_page_has_keyset_order_and_validates_arguments(knowledge_rows):
    repo = KnowledgeRepository(knowledge_rows.database)
    ids = await repo.add_chunks([ChunkDraft(knowledge_rows.token, '第一页', '答案'),
                                 ChunkDraft(knowledge_rows.token, 'pending', '答案'),
                                 ChunkDraft(knowledge_rows.token, '第二页', '答案')])
    await repo.mark_done([ids[0], ids[2]])
    assert hasattr(repo, 'done_page'), 'done pagination is missing'
    first = await repo.done_page(after_id=ids[0] - 1, limit=1)
    assert [row.id for row in first] == [ids[0]]
    assert [row.id for row in await repo.done_page(after_id=ids[0], limit=1)] == [ids[2]]
    for after_id, limit in [(-1, 20), (True, 20), (0, 0), (0, True), (0, 1.5)]:
        with pytest.raises(ValueError):
            await repo.done_page(after_id=after_id, limit=limit)


async def test_real_rebuild_preserves_pending_then_recovers_confirmed_write(knowledge_rows, milvus_collection):
    repo = KnowledgeRepository(knowledge_rows.database)
    ids = await repo.add_chunks([ChunkDraft(knowledge_rows.token, question, '合成答案')
                                 for question in ['旧done一', '旧done二', 'pending']])
    await repo.mark_done(ids[:2])
    before = await states(knowledge_rows.database, ids)
    owned = OwnedRepository(knowledge_rows.database, ids)
    service = milvus_collection
    index = HybridMilvusIndex(service.uri, collection=service.name, client=service.client)
    worker = jobs(owned, Embedder(), index)
    async with job_lock(knowledge_rows.database):
        assert (await worker.rebuild_done(1))['ready']
    assert await index.all_ids() == set(ids[:2])
    assert await states(knowledge_rows.database, ids) == before

    class CommitFaultRepository(OwnedRepository):
        async def mark_done(self, identifiers):
            raise RuntimeError('controlled MySQL status commit interruption')
    interrupted = jobs(CommitFaultRepository(knowledge_rows.database, ids), Embedder(), index)
    async with job_lock(knowledge_rows.database):
        with pytest.raises(RuntimeError, match='commit interruption'):
            await interrupted.vectorize_pending(1)
    assert await index.all_ids() == set(ids)
    assert await states(knowledge_rows.database, ids) == before
    async with job_lock(knowledge_rows.database):
        assert await worker.vectorize_pending(1) == 1
        assert (await worker.verify_done(1))['ready']
    assert await index.all_ids() == set(ids)
    assert (await states(knowledge_rows.database, ids))[-1] == (ids[-1], 'done', str(ids[-1]))
    # 等数量错误正文必须阻止切换，恢复正文后额外主键也必须被发现。
    row = (await index.get_rows([ids[0]]))[0]
    await index.upsert([IndexedChunk(row.id, row.embedding, '错误正文', row.category)])
    verification = await worker.verify_done(1)
    assert not verification['ready'] and verification['mismatched_ids'] == [ids[0]]
    await index.upsert([row, IndexedChunk(9223372036854775807, row.embedding, '额外正文', row.category)])
    verification = await worker.verify_done(1)
    assert not verification['ready'] and verification['extra_ids'] == [9223372036854775807]
    print(f'real pending recovery: original_done={ids[:2]}, rebuilt={ids[:2]}, resumed={ids}')


async def test_owned_process_interrupted_rebuild_replays_same_primary_keys(knowledge_rows, milvus_collection, tmp_path):
    repo = KnowledgeRepository(knowledge_rows.database)
    ids = await repo.add_chunks([ChunkDraft(knowledge_rows.token, f'中断问题{i}', '合成答案') for i in range(3)])
    await repo.mark_done(ids)
    before = await states(knowledge_rows.database, ids)
    owned = OwnedRepository(knowledge_rows.database, ids)
    service = milvus_collection
    signal = tmp_path / 'written.json'
    code = textwrap.dedent('''
        import asyncio, json, sys
        from pathlib import Path
        from app.config import load_settings
        from app.db.session import Database
        from app.knowledge.locking import job_lock
        from app.retrieval.milvus import HybridMilvusIndex
        from tests.integration.test_hybrid_recovery import OwnedRepository
        from tests.test_hybrid_jobs import Embedder, jobs
        async def main():
            settings = load_settings()
            database = Database(settings.database_url.set(host='127.0.0.1', port=3308,
                database='customer_service_test', username='customer_service'))
            ids = json.loads(sys.argv[1])
            class PausedIndex(HybridMilvusIndex):
                async def upsert(self, rows):
                    actual = await super().upsert(rows)
                    Path(sys.argv[3]).write_text(json.dumps(actual), encoding='utf-8')
                    await asyncio.Event().wait()
                    return actual
            index = PausedIndex('http://127.0.0.1:19530', collection=sys.argv[2])
            try:
                async with job_lock(database):
                    await jobs(OwnedRepository(database, ids), Embedder(), index).rebuild_done(1)
            finally:
                await index.aclose()
                await database.dispose()
        try:
            asyncio.run(main())
        except Exception as exc:
            print(type(exc).__name__, file=sys.stderr)
            sys.exit(1)
    ''')
    process = await asyncio.create_subprocess_exec(sys.executable, '-c', code, json.dumps(ids),
        service.name, str(signal), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    try:
        async with asyncio.timeout(30):
            while not signal.exists():
                if process.returncode is not None:
                    _, error = await process.communicate()
                    pytest.fail(f'owned child exited before write: {error.decode().strip()}')
                await asyncio.sleep(0.05)
        assert json.loads(signal.read_text(encoding='utf-8')) == [ids[0]]
    finally:
        if process.returncode is None:
            process.terminate()
        await asyncio.wait_for(process.communicate(), 10)
    index = HybridMilvusIndex(service.uri, collection=service.name, client=service.client)
    interrupted_ids = await index.all_ids()
    assert interrupted_ids == {ids[0]}
    assert await states(knowledge_rows.database, ids) == before
    async with job_lock(knowledge_rows.database):
        result = await jobs(owned, Embedder(), index).rebuild_done(1)
        assert result['ready']
        assert (await jobs(owned, None, index).verify_done(1))['ready']
    assert await index.all_ids() == set(ids)
    assert await states(knowledge_rows.database, ids) == before
    print(f'owned process recovery: original={ids}, interrupted={sorted(interrupted_ids)}, resumed={sorted(await index.all_ids())}')
