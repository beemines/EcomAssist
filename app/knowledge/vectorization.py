"""Recover pending rows using MySQL ids as idempotent Milvus primary keys."""

from app.knowledge.embeddings import validate_vector
from app.knowledge.types import Embedder, VectorIndex, embedding_text, validate_id
from app.knowledge.vectors import validate_acknowledged_ids
from app.repositories.knowledge import KnowledgeRepository


class PendingVectorizer:
    def __init__(self, repository: KnowledgeRepository, embedder: Embedder, index: VectorIndex):
        self.repository, self.embedder, self.index = repository, embedder, index

    async def run(self, batch_size: int = 20) -> int:
        if type(batch_size) is not int or batch_size < 1:
            raise ValueError('batch size must be a positive integer')
        count = 0
        while records := await self.repository.pending(batch_size):
            ids = [record.id for record in records]
            for identifier in ids:
                validate_id(identifier)
            if len(set(ids)) != len(ids):
                raise ValueError('duplicate pending knowledge ids')
            vectors = await self.embedder.embed([embedding_text(record) for record in records])
            if not isinstance(vectors, list) or len(vectors) != len(records):
                raise ValueError('embedding count differs from pending chunks')
            rows = list(zip(ids, [validate_vector(vector) for vector in vectors]))
            actual = await self.index.upsert(rows)
            validate_acknowledged_ids(actual, ids)
            # Every network operation is finished before this short MySQL transaction.
            await self.repository.mark_done(ids)
            count += len(ids)
        return count
