# 统一检索测试只替换外部边界，验证策略、权威正文与有限 JSON 输出。
import importlib.util
import json
from types import SimpleNamespace

import pytest

from app.knowledge.types import ChunkRecord, VectorHit
from app.retrieval.types import QueryPlan, RerankHit
from tests.ch03_fakes import RecordingEmbedder


class Planner:
    # 记录理解次数，用固定标准问法隔离付费模型。
    def __init__(self):
        self.calls = []

    # 标准问法故意省略型号，测试稀疏查询仍保留本轮原话。
    async def plan(self, raw_question):
        self.calls.append(raw_question)
        return QueryPlan(standard='退货规则', expansions=['退款要求'])


class RecallIndex:
    # 保存召回主键和边界调用，禁止任何索引正文进入服务。
    def __init__(self, hits):
        self.hits, self.calls = hits, []

    # 记录策略与分类，模拟 Milvus 有序候选。
    async def recall(self, vector, text, *, strategy, category=None):
        self.calls.append((vector, text, strategy, category))
        return self.hits


class Authority:
    # 保存数据库原文和请求主键，允许模拟缺行、未完成与分类漂移。
    def __init__(self, rows):
        self.rows, self.calls = rows, []

    # 故意逆序返回记录，让服务自己对齐索引顺序并复核完成状态。
    async def get_done(self, ids):
        self.calls.append(ids)
        return [row for row in reversed(self.rows) if row.id in ids]


class Reranker:
    # 配置高阈值，证明通用排序不会提前执行线上证据门槛。
    def __init__(self, hits=()):
        self.hits, self.calls = list(hits), []
        self.settings = SimpleNamespace(rerank_min_score=.99)

    # 记录本轮原话与权威三栏正文，返回位置分数供服务回填。
    async def rank(self, query, documents, *, top_n=10):
        self.calls.append((query, documents, top_n))
        return self.hits


# 在业务断言处报告缺少新功能，避免 RED 只显示模块导入错误。
def service_parts(hits=(), rows=(), rerank_hits=()):
    assert importlib.util.find_spec('app.retrieval.service') is not None, 'unified retrieval service is missing'
    from app.retrieval.service import RetrievalService, faq_payload
    repo, embedder, index = Authority(list(rows)), RecordingEmbedder(), RecallIndex(list(hits))
    planner, reranker = Planner(), Reranker(rerank_hits)
    service = RetrievalService(repo, embedder, index, planner, reranker)
    return service, faq_payload, repo, embedder, index, planner, reranker


async def test_recall_candidates_is_bounded_without_planning_or_finalizing():
    """可复用召回入口只执行完整查询的嵌入和hybrid，重复首项不影响前50唯一项。"""
    service, _, repo, embedder, index, planner, reranker = service_parts(
        [VectorHit(2, .9), VectorHit(2, .8), VectorHit(1, .7),
         *[VectorHit(i, .1) for i in range(3, 70)]])
    candidates = await service.recall_candidates('完整问题', category='售后')
    assert candidates[:2] == [VectorHit(2, .9), VectorHit(1, .7)] and len(candidates) == 50
    assert embedder.texts == ['完整问题'] and index.calls[0][1:] == ('完整问题', 'hybrid', '售后')
    assert repo.calls == planner.calls == reranker.calls == []


# 错误分支、错误查询或错误分数标签都会破坏这四种策略的共同契约。
@pytest.mark.parametrize('strategy,index_strategy,score_kind', [
    ('dense', 'dense', 'cosine'), ('bm25', 'bm25', 'bm25'),
    ('hybrid', 'hybrid', 'rrf'), ('hybrid_rerank', 'hybrid', 'rerank'),
])
async def test_strategies_use_correct_query_and_score_kind(strategy, index_strategy, score_kind):
    row = ChunkRecord('售后', '退货问题', '权威答案', id=7, vectorize_status='done')
    service, payload, repo, embedder, index, planner, reranker = service_parts(
        [VectorHit(7, .8)], [row], [RerankHit(index=0, score=.12)])
    bundle = await service.retrieve('SKU-X9 能退吗', category='售后', strategy=strategy)
    assert bundle.strategy == strategy and planner.calls == ['SKU-X9 能退吗']
    vector, text, actual_strategy, category = index.calls[0]
    assert actual_strategy == index_strategy and category == '售后'
    assert embedder.texts == ([] if strategy == 'bm25' else ['退货规则'])
    assert vector == (None if strategy == 'bm25' else [1.0] + [0.0] * 1023)
    assert text == (None if strategy == 'dense' else '退货规则\n退款要求\nSKU-X9 能退吗')
    assert bundle.matches[0].score_kind == score_kind
    assert bundle.matches[0].score == (.12 if strategy == 'hybrid_rerank' else .8)
    assert payload(bundle)['matches'][0]['answer'] == '权威答案'
    assert len(reranker.calls) == (1 if strategy == 'hybrid_rerank' else 0)


# 同一冻结理解结果用于四策略比较时，服务不能重复请求理解模型。
async def test_four_strategies_share_one_frozen_query_plan():
    service, _, _, _, _, planner, _ = service_parts()
    plan = await planner.plan('SKU-X9 能退吗')
    for strategy in ('dense', 'bm25', 'hybrid', 'hybrid_rerank'):
        bundle = await service.retrieve('SKU-X9 能退吗', strategy=strategy, query_plan=plan)
        assert bundle.query == plan and bundle.matches == []
    assert planner.calls == ['SKU-X9 能退吗']


# 去重、完成状态与分类复核必须发生在权威正文重排前，位置索引不能映射到旧候选。
async def test_rerank_indices_align_authoritative_valid_deduplicated_candidates():
    big_id = 9007199254740993
    rows = [ChunkRecord('售后', '问题一', '答案一', id=big_id, vectorize_status='done'),
            ChunkRecord('售后', '问题二', '答案二', id=4, vectorize_status='done'),
            ChunkRecord('配送', '漂移分类', '不该出现', id=3, vectorize_status='done'),
            ChunkRecord('售后', '待处理', '不该出现', id=2, vectorize_status='pending')]
    hits = [VectorHit(99, .9), VectorHit(big_id, .8), VectorHit(big_id, .7),
            VectorHit(3, .6), VectorHit(2, .5), VectorHit(4, .4)]
    service, payload, repo, _, _, _, reranker = service_parts(
        hits, rows, [RerankHit(index=1, score=.2), RerankHit(index=0, score=.1)])
    bundle = await service.retrieve('原问题', category='售后')
    assert repo.calls == [[99, big_id, 3, 2, 4]]
    assert [hit.id for hit in bundle.candidates] == [99, big_id, 3, 2, 4]
    assert reranker.calls == [('原问题', ['category: 售后\nquestions: 问题一\nanswer: 答案一',
                                      'category: 售后\nquestions: 问题二\nanswer: 答案二'], 10)]
    assert [item.chunk.id for item in bundle.matches] == [4, big_id]
    assert [item.score for item in bundle.matches] == [.2, .1]
    result = payload(bundle)
    assert result['matches'][1]['id'] == big_id and type(result['matches'][1]['id']) is int
    assert result['retrieval'] == {'strategy': 'hybrid_rerank', 'candidate_count': 5, 'match_count': 2}


# 五十条候选只有最终十条正文可被序列化，章节路径保留为证据元数据。
@pytest.mark.parametrize('strategy', ['dense', 'bm25', 'hybrid', 'hybrid_rerank'])
async def test_top_ten_payload_never_serializes_candidate_texts(strategy):
    rows = [ChunkRecord('售后', f'问题{i}', f'专属答案{i}', section_path='政策/退货',
                        id=i, vectorize_status='done') for i in range(1, 51)]
    service, payload, _, _, _, _, _ = service_parts(
        [VectorHit(i, 1 / i) for i in range(1, 51)], rows,
        [RerankHit(index=i, score=1 / (i + 1)) for i in range(10)])
    bundle = await service.retrieve('问题', strategy=strategy)
    result = payload(bundle)
    assert len(bundle.candidates) == 50 and len(bundle.matches) == len(result['matches']) == 10
    assert result['found'] is True and result['matches'][0]['section_path'] == '政策/退货'
    assert set(result['matches'][0]) == {'id', 'question', 'answer', 'category', 'section_path', 'score', 'score_kind'}
    serialized = json.dumps(result, ensure_ascii=False)
    assert '专属答案11' not in serialized and 'candidates' not in result
    assert result['retrieval']['candidate_count'] == 50


# 缺失、pending 与品类漂移导致无合法证据时，不能伪造 found 或启动空重排。
async def test_no_legal_authority_rows_returns_found_false():
    rows = [ChunkRecord('其他', '漂移', '旧文', id=1, vectorize_status='done'),
            ChunkRecord('售后', '未完', '旧文', id=2)]
    service, payload, _, _, _, _, reranker = service_parts(
        [VectorHit(i, .8) for i in (1, 2, 3)], rows)
    result = payload(await service.retrieve('问题', category='售后'))
    assert result == {'found': False, 'matches': [], 'retrieval': {
        'strategy': 'hybrid_rerank', 'candidate_count': 3, 'match_count': 0}}
    assert reranker.calls == []


# 任一外部阶段故障必须传播，不能当成无证据成功结果。
@pytest.mark.parametrize('stage', ['planner', 'embedder', 'index', 'repository', 'reranker'])
async def test_dependency_errors_propagate_without_fallback(stage, monkeypatch):
    service, _, repo, embedder, index, planner, reranker = service_parts(
        [VectorHit(1, .8)], [ChunkRecord('售后', '问', '答', id=1, vectorize_status='done')])
    target, method = {'planner': (planner, 'plan'), 'embedder': (embedder, 'embed'),
                      'index': (index, 'recall'), 'repository': (repo, 'get_done'),
                      'reranker': (reranker, 'rank')}[stage]

    # 仅替换当前外部边界，不改动服务的错误处理。
    async def fail(*args, **kwargs):
        raise RuntimeError('synthetic dependency failure')

    monkeypatch.setattr(target, method, fail)
    with pytest.raises(RuntimeError, match='synthetic dependency failure'):
        await service.retrieve('问题')


# 无效策略与分类必须在模型/索引之前拒绝，避免错误输入造成付费调用。
@pytest.mark.parametrize('kwargs', [{'strategy': 'invalid'}, {'category': 'x' * 256}])
async def test_invalid_arguments_fail_before_dependencies(kwargs):
    service, _, _, embedder, index, planner, _ = service_parts()
    with pytest.raises(ValueError):
        await service.retrieve('问题', **kwargs)
    assert planner.calls == embedder.texts == index.calls == []


@pytest.mark.parametrize('category', ['', ' \t', 7, True, '中' * 256])
async def test_retrieval_category_rejected_before_any_dependency(category):
    """分类不合法时必须早拒，不能调用改写、嵌入、索引或权威仓储。"""
    service, _, repo, embedder, index, planner, reranker = service_parts()
    with pytest.raises(ValueError):
        await service.retrieve('问题', category=category)
    assert planner.calls == embedder.texts == index.calls == repo.calls == reranker.calls == []


@pytest.mark.parametrize('raw', ['', ' \t', None, 7, True, '中' * 513])
async def test_existing_raw_question_guards_precede_all_dependencies(raw):
    """原话为空、非文本或超长时保持现有早拒，不花费模型和索引请求。"""
    from app.core.errors import InputTooLong
    service, _, repo, embedder, index, planner, reranker = service_parts()
    with pytest.raises((ValueError, InputTooLong)):
        await service.retrieve(raw)
    assert planner.calls == embedder.texts == index.calls == repo.calls == reranker.calls == []


@pytest.mark.parametrize('plan', [{}, '伪计划', 7, True])
async def test_existing_injected_plan_guard_precedes_all_dependencies(plan):
    """非法注入计划在改写或召回前拒绝，不能当作冻结的可信计划。"""
    service, _, repo, embedder, index, planner, reranker = service_parts()
    with pytest.raises(ValueError):
        await service.retrieve('问题', query_plan=plan)
    assert planner.calls == embedder.texts == index.calls == repo.calls == reranker.calls == []
