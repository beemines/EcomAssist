# MySQL 原文与状态是权威源；混合集合以相同主键重建、恢复和独立核验。
from app.knowledge.embeddings import validate_vector
from app.knowledge.types import ChunkRecord, Embedder, embedding_text
from app.knowledge.vectors import validate_acknowledged_ids
from app.repositories.knowledge import KnowledgeRepository
from app.retrieval.milvus import HybridMilvusIndex
from app.retrieval.types import IndexedChunk


# 三种作业都在查询或外部调用前拒绝非法批次数量。
def _batch_size(value: int) -> None:
    if type(value) is not int or value < 1:
        raise ValueError('batch size must be a positive integer')


class HybridKnowledgeJobs:
    # 独立核验不需要嵌入器；命令调用方在整个作业期间持有原 MySQL 命名锁。
    def __init__(self, repository: KnowledgeRepository, embedder: Embedder | None, index: HybridMilvusIndex):
        self.repository, self.embedder, self.index = repository, embedder, index

    # 仓储读取已结束短事务，随后嵌入三栏正文、按原主键覆盖并核对 ACK 和读回。
    async def _write(self, records: list[ChunkRecord]) -> None:
        if self.embedder is None:
            raise ValueError('embedding is required to write hybrid knowledge')
        texts = [embedding_text(record) for record in records]
        vectors = await self.embedder.embed(texts)
        if not isinstance(vectors, list) or len(vectors) != len(records):
            raise ValueError('embedding count differs from knowledge chunks')
        rows = [IndexedChunk(record.id, vector, text, record.category)
                for record, vector, text in zip(records, vectors, texts)]
        ids = [row.id for row in rows]
        validate_acknowledged_ids(await self.index.upsert(rows), ids)
        await self.index.verify_rows(rows)

    # 重建只遍历 done，不改变任何 MySQL 状态；每批读回后最后核对全集与原文。
    async def rebuild_done(self, batch_size: int = 20) -> dict:
        _batch_size(batch_size)
        after_id = 0
        while records := await self.repository.done_page(after_id=after_id, limit=batch_size):
            await self._write(records)
            after_id = records[-1].id
        return await self.verify_done(batch_size)

    # ACK 与读回全部成功才开启下一短事务标记 done，失败重放仍复用同一主键。
    async def vectorize_pending(self, batch_size: int = 20) -> int:
        _batch_size(batch_size)
        count = 0
        while records := await self.repository.pending(batch_size):
            await self._write(records)
            await self.repository.mark_done([record.id for record in records])
            count += len(records)
        return count

    # 独立核验不重新嵌入；读回字段精确比较，Dense 只检查固定维度及有限值。
    async def verify_done(self, batch_size: int = 20) -> dict:
        _batch_size(batch_size)
        mysql_ids, missing, mismatched = set(), set(), set()
        after_id = 0
        while records := await self.repository.done_page(after_id=after_id, limit=batch_size):
            ids = [record.id for record in records]
            mysql_ids.update(ids)
            try:
                actual = {row.id: row for row in await self.index.get_rows(ids)}
            except ValueError:
                # 适配器拒绝非法读回时整批不能核验通过，保守报告受影响的主键。
                mismatched.update(ids)
            else:
                for record in records:
                    row = actual.get(record.id)
                    if row is None:
                        missing.add(record.id)
                        continue
                    try:
                        validate_vector(row.embedding)
                    except ValueError:
                        mismatched.add(record.id)
                    if row.text != embedding_text(record) or row.category != record.category:
                        mismatched.add(record.id)
            after_id = records[-1].id
        vector_ids = await self.index.all_ids()
        missing.update(mysql_ids - vector_ids)
        extra = vector_ids - mysql_ids
        return dict(ready=not (missing or extra or mismatched), mysql_count=len(mysql_ids),
                    vector_count=len(vector_ids), missing_ids=sorted(missing), extra_ids=sorted(extra),
                    mismatched_ids=sorted(mismatched))
