"""退款显式确认：不可变完成根与SQL归属提供权限，不调用Agent工具。"""
import json
from uuid import UUID

from pydantic import ValidationError

from app.core.errors import ServiceError
from app.orders.types import OrderSnapshot
from app.refunds.types import REFUND_REASONS, RefundActionRequest, RefundDraft, RefundOfferLocator, RefundReceipt
from app.repositories.conversations import _conversation_id
from app.workflow.logging import log_audit
from app.workflow.persistence import checkpoint_config, durable_completed_root


def _invalid():
    """统一拒绝不合法退款许可，避免暴露原始快照内容。"""
    return ServiceError('invalid_refund_action', '该回复不允许提交退款申请。', 422)


class RefundActionService:
    """共用聊天会话锁，只读原历史根并构造服务器草稿。"""
    def __init__(self, graph, repository, refunds, checkpointer, locks):
        """复用真实图、SQL仓储、saver与当前会话占用服务。"""
        self.graph, self.repository, self.refunds = graph, repository, refunds
        self.checkpointer, self.locks = checkpointer, locks

    async def _draft(self, conversation_id: str, payload: RefundOfferLocator, *, offer_id=None) -> RefundDraft:
        """提交和只读刷新共用不可变根、实际耐久性、SQL归属及原轮校验。"""
        snapshot = await self.graph.aget_state(checkpoint_config(conversation_id, checkpoint_id=payload.checkpoint_id))
        state, saved = snapshot.values, snapshot.config.get('configurable', {})
        if (not state or saved.get('thread_id') != conversation_id or saved.get('checkpoint_ns') != ''
                or saved.get('checkpoint_id') != payload.checkpoint_id):
            raise ServiceError('action_not_found', '完成快照不存在。', 404)
        if (snapshot.next or state.get('state_version') != 2 or state.get('turn_status') != 'completed'
                or state.get('conversation_id') != conversation_id
                or state.get('final_message_id') != payload.assistant_message_id
                or state.get('intent') != '退款退货' or state.get('route') != 'after_sales'
                or state.get('quality', {}).get('useful') is not True or state.get('reply_mode') != 'answer'
                or state.get('refund_decision') not in ('eligible', 'needs_review')
                or not state.get('decision_reason') or not state.get('final_answer')
                or not await durable_completed_root(self.checkpointer, snapshot, conversation_id,
                    checkpoint_id=payload.checkpoint_id)):
            raise _invalid()
        offer = state.get('refund_offer')
        if (not isinstance(offer, dict) or (offer_id is not None and offer.get('offer_id') != offer_id)
                or offer.get('assistant_message_id') != payload.assistant_message_id
                or offer.get('turn_id') != state.get('user_message_id')
                or offer.get('order_snapshot') != state.get('order_snapshot')
                or not offer.get('policy_snapshot') or offer.get('policy_snapshot') != state.get('evidence_payload')
                or offer.get('refund_decision') != state.get('refund_decision')
                or offer.get('decision_reason') != state.get('decision_reason')):
            raise _invalid()
        try:
            server_offer_id = offer.get('offer_id')
            if not isinstance(server_offer_id, str) or str(UUID(server_offer_id)) != server_offer_id:
                raise ValueError('invalid server offer identity')
            uid = _conversation_id(state.get('user_message_id'))
            order = OrderSnapshot.model_validate_json(json.dumps(offer['order_snapshot'], allow_nan=False))
        except (ServiceError, ValidationError, ValueError, TypeError):
            raise _invalid() from None
        owner = await self.repository.get_user_id(conversation_id)
        rows = await self.repository.load_messages(conversation_id)
        aid = int(payload.assistant_message_id)
        user = next((r for r in rows if r.id == uid), None)
        assistant = next((r for r in rows if r.id == aid), None)
        if (order.user_id != owner or user is None or user.role != 'user'
                or user.content != state.get('raw_question') or not user.content or not user.content.strip()
                or assistant is None or assistant.role != 'assistant' or assistant.tool_calls is not None
                or assistant.content != state.get('final_answer') or uid >= aid
                or any(r.role == 'user' and uid < r.id < aid for r in rows)):
            raise _invalid()
        draft = RefundDraft(conversation_id=conversation_id, user_message_id=str(uid),
            assistant_message_id=payload.assistant_message_id, checkpoint_id=payload.checkpoint_id,
            offer_id=offer['offer_id'], user_id=owner, order_id=order.order_id,
            amount_cents=order.amount_cents, currency=order.currency,
            order_snapshot=offer['order_snapshot'], policy_snapshot=offer['policy_snapshot'],
            decision_snapshot={'refund_decision': offer['refund_decision'], 'decision_reason': offer['decision_reason']},
            raw_question=user.content, final_answer=assistant.content)
        return draft

    async def offer(self, conversation_id: str, payload: RefundOfferLocator) -> dict:
        """刷新复用原根权限校验，只投影既有公开字段，不写MySQL或检查点。"""
        _conversation_id(conversation_id)
        lease = self.locks.acquire(conversation_id)
        try:
            draft = await self._draft(conversation_id, payload)
            order = OrderSnapshot.model_validate_json(json.dumps(draft.order_snapshot))
            decision = draft.decision_snapshot
            return {'assistant_message_id': draft.assistant_message_id, 'checkpoint_id': draft.checkpoint_id,
                'offer_id': draft.offer_id, 'order': order.to_card(),
                'refund_decision': decision['refund_decision'], 'decision_reason': decision['decision_reason'],
                'reasons': [{'code': code, 'label': label} for code, label in REFUND_REASONS]}
        finally:
            lease.release()

    async def submit(self, conversation_id: str, payload: RefundActionRequest) -> RefundReceipt:
        """原根许可和原轮SQL通过后保存待审申请，成功提交后才审计返回。"""
        _conversation_id(conversation_id)
        lease = self.locks.acquire(conversation_id)
        try:
            draft = await self._draft(conversation_id, payload, offer_id=payload.offer_id)
            receipt = await self.refunds.create_pending(draft, payload.reason)
            log_audit('workflow_refund', phase='result', outcome='success', action='submit_refund',
                conversation_id=conversation_id, user_message_id=draft.user_message_id,
                assistant_message_id=draft.assistant_message_id, request_no=receipt.request_no)
            return receipt
        finally:
            lease.release()
