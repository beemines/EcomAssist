# 历史问答先暂存，再按全局问答对自动去重入库；这里没有人工审批步骤。
import hashlib
import json
import unicodedata
from datetime import datetime

from app.knowledge.history import validate_batch_size, window
from app.knowledge.types import validate_id


# 分别对问题和答案做 NFKC 与空白归一化，返回用于精确比较的成对文本。
def normalize_qa(question: str, answer: str) -> tuple[str, str]:
    return tuple(' '.join(unicodedata.normalize('NFKC', value).split()) for value in (question, answer))


# 在全部已入库问答与当前待决记录间按归一化问答对去重，自动入库保留项并标记重复项。
async def deduplicate_staging(repository) -> dict[str, int]:
    # 已入库条目的多行问题分别与同一答案成对，建立全局精确去重基线。
    seen = {normalize_qa(q, a) for questions, a in await repository.qa_pairs()
        for q in questions.splitlines() if q.strip()}
    kept, discarded = [], []
    for row in await repository.extracted():
        pair = normalize_qa(row.question, row.answer)
        if pair in seen:
            discarded.append(row.id)
        else:
            kept.append(row.id)
            # 新保留项立即加入集合，同一批暂存记录中的后续重复也会被丢弃。
            seen.add(pair)
    # 仓储在同一事务内把保留项转为 pending 知识并写入暂存决策，后续可继续向量化。
    promoted = await repository.promote(kept, discarded)
    return {'kept': len(promoted), 'discarded': len(discarded)}


class MiningBatchError(RuntimeError):
    """Only validated source IDs and derived batch/window identity are printable."""
    # 仅以已验证的来源 id、窗口、批次号及错误类型生成批次诊断，避免包含会话正文。
    def __init__(self, batch_no, start, end, sources, error_type):
        refs = ','.join(f'conversation:{cid}:message:{mid}' for cid, mid in sources)
        super().__init__(f'Knowledge mining batch failed ({error_type}); batch_no={batch_no}; '
            f'Beijing window=[{start.isoformat()}, {end.isoformat()}); sources={refs}')


class ConversationMiningJob:
    """Called under the CLI's single outer lock; repository owns transactions."""
    # 接收历史查询、知识仓储与抽取器，由外层 CLI 的同一任务锁保护整个流程。
    def __init__(self, history, repository, extractor):
        self.history, self.repository, self.extractor = history, repository, extractor

    # 在指定时间窗口分页抽取并暂存会话 QA，最后执行全局去重与自动入库，返回各阶段计数。
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
            # 批次身份由窗口和来源快照派生，重跑相同输入沿用批次号以支持幂等暂存。
            identity = [start.isoformat(), end.isoformat(), sources]
            batch_no = hashlib.sha256(json.dumps(identity, separators=(',', ':')).encode()).hexdigest()
            try:
                items = await self.extractor.extract(rows)
                counts['staged'] += await self.repository.stage(batch_no, items)
            except Exception as exc:
                raise MiningBatchError(batch_no, start, end, sources, type(exc).__name__) from exc
            counts['conversations'] += len(rows)
            after_id = rows[-1].id
        # 去重覆盖全部 extracted 暂存项，并非仅处理本次窗口产生的条目。
        counts.update(await deduplicate_staging(self.repository))
        return counts
