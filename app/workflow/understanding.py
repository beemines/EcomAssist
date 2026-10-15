"""一次严格 JSON 调用完成指代理解和口语归一，不在此处分类或查询订单。"""
import asyncio
import math
import re
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
from app.workflow.intent import social_fast_path
from app.workflow.prompts import UNDERSTANDING_SYSTEM


_LEADING_GREETING = re.compile(r'^(?:你好|您好|嗨|哈喽)[，,！!。\.\s]+')


def preserve_dropped_greeting(raw_question: str, resolved_question: str) -> str:
    """仅模型删去明确问候且后缀逐字相同时还原原话，不推断任何业务语义。"""
    prefix = _LEADING_GREETING.match(raw_question)
    if prefix is not None and raw_question[prefix.end():] == resolved_question:
        return raw_question
    return resolved_question


@dataclass(frozen=True)
class Resolution:
    """改写标记由服务端比较原话计算，不要求模型输出额外字段。"""
    query: str
    changed: bool


class _UnderstandingOutput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    query: str = Field(min_length=1, max_length=512)

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

    async def resolve(self, raw_question: str, history: list[BaseMessage]) -> Resolution:
        """社交原样快路，其余只信预算内完整历史；非法输出保持服务错误。"""
        if not isinstance(raw_question, str) or not raw_question.strip():
            raise ValueError('raw question must be nonempty')
        self.usage = dict.fromkeys(self.usage, 0)
        if social_fast_path(raw_question):
            return Resolution(raw_question, False)
        messages = build_tool_messages(SystemMessage(UNDERSTANDING_SYSTEM), completed_history(history),
            HumanMessage(raw_question), self.input_budget, tool_schema=[])
        cost = estimate_call_input(messages, [])
        # 调用已开始即保守计费；有原始实测响应时在协议校验前替换。
        ledger = UsageLedger()
        record_usage(None, ledger, estimated_input=cost, output_limit=2048)
        self.usage = {key: getattr(ledger, key) for key in self.usage}
        try:
            async with asyncio.timeout(self.timeout_seconds):
                output = await self.model.ainvoke(messages)
        except LengthFinishReasonError as exc:
            raise invalid_output(finish_reason='length') from exc
        except ContentFilterFinishReasonError as exc:
            raise invalid_output(finish_reason='content_filter') from exc
        except (TimeoutError, httpx.TimeoutException, APITimeoutError) as exc:
            raise ServiceError('upstream_timeout', '模型响应超时，请稍后重试。', 504) from exc
        except Exception as exc:
            raise ServiceError('upstream_error', '模型服务暂时不可用，请稍后重试。', 502) from exc
        raw = output.get('raw') if isinstance(output, dict) else None
        ledger = UsageLedger()
        record_usage(raw, ledger, estimated_input=cost, output_limit=2048)
        self.usage = {key: getattr(ledger, key) for key in self.usage}
        if (not isinstance(raw, AIMessage) or raw.response_metadata.get('finish_reason') != 'stop'
                or raw.tool_calls or raw.invalid_tool_calls or raw.additional_kwargs.get('tool_calls')):
            raise invalid_output(finish_reason=raw.response_metadata.get('finish_reason') if isinstance(raw, AIMessage) else None)
        result = validate_structured_output(output, _UnderstandingOutput)
        query = preserve_dropped_greeting(raw_question, result.query)
        validate_resolved_entities(raw_question, query, messages[1:-1])

        return Resolution(query, query != raw_question)
