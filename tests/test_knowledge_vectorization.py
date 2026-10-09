# 双写向量化测试，覆盖 pending 批处理、主键确认、失败重跑和客户端清理。
import asyncio

import pytest

from app.knowledge.types import ChunkRecord
from tests.ch03_fakes import MemoryKnowledgeRepository, MemoryVectorIndex, RecordingEmbedder


# 用指定仓储、嵌入器与索引构造真实待处理向量化任务。
def worker(repo, embedder, index):
    try:
        from app.knowledge.vectorization import PendingVectorizer
    except ImportError:
        pytest.fail('pending vectorizer is missing')
    return PendingVectorizer(repo, embedder, index)


# 构造带 SQL 主键和非嵌入元数据的待处理知识记录。
def record(identifier=7):
    return ChunkRecord('运费', '配送费用', '标准配送8元。', section_path='not embedded', id=identifier)


# 验证只嵌入三个权威字段，向量主键与 SQL 编号相同，并逐批处理到清空。
async def test_vectors_only_three_fields_marks_same_id_and_drains_batches():
    repo, embedder, index = MemoryKnowledgeRepository([record(7), record(9)]), RecordingEmbedder(), MemoryVectorIndex()
    assert await worker(repo, embedder, index).run(batch_size=1) == 2
    assert embedder.texts == ['category: 运费\nquestions: 配送费用\nanswer: 标准配送8元。'] * 2
    assert index.ids == {7, 9}
    assert [(row.id, row.vector_id) for row in await repo.get_done([7, 9])] == [(7, '7'), (9, '9')]
    assert await worker(repo, embedder, index).run() == 0


# 验证嵌入、写向量、标记或取消故障后仍待处理，重放只覆盖同一主键。
@pytest.mark.parametrize('failure', ['embed', 'upsert', 'mark', 'cancel'])
async def test_failure_keeps_pending_and_replay_upserts_unique_primary_key(failure):
    repo, embedder, index = MemoryKnowledgeRepository([record()]), RecordingEmbedder(), MemoryVectorIndex()
    target = {'embed': embedder, 'upsert': index, 'mark': repo, 'cancel': index}[failure]
    method = {'embed': 'embed', 'upsert': 'upsert', 'mark': 'mark_done', 'cancel': 'upsert'}[failure]
    original = getattr(target, method)
    # 按阶段注入异常；写向量或取消场景先写后失败，模拟确认丢失并检验幂等重放。
    async def fail(*args):
        if failure in ('upsert', 'cancel'):
            await original(*args)  # service wrote, acknowledgement was lost
        raise asyncio.CancelledError() if failure == 'cancel' else RuntimeError('synthetic interruption')
    setattr(target, method, fail)
    with pytest.raises(asyncio.CancelledError if failure == 'cancel' else RuntimeError):
        await worker(repo, embedder, index).run()
    assert await repo.get_done([7]) == []
    setattr(target, method, original)
    assert await worker(repo, embedder, index).run() == 1
    assert index.ids == {7}
    assert (await repo.get_done([7]))[0].vector_id == '7'
    assert index.upsert_calls == (1 if failure == 'embed' else 2)


# 验证返回缺失、错配、重复或布尔主键的写入确认不能触发 SQL 完成标记。
@pytest.mark.parametrize('ids', [[8], [], [7, 7], [True]])
async def test_unacknowledged_primary_keys_never_mark_done(ids):
    class BadIndex(MemoryVectorIndex):
        # 先模拟成功写入再返回非法主键确认，构造不可信索引响应。
        async def upsert(self, rows):
            await super().upsert(rows)
            return ids
    repo = MemoryKnowledgeRepository([record()])
    with pytest.raises(ValueError):
        await worker(repo, RecordingEmbedder(), BadIndex()).run()
    assert await repo.get_done([7]) == []
    assert repo.mark_calls == 0


# 验证非法或越界 SQL 主键在嵌入、向量写入与完成提交前被拒绝。
@pytest.mark.parametrize('identifier', [0, -1, 9223372036854775808, True])
async def test_invalid_mysql_id_never_reaches_embedding_or_mark_done(identifier):
    repo, embedder, index = MemoryKnowledgeRepository([record(identifier)]), RecordingEmbedder(), MemoryVectorIndex()
    with pytest.raises(ValueError):
        await worker(repo, embedder, index).run()
    assert embedder.texts == []
    assert index.ids == set()
    assert repo.mark_calls == 0


# 验证不可信嵌入器的空批次、维度错误、布尔或 NaN 向量不能写入索引。
@pytest.mark.parametrize('vectors', [[], [[1.0] * 1023], [[True] + [0.0] * 1023], [[float('nan')] * 1024]])
async def test_untrusted_embedder_cannot_write_invalid_vectors(vectors):
    class BadEmbedder:
        # 返回参数化非法向量，绕过云适配器以检验作业自身的防御校验。
        async def embed(self, texts):
            return vectors
    repo, index = MemoryKnowledgeRepository([record()]), MemoryVectorIndex()
    with pytest.raises(ValueError):
        await worker(repo, BadEmbedder(), index).run()
    assert index.ids == set()
    assert repo.mark_calls == 0


# 验证批次数量拒绝零、负数、布尔值和小数。
@pytest.mark.parametrize('batch_size', [0, -1, True, 1.5])
async def test_invalid_batch_size_rejected(batch_size):
    with pytest.raises(ValueError):
        await worker(MemoryKnowledgeRepository([]), RecordingEmbedder(), MemoryVectorIndex()).run(batch_size)
