"""Short SQL coordination; every execution owns an immutable model snapshot."""
from dataclasses import asdict
from collections.abc import Sequence
from datetime import datetime
from app.context.layers import ContextCapacityError, _compact_layer2, freeze_record, history_tokens, plan_layers
from app.context.view import build_snapshot, _summary_cost
from app.context.types import ContextAnchors, ContextBudget, ContextSnapshot, FrozenMessage, SummarySegment
from app.repositories.records import MessageRecord
from app.context.logging import budget_fields
from app.core.errors import ServiceError


def serialize_snapshot(snapshot):
    return dict(snapshot_id=snapshot.snapshot_id, conversation_id=snapshot.conversation_id,
        user_message_id=snapshot.user_message_id,
        anchors={key: str(value) if value is not None else None for key, value in asdict(snapshot.anchors).items()},
        summaries=[dict(seq=s.seq, from_msg_id=str(s.from_msg_id), upto_msg_id=str(s.upto_msg_id),
                        content=s.content, created_at=s.created_at.isoformat()) for s in snapshot.summaries],
        omitted_summary_seqs=list(snapshot.omitted_summary_seqs),
        layer1=[asdict(row) for row in snapshot.layer1], layer2=[asdict(row) for row in snapshot.layer2],
        budget=budget_fields(snapshot.budget))


def restore_snapshot(saved, budget):
    """Keep chosen rows/segments, but recheck them against this deployment's limits."""
    anchors = ContextAnchors(**{key: int(value) if value is not None else None for key, value in saved['anchors'].items()})
    segments = tuple(SummarySegment(s['seq'], int(s['from_msg_id']), int(s['upto_msg_id']), s['content'],
                                   datetime.fromisoformat(s['created_at'])) for s in saved['summaries'])
    snapshot = ContextSnapshot(saved['snapshot_id'], saved['conversation_id'], saved['user_message_id'], anchors,
        segments, tuple(saved['omitted_summary_seqs']), tuple(FrozenMessage(**row) for row in saved['layer1']),
        tuple(FrozenMessage(**row) for row in saved['layer2']), budget)
    if (history_tokens((*snapshot.layer2, *snapshot.layer1)) > budget.history
            or _summary_cost(snapshot.summaries) > budget.summary):
        raise ServiceError('context_configuration_conflict', '暂停会话的上下文超出当前部署预算，请恢复兼容配置。', 409)
    return snapshot


class ContextCoordinator:
    def __init__(self, repository, manager, settings, *, context_logger=None):
        self.repository, self.manager, self.settings = repository, manager, settings
        self.logger = context_logger

    async def prepare(self, conversation_id: str, user_message_id: str, rows: Sequence[MessageRecord],
                      budget: ContextBudget) -> ContextSnapshot:
        # Only a competing SQL commit causes a fresh read; never wait for generation.
        for _ in range(3):
            anchors, summaries = await self.repository.load(conversation_id)
            try:
                plan = plan_layers(rows, anchors, budget, current_user_id=int(user_message_id))
            except ContextCapacityError:
                # Already eligible backlog must be admitted even when this turn cannot
                # reach on_completed. Otherwise every later turn repeats the failure.
                backlog = tuple(freeze_record(row) for row in rows
                    if (anchors.summary_upto or 0) < row.id <= (anchors.layer1_from or 0))
                if backlog:
                    self.manager.notify(conversation_id, layer2_tokens=history_tokens(_compact_layer2(backlog)), budget=budget)
                raise
            if plan.anchors.layer1_from != anchors.layer1_from:
                if not await self.repository.advance_layer1(conversation_id, expected=anchors,
                                                            upto_msg_id=plan.anchors.layer1_from):
                    continue
                if self.logger is not None:
                    self.logger.event('context_downgrade', dict(conversation_id=conversation_id,
                        user_message_id=user_message_id, old_l=str(anchors.layer1_from) if anchors.layer1_from else None,
                        new_l=str(plan.anchors.layer1_from), ranges=[[str(a), str(b)] for a, b in plan.downgrade_ranges],
                        layer1_tokens=plan.layer1_tokens, layer2_tokens=plan.layer2_tokens))
            result = build_snapshot(plan, summaries, conversation_id=conversation_id,
                                    user_message_id=user_message_id, budget=budget)
            if plan.layer2_tokens > budget.layer2:
                self.manager.notify(conversation_id, layer2_tokens=plan.layer2_tokens, budget=budget)
            return result
        raise ServiceError('context_conflict', '会话上下文正在更新，请重试。', 409)

    def on_completed(self, snapshot: ContextSnapshot) -> None:
        self.manager.notify(snapshot.conversation_id, layer2_tokens=history_tokens(snapshot.layer2), budget=snapshot.budget)
