"""纯退款协议与不可变服务器草稿，不依赖数据库或Workflow。"""
from dataclasses import dataclass
import json
import re
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


RefundReason = Literal['unwanted', 'quality', 'not_as_described', 'wrong_or_missing', 'damaged', 'other']
REFUND_REASONS = (('unwanted', '不想要了'), ('quality', '质量问题'), ('not_as_described', '与描述不符'),
    ('wrong_or_missing', '发错/漏发'), ('damaged', '运输破损'), ('other', '其他'))


class RefundOfferLocator(BaseModel):
    """刷新只接受原助手消息与原完成根两个结构定位字段。"""
    model_config = ConfigDict(extra='forbid', strict=True)
    assistant_message_id: str = Field(min_length=1, max_length=20)
    checkpoint_id: str = Field(min_length=1, max_length=128)

    @field_validator('assistant_message_id')
    @classmethod
    def valid_message(cls, value):
        """仅接受无前导零的正BIGINT字符串。"""
        if not re.fullmatch(r'[1-9][0-9]{0,19}', value) or int(value) > 18446744073709551615:
            raise ValueError('invalid assistant identity')
        return value

    @field_validator('checkpoint_id')
    @classmethod
    def valid_uuid(cls, value):
        """拒绝非规范UUID及带子图路径的定位。"""
        if str(UUID(value)) != value:
            raise ValueError('invalid immutable identity')
        return value


class RefundActionRequest(RefundOfferLocator):
    """浏览器提交额外提供原表单offer与必选原因，恰好四字段。"""
    offer_id: str = Field(min_length=1, max_length=64)
    reason: RefundReason

    @field_validator('offer_id')
    @classmethod
    def valid_offer(cls, value):
        """表单身份同样必须是服务器生成的规范UUID。"""
        if str(UUID(value)) != value:
            raise ValueError('invalid offer identity')
        return value


@dataclass(frozen=True, init=False)
class RefundDraft:
    """服务器内部草稿；JSON按值冻结，读取快照返回副本。"""
    conversation_id: str
    user_message_id: str
    assistant_message_id: str
    checkpoint_id: str
    offer_id: str
    user_id: str
    order_id: str
    amount_cents: int
    currency: str
    raw_question: str
    final_answer: str
    _order_json: str
    _policy_json: str
    _decision_json: str

    def __init__(self, *, conversation_id, user_message_id, assistant_message_id, checkpoint_id,
            offer_id, user_id, order_id, amount_cents, currency, order_snapshot, policy_snapshot,
            decision_snapshot, raw_question, final_answer):
        """只接收服务已核验的原轮身份和事实，序列化切断所有可变别名。"""
        values = locals().copy()
        for name in ('conversation_id', 'user_message_id', 'assistant_message_id', 'checkpoint_id',
                'offer_id', 'user_id', 'order_id', 'amount_cents', 'currency', 'raw_question', 'final_answer'):
            object.__setattr__(self, name, values[name])
        for name, data in (('_order_json', order_snapshot), ('_policy_json', policy_snapshot),
                ('_decision_json', decision_snapshot)):
            object.__setattr__(self, name, json.dumps(data, ensure_ascii=False, allow_nan=False, separators=(',', ':')))

    @property
    def order_snapshot(self):
        """返回订单事实副本，不开放草稿内部写入。"""
        return json.loads(self._order_json)

    @property
    def policy_snapshot(self):
        """返回当时完整政策副本。"""
        return json.loads(self._policy_json)

    @property
    def decision_snapshot(self):
        """返回独立于用户表单原因的模型判断副本。"""
        return json.loads(self._decision_json)


class RefundReceipt(BaseModel):
    """提交完成后唯一公开的待审核结果。"""
    model_config = ConfigDict(extra='forbid', strict=True, frozen=True)
    request_no: str
    status: Literal['待审核'] = '待审核'
    order_id: str
    amount_cents: int = Field(ge=0)
    currency: Literal['CNY']
