# 统一检索组合单轮查询理解、服务端召回、MySQL 权威回填和可选重排。
from typing import Literal

from app.core.errors import InputTooLong
from app.knowledge.types import Embedder, embedding_text, validate_text
from app.repositories.knowledge import KnowledgeRepository
from app.retrieval.milvus import HybridMilvusIndex
from app.retrieval.query import QueryPlanner
from app.retrieval.rerank import SiliconFlowReranker
from app.retrieval.types import QueryPlan, RetrievalBundle, ScoredChunk


class RetrievalService:
    # 只组合调用方管理的依赖，不创建客户端或改变其生命周期。
    def __init__(self, repository: KnowledgeRepository, embedder: Embedder,
                 index: HybridMilvusIndex, planner: QueryPlanner, reranker: SiliconFlowReranker):
        self.repository, self.embedder, self.index = repository, embedder, index
        self.planner, self.reranker = planner, reranker

    # 单轮仅理解一次；冻结计划用于公平比较策略，任何依赖故障或取消直接传播。
    async def retrieve(self, raw_question: str, *, category: str | None = None,
                       strategy: Literal['dense', 'bm25', 'hybrid', 'hybrid_rerank'] = 'hybrid_rerank',
                       query_plan: QueryPlan | None = None) -> RetrievalBundle:
        if strategy not in ('dense', 'bm25', 'hybrid', 'hybrid_rerank'):
            raise ValueError('invalid retrieval strategy')
        if not isinstance(raw_question, str) or not raw_question.strip():
            raise ValueError('raw question must be nonempty text')
        if len(raw_question) > 512:
            raise InputTooLong()
        validate_text('category', category, 255, nullable=True)
        if query_plan is not None and not isinstance(query_plan, QueryPlan):
            raise ValueError('query plan must be a QueryPlan')
        plan = query_plan if query_plan is not None else await self.planner.plan(raw_question)
        vector = None
        if strategy != 'bm25':
            vectors = await self.embedder.embed([plan.standard])
            vector = vectors[0]
        # 原话完整加入稀疏查询，保留型号、数字与限制条件；同文本只出现一次。
        text = None if strategy == 'dense' else '\n'.join(dict.fromkeys(
            [plan.standard, *plan.expansions, raw_question]))
        index_strategy = 'hybrid' if strategy == 'hybrid_rerank' else strategy
        hits = await self.index.recall(vector, text, strategy=index_strategy, category=category)
        # 首次出现决定候选位置与召回分数；去重后才进入拒绝重复主键的仓储。
        by_id = {}
        for hit in hits:
            by_id.setdefault(hit.id, hit)
        candidates = list(by_id.values())[:50]
        rows = await self.repository.get_done([hit.id for hit in candidates]) if candidates else []
        authoritative = {row.id: row for row in rows if row.vectorize_status == 'done'
                         and (category is None or row.category == category)}
        valid = [(hit, authoritative[hit.id]) for hit in candidates if hit.id in authoritative]
        if strategy == 'hybrid_rerank' and valid:
            # 重排位置始终映射到实际提交的权威正文，不映射到含缺行的原召回列表。
            ranked = await self.reranker.rank(raw_question, [embedding_text(row) for _, row in valid], top_n=10)
            matches = [ScoredChunk(valid[hit.index][1], hit.score, 'rerank') for hit in ranked[:10]]
        else:
            score_kind = {'dense': 'cosine', 'bm25': 'bm25', 'hybrid': 'rrf', 'hybrid_rerank': 'rerank'}[strategy]
            matches = [ScoredChunk(row, hit.score, score_kind) for hit, row in valid[:10]]
        # 通用服务保留低分；证据门槛和自评由后续线上消费方执行。
        return RetrievalBundle(plan, strategy, candidates, matches)


# 仅序列化最终十条证据及策略计数，不能泄露五十候选的完整正文。
def faq_payload(bundle: RetrievalBundle) -> dict:
    matches = [{'id': item.chunk.id, 'question': item.chunk.questions, 'answer': item.chunk.answer,
                'category': item.chunk.category, 'section_path': item.chunk.section_path,
                'score': item.score, 'score_kind': item.score_kind} for item in bundle.matches[:10]]
    return {'found': bool(matches), 'matches': matches, 'retrieval': {
        'strategy': bundle.strategy, 'candidate_count': len(bundle.candidates), 'match_count': len(matches)}}
