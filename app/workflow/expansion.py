"""订单已明确后的严格查询扩写；不猜售后事实，不降级旧规划协议。"""
import asyncio
import json
import math
from typing import Annotated

import httpx
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from openai import APITimeoutError, ContentFilterFinishReasonError, LengthFinishReasonError
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.agent.controls import UsageLedger, estimate_call_input, record_usage
from app.core.errors import InputTooLong, ServiceError
from app.core.extraction import invalid_output, validate_structured_output
from app.orders.types import OrderSnapshot
from app.retrieval.service import _caller_cancellation, _exception_chain
from app.workflow.prompts import EXPANSION_SYSTEM
from app.workflow.context_budget import stage_packet, standalone_packet
from app.context.logging import log_model_call, log_calibration
from app.context.tokens import estimate_payload


class _ExpansionOutput(BaseModel):
    """原始协议只有2～3条完整查询，不接收旧短词扩展协议。"""
    model_config = ConfigDict(extra='forbid', strict=True)
    queries: list[Annotated[str, Field(min_length=1, max_length=512)]] = Field(min_length=2, max_length=3)

    @field_validator('queries')
    @classmethod
    def nonblank_queries(cls, value: list[str]) -> list[str]:
        """保留原文空白，但拒绝不能形成检索文本的空白项。"""
        if any(not query.strip() for query in value):
            raise ValueError('queries must be nonblank')
        return value


class QueryExpander:
    """复用理解器的单次期限、严格原始响应及 usage 口径。"""
    def __init__(self, model, *, input_budget: int, timeout_seconds: float):
        """绑定调用方模型，不创建客户端或改变模型、重试配置。"""
        if type(input_budget) is not int or input_budget <= 0:
            raise ValueError('expansion input budget must be positive')
        if type(timeout_seconds) not in (int, float) or not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError('expansion timeout must be finite and positive')
        self.model = model.with_structured_output(_ExpansionOutput, method='json_mode', include_raw=True)
        self.input_budget, self.timeout_seconds = input_budget, timeout_seconds
        self.usage = {'actual': 0, 'estimated': 0, 'actual_calls': 0, 'estimated_calls': 0}

    async def expand(self, question: str, order: OrderSnapshot, *, snapshot=None, raw_question=None,
                     context_logger=None, on_packet=None, on_calibration=None, output_tokens=2048) -> tuple[str, ...]:
        """原问题首条逐字保留；重复归一空白后不足两条视为坏协议。"""
        self.usage = dict.fromkeys(self.usage, 0)
        if not isinstance(question, str) or not question.strip():
            raise ValueError('question must be nonempty text')
        if len(question) > 512:
            raise InputTooLong()
        if not isinstance(order, OrderSnapshot):
            raise ValueError('order must be an OrderSnapshot')
        messages = [SystemMessage(EXPANSION_SYSTEM), HumanMessage(json.dumps(
            {'question': question, 'order': order.model_dump(mode='json')}, ensure_ascii=False))]
        packet = (stage_packet(snapshot, system=messages[0], raw_question=raw_question or question,
            attachment={'resolved_question': question, 'order': order.model_dump(mode='json')}, output_tokens=output_tokens)
            if snapshot is not None else standalone_packet(messages, output_tokens=output_tokens))
        messages, cost = packet.messages, packet.estimated_tokens
        if snapshot is None and cost > self.input_budget:
            raise InputTooLong()
        loop, task = asyncio.get_running_loop(), asyncio.current_task()
        deadline = loop.time() + self.timeout_seconds
        # 调用已开始即保守计费；有原始实测响应时在协议校验前替换。
        ledger = UsageLedger()
        record_usage(None, ledger, estimated_input=cost, output_limit=output_tokens)
        self.usage = {key: getattr(ledger, key) for key in self.usage}
        log_model_call(context_logger, packet, phase='expansion', on_packet=on_packet,
            conversation_id=snapshot.conversation_id if snapshot else None,
            user_message_id=snapshot.user_message_id if snapshot else None)
        output = None
        try:
            async with asyncio.timeout(self.timeout_seconds):
                output = await self.model.ainvoke(messages)
            if task is not None and task.cancelling():
                raise asyncio.CancelledError()
            if loop.time() >= deadline:
                raise TimeoutError()
        except LengthFinishReasonError as exc:
            raise invalid_output(finish_reason='length') from exc
        except ContentFilterFinishReasonError as exc:
            raise invalid_output(finish_reason='content_filter') from exc
        except (TimeoutError, httpx.TimeoutException, APITimeoutError) as exc:
            raise ServiceError('upstream_timeout', '模型响应超时，请稍后重试。', 504) from exc
        except Exception as exc:
            cancellation = _caller_cancellation(exc)
            if cancellation is not None:
                raise cancellation
            if task is not None and task.cancelling():
                raise asyncio.CancelledError() from None
            if any(isinstance(item, (TimeoutError, httpx.TimeoutException, APITimeoutError))
                   for item in _exception_chain(exc)):
                raise ServiceError('upstream_timeout', '模型响应超时，请稍后重试。', 504) from exc
            raise ServiceError('upstream_error', '模型服务暂时不可用，请稍后重试。', 502) from exc
        finally:
            log_calibration(context_logger, packet, output.get('raw') if isinstance(output, dict) else None,
                            phase='expansion', on_calibration=on_calibration)
        raw = output.get('raw') if isinstance(output, dict) else None
        ledger = UsageLedger()
        record_usage(raw, ledger, estimated_input=cost, output_limit=output_tokens)
        self.usage = {key: getattr(ledger, key) for key in self.usage}
        if (not isinstance(raw, AIMessage) or raw.response_metadata.get('finish_reason') != 'stop'
                or raw.tool_calls or raw.invalid_tool_calls or raw.additional_kwargs.get('tool_calls')):
            raise invalid_output(finish_reason=raw.response_metadata.get('finish_reason') if isinstance(raw, AIMessage) else None)
        result = validate_structured_output(output, _ExpansionOutput)
        if result.queries[0] != question:
            raise invalid_output()
        unique = {}
        for query in result.queries:
            unique.setdefault(''.join(query.split()), query)
        if len(unique) < 2:
            raise invalid_output()

        return tuple(unique.values())
