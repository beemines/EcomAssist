import hashlib
import json
import unicodedata
from datetime import datetime

from app.knowledge.history import validate_batch_size, window


def normalize_qa(question: str, answer: str) -> tuple[str, str]:
    return tuple(' '.join(unicodedata.normalize('NFKC', value).split()) for value in (question, answer))


async def deduplicate_staging(repository) -> dict[str, int]:
    seen = {normalize_qa(q, a) for q, a in await repository.qa_pairs()}
    kept, discarded = [], []
    for row in await repository.extracted():
        pair = normalize_qa(row.question, row.answer)
        if pair in seen:
            discarded.append(row.id)
        else:
            kept.append(row.id)
            seen.add(pair)
    promoted = await repository.promote(kept, discarded)
    return {'kept': len(promoted), 'discarded': len(discarded)}


class ConversationMiningJob:
    """Called under the CLI's single outer lock; repository owns transactions."""
    def __init__(self, history, repository, extractor):
        self.history, self.repository, self.extractor = history, repository, extractor

    async def run(self, start: datetime, end: datetime, batch_size: int = 20) -> dict[str, int]:
        start, end = window(start, end)
        validate_batch_size(batch_size)
        counts = {'conversations': 0, 'staged': 0, 'kept': 0, 'discarded': 0}
        after_id = 0
        while rows := await self.history.completed(start, end, after_id, batch_size):
            identity = [start.isoformat(), end.isoformat(), [(r.id, r.last_message_id) for r in rows]]
            batch_no = hashlib.sha256(json.dumps(identity, separators=(',', ':')).encode()).hexdigest()
            items = await self.extractor.extract(rows)
            counts['staged'] += await self.repository.stage(batch_no, items)
            counts['conversations'] += len(rows)
            after_id = rows[-1].id
        counts.update(await deduplicate_staging(self.repository))
        return counts
