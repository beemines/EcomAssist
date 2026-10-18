"""一次严格 JSON 调用完成指代理解和口语归一，不在此处分类或查询订单。"""
import asyncio
import math
import re
import json
from dataclasses import dataclass

import httpx
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from openai import APITimeoutError, ContentFilterFinishReasonError, LengthFinishReasonError
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.agent.controls import UsageLedger, estimate_call_input, record_usage
from app.core.errors import ServiceError
from app.core.extraction import invalid_output, validate_structured_output
from app.core.tool_history import build_tool_messages
from app.workflow.entities import completed_history, validate_resolved_entities
from app.workflow.entities import validate_snapshot_entities
from app.context.view import compose_call
from app.context.tokens import estimate_text_tokens
from app.core.errors import InputTooLong
from app.workflow.intent import social_fast_path
from app.workflow.prompts import UNDERSTANDING_SYSTEM


_LEADING_GREETING = re.compile(r'^(?:你好|您好|嗨|哈喽)[，,！!。\.\s]+')


def build_understanding_messages(raw_question: str, history: list[BaseMessage], budget: int) -> list[BaseMessage]:
    """先校验完整轮次，再仅投影订单来源配对；原整轮预算裁剪仍最后执行。"""
    turns = []
    for turn in completed_history(history):
        kept = [turn[0]]
        for request, result in zip(turn[1:-1:2], turn[2:-1:2]):
            if request.tool_calls[0]['name'] in {'query_order', 'query_logistics'}:
                # 原错误结果也原样保留，事实资格仍由实际保留消息的实体校验决定。
                kept.extend((request, result))
        turns.append([*kept, turn[-1]])
    return build_tool_messages(SystemMessage(UNDERSTANDING_SYSTEM), turns,
        HumanMessage(raw_question), budget, tool_schema=[])


def preserve_dropped_greeting(raw_question: str, resolved_question: str) -> str:
    """仅模型删去明确问候且后缀逐字相同时还原原话，不推断任何业务语义。"""
    prefix = _LEADING_GREETING.match(raw_question)
    if prefix is not None and raw_question[prefix.end():] == resolved_question:
        return raw_question
    return resolved_question


def understanding_packet(raw_question, snapshot, *, output_tokens=2048):
    return compose_call(snapshot, system=SystemMessage(UNDERSTANDING_SYSTEM),
        current=HumanMessage(raw_question, id=snapshot.user_message_id), attachment={},
        pending=(), tools=(), output_tokens=output_tokens)


@dataclass(frozen=True)
class Resolution:
    """改写标记由服务端比较原话计算，不要求模型输出额外字段。"""
    query: str
    changed: bool


class _UnderstandingOutput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    query: str = Field(min_length=1, max_length=20000)

    @field_validator('query')
    @classmethod
    def nonblank_query(cls, value: str) -> str:
        """拒绝全空白结果，但不去掉完整问题原有空白。"""
        if not value.strip():
            raise ValueError('query must be nonblank')
        return value


class QueryUnderstanding:
    """读取调用方提供的本会话历史，复用原整轮裁剪与 usage 账本。"""

    def __init__(self, model, *, input_budget: int, timeout_seconds: float):
        """绑定独立 query Schema 与原始输出，约束输入和单次超时。"""
        if type(input_budget) is not int or input_budget <= 0:
            raise ValueError('understanding input budget must be positive')
        if type(timeout_seconds) not in (int, float) or not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError('understanding timeout must be finite and positive')
        self.model = model.with_structured_output(_UnderstandingOutput, method='json_mode', include_raw=True)
        self.input_budget, self.timeout_seconds = input_budget, timeout_seconds
        self.usage = {'actual': 0, 'estimated': 0, 'actual_calls': 0, 'estimated_calls': 0}

    async def resolve(self, raw_question: str, history: list[BaseMessage], *, snapshot=None,
                      provenance=(), context_logger=None, call_index=1, output_tokens=2048) -> Resolution:
        """社交原样快路，其余只信预算内完整历史；非法输出保持服务错误。"""
        if not isinstance(raw_question, str) or not raw_question.strip():
            raise ValueError('raw question must be nonempty')
        self.usage = dict.fromkeys(self.usage, 0)
        if social_fast_path(raw_question):
            return Resolution(raw_question, False)
        if len(raw_question) > 20000 or estimate_text_tokens(json.dumps({'query': raw_question}, ensure_ascii=False)) > output_tokens:
            raise InputTooLong()
        packet = understanding_packet(raw_question, snapshot, output_tokens=output_tokens) if snapshot else None
        messages = list(packet.messages) if packet else build_understanding_messages(raw_question, history, self.input_budget)
        cost = packet.estimated_tokens if packet is not None else estimate_call_input(messages, [])
        # 调用已开始即保守计费；有原始实测响应时在协议校验前替换。
        ledger = UsageLedger()
        record_usage(None, ledger, estimated_input=cost, output_limit=output_tokens)
        self.usage = {key: getattr(ledger, key) for key in self.usage}
        output = None
        try:
            async with asyncio.timeout(self.timeout_seconds):
                if context_logger is not None and packet is not None:
                    context_logger.history(snapshot, consumer='understanding', packet=packet, sent=True)
                    context_logger.model(packet, conversation_id=snapshot.conversation_id,
                        user_message_id=snapshot.user_message_id, phase='understanding', call_index=call_index)
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
                                phase='understanding')
        raw = output.get('raw') if isinstance(output, dict) else None
        ledger = UsageLedger()
        record_usage(raw, ledger, estimated_input=cost, output_limit=output_tokens)
        self.usage = {key: getattr(ledger, key) for key in self.usage}
        rejection = 'raw'
        try:
            if (not isinstance(raw, AIMessage) or raw.response_metadata.get('finish_reason') != 'stop'
                    or raw.tool_calls or raw.invalid_tool_calls or raw.additional_kwargs.get('tool_calls')):
                raise invalid_output(finish_reason=raw.response_metadata.get('finish_reason') if isinstance(raw, AIMessage) else None)
            rejection = 'schema'
            result = validate_structured_output(output, _UnderstandingOutput)
            query = preserve_dropped_greeting(raw_question, result.query)
            if snapshot is None and len(query) > 512:
                raise invalid_output()  # Legacy callers retain the old contract until activation.
            if estimate_text_tokens(json.dumps({'query': query}, ensure_ascii=False)) > output_tokens:
                raise invalid_output()
            rejection = 'entity'
            if snapshot is not None:
                validate_snapshot_entities(raw_question, query, snapshot, provenance)
            else:
                validate_resolved_entities(raw_question, query, messages[1:-1])
        except ServiceError:
            if context_logger is not None and snapshot is not None:
                try:
                    text = raw.text if isinstance(raw, AIMessage) else ''
                    finish = raw.response_metadata.get('finish_reason') if isinstance(raw, AIMessage) else None
                    context_logger.event('understanding_control_rejected', {
                        'conversation_id': snapshot.conversation_id, 'user_message_id': snapshot.user_message_id,
                        'snapshot_id': snapshot.snapshot_id, 'rejection': rejection, 'call_index': call_index,
                        'finish_reason': finish if type(finish) is str and finish in (
                            'stop', 'length', 'content_filter', 'tool_calls', 'function_call') else None,
                        'control_text': text[:8192], 'control_text_length': len(text),
                        'control_text_truncated': len(text) > 8192})
                except Exception:
                    pass
            raise

        return Resolution(query, query != raw_question)
