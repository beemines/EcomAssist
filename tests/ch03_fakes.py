from dataclasses import replace


class MemoryVectorIndex:
    def __init__(self):
        self.rows = {}
        self.upsert_calls = 0

    @property
    def ids(self):
        return set(self.rows)

    async def upsert(self, rows):
        self.upsert_calls += 1
        self.rows.update(rows)
        return [identifier for identifier, _ in rows]


class RecordingEmbedder:
    def __init__(self):
        self.texts = []

    async def embed(self, texts):
        self.texts.extend(texts)
        return [[1.0] + [0.0] * 1023 for _ in texts]


class MemoryKnowledgeRepository:
    def __init__(self, records):
        self.records = {record.id: record for record in records}
        self.mark_calls = 0

    async def pending(self, limit=20):
        return [row for _, row in sorted(self.records.items()) if row.vectorize_status == 'pending'][:limit]

    async def mark_done(self, ids):
        self.mark_calls += 1
        for identifier in ids:
            self.records[identifier] = replace(self.records[identifier], vector_id=str(identifier), vectorize_status='done')

    async def get_done(self, ids):
        return [self.records[identifier] for identifier in ids if self.records[identifier].vectorize_status == 'done']
