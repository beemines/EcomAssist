from app.db.session import Database
from app.knowledge.types import Embedder, VectorIndex
from app.repositories.knowledge import KnowledgeRepository


class FAQRepository:
    """Dense hits determine order; MySQL done rows own the answer text."""

    def __init__(self, database: Database, embedder: Embedder, index: VectorIndex):
        self.database = database
        self.embedder = embedder
        self.index = index
        self.knowledge = KnowledgeRepository(database)

    async def search(self, keyword: str, limit: int = 3) -> list[dict]:
        if not isinstance(keyword, str) or not 1 <= len(keyword) <= 128:
            raise ValueError("Invalid FAQ keyword.")
        if type(limit) is not int or limit < 1:
            raise ValueError("Invalid FAQ limit.")
        vectors = await self.embedder.embed([keyword])
        hits = await self.index.search(vectors[0], limit=min(limit, 3))
        rows = await self.knowledge.get_done([hit.id for hit in hits])
        by_id = {row.id: row for row in rows}
        return [{"id": hit.id, "question": by_id[hit.id].questions,
                 "answer": by_id[hit.id].answer, "category": by_id[hit.id].category}
                for hit in hits if hit.id in by_id]
