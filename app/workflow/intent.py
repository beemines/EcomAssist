"""严格七意图 JSON 分类；明确整句社交使用零调用规则。"""
import asyncio
import math
import re
from typing import Literal

import httpx
from langchain_core.messages import AIMessage
from openai import APITimeoutError, ContentFilterFinishReasonError, LengthFinishReasonError
from pydantic import BaseModel, ConfigDict

from app.agent.controls import UsageLedger, estimate_call_input, record_usage
from app.core.errors import InputTooLong, ServiceError
from app.core.extraction import invalid_output, validate_structured_output
from app.workflow.prompts import build_intent_messages


Intent = Literal['物流','订单','商品咨询','退款退货','售后','投诉','闲聊']
Route = Literal['knowledge','business','complaint','social']
_SOCIAL = re.compile(r'(?:你好|您好|嗨|哈喽|谢谢(?:你|您)?|多谢|辛苦了|再见|拜拜|早上好|下午好|晚上好)[！!。.?？\s]*')
_ROUTES = {'商品咨询': 'knowledge', '退款退货': 'knowledge', '物流': 'business',
           '订单': 'business', '售后': 'business', '投诉': 'complaint', '闲聊': 'social'}


class _IntentOutput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    intent: Intent


def social_fast_path(raw_question: str) -> bool:
    """仅整句固定问候、感谢、告别命中，业务内容不会因问候被吞掉。"""
    return isinstance(raw_question, str) and _SOCIAL.fullmatch(raw_question.strip()) is not None


def route_intent(intent: Intent) -> Route:
    """七类固定映射；非法标签显式报错，不能悄悄降级。"""
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

    async def classify(self, raw_question: str) -> Intent:
        """只处理本轮原话；无效 JSON、非 stop 或上游故障全部保持错误。"""
        if not isinstance(raw_question, str) or not raw_question.strip():
            raise ValueError('raw question must be nonempty')
        self.usage = dict.fromkeys(self.usage, 0)
        if social_fast_path(raw_question):
            return '闲聊'
        messages = build_intent_messages(raw_question)
        cost = estimate_call_input(messages, [])
        if cost > self.input_budget:
            raise InputTooLong()
        try:
            async with asyncio.timeout(self.timeout_seconds):
                output = await self.model.ainvoke(messages)
        except (LengthFinishReasonError, ContentFilterFinishReasonError) as exc:
            raise invalid_output() from exc
        except (TimeoutError, httpx.TimeoutException, APITimeoutError) as exc:
            raise ServiceError('upstream_timeout', '模型响应超时，请稍后重试。', 504) from exc
        except Exception as exc:
            raise ServiceError('upstream_error', '模型服务暂时不可用，请稍后重试。', 502) from exc
        raw = output.get('raw') if isinstance(output, dict) else None
        if (not isinstance(raw, AIMessage) or raw.response_metadata.get('finish_reason') != 'stop'
                or raw.tool_calls or raw.invalid_tool_calls or raw.additional_kwargs.get('tool_calls')):
            raise invalid_output()
        result = validate_structured_output(output, _IntentOutput)
        ledger = UsageLedger()
        record_usage(raw, ledger, estimated_input=cost, output_limit=2048)
        self.usage = {key: getattr(ledger, key) for key in self.usage}
        return result.intent
