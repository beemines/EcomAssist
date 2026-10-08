# 知识库测试替身，在内存中记录嵌入、向量与知识写入，便于注入故障。
from dataclasses import replace


class MemoryVectorIndex:
    # 初始化内存向量记录及写入计数，供向量化流程断言使用。
    def __init__(self):
        self.rows = {}
        self.upsert_calls = 0

    # 返回已经写入向量索引的知识编号集合。
    @property
    def ids(self):
        return set(self.rows)

    # 在内存中覆盖向量记录，并记录批量写入次数与返回编号。
    async def upsert(self, rows):
        self.upsert_calls += 1
        self.rows.update(rows)
        return [identifier for identifier, _ in rows]


class RecordingEmbedder:
    # 保存待核对的嵌入文本，避免测试调用真实模型。
    def __init__(self):
        self.texts = []

    # 记录输入文本并为每条返回固定的 1024 维向量。
    async def embed(self, texts):
        self.texts.extend(texts)
        return [[1.0] + [0.0] * 1023 for _ in texts]


class MemoryKnowledgeRepository:
    # 按知识编号建立内存仓储，并初始化完成状态的更新计数。
    def __init__(self, records):
        self.records = {record.id: record for record in records}
        self.mark_calls = 0

    # 按编号顺序返回指定数量的待向量化记录。
    async def pending(self, limit=20):
        return [row for _, row in sorted(self.records.items()) if row.vectorize_status == 'pending'][:limit]

    # 记录批次提交，并把指定知识条目标记为已向量化。
    async def mark_done(self, ids):
        self.mark_calls += 1
        for identifier in ids:
            self.records[identifier] = replace(self.records[identifier], vector_id=str(identifier), vectorize_status='done')

    # 仅返回指定编号中已完成向量化的知识记录。
    async def get_done(self, ids):
        return [self.records[identifier] for identifier in ids if self.records[identifier].vectorize_status == 'done']
