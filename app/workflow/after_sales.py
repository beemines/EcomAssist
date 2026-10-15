"""订单锚定、售后控制与完成答案的申请许可；不执行退款写入。"""
from copy import deepcopy
from typing import Literal
from uuid import uuid4

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.core.extraction import invalid_output, validate_structured_output
from app.workflow.entities import explicit_order_ids, validate_resolved_entities


class AfterSalesControl(BaseModel):
    """仅用于已过政策闸的订单售后出口，保留严格原始协议。"""
    model_config = ConfigDict(extra='forbid', strict=True)
    reply_mode: Literal['answer', 'clarification']
    suggested_actions: list[Literal['handoff', 'create_ticket']] = Field(max_length=2)
    refund_decision: Literal['eligible', 'needs_review', 'ineligible', 'not_applicable']
    decision_reason: str = Field(min_length=1, max_length=256)

    @field_validator('decision_reason')
    @classmethod
    def nonblank_reason(cls, value):
        """拒绝空白理由，不能用缺失说明生成许可。"""
        if not value.strip():
            raise ValueError('decision reason must be nonblank')
        return value

    @field_validator('suggested_actions')
    @classmethod
    def unique_actions(cls, value):
        """动作建议按首次出现顺序去重。"""
        return list(dict.fromkeys(value))


def resolve_order_anchor(raw_question: str, resolved_question: str, history: list[BaseMessage]) -> str | None:
    """只用Task2可追溯明确订单实体，不从型号或候选列表猜订单。"""
    validate_resolved_entities(raw_question, resolved_question, history)
    identifiers = explicit_order_ids(raw_question) or explicit_order_ids(resolved_question)
    return next(iter(identifiers)) if len(identifiers) == 1 else None


def parse_after_sales_control(reply, intent: str) -> AfterSalesControl:
    """拒绝与办理方向或澄清相矛盾的申请判断，不从正文纠正。"""
    try:
        parsed = AfterSalesControl.model_validate_json(reply.text)
    except ValidationError as exc:
        raise invalid_output() from exc
    control = validate_structured_output({'raw': reply, 'parsed': parsed, 'parsing_error': None}, AfterSalesControl)
    if (intent == '售后' and control.refund_decision != 'not_applicable'
            or intent == '退款退货' and control.refund_decision == 'not_applicable'
            or control.reply_mode == 'clarification' and control.refund_decision in ('eligible', 'needs_review')):
        raise invalid_output()
    return control


def make_refund_offer(state) -> dict | None:
    """SQL最终答案保存后冻结许可快照；根检查点确认及公开发布由服务负责。"""
    if (state.get('state_version') != 2 or state.get('intent') != '退款退货'
            or state.get('route') != 'after_sales' or not state.get('order_snapshot')
            or state.get('quality', {}).get('useful') is not True or state.get('reply_mode') != 'answer'
            or state.get('refund_decision') not in ('eligible', 'needs_review')
            or not state.get('decision_reason') or not state.get('final_message_id')
            or state.get('turn_status') != 'completed' or not state.get('final_answer')):
        return None
    return deepcopy({'offer_id': str(uuid4()), 'assistant_message_id': state['final_message_id'],
        'turn_id': state['user_message_id'], 'order_snapshot': state['order_snapshot'],
        'policy_snapshot': state['evidence_payload'], 'refund_decision': state['refund_decision'],
        'decision_reason': state['decision_reason']})
