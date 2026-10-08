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


# 验证索引初始化与向量化命令共享任务锁，成功或失败均释放所持资源。
@pytest.mark.parametrize('command', ['init-vectors', 'vectorize-pending'])
@pytest.mark.parametrize('failure', [False, True])
async def test_cli_vector_jobs_share_lock_release_clients_and_database(monkeypatch, command, failure):
    from argparse import Namespace
    from contextlib import asynccontextmanager
    from app.knowledge import cli
    state = {'locked': False, 'closed': [], 'batch_size': None}
    class Database:
        # 接受数据库配置而不创建连接，隔离命令行编排测试。
        def __init__(self, url): pass
        # 记录数据库关闭，核对命令退出时的释放。
        async def dispose(self): state['closed'].append('database')
    # 标记任务锁的进入与退出，供索引准备和向量化检查持锁状态。
    @asynccontextmanager
    async def lock(database):
        state['locked'] = True
        try: yield
        finally: state['locked'] = False
    class Index:
        # 核对 Milvus 端点与超时传递，同时避免真实服务连接。
        def __init__(self, uri, **kwargs):
            assert str(uri).rstrip('/') == 'http://127.0.0.1:19530'
            assert kwargs['timeout'] == 3
        # 确认集合准备发生在锁内，并按场景注入准备故障。
        async def ensure_collection(self):
            assert state['locked']
            if failure: raise RuntimeError('synthetic failure')
        # 记录索引关闭，以验证失败路径资源回收。
        async def aclose(self): state['closed'].append('index')
    class Embedder:
        # 接受嵌入配置而不创建云客户端。
        def __init__(self, config): pass
        # 记录嵌入关闭，以核对仅向量化命令持有该资源。
        async def aclose(self): state['closed'].append('embedder')
    class Vectorizer:
        # 接受向量化依赖，替代真实批次工作。
        def __init__(self, repo, embedder, index): pass
        # 确认向量化持锁并记录命令传入的批次数量，支持作业故障。
        async def run(self, batch_size=20):
            assert state['locked']
            state['batch_size'] = batch_size
            if failure: raise RuntimeError('synthetic failure')
            return 1
    monkeypatch.setattr(cli, 'Database', Database)
    monkeypatch.setattr(cli, 'load_settings', lambda: Namespace(database_url='synthetic', milvus_uri='http://127.0.0.1:19530', milvus_timeout_seconds=3))
    monkeypatch.setattr(cli, 'job_lock', lock)
    monkeypatch.setattr(cli, 'MilvusIndex', Index, raising=False)
    monkeypatch.setattr(cli, 'SiliconFlowEmbedder', Embedder, raising=False)
    monkeypatch.setattr(cli, 'PendingVectorizer', Vectorizer, raising=False)
    args = cli.parser().parse_args([command] + (['--batch-size', '2'] if command == 'vectorize-pending' else []))
    if failure:
        with pytest.raises(RuntimeError): await cli.run(args)
    else:
        await cli.run(args)
    assert not state['locked']
    assert set(state['closed']) == ({'database', 'index', 'embedder'} if command == 'vectorize-pending' else {'database', 'index'})
    if command == 'vectorize-pending': assert state['batch_size'] == 2
