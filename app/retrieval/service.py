# 统一检索组合单轮查询理解、服务端召回、MySQL 权威回填和可选重排。
import asyncio
import json
import logging
from typing import Literal

from langchain_core.exceptions import OutputParserException
from openai import ContentFilterFinishReasonError, LengthFinishReasonError
from pydantic import ValidationError

from app.core.errors import InputTooLong, ServiceError
from app.knowledge.types import Embedder, VectorHit, embedding_text
from app.repositories.knowledge import KnowledgeRepository
from app.retrieval.milvus import HybridMilvusIndex
from app.retrieval.query import QueryPlanner
from app.retrieval.rerank import SiliconFlowReranker
from app.retrieval.types import QueryPlan, RetrievalBundle, ScoredChunk, validate_category


logger = logging.getLogger(__name__)


def _exception_chain(exc: BaseException):
    """检查原因与上下文并防止环引用，不读取可能包含请求或密钥的异常正文。"""
    pending, seen = [exc], set()
    while pending:
        current = pending.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))
        yield current
        pending.extend(link for link in (current.__cause__, current.__context__) if link is not None)


def _can_degrade_rewrite(exc: Exception) -> bool:
    """仅无效结构及已知解析链可降级；超时、取消、输入与未知原因均拒绝。"""
    if not isinstance(exc, ServiceError) or exc.code != 'invalid_structured_output':
        return False
    for current in _exception_chain(exc):
        if isinstance(current, ServiceError) and current.code != 'invalid_structured_output':
            return False
        if not isinstance(current, (ServiceError, ValidationError, OutputParserException, json.JSONDecodeError,
                                    LengthFinishReasonError, ContentFilterFinishReasonError)):
            return False
    return True


def _caller_cancellation(exc: BaseException) -> asyncio.CancelledError | None:
    """期限内部取消属于TimeoutError；仅传播没有期限祖先的调用方取消。"""
    pending, seen = [(exc, False)], set()
    while pending:
        current, deadline_owned = pending.pop()
        key = (id(current), deadline_owned)
        if key in seen:
            continue
        seen.add(key)
        if isinstance(current, asyncio.CancelledError) and not deadline_owned:
            return current
        deadline_owned = deadline_owned or isinstance(current, TimeoutError)
        pending.extend((link, deadline_owned) for link in (current.__cause__, current.__context__)
                       if link is not None)
    return None


def _log_rewrite_failure(exc: BaseException, *, degraded: bool = False) -> None:
    """日志仅含固定阶段、白名单码、类型与可选降级标记，禁止正文与堆栈。"""
    code = 'rewrite_error'
    if isinstance(exc, ServiceError) and exc.code in (
            'invalid_structured_output', 'upstream_timeout', 'upstream_error', 'input_too_long'):
        code = exc.code
    elif isinstance(exc, asyncio.CancelledError):
        code = 'cancelled'
    elif isinstance(exc, TimeoutError):
        code = 'upstream_timeout'
    message = 'stage=rewrite code=%s type=%s' + (' status=degraded' if degraded else '')
    logger.warning(message, code, type(exc).__name__)


def _ensure_active() -> None:
    """下层吞掉计时器或调用方取消也不能让迟到结果进入下一阶段。"""
    task = asyncio.current_task()
    if task is not None and task.cancelling():
        raise asyncio.CancelledError()


class RetrievalService:
    # 只组合调用方管理的依赖，不创建客户端或改变其生命周期。
    def __init__(self, repository: KnowledgeRepository, embedder: Embedder,
                 index: HybridMilvusIndex, planner: QueryPlanner, reranker: SiliconFlowReranker):
        self.repository, self.embedder, self.index = repository, embedder, index
        self.planner, self.reranker = planner, reranker

    # 单轮仅理解一次；结构无效时使用完整原话，其他依赖故障或取消直接传播。
    async def retrieve(self, raw_question: str, *, category: str | None = None,
                       strategy: Literal['dense', 'bm25', 'hybrid', 'hybrid_rerank'] = 'hybrid_rerank',
                       query_plan: QueryPlan | None = None) -> RetrievalBundle:
        if strategy not in ('dense', 'bm25', 'hybrid', 'hybrid_rerank'):
            raise ValueError('invalid retrieval strategy')
        if not isinstance(raw_question, str) or not raw_question.strip():
            raise ValueError('raw question must be nonempty text')
        if len(raw_question) > 512:
            raise InputTooLong()
        validate_category(category)
        if query_plan is not None and not isinstance(query_plan, QueryPlan):
            raise ValueError('query plan must be a QueryPlan')
        plan = query_plan
        if plan is None:
            # 保留规划器已有期限；下层吞掉计时器取消也不能让迟到结果进入检索。
            loop = asyncio.get_running_loop()
            deadline = loop.time() + getattr(self.planner, 'timeout', 60)
            task = asyncio.current_task()
            try:
                plan = await self.planner.plan(raw_question)
                if task is not None and task.cancelling():
                    raise asyncio.CancelledError()
                if loop.time() >= deadline:
                    raise ServiceError('upstream_timeout', '模型响应超时，请稍后重试。', 504)
            except asyncio.CancelledError as exc:
                _log_rewrite_failure(exc)
                raise
            except Exception as exc:
                # 下层包装或吞掉取消时，不能把取消归一为成功检索。
                cancellation = _caller_cancellation(exc)
                if cancellation is not None:
                    _log_rewrite_failure(cancellation)
                    raise cancellation
                if task is not None and task.cancelling():
                    _log_rewrite_failure(asyncio.CancelledError())
                    raise asyncio.CancelledError() from None
                degraded = _can_degrade_rewrite(exc)
                if degraded and loop.time() >= deadline:
                    timeout = ServiceError('upstream_timeout', '模型响应超时，请稍后重试。', 504)
                    _log_rewrite_failure(timeout)
                    raise timeout from exc
                _log_rewrite_failure(exc, degraded=degraded)
                if not degraded:
                    raise
                plan = QueryPlan(standard=raw_question, expansions=[])
        vector = None
        if strategy != 'bm25':
            vectors = await self.embedder.embed([plan.standard])
            vector = vectors[0]
        # 原话完整加入稀疏查询，保留型号、数字与限制条件；同文本只出现一次。
        text = None if strategy == 'dense' else '\n'.join(dict.fromkeys(
            [plan.standard, *plan.expansions, raw_question]))
        index_strategy = 'hybrid' if strategy == 'hybrid_rerank' else strategy
        hits = await self.index.recall(vector, text, strategy=index_strategy, category=category)
        return await self.finalize_candidates(question=raw_question, plan=plan, candidates=hits,
                                              category=category, strategy=strategy)

    async def recall_candidates(self, query: str, *, category: str | None = None) -> list[VectorHit]:
        """单条完整查询仅做嵌入与原生hybrid，去重截断50；不调用规划或重排。"""
        if not isinstance(query, str) or not query.strip():
            raise ValueError('query must be nonempty text')
        if len(query) > 512:
            raise InputTooLong()
        validate_category(category)
        vectors = await self.embedder.embed([query])
        _ensure_active()
        hits = await self.index.recall(vectors[0], query, strategy='hybrid', category=category)
        _ensure_active()
        by_id = {}
        for hit in hits:
            by_id.setdefault(hit.id, hit)
        return list(by_id.values())[:50]

    async def finalize_candidates(self, *, question: str, plan: QueryPlan, candidates: list[VectorHit],
                                  category: str | None, strategy: str,
                                  rerank_question: str | None = None) -> RetrievalBundle:
        """复用四策略的权威回填与至多一次重排，最终最多十条证据。"""
        _ensure_active()
        if strategy not in ('dense', 'bm25', 'hybrid', 'hybrid_rerank'):
            raise ValueError('invalid retrieval strategy')
        if rerank_question is not None and (strategy != 'hybrid_rerank'
                or not isinstance(rerank_question, str) or not rerank_question.strip()
                or len(rerank_question) > 512):
            raise ValueError('rerank question must be bounded text for hybrid_rerank')
        validate_category(category)
        # 首次出现决定候选位置与召回分数；去重后才进入拒绝重复主键的仓储。
        by_id = {}
        for hit in candidates:
            by_id.setdefault(hit.id, hit)
        candidates = list(by_id.values())[:50]
        rows = await self.repository.get_done([hit.id for hit in candidates]) if candidates else []
        _ensure_active()
        authoritative = {row.id: row for row in rows if row.vectorize_status == 'done'
                         and (category is None or row.category == category)}
        valid = [(hit, authoritative[hit.id]) for hit in candidates if hit.id in authoritative]
        if strategy == 'hybrid_rerank' and valid:
            # 重排位置始终映射到实际提交的权威正文，不映射到含缺行的原召回列表。
            ranked = await self.reranker.rank(question if rerank_question is None else rerank_question,
                [embedding_text(row) for _, row in valid], top_n=10)
            _ensure_active()
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
