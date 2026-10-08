# 历史问答挖掘测试，覆盖文本规范化、跨批次去重、冲突答案保留及提升失败重跑。
import importlib
from datetime import datetime

import pytest

from app.knowledge.types import ExtractedQA, StagedQA
from tests.test_knowledge_extraction import conversation

START, END = datetime(2026, 10, 6), datetime(2026, 10, 7)


# 加载会话挖掘与暂存去重模块，缺失实现时明确失败。
def mining():
    try:
        return importlib.import_module('app.knowledge.mining')
    except ImportError:
        pytest.fail('conversation mining is missing')


class History:
    # 检查时间窗口并按会话编号分页返回合成已完成会话。
    async def completed(self, start, end, after_id=0, limit=20):
        assert (start, end) == (START, END)
        return [conversation(i) for i in range(1, 4) if i > after_id][:limit]


class Repository:
    # 准备暂存行、已入库问答与批次记录，并提供晋级故障开关。
    def __init__(self):
        self.rows, self.pairs, self.batches = [], [('已经入库?', '答案')], []
        self.fail = False

    # 按批次、来源及问答内容去重暂存，返回实际新增行数。
    async def stage(self, batch_no, items):
        self.batches.append(batch_no)
        count = 0
        for item in items:
            if any((r.batch_no, r.source_ref, r.question, r.answer) == (batch_no, item.source_ref, item.question, item.answer) for r in self.rows):
                continue
            self.rows.append(StagedQA(**item.__dict__, id=len(self.rows) + 1, batch_no=batch_no))
            count += 1
        return count

    # 只返回尚未决定保留或丢弃的暂存问答。
    async def extracted(self):
        return [r for r in self.rows if r.status == 'extracted']

    # 返回已入库问答副本，供全局去重比较。
    async def qa_pairs(self):
        return self.pairs.copy()

    # 按保留和丢弃编号更新暂存状态与知识问答，支持提交前故障。
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
    # 生成跨会话重复、空白标点变体、冲突答案和已入库问答的抽取结果。
    async def extract(self, rows):
        values = {
            1: [('　邮费多少？\n', '标准配送  8元。'), ('邮费多少?', '标准配送 8元。')],
            2: [('邮费多少？', '标准配送 8元。'), ('邮费多少？', '标准配送12元。')],
            3: [('已经入库？', '答案')],
        }
        return [ExtractedQA(f'conversation:{r.id}:message:{r.last_message_id}', q, a) for r in rows for q, a in values[r.id]]


# 验证全角标点和首尾、重复空白被规范化，同时保留答案内容。
def test_nfkc_whitespace_normalization_keeps_answer_conflicts_distinct():
    assert mining().normalize_qa('　邮费多少？\n', '标准配送  8元。') == ('邮费多少?', '标准配送 8元。')


# 验证跨页与已有知识全局去重，保留冲突答案且重跑相同窗口不重复暂存。
async def test_global_dedup_across_batches_database_and_repeat_window():
    repo = Repository()
    job = mining().ConversationMiningJob(History(), repo, Extractor())
    result = await job.run(START, END, 1)
    assert result == {'conversations': 3, 'staged': 5, 'kept': 2, 'discarded': 3}
    assert len(set(repo.batches)) == 3 and all(len(b) == 64 for b in repo.batches)
    assert [r.status for r in repo.rows] == ['kept', 'discarded', 'discarded', 'kept', 'discarded']
    # 重放同一时间窗口并返回新增保留数，用于断言幂等结果。
    async def rerun_same_window():
        return (await job.run(START, END, 1))['kept']
    assert await rerun_same_window() == 0
    assert len(repo.rows) == 5


# 验证晋级失败后暂存仍可处理，后续重试能恢复并保留正确数量。
async def test_promotion_failure_keeps_staging_available_for_retry():
    repo = Repository()
    repo.fail = True
    job = mining().ConversationMiningJob(History(), repo, Extractor())
    with pytest.raises(RuntimeError, match='promotion'):
        await job.run(START, END)
    assert all(r.status == 'extracted' for r in repo.rows)
    repo.fail = False
    assert (await job.run(START, END))['kept'] == 2


# 验证已有多行问法逐项规范化去重，答案不同的问答仍被保留。
async def test_existing_multiline_questions_dedup_each_normalized_variant_but_keep_conflict():
    repo = Repository()
    repo.pairs = [('　邮费是多少？\n \n快递费用  怎么收？\n', '标准配送  8元。')]
    await repo.stage('synthetic', [
        ExtractedQA('conversation:1:message:11', '邮费是多少?', '标准配送 8元。'),
        ExtractedQA('conversation:2:message:21', '快递费用 怎么收?', '标准配送 8元。'),
        ExtractedQA('conversation:3:message:31', '快递费用 怎么收?', '标准配送12元。'),
    ])
    assert await mining().deduplicate_staging(repo) == {'kept': 1, 'discarded': 2}
    assert [row.status for row in repo.rows] == ['discarded', 'discarded', 'kept']
    assert repo.pairs[-1] == ('快递费用 怎么收?', '标准配送12元。')


# 验证零、负数、超上限或布尔批次数量在读取历史前被拒绝。
@pytest.mark.parametrize('batch', [0, -1, 21, True])
async def test_invalid_batch_size_fails_before_history_reads(batch):
    with pytest.raises(ValueError):
        await mining().ConversationMiningJob(History(), Repository(), Extractor()).run(START, END, batch)
