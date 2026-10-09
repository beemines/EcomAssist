# 混合作业的状态恢复与切换核验；替身只隔离数据库和外部嵌入/索引服务。
from dataclasses import replace

import pytest

from app.knowledge.types import ChunkRecord


def jobs(repository, embedder, index):
    try:
        from app.knowledge.hybrid_jobs import HybridKnowledgeJobs
    except ImportError:
        pytest.fail('hybrid knowledge jobs are missing')
    return HybridKnowledgeJobs(repository, embedder, index)


def record(identifier, status='done'):
    return ChunkRecord('耳机', f'问题{identifier}', f'答案{identifier}', id=identifier,
                       vector_id=str(identifier) if status == 'done' else None, vectorize_status=status)


class Repository:
    def __init__(self, rows):
        self.rows = {row.id: row for row in rows}
        self.marked = []

    async def done_page(self, *, after_id=0, limit=20):
        return [row for identifier, row in sorted(self.rows.items())
                if identifier > after_id and row.vectorize_status == 'done'][:limit]

    async def pending(self, limit=20):
        return [row for _, row in sorted(self.rows.items()) if row.vectorize_status == 'pending'][:limit]

    async def mark_done(self, ids):
        self.marked.extend(ids)
        for identifier in ids:
            self.rows[identifier] = replace(self.rows[identifier], vectorize_status='done', vector_id=str(identifier))


class Embedder:
    def __init__(self):
        self.texts = []

    async def embed(self, texts):
        self.texts.extend(texts)
        return [[0.1] * 1024 for _ in texts]


class Index:
    def __init__(self, *, interrupt_at=None, false_ack=False, bad_readback=False):
        self.rows = {}
        self.calls = 0
        self.interrupt_at = interrupt_at
        self.false_ack = false_ack
        self.bad_readback = bad_readback

    async def upsert(self, rows):
        self.calls += 1
        if self.calls == self.interrupt_at:
            raise RuntimeError('controlled batch interruption')
        self.rows.update({row.id: row for row in rows})
        return [999] if self.false_ack else [row.id for row in rows]

    async def get_rows(self, ids):
        return [self.rows[identifier] for identifier in ids if identifier in self.rows]

    async def verify_rows(self, rows):
        if self.bad_readback or await self.get_rows([row.id for row in rows]) != rows:
            raise ValueError('readback mismatch')
        # 真实公开接口成功返回 None。

    async def all_ids(self):
        return set(self.rows)


async def test_rebuild_covers_done_without_promoting_pending():
    repo, embedder, index = Repository([record(3), record(8), record(12, 'pending')]), Embedder(), Index()
    result = await jobs(repo, embedder, index).rebuild_done(1)
    assert result == dict(ready=True, mysql_count=2, vector_count=2, missing_ids=[], extra_ids=[], mismatched_ids=[])
    assert await index.all_ids() == {3, 8}
    assert repo.rows[12].vectorize_status == 'pending' and repo.rows[12].vector_id is None
    assert repo.marked == []
    assert index.rows[3].text == 'category: 耳机\nquestions: 问题3\nanswer: 答案3'
    assert index.rows[3].category == '耳机'
    assert len(embedder.texts) == 2


async def test_interrupted_rebuild_resumes_with_same_primary_keys():
    repo, index = Repository([record(3), record(8), record(15)]), Index(interrupt_at=2)
    worker = jobs(repo, Embedder(), index)
    with pytest.raises(RuntimeError, match='interruption'):
        await worker.rebuild_done(1)
    assert await index.all_ids() == {3}
    assert (await worker.rebuild_done(1))['ready']
    assert await index.all_ids() == {3, 8, 15}
    assert repo.marked == []


@pytest.mark.parametrize('failure', ['false_ack', 'bad_readback'])
async def test_pending_is_not_promoted_without_ack_and_readback(failure):
    repo, index = Repository([record(5, 'pending')]), Index(**{failure: True})
    with pytest.raises(ValueError):
        await jobs(repo, Embedder(), index).vectorize_pending()
    assert repo.rows[5].vectorize_status == 'pending' and repo.marked == []


async def test_pending_write_recovers_when_status_commit_fails():
    class CommitFaultRepository(Repository):
        async def mark_done(self, ids):
            if not self.marked:
                self.marked.append('failed')
                raise RuntimeError('controlled commit interruption')
            await super().mark_done(ids)
    repo, index = CommitFaultRepository([record(5, 'pending')]), Index()
    worker = jobs(repo, Embedder(), index)
    with pytest.raises(RuntimeError, match='commit interruption'):
        await worker.vectorize_pending()
    assert await index.all_ids() == {5} and repo.rows[5].vectorize_status == 'pending'
    assert await worker.vectorize_pending() == 1
    assert await index.all_ids() == {5} and repo.rows[5].vectorize_status == 'done'


@pytest.mark.parametrize('damage,want', [
    ('wrong_id', dict(missing_ids=[3], extra_ids=[99], mismatched_ids=[])),
    ('text', dict(missing_ids=[], extra_ids=[], mismatched_ids=[3])),
    ('category', dict(missing_ids=[], extra_ids=[], mismatched_ids=[3])),
    ('extra', dict(missing_ids=[], extra_ids=[99], mismatched_ids=[])),
    ('dimension', dict(missing_ids=[], extra_ids=[], mismatched_ids=[3])),
    ('nan', dict(missing_ids=[], extra_ids=[], mismatched_ids=[3])),
])
async def test_verification_rejects_wrong_ids_fields_or_dense_values_without_embedding(damage, want):
    repo, index = Repository([record(3)]), Index()
    await jobs(repo, Embedder(), index).rebuild_done()
    row = index.rows[3]
    if damage == 'wrong_id':
        index.rows = {99: replace(row, id=99)}
    elif damage == 'extra':
        index.rows[99] = replace(row, id=99)
    elif damage in ('text', 'category'):
        index.rows[3] = replace(row, **{damage: '错误值'})
    elif damage == 'dimension':
        row.embedding.pop()
    else:
        row.embedding[0] = float('nan')
    result = await jobs(repo, None, index).verify_done(1)
    assert result == dict(ready=False, mysql_count=1, vector_count=len(index.rows), **want)


@pytest.mark.parametrize('method', ['rebuild_done', 'vectorize_pending', 'verify_done'])
@pytest.mark.parametrize('batch_size', [0, -1, True, 1.5])
async def test_invalid_batch_size_is_rejected_before_external_work(method, batch_size):
    with pytest.raises(ValueError):
        await getattr(jobs(Repository([]), None, Index()), method)(batch_size)
