import pytest
from dataclasses import replace
from tests.test_hybrid_jobs import Repository, Embedder, Index, record


class SelectedRepository(Repository):
    async def pending_by_ids(self, ids):
        return [self.rows[i] for i in ids if i in self.rows and self.rows[i].vectorize_status == 'pending']
    async def get_done(self, ids):
        return [self.rows[i] for i in ids if i in self.rows and self.rows[i].vectorize_status == 'done']


async def test_publication_does_not_consume_unrelated_pending():
    from app.knowledge.hybrid_jobs import HybridKnowledgeJobs
    repo, embedder, index = SelectedRepository([record(3, 'pending'), record(8, 'pending')]), Embedder(), Index()
    jobs = HybridKnowledgeJobs(repo, embedder, index)
    assert await jobs.vectorize_ids([3]) == 1
    assert set(index.rows) == {3} and repo.rows[8].vectorize_status == 'pending'
    assert '问题3' in embedder.texts[0] and all('问题8' not in text for text in embedder.texts)
    assert await jobs.vectorize_ids([3]) == 0
    assert len(embedder.texts) == 1


@pytest.mark.parametrize('damage', ['ack', 'readback', 'embedding'])
async def test_publication_failure_keeps_original_pending_id(damage):
    from app.knowledge.hybrid_jobs import HybridKnowledgeJobs
    repo = SelectedRepository([record(3, 'pending')])
    index = Index(false_ack=damage=='ack', bad_readback=damage=='readback')
    class Flaky(Embedder):
        async def embed(self, texts):
            if damage == 'embedding': raise TimeoutError()
            return await super().embed(texts)
    with pytest.raises((TimeoutError, ValueError)):
        await HybridKnowledgeJobs(repo, Flaky(), index).vectorize_ids([3])
    assert not repo.marked and repo.rows[3].vectorize_status == 'pending'


async def test_runtime_starts_and_closes_publication_before_resources(monkeypatch):
    from app.flywheel.runtime import FlywheelRuntime
    from tests.test_flywheel_processing import JsonModel
    from tests.fakes import fake_settings
    from contextlib import AsyncExitStack
    events = []
    runtime = FlywheelRuntime(object(), JsonModel([]), fake_settings(), publication_jobs=object())
    class Worker:
        def start(self): events.append('publication-start')
        async def close(self, timeout_seconds=30): events.append('publication-close')
    runtime.publication_worker = Worker()
    runtime._resources = AsyncExitStack()
    runtime._resources.callback(lambda: events.append('resources-close'))
    # Isolate the unrelated normalization loop, not publication behavior.
    monkeypatch.setattr(runtime.worker, 'start', lambda: None)
    runtime.start()
    await runtime.close()
    assert events == ['publication-start', 'publication-close', 'resources-close']


async def test_runtime_keeps_resource_ownership_if_publication_shutdown_is_pending():
    from app.flywheel.runtime import FlywheelRuntime
    from tests.test_flywheel_processing import JsonModel
    from tests.fakes import fake_settings
    from contextlib import AsyncExitStack
    events = []
    runtime = FlywheelRuntime(object(), JsonModel([]), fake_settings(), publication_jobs=object())
    class Worker:
        async def close(self, timeout_seconds=30): raise RuntimeError('pending controlled cleanup')
    runtime.publication_worker = Worker()
    runtime._resources = AsyncExitStack()
    runtime._resources.callback(lambda: events.append('resources-close'))
    with pytest.raises(RuntimeError): await runtime.close()
    assert not events and runtime._resources is not None
