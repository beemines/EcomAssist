# 双写依靠 pending 状态恢复；重试复用 MySQL 主键，避免向量写成重复记录。
"""Recover pending rows using MySQL ids as idempotent Milvus primary keys."""

from app.knowledge.embeddings import validate_vector
from app.knowledge.types import Embedder, VectorIndex, embedding_text, validate_id
from app.knowledge.vectors import validate_acknowledged_ids
from app.repositories.knowledge import KnowledgeRepository


class PendingVectorizer:
    # 接收知识仓储、嵌入器和向量索引，组合待处理记录的双写恢复流程。
    def __init__(self, repository: KnowledgeRepository, embedder: Embedder, index: VectorIndex):
        self.repository, self.embedder, self.index = repository, embedder, index

    # 逐批处理 pending 记录；以 MySQL id 写入向量并确认回包，再标记完成，返回处理条数。
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
            # pending 查询已结束仓储事务；嵌入和向量写入阶段不占用 MySQL 长事务。
            vectors = await self.embedder.embed([embedding_text(record) for record in records])
            if not isinstance(vectors, list) or len(vectors) != len(records):
                raise ValueError('embedding count differs from pending chunks')
            rows = list(zip(ids, [validate_vector(vector) for vector in vectors]))
            actual = await self.index.upsert(rows)
            validate_acknowledged_ids(actual, ids)
            # 外部写入和主键确认都成功后才开启短事务标记 done；此前失败仍可重试同一 id。
            await self.repository.mark_done(ids)
            count += len(ids)
        return count
