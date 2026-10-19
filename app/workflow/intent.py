"""严格八意图 JSON 分类；明确整句社交使用零调用规则。"""
import asyncio
import math
import re
from dataclasses import dataclass
from typing import Literal

import httpx
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from openai import APITimeoutError, ContentFilterFinishReasonError, LengthFinishReasonError
from pydantic import BaseModel, ConfigDict, Field

from app.agent.controls import UsageLedger, estimate_call_input, record_usage
from app.core.errors import InputTooLong, ServiceError
from app.core.extraction import invalid_output, validate_structured_output
from app.workflow.prompts import build_intent_messages
from app.workflow.prompts import INTENT_SYSTEM
from app.context.view import compose_call


def intent_packet(raw_question, snapshot, *, resolved_question=None, output_tokens=2048, ticket_request=None):
    attachment = {'resolved_question': resolved_question or raw_question}
    if ticket_request:
        attachment['ticket_request'] = {'active': True, 'origin_user_message_id': ticket_request['origin_user_message_id']}
    return compose_call(snapshot, system=SystemMessage(INTENT_SYSTEM),
        current=HumanMessage(resolved_question or raw_question, id=snapshot.user_message_id),
        attachment=attachment, pending=(), tools=(),
        output_tokens=output_tokens)


Intent = Literal['物流','订单','商品咨询','退款退货','售后','投诉','闲聊','其他','工单']
Route = Literal['knowledge','business','after_sales','complaint','social','other']
_SOCIAL = re.compile(r'(?:你好|您好|嗨|哈喽|谢谢(?:你|您)?|多谢|辛苦了|再见|拜拜|早上好|下午好|晚上好)[！!。.?？\s]*')
_ROUTES = {'工单': 'business', '商品咨询': 'knowledge', '退款退货': 'after_sales', '物流': 'business',
           '订单': 'business', '售后': 'after_sales', '投诉': 'complaint', '闲聊': 'social', '其他': 'other'}


@dataclass(frozen=True)
class IntentResult:
    """模型原始标签与工程阈值后的有效标签独立保留。"""
    raw_intent: Intent
    intent: Intent
    confidence: float


class _IntentOutput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    intent: Intent
    confidence: float = Field(ge=0, le=1, allow_inf_nan=False)


def has_explicit_ticket_request(text: str) -> bool:
    """Trusted write evidence only; LLM still selects business intent."""
    if re.search(r'(?:不要|不想|不需要|不用|不必|别|不|没|未|取消)[^，。！？!?,;；\n]{0,12}(?:工单|建单|提交)|(?:怎么|如何)[^，。！？!?,;；\n]{0,10}(?:工单|建单)', text):
        return False
    if re.search(r'(?:能不能|可以)[^，。！？!?,;；\n]{0,10}(?:工单|建单)', text) and not re.search(r'(?:帮我|给我|我要|我想|请)', text):
        return False
    return re.search(r'(?:帮我|给我|我要|我想|请)[^，。！？!?,;；\n]{0,12}(?:建|创建|提交|开)[个一张份]*[^，。！？!?,;；\n]{0,8}工单|(?:创建|提交|建|开)[个一张份]*(?:售后|投诉|咨询)?工单', text) is not None


def social_fast_path(raw_question: str) -> bool:
    """仅整句固定问候、感谢、告别命中，业务内容不会因问候被吞掉。"""
    return isinstance(raw_question, str) and _SOCIAL.fullmatch(raw_question.strip()) is not None


def route_intent(intent: Intent) -> Route:
    """八类固定映射；非法标签显式报错，不能悄悄降级。"""
    return _ROUTES[intent]


class IntentClassifier:
    """调用方拥有模型；合法输出必须与 untouched JSON 完全一致。"""

    def __init__(self, model, *, input_budget: int, timeout_seconds: float):
        """绑定严格 JSON 模式及原始响应，保存输入/超时约束。"""
        if type(input_budget) is not int or input_budget <= 0:
            raise ValueError('intent input budget must be positive')
        if type(timeout_seconds) not in (int, float) or not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError('intent timeout must be finite and positive')
        self.model = model.with_structured_output(_IntentOutput, method='json_mode', include_raw=True)
        self.input_budget, self.timeout_seconds = input_budget, timeout_seconds
        self.usage = {'actual': 0, 'estimated': 0, 'actual_calls': 0, 'estimated_calls': 0}

    async def classify(self, raw_question: str, *, snapshot=None, resolved_question=None,
                       context_logger=None, call_index=2, output_tokens=2048, ticket_request=None) -> IntentResult:
        """只处理本轮原话；无效 JSON、非 stop 或上游故障全部保持错误。"""
        if not isinstance(raw_question, str) or not raw_question.strip():
            raise ValueError('raw question must be nonempty')
        self.usage = dict.fromkeys(self.usage, 0)
        if social_fast_path(raw_question):
            return IntentResult('闲聊', '闲聊', 1.0)
        packet = intent_packet(raw_question, snapshot, resolved_question=resolved_question,
                               output_tokens=output_tokens, ticket_request=ticket_request) if snapshot else None
        messages = list(packet.messages) if packet else build_intent_messages(raw_question)
        if packet is None and ticket_request:
            messages.append(HumanMessage('当前为用户主动要求建单后的补充轮，先核对是否仍在补充问题描述；明确切换/否定优先。'))
        cost = packet.estimated_tokens if packet is not None else estimate_call_input(messages, [])
        if packet is None and cost > self.input_budget:
            raise InputTooLong()
        # 调用已开始即保守计费；有原始实测响应时在协议校验前替换。
        ledger = UsageLedger()
        record_usage(None, ledger, estimated_input=cost, output_limit=output_tokens)
        self.usage = {key: getattr(ledger, key) for key in self.usage}
        output = None
        try:
            async with asyncio.timeout(self.timeout_seconds):
                if context_logger is not None and packet is not None:
                    context_logger.history(snapshot, consumer='classification', packet=packet, sent=True)
                    context_logger.model(packet, conversation_id=snapshot.conversation_id,
                        user_message_id=snapshot.user_message_id, phase='classification', call_index=call_index)
                output = await self.model.ainvoke(messages)
        except LengthFinishReasonError as exc:
            raise invalid_output(finish_reason='length') from exc
        except ContentFilterFinishReasonError as exc:
            raise invalid_output(finish_reason='content_filter') from exc
        except (TimeoutError, httpx.TimeoutException, APITimeoutError) as exc:
            raise ServiceError('upstream_timeout', '模型响应超时，请稍后重试。', 504) from exc
        except Exception as exc:
            raise ServiceError('upstream_error', '模型服务暂时不可用，请稍后重试。', 502) from exc
        finally:
            if packet is not None:
                from app.context.logging import log_calibration
                log_calibration(context_logger, packet, output.get('raw') if isinstance(output, dict) else None,
                                phase='classification')
        raw = output.get('raw') if isinstance(output, dict) else None
        ledger = UsageLedger()
        record_usage(raw, ledger, estimated_input=cost, output_limit=output_tokens)
        self.usage = {key: getattr(ledger, key) for key in self.usage}
        try:
            if (not isinstance(raw, AIMessage) or raw.response_metadata.get('finish_reason') != 'stop'
                    or raw.tool_calls or raw.invalid_tool_calls or raw.additional_kwargs.get('tool_calls')):
                raise invalid_output(finish_reason=raw.response_metadata.get('finish_reason') if isinstance(raw, AIMessage) else None)
            result = validate_structured_output(output, _IntentOutput)
            if result.intent == '工单' and not (ticket_request or has_explicit_ticket_request(raw_question)):
                raise invalid_output()
        except ServiceError:
            if context_logger is not None and snapshot is not None:
                try:
                    text = raw.text if isinstance(raw, AIMessage) else ''
                    finish = raw.response_metadata.get('finish_reason') if isinstance(raw, AIMessage) else None
                    context_logger.event('intent_control_rejected', {
                        'conversation_id': snapshot.conversation_id, 'user_message_id': snapshot.user_message_id,
                        'snapshot_id': snapshot.snapshot_id,
                        'finish_reason': finish if type(finish) is str and finish in (
                            'stop', 'length', 'content_filter', 'tool_calls', 'function_call') else None,
                        'control_text': text[:8192], 'control_text_length': len(text),
                        'control_text_truncated': len(text) > 8192})
                except Exception:
                    # Optional evidence must never replace the original rejection or expose its body.
                    pass
            raise
        return IntentResult(result.intent, result.intent if result.confidence >= 0.70 else '其他', result.confidence)
