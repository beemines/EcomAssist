import hashlib
import json
import unicodedata
from datetime import datetime

from app.knowledge.history import validate_batch_size, window
from app.knowledge.types import validate_id


def normalize_qa(question: str, answer: str) -> tuple[str, str]:
    return tuple(' '.join(unicodedata.normalize('NFKC', value).split()) for value in (question, answer))


async def deduplicate_staging(repository) -> dict[str, int]:
    seen = {normalize_qa(q, a) for questions, a in await repository.qa_pairs()
        for q in questions.splitlines() if q.strip()}
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


class MiningBatchError(RuntimeError):
    """Only validated source IDs and derived batch/window identity are printable."""
    def __init__(self, batch_no, start, end, sources, error_type):
        refs = ','.join(f'conversation:{cid}:message:{mid}' for cid, mid in sources)
        super().__init__(f'Knowledge mining batch failed ({error_type}); batch_no={batch_no}; '
            f'Beijing window=[{start.isoformat()}, {end.isoformat()}); sources={refs}')


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
            sources = [(r.id, r.last_message_id) for r in rows]
            for cid, mid in sources:
                validate_id(cid)
                validate_id(mid)
            identity = [start.isoformat(), end.isoformat(), sources]
            batch_no = hashlib.sha256(json.dumps(identity, separators=(',', ':')).encode()).hexdigest()
            try:
                items = await self.extractor.extract(rows)
                counts['staged'] += await self.repository.stage(batch_no, items)
            except Exception as exc:
                raise MiningBatchError(batch_no, start, end, sources, type(exc).__name__) from exc
            counts['conversations'] += len(rows)
            after_id = rows[-1].id
        counts.update(await deduplicate_staging(self.repository))
        return counts
