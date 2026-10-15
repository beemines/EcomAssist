"""退款短事务与MySQL唯一键幂等，绝不执行支付或修改工单/订单。"""
import hashlib
import json
import math
import struct

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError

from app.core.errors import ServiceError
from app.db.models import Conversation, Message, RefundRequest
from app.repositories.conversations import _conversation_id, _require_conversation
from app.refunds.types import REFUND_REASONS, RefundDraft, RefundReason, RefundReceipt


def pending_key(user_id: str, order_id: str) -> str:
    """规范UTF-8 JSON数组编码身份，避免字符串拼接歧义。"""
    encoded = json.dumps([user_id, order_id], ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(encoded.encode('utf-8')).hexdigest()


def _conflict():
    """冲突只报告已有申请，不透露其他会话或用户收据。"""
    return ServiceError('refund_conflict', '该订单已有申请或表单内容与原申请冲突。', 409)


def _receipt(row):
    """仅从已提交或将由当前事务提交的记录投影固定结果。"""
    return RefundReceipt(request_no=row.request_no, status=row.status, order_id=row.order_id,
        amount_cents=row.amount_cents, currency=row.currency)


def same_policy_snapshot(stored, original, path=()):
    """仅matches[i].score允许已实测MySQL JSON往返的一ULP，业务/原文/结构严格相等。"""
    if type(stored) is not type(original):
        return False
    if isinstance(stored, dict):
        return stored.keys() == original.keys() and all(
            same_policy_snapshot(stored[key], original[key], (*path, key)) for key in stored)
    if isinstance(stored, list):
        return len(stored) == len(original) and all(
            same_policy_snapshot(a, b, (*path, index)) for index, (a, b) in enumerate(zip(stored, original)))
    if (len(path) == 3 and path[0] == 'matches' and type(path[1]) is int and path[2] == 'score'
            and type(stored) is float):
        if not math.isfinite(stored) or not math.isfinite(original):
            return False
        # 不按十进制截断、不忽略score；仅相邻IEEE754 double表示被视为同一存储值。
        first = struct.unpack('>Q', struct.pack('>d', stored))[0]
        second = struct.unpack('>Q', struct.pack('>d', original))[0]
        return abs(first - second) <= 1
    return stored == original


def _same_submission(row, draft, reason):
    """所有归属与原始业务字段相同才能返回原收据，绝不覆盖。"""
    return (row.offer_id == draft.offer_id and row.conversation_id == int(draft.conversation_id)
        and row.user_message_id == int(draft.user_message_id)
        and row.assistant_message_id == int(draft.assistant_message_id)
        and row.checkpoint_id == draft.checkpoint_id and row.user_id == draft.user_id
        and row.order_id == draft.order_id and row.reason == reason
        and row.amount_cents == draft.amount_cents and row.currency == draft.currency
        and row.order_snapshot == draft.order_snapshot and same_policy_snapshot(row.policy_snapshot, draft.policy_snapshot)
        and row.decision_snapshot == draft.decision_snapshot and row.status == '待审核')


class RefundRepository:
    """同会话行锁与跨会话pending_key唯一键共同保证只写一条。"""
    def __init__(self, database):
        """保存已注入数据库。"""
        self.database = database

    async def _existing(self, session, draft, reason):
        """读取同offer或同用户订单；只有完整同源重试能得到原收据。"""
        rows = (await session.scalars(select(RefundRequest).where(or_(
            RefundRequest.offer_id == draft.offer_id,
            RefundRequest.pending_key == pending_key(draft.user_id, draft.order_id))))).all()
        if not rows:
            return None
        if len(rows) == 1 and _same_submission(rows[0], draft, reason):
            return _receipt(rows[0])
        raise _conflict()

    async def _validate_turn(self, session, draft):
        """锁会话并重新核对owner、两条SQL消息及其间的原轮关系。"""
        cid = _conversation_id(draft.conversation_id)
        conversation = await session.scalar(select(Conversation).where(Conversation.id == cid).with_for_update())
        _require_conversation(conversation, open_only=False)
        rows = (await session.scalars(select(Message).where(Message.conversation_id == cid,
            Message.id >= int(draft.user_message_id), Message.id <= int(draft.assistant_message_id)))).all()
        user = next((r for r in rows if r.id == int(draft.user_message_id)), None)
        assistant = next((r for r in rows if r.id == int(draft.assistant_message_id)), None)
        if (conversation.user_id != draft.user_id or user is None or user.role != 'user'
                or user.content != draft.raw_question or assistant is None or assistant.role != 'assistant'
                or assistant.tool_calls is not None or assistant.content != draft.final_answer
                or int(draft.user_message_id) >= int(draft.assistant_message_id)
                or any(r.role == 'user' and r.id != user.id for r in rows)):
            raise ServiceError('invalid_refund_action', '回复与原用户消息不匹配。', 422)
        return conversation

    async def create_pending(self, draft: RefundDraft, reason: RefundReason) -> RefundReceipt:
        """事务提交后返回待审；1062退出失败事务，再用新Session核对同源幂等。"""
        if reason not in dict(REFUND_REASONS):
            raise ServiceError('invalid_refund_action', '退款原因不合法。', 422)
        try:
            async with self.database.session() as session, session.begin():
                conversation = await self._validate_turn(session, draft)
                receipt = await self._existing(session, draft, reason)
                if receipt is None:
                    _require_conversation(conversation)
                    row = RefundRequest(request_no='R' + hashlib.sha256(draft.offer_id.encode('utf-8')).hexdigest(),
                        conversation_id=int(draft.conversation_id), user_message_id=int(draft.user_message_id),
                        assistant_message_id=int(draft.assistant_message_id), checkpoint_id=draft.checkpoint_id,
                        offer_id=draft.offer_id, user_id=draft.user_id, order_id=draft.order_id,
                        pending_key=pending_key(draft.user_id, draft.order_id), reason=reason,
                        amount_cents=draft.amount_cents, currency=draft.currency,
                        order_snapshot=draft.order_snapshot, policy_snapshot=draft.policy_snapshot,
                        decision_snapshot=draft.decision_snapshot)
                    session.add(row)
                    await session.flush()
                    await session.refresh(row)
                    receipt = _receipt(row)
            return receipt
        except IntegrityError as exc:
            if not getattr(exc.orig, 'args', ()) or exc.orig.args[0] != 1062:
                raise
            # 原事务上下文已回滚并关闭，不能在失败Session中继续读。
            async with self.database.session() as session, session.begin():
                await self._validate_turn(session, draft)
                receipt = await self._existing(session, draft, reason)
                if receipt is None:
                    raise _conflict() from exc
                return receipt
