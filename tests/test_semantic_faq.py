# 保留旧 Dense 投影入口，并验证统一 FAQ 的故障、零重试和取消传播。
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


# 旧 Dense 故障样例通过真实统一服务复用受控依赖，线上工具不再调用旧 search。
def connect_retriever(faq):
    from app.retrieval.service import RetrievalService
    from app.retrieval.types import QueryPlan
    class Planner:
        # 受控查询计划避免云端请求，仍让真实服务读取完整原话。
        async def plan(self, question):
            return QueryPlan(standard=question, expansions=[])
    class Index:
        # 复用旧故障索引作为受控召回源，不加入生产 Dense 回退。
        async def recall(self, vector, text, **kwargs):
            return await faq.index.search(vector, limit=3)
    class Reranker:
        # 故障样例不得到达正常重排阶段。
        async def rank(self, *args, **kwargs):
            raise AssertionError('failed retrieval reached reranker')
    faq.retriever = RetrievalService(faq.knowledge, faq.embedder, Index(), Planner(), Reranker())
    return faq


class SearchIndex:
    # 配置向量命中或检索故障，并记录查询参数供断言。
    def __init__(self, hits=(), failure=None):
        self.hits, self.failure, self.calls = list(hits), failure, []

    # 记录向量与数量，按场景返回命中或抛出预设索引故障。
    async def search(self, vector, limit=3):
        self.calls.append((vector, limit))
        if self.failure:
            raise self.failure
        return self.hits[:limit]


class NoSQL:
    # 任何 SQL 会话访问都立即失败，检测无向量命中时的多余查询。
    def session(self):
        raise AssertionError('must not query SQL without dense hits')


# 确认 FAQ 支持稠密检索依赖注入，并构造禁止无命中 SQL 访问的仓储。
def make_faq(embedder, index):
    # 旧实现应在业务断言处失败，避免因为测试替身参数不兼容而报 TypeError。
    import inspect
    assert 'embedder' in inspect.signature(FAQRepository).parameters, 'FAQ has no dense dependencies'
    return FAQRepository(NoSQL(), embedder, index)


# 验证稠密命中映射为兼容的 FAQ 字段，按相似度排序并过滤未完成或缺失行。
async def test_dense_hits_project_old_fields_in_similarity_order(monkeypatch):
    embedder = RecordingEmbedder()
    index = SearchIndex([VectorHit(92, .9), VectorHit(14, .8), VectorHit(53, .7)])
    requested = []

    # 返回与命中顺序不同的完成记录并省略第三条，模拟 SQL 排序与完成状态过滤。
    async def get_done(repo, ids):
        requested.append(ids)
        # SQL 返回顺序与相似度顺序不同，第三个命中尚待向量化或原文缺失，需过滤。
        return [ChunkRecord('售后', '退货规则', '七天', id=14, vectorize_status='done'),
                ChunkRecord('配送', '运费规则', '八元', id=92, vectorize_status='done')]

    monkeypatch.setattr(KnowledgeRepository, 'get_done', get_done)
    result = await make_faq(embedder, index).search('邮费是多少', limit=10)
    assert result == [{'id': 92, 'question': '运费规则', 'answer': '八元', 'category': '配送'},
                      {'id': 14, 'question': '退货规则', 'answer': '七天', 'category': '售后'}]
    assert embedder.texts == ['邮费是多少']
    assert requested == [[92, 14, 53]]
    assert index.calls == [([1.0] + [0.0] * 1023, 3)]


# 验证稠密检索数量最多三条，空命中直接返回且不查询 SQL。
@pytest.mark.parametrize('limit', [1, 2, 3, 10])
async def test_dense_limit_caps_at_three_and_empty_hits_never_query_sql(limit):
    index = SearchIndex()
    assert await make_faq(RecordingEmbedder(), index).search(' \t邮费\n ', limit) == []
    assert index.calls[0][1] == min(limit, 3)


# 验证直接检索的非法关键词或数量在嵌入与索引调用前被拒绝。
@pytest.mark.parametrize('keyword,limit', [('', 3), ('x' * 129, 3), (1, 3), ('x', 0), ('x', True), ('x', 1.5)])
async def test_bad_direct_arguments_do_not_embed(keyword, limit):
    embedder, index = RecordingEmbedder(), SearchIndex()
    with pytest.raises(ValueError):
        await make_faq(embedder, index).search(keyword, limit)
    assert embedder.texts == [] and index.calls == []


# 验证嵌入、索引或 SQL 任一故障转换为安全工具错误，不回退字面查询。
@pytest.mark.parametrize('stage', ['embed', 'vector', 'sql'])
async def test_dense_failure_is_tool_error_without_like_fallback(monkeypatch, stage):
    class Embedder(RecordingEmbedder):
        # 仅在指定阶段注入嵌入故障，其余场景沿用固定向量以定位故障边界。
        async def embed(self, texts):
            if stage == 'embed':
                raise RuntimeError('synthetic private provider details')
            return await super().embed(texts)

    # 在知识回填时抛出私密数据库故障，检验工具层脱敏。
    async def failed_sql(repo, ids):
        raise RuntimeError('synthetic private database details')

    monkeypatch.setattr(KnowledgeRepository, 'get_done', failed_sql)
    index = SearchIndex([VectorHit(1, .9)], RuntimeError('synthetic vector failure') if stage == 'vector' else None)
    faq = connect_retriever(make_faq(Embedder(), index))
    registry = build_registry(faq, TicketStub(), ToolContext('10', 42, '邮费是多少'))
    outcome = await ToolExecutor().execute(ToolCall('faq', 'query_faq', {'keyword': '邮费是多少'}), registry)
    assert outcome.content == {'error': {'code': 'tool_execution_error', 'message': '工具执行失败。'}}
    assert outcome.status == 'error' and outcome.attempts == 1
    assert len(index.calls) == (0 if stage == 'embed' else 1)


class WaitingEmbedder:
    # 创建嵌入启动信号并初始化调用、取消计数，用于可控超时与取消测试。
    def __init__(self):
        self.started, self.cancelled, self.calls = asyncio.Event(), 0, 0

    # 发出启动信号后永久等待，取消时计数以核对每次检索都已停止。
    async def embed(self, texts):
        self.calls += 1
        self.started.set()
        try:
            await asyncio.Event().wait()
        finally:
            self.cancelled += 1


# 构造实际工具聊天服务，使用短超时和指定重试上限处理 FAQ 查询。
def chat_service(faq, retries):
    model = ToolModel(selected_call('query_faq', {'keyword': '邮费是多少'}))
    faq = connect_retriever(faq)
    settings = fake_settings(tool_timeout_seconds=.01, tool_max_retries=retries, faq_timeout_seconds=.01)
    service = ToolChatService(model, ToolRepository(),
        lambda ctx: build_registry(faq, TicketStub(), ctx), ConversationLocks(), settings)
    return service, model


# FAQ 超时取消本次检索且始终零重试，不进入自由文本最终回答。
@pytest.mark.parametrize('retries,attempts', [(0, 1), (1, 1)])
async def test_faq_timeout_stops_retrieval_without_retry_or_free_answer(retries, attempts):
    embedder, index = WaitingEmbedder(), SearchIndex()
    service, model = chat_service(make_faq(embedder, index), retries)
    events = await collect(service, await service.prepare('10', '邮费是多少'))
    assert embedder.calls == embedder.cancelled == attempts
    assert index.calls == []
    assert model.selection_requests == 1 and model.final_stream_requests == 0
    assert events[-1].event == 'error' and events[-1].data['code'] == 'tool_timeout'


# 验证外部取消嵌入会传播取消、释放锁，且不再检索向量或启动最终模型。
async def test_outer_cancel_during_embedding_has_no_vector_sql_or_model_retry():
    embedder, index = WaitingEmbedder(), SearchIndex()
    service, model = chat_service(make_faq(embedder, index), 1)
    service.executor.overrides['query_faq'] = (2, 0)
    task = asyncio.create_task(collect(service, await service.prepare('10', '邮费是多少')))
    await asyncio.wait_for(embedder.started.wait(), 1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert embedder.calls == embedder.cancelled == 1
    assert index.calls == []
    assert model.selection_requests == 1 and model.final_stream_requests == 0
    service.locks.acquire('10').release()


# 新接口必须传递完整原话和分类并保持旧三个位置参数可用。
async def test_retrieve_adapter_uses_original_question_and_category():
    from tests.test_retrieval_service import service_parts
    service, _, _, embedder, index, planner, _ = service_parts(
        [VectorHit(8, .7)], [ChunkRecord('售后', '能退吗', '权威答案', id=8, vectorize_status='done')], [])
    # 本测试使用不重排的服务代理，验证 adapter 的默认调用而不引入真实云端。
    class Retriever:
        # adapter 必须使用原问题并传递品类，不允许只用抽取关键词检索。
        async def retrieve(self, raw_question, *, category=None):
            return await service.retrieve(raw_question, category=category, strategy='hybrid')

    import inspect
    assert 'retriever' in inspect.signature(FAQRepository).parameters, 'FAQ adapter is missing'
    faq = FAQRepository(NoSQL(), embedder, index, retriever=Retriever())
    result = await faq.retrieve('能退吗', raw_question='SKU-X9 能退吗', category='售后')
    assert result['found'] is True and result['matches'][0]['answer'] == '权威答案'
    assert planner.calls == ['SKU-X9 能退吗'] and index.calls[0][3] == '售后'


# 缺少新依赖时必须明确失败，不能静默使用旧 Dense 或 LIKE。
async def test_retrieve_without_retriever_does_not_use_legacy_search():
    embedder, index = RecordingEmbedder(), SearchIndex()
    faq = make_faq(embedder, index)
    assert hasattr(faq, 'retrieve'), 'FAQ adapter is missing'
    with pytest.raises(RuntimeError, match='retriever'):
        await faq.retrieve('邮费', raw_question='邮费是多少')
    assert embedder.texts == index.calls == []


# keyword 仍须是原话连续片段，非法长度或来源不能触发新服务。
@pytest.mark.parametrize('keyword,raw_question', [('', '问题'), ('x' * 129, 'x' * 129),
                                                  ('能退吗', '多久能退款'), (1, '问题')])
async def test_retrieve_keyword_contract_rejects_invalid_input(keyword, raw_question):
    class Retriever:
        # 任一非法输入进入依赖都是 adapter 的回归。
        async def retrieve(self, *args, **kwargs):
            raise AssertionError('invalid input reached retriever')

    import inspect
    assert 'retriever' in inspect.signature(FAQRepository).parameters, 'FAQ adapter is missing'
    faq = FAQRepository(NoSQL(), RecordingEmbedder(), SearchIndex(), retriever=Retriever())
    with pytest.raises(ValueError):
        await faq.retrieve(keyword, raw_question=raw_question)


# 新 adapter 不能将连接故障转为 found=false。
async def test_retrieve_adapter_propagates_dependency_failure():
    class Retriever:
        # 模拟新服务的连接故障并要求直接传播。
        async def retrieve(self, *args, **kwargs):
            raise RuntimeError('synthetic retrieval failure')

    import inspect
    assert 'retriever' in inspect.signature(FAQRepository).parameters, 'FAQ adapter is missing'
    faq = FAQRepository(NoSQL(), RecordingEmbedder(), SearchIndex(), retriever=Retriever())
    with pytest.raises(RuntimeError, match='synthetic retrieval failure'):
        await faq.retrieve('邮费', raw_question='邮费是多少')
