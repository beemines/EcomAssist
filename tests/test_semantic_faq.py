import asyncio
import pytest

from app.knowledge.types import ChunkRecord, VectorHit
from app.repositories.faq import FAQRepository
from app.repositories.knowledge import KnowledgeRepository
from app.tools.executor import ToolExecutor
from app.tools.registry import build_registry
from app.tools.types import ToolCall, ToolContext
from tests.ch03_fakes import RecordingEmbedder
from tests.test_business_tools import TicketStub
from tests.tool_fakes import ToolModel, ToolRepository, collect, selected_call
from tests.fakes import fake_settings
from app.core.tool_chat import ToolChatService
from app.core.conversation_locks import ConversationLocks


class SearchIndex:
    def __init__(self, hits=(), failure=None):
        self.hits, self.failure, self.calls = list(hits), failure, []

    async def search(self, vector, limit=3):
        self.calls.append((vector, limit))
        if self.failure:
            raise self.failure
        return self.hits[:limit]


class NoSQL:
    def session(self):
        raise AssertionError('must not query SQL without dense hits')


def make_faq(embedder, index):
    # Give the original implementation a deliberate assertion RED, not TypeError.
    import inspect
    assert 'embedder' in inspect.signature(FAQRepository).parameters, 'FAQ has no dense dependencies'
    return FAQRepository(NoSQL(), embedder, index)


async def test_dense_hits_project_old_fields_in_similarity_order(monkeypatch):
    embedder = RecordingEmbedder()
    index = SearchIndex([VectorHit(92, .9), VectorHit(14, .8), VectorHit(53, .7)])
    requested = []

    async def get_done(repo, ids):
        requested.append(ids)
        # SQL ordering differs; third hit is pending or absent and is filtered.
        return [ChunkRecord('售后', '退货规则', '七天', id=14, vectorize_status='done'),
                ChunkRecord('配送', '运费规则', '八元', id=92, vectorize_status='done')]

    monkeypatch.setattr(KnowledgeRepository, 'get_done', get_done)
    result = await make_faq(embedder, index).search('邮费是多少', limit=10)
    assert result == [{'id': 92, 'question': '运费规则', 'answer': '八元', 'category': '配送'},
                      {'id': 14, 'question': '退货规则', 'answer': '七天', 'category': '售后'}]
    assert embedder.texts == ['邮费是多少']
    assert requested == [[92, 14, 53]]
    assert index.calls == [([1.0] + [0.0] * 1023, 3)]


@pytest.mark.parametrize('limit', [1, 2, 3, 10])
async def test_dense_limit_caps_at_three_and_empty_hits_never_query_sql(limit):
    index = SearchIndex()
    assert await make_faq(RecordingEmbedder(), index).search(' \t邮费\n ', limit) == []
    assert index.calls[0][1] == min(limit, 3)


@pytest.mark.parametrize('keyword,limit', [('', 3), ('x' * 129, 3), (1, 3), ('x', 0), ('x', True), ('x', 1.5)])
async def test_bad_direct_arguments_do_not_embed(keyword, limit):
    embedder, index = RecordingEmbedder(), SearchIndex()
    with pytest.raises(ValueError):
        await make_faq(embedder, index).search(keyword, limit)
    assert embedder.texts == [] and index.calls == []


@pytest.mark.parametrize('stage', ['embed', 'vector', 'sql'])
async def test_dense_failure_is_tool_error_without_like_fallback(monkeypatch, stage):
    class Embedder(RecordingEmbedder):
        async def embed(self, texts):
            if stage == 'embed':
                raise RuntimeError('synthetic private provider details')
            return await super().embed(texts)

    async def failed_sql(repo, ids):
        raise RuntimeError('synthetic private database details')

    monkeypatch.setattr(KnowledgeRepository, 'get_done', failed_sql)
    index = SearchIndex([VectorHit(1, .9)], RuntimeError('synthetic vector failure') if stage == 'vector' else None)
    faq = make_faq(Embedder(), index)
    registry = build_registry(faq, TicketStub(), ToolContext('10', 42, '邮费是多少'))
    outcome = await ToolExecutor().execute(ToolCall('faq', 'query_faq', {'keyword': '邮费是多少'}), registry)
    assert outcome.content == {'error': {'code': 'tool_execution_error', 'message': '工具执行失败。'}}
    assert outcome.status == 'error' and outcome.attempts == 1
    assert len(index.calls) == (0 if stage == 'embed' else 1)


class WaitingEmbedder:
    def __init__(self):
        self.started, self.cancelled, self.calls = asyncio.Event(), 0, 0

    async def embed(self, texts):
        self.calls += 1
        self.started.set()
        try:
            await asyncio.Event().wait()
        finally:
            self.cancelled += 1


def chat_service(faq, retries):
    model = ToolModel(selected_call('query_faq', {'keyword': '邮费是多少'}))
    settings = fake_settings(tool_timeout_seconds=.01, tool_max_retries=retries)
    service = ToolChatService(model, ToolRepository(),
        lambda ctx: build_registry(faq, TicketStub(), ctx), ConversationLocks(), settings)
    return service, model


@pytest.mark.parametrize('retries,attempts', [(0, 1), (1, 2)])
async def test_tool_timeout_stops_each_retrieval_and_preserves_bounded_retry(retries, attempts):
    embedder, index = WaitingEmbedder(), SearchIndex()
    service, model = chat_service(make_faq(embedder, index), retries)
    events = await collect(service, await service.prepare('10', '邮费是多少'))
    assert embedder.calls == embedder.cancelled == attempts
    assert index.calls == []
    assert model.selection_requests == model.final_stream_requests == 1
    assert any(event.data.get('status') == 'error' for event in events)
    assert events[-1].event == 'done'
    assert 'tool_timeout' in model.final_input[-1].content


async def test_outer_cancel_during_embedding_has_no_vector_sql_or_model_retry():
    embedder, index = WaitingEmbedder(), SearchIndex()
    service, model = chat_service(make_faq(embedder, index), 1)
    service.executor.timeout_seconds = 2
    task = asyncio.create_task(collect(service, await service.prepare('10', '邮费是多少')))
    await asyncio.wait_for(embedder.started.wait(), 1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert embedder.calls == embedder.cancelled == 1
    assert index.calls == []
    assert model.selection_requests == 1 and model.final_stream_requests == 0
    service.locks.acquire('10').release()
