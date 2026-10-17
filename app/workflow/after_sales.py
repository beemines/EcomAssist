"""订单锚定、售后控制与完成答案的申请许可；不执行退款写入。"""
from copy import deepcopy
from typing import Literal
from uuid import uuid4

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.core.extraction import invalid_output, validate_structured_output
from app.workflow.entities import explicit_order_ids, validate_resolved_entities


from app.workflow.controls import UnifiedAgentControl, parse_control, validate_control

AfterSalesControl = UnifiedAgentControl


def resolve_order_anchor(raw_question: str, resolved_question: str, history: list[BaseMessage]) -> str | None:
    """只用Task2可追溯明确订单实体，不从型号或候选列表猜订单。"""
    validate_resolved_entities(raw_question, resolved_question, history)
    identifiers = explicit_order_ids(raw_question) or explicit_order_ids(resolved_question)
    return next(iter(identifiers)) if len(identifiers) == 1 else None


def parse_after_sales_control(reply, intent: str) -> AfterSalesControl:
    return parse_control(reply, route='after_sales', intent=intent)


def validate_after_sales_control(control: AfterSalesControl, intent: str) -> AfterSalesControl:
    return validate_control(control, route='after_sales', intent=intent)

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
