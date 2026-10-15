"""有界顺序多查询召回；第二层RRF只聚合主键，统一回填和一次重排。"""
from dataclasses import dataclass
from math import fsum

from app.knowledge.types import VectorHit
from app.retrieval.service import (
    RetrievalService, _caller_cancellation, _ensure_active, _exception_chain, faq_payload,
)
from app.retrieval.types import QueryPlan, validate_category


@dataclass(frozen=True)
class WorkflowRetrieval:
    """严格证据payload保持既有Schema，来源与计数仅供内部审计。"""
    payload: dict
    audit: dict


class WorkflowRetriever:
    """调用方拥有统一FAQ期限，本层不设单路重试或挽救残缺结果。"""
    def __init__(self, retriever: RetrievalService):
        """仅绑定已有检索服务，不创建客户端或知识副本。"""
        self.retriever = retriever

    async def retrieve(self, *, question: str, queries: tuple[str, ...],
                       category: str | None) -> WorkflowRetrieval:
        """每路唯一排名贡献1/(60+rank)，按分数降序和主键升序截断50。"""
        plan = QueryPlan(standard=question, expansions=[])
        validate_category(category)
        if (not isinstance(queries, tuple) or not 1 <= len(queries) <= 3 or queries[0] != question
                or any(not isinstance(query, str) or not query.strip() or len(query) > 512 for query in queries)
                or len({''.join(query.split()) for query in queries}) != len(queries)):
            raise ValueError('queries must contain the question first and one to three unique nonblank queries')
        provenance, counts = {}, []
        try:
            _ensure_active()
            if len(queries) == 1:
                # 纯FAQ明确跳过旧planner，保留单查询原生hybrid候选及得分。
                bundle = await self.retriever.retrieve(question, category=category,
                    strategy='hybrid_rerank', query_plan=plan)
                candidates = bundle.candidates
                counts.append(len(candidates))
                provenance = {hit.id: [{'query_index': 0, 'rank': rank}]
                              for rank, hit in enumerate(candidates, start=1)}
            else:
                for query_index, query in enumerate(queries):
                    hits = await self.retriever.recall_candidates(query, category=category)
                    _ensure_active()
                    # 防御每路重复主键；重复项既不额外加分，也不占后续唯一排名。
                    unique = dict.fromkeys(hit.id for hit in hits)
                    counts.append(len(unique))
                    for rank, identifier in enumerate(unique, start=1):
                        provenance.setdefault(identifier, []).append({'query_index': query_index, 'rank': rank})
                # fsum避免相同名次集合仅因浮点累加顺序不同而破坏主键稳定决胜。
                scores = {identifier: fsum(1 / (60 + source['rank']) for source in sources)
                          for identifier, sources in provenance.items()}
                candidates = [VectorHit(identifier, scores[identifier]) for identifier in sorted(
                    scores, key=lambda identifier: (-scores[identifier], identifier))[:50]]
                bundle = await self.retriever.finalize_candidates(question=question, plan=plan,
                    candidates=candidates, category=category, strategy='hybrid_rerank')
            _ensure_active()
        except BaseException as exc:
            # 包装链不能把调用方取消或期限变成普通解析失败/部分成功。
            cancellation = _caller_cancellation(exc)
            if cancellation is not None:
                raise cancellation
            _ensure_active()
            timeout = next((item for item in _exception_chain(exc) if isinstance(item, TimeoutError)), None)
            if timeout is not None:
                raise timeout
            raise
        return WorkflowRetrieval(faq_payload(bundle), {
            'query_count': len(queries), 'lane_candidate_counts': counts,
            'candidate_count': len(candidates), 'union_count': len(provenance),
            'provenance': {hit.id: provenance[hit.id] for hit in candidates},
        })
