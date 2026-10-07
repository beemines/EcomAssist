import importlib
from datetime import datetime

import pytest

from app.knowledge.types import ExtractedQA, StagedQA
from tests.test_knowledge_extraction import conversation

START, END = datetime(2026, 10, 6), datetime(2026, 10, 7)


def mining():
    try:
        return importlib.import_module('app.knowledge.mining')
    except ImportError:
        pytest.fail('conversation mining is missing')


class History:
    async def completed(self, start, end, after_id=0, limit=20):
        assert (start, end) == (START, END)
        return [conversation(i) for i in range(1, 4) if i > after_id][:limit]


class Repository:
    def __init__(self):
        self.rows, self.pairs, self.batches = [], [('已经入库?', '答案')], []
        self.fail = False

    async def stage(self, batch_no, items):
        self.batches.append(batch_no)
        count = 0
        for item in items:
            if any((r.batch_no, r.source_ref, r.question, r.answer) == (batch_no, item.source_ref, item.question, item.answer) for r in self.rows):
                continue
            self.rows.append(StagedQA(**item.__dict__, id=len(self.rows) + 1, batch_no=batch_no))
            count += 1
        return count

    async def extracted(self):
        return [r for r in self.rows if r.status == 'extracted']

    async def qa_pairs(self):
        return self.pairs.copy()

    async def promote(self, kept, discarded):
        if self.fail:
            raise RuntimeError('promotion failure')
        from dataclasses import replace
        for row in self.rows:
            if row.id in kept:
                self.pairs.append((row.question, row.answer))
        self.rows = [replace(r, status='kept' if r.id in kept else 'discarded' if r.id in discarded else r.status) for r in self.rows]
        return kept


class Extractor:
    async def extract(self, rows):
        values = {
            1: [('　邮费多少？\n', '标准配送  8元。'), ('邮费多少?', '标准配送 8元。')],
            2: [('邮费多少？', '标准配送 8元。'), ('邮费多少？', '标准配送12元。')],
            3: [('已经入库？', '答案')],
        }
        return [ExtractedQA(f'conversation:{r.id}:message:{r.last_message_id}', q, a) for r in rows for q, a in values[r.id]]


def test_nfkc_whitespace_normalization_keeps_answer_conflicts_distinct():
    assert mining().normalize_qa('　邮费多少？\n', '标准配送  8元。') == ('邮费多少?', '标准配送 8元。')


async def test_global_dedup_across_batches_database_and_repeat_window():
    repo = Repository()
    job = mining().ConversationMiningJob(History(), repo, Extractor())
    result = await job.run(START, END, 1)
    assert result == {'conversations': 3, 'staged': 5, 'kept': 2, 'discarded': 3}
    assert len(set(repo.batches)) == 3 and all(len(b) == 64 for b in repo.batches)
    assert [r.status for r in repo.rows] == ['kept', 'discarded', 'discarded', 'kept', 'discarded']
    async def rerun_same_window():
        return (await job.run(START, END, 1))['kept']
    assert await rerun_same_window() == 0
    assert len(repo.rows) == 5


async def test_promotion_failure_keeps_staging_available_for_retry():
    repo = Repository()
    repo.fail = True
    job = mining().ConversationMiningJob(History(), repo, Extractor())
    with pytest.raises(RuntimeError, match='promotion'):
        await job.run(START, END)
    assert all(r.status == 'extracted' for r in repo.rows)
    repo.fail = False
    assert (await job.run(START, END))['kept'] == 2


@pytest.mark.parametrize('batch', [0, -1, 21, True])
async def test_invalid_batch_size_fails_before_history_reads(batch):
    with pytest.raises(ValueError):
        await mining().ConversationMiningJob(History(), Repository(), Extractor()).run(START, END, batch)
