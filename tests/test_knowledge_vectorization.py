import asyncio

import pytest

from app.knowledge.types import ChunkRecord
from tests.ch03_fakes import MemoryKnowledgeRepository, MemoryVectorIndex, RecordingEmbedder


def worker(repo, embedder, index):
    try:
        from app.knowledge.vectorization import PendingVectorizer
    except ImportError:
        pytest.fail('pending vectorizer is missing')
    return PendingVectorizer(repo, embedder, index)


def record(identifier=7):
    return ChunkRecord('运费', '配送费用', '标准配送8元。', section_path='not embedded', id=identifier)


async def test_vectors_only_three_fields_marks_same_id_and_drains_batches():
    repo, embedder, index = MemoryKnowledgeRepository([record(7), record(9)]), RecordingEmbedder(), MemoryVectorIndex()
    assert await worker(repo, embedder, index).run(batch_size=1) == 2
    assert embedder.texts == ['category: 运费\nquestions: 配送费用\nanswer: 标准配送8元。'] * 2
    assert index.ids == {7, 9}
    assert [(row.id, row.vector_id) for row in await repo.get_done([7, 9])] == [(7, '7'), (9, '9')]
    assert await worker(repo, embedder, index).run() == 0


@pytest.mark.parametrize('failure', ['embed', 'upsert', 'mark', 'cancel'])
async def test_failure_keeps_pending_and_replay_upserts_unique_primary_key(failure):
    repo, embedder, index = MemoryKnowledgeRepository([record()]), RecordingEmbedder(), MemoryVectorIndex()
    target = {'embed': embedder, 'upsert': index, 'mark': repo, 'cancel': index}[failure]
    method = {'embed': 'embed', 'upsert': 'upsert', 'mark': 'mark_done', 'cancel': 'upsert'}[failure]
    original = getattr(target, method)
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


@pytest.mark.parametrize('ids', [[8], [], [7, 7], [True]])
async def test_unacknowledged_primary_keys_never_mark_done(ids):
    class BadIndex(MemoryVectorIndex):
        async def upsert(self, rows):
            await super().upsert(rows)
            return ids
    repo = MemoryKnowledgeRepository([record()])
    with pytest.raises(ValueError):
        await worker(repo, RecordingEmbedder(), BadIndex()).run()
    assert await repo.get_done([7]) == []
    assert repo.mark_calls == 0


@pytest.mark.parametrize('identifier', [0, -1, 9223372036854775808, True])
async def test_invalid_mysql_id_never_reaches_embedding_or_mark_done(identifier):
    repo, embedder, index = MemoryKnowledgeRepository([record(identifier)]), RecordingEmbedder(), MemoryVectorIndex()
    with pytest.raises(ValueError):
        await worker(repo, embedder, index).run()
    assert embedder.texts == []
    assert index.ids == set()
    assert repo.mark_calls == 0


@pytest.mark.parametrize('vectors', [[], [[1.0] * 1023], [[True] + [0.0] * 1023], [[float('nan')] * 1024]])
async def test_untrusted_embedder_cannot_write_invalid_vectors(vectors):
    class BadEmbedder:
        async def embed(self, texts):
            return vectors
    repo, index = MemoryKnowledgeRepository([record()]), MemoryVectorIndex()
    with pytest.raises(ValueError):
        await worker(repo, BadEmbedder(), index).run()
    assert index.ids == set()
    assert repo.mark_calls == 0


@pytest.mark.parametrize('batch_size', [0, -1, True, 1.5])
async def test_invalid_batch_size_rejected(batch_size):
    with pytest.raises(ValueError):
        await worker(MemoryKnowledgeRepository([]), RecordingEmbedder(), MemoryVectorIndex()).run(batch_size)


@pytest.mark.parametrize('command', ['init-vectors', 'vectorize-pending'])
@pytest.mark.parametrize('failure', [False, True])
async def test_cli_vector_jobs_share_lock_release_clients_and_database(monkeypatch, command, failure):
    from argparse import Namespace
    from contextlib import asynccontextmanager
    from app.knowledge import cli
    state = {'locked': False, 'closed': [], 'batch_size': None}
    class Database:
        def __init__(self, url): pass
        async def dispose(self): state['closed'].append('database')
    @asynccontextmanager
    async def lock(database):
        state['locked'] = True
        try: yield
        finally: state['locked'] = False
    class Index:
        def __init__(self, uri, **kwargs):
            assert str(uri).rstrip('/') == 'http://127.0.0.1:19530'
            assert kwargs['timeout'] == 3
        async def ensure_collection(self):
            assert state['locked']
            if failure: raise RuntimeError('synthetic failure')
        async def aclose(self): state['closed'].append('index')
    class Embedder:
        def __init__(self, config): pass
        async def aclose(self): state['closed'].append('embedder')
    class Vectorizer:
        def __init__(self, repo, embedder, index): pass
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
