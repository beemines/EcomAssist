# 保持 FAQ 工具返回契约，通过 Dense 向量检索命中并从 MySQL 读取权威原文。
from app.db.session import Database
from app.knowledge.types import Embedder, VectorIndex
from app.repositories.knowledge import KnowledgeRepository


class FAQRepository:
    """Dense hits determine order; MySQL done rows own the answer text."""

    # 组合数据库权威文本仓储、向量生成器和向量检索索引。
    def __init__(self, database: Database, embedder: Embedder, index: VectorIndex):
        self.database = database
        self.embedder = embedder
        self.index = index
        self.knowledge = KnowledgeRepository(database)

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
