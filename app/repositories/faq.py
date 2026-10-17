# 保留旧 Dense 评估入口，并通过显式依赖提供统一 FAQ 检索契约。
from app.db.session import Database
from app.knowledge.types import Embedder, VectorIndex
from app.repositories.knowledge import KnowledgeRepository
from app.retrieval.service import RetrievalService, faq_payload
from app.retrieval.types import QueryPlan


class FAQRepository:
    """Dense hits determine order; MySQL done rows own the answer text."""

    # 保留三个位置参数，统一检索依赖仅通过可选关键字显式注入。
    def __init__(self, database: Database, embedder: Embedder, index: VectorIndex,
                 *, retriever: RetrievalService | None = None):
        self.database = database
        self.embedder = embedder
        self.index = index
        self.knowledge = KnowledgeRepository(database)
        self.retriever = retriever

    # keyword 保持原话片段约束；新路径始终用本轮完整原话和分类进行检索。
    async def retrieve(self, keyword: str, *, raw_question: str, category: str | None = None,
                       query_plan: QueryPlan | None = None, top_k: int = 10) -> dict:
        if (not isinstance(keyword, str) or not 1 <= len(keyword) <= 128
                or not isinstance(raw_question, str) or keyword not in raw_question):
            raise ValueError('Invalid FAQ keyword or raw question.')
        if self.retriever is None:
            raise RuntimeError('FAQ retriever is required for unified retrieval')
        # Only trusted Workflow execution supplies a validated resolved plan.
        # Raw text remains the keyword authority; legacy calls retain planning.
        options = {'query_plan': query_plan, 'top_k': top_k} if query_plan is not None or top_k != 10 else {}
        question = query_plan.standard if query_plan is not None else raw_question
        return faq_payload(await self.retriever.retrieve(question, category=category, **options))

    # 语义检索最多三条命中，按命中顺序返回已完成向量化的数据库原文。
    async def search(self, keyword: str, limit: int = 3) -> list[dict]:
        if not isinstance(keyword, str) or not 1 <= len(keyword) <= 128:
            raise ValueError("Invalid FAQ keyword.")
        if type(limit) is not int or limit < 1:
            raise ValueError("Invalid FAQ limit.")
        vectors = await self.embedder.embed([keyword])
        hits = await self.index.search(vectors[0], limit=min(limit, 3))
        # 向量索引只决定命中顺序，答案以 MySQL 已完成记录的原文为准。
        rows = await self.knowledge.get_done([hit.id for hit in hits])
        by_id = {row.id: row for row in rows}
        return [{"id": hit.id, "question": by_id[hit.id].questions,
                 "answer": by_id[hit.id].answer, "category": by_id[hit.id].category}
                for hit in hits if hit.id in by_id]
