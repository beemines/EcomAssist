# 单轮查询理解：限时调用、原始 JSON 复核与确定性的保守约束保护。
import asyncio
import math
import re
from typing import Any

import httpx
from langchain_core.messages import AIMessage
from openai import APITimeoutError, ContentFilterFinishReasonError, LengthFinishReasonError

from app.core.errors import InputTooLong, ServiceError
from app.core.extraction import invalid_output, validate_structured_output
from app.core.memory import estimate_tokens
from app.core.prompts import build_query_messages
from app.retrieval.types import QueryPlan


# 不声称理解任意品牌语义：对型号、数值、否定和条件句直接保留整条原话。
_CONSTRAINT = re.compile(r'[A-Za-z0-9]|不|没|未|无|别|只|除|且|并|同时|如果|若|但是|但|才|内|超过|至少|最多')
# 中文连续内容保留原样，仅允许移除明确的提问语气，未知品牌自然留在内容段中。
_QUESTION_FILLER = re.compile(r'请问|麻烦|帮我|怎么|如何|咋办|咋整|能否|是否|可以|吗|呢|啊|呀')
_RETRIEVAL_FILLER = re.compile(r'流程|办理|申请|问题|政策|规定|方式|处理|查询')


# 仅放行原始内容与通用检索连接词；未知新增中文内容可能是品牌或条件，保守回退。
def _preserves_content(text: str, anchors: list[str]) -> bool:
    remainder = text
    for anchor in anchors:
        if anchor not in text:
            return False
        remainder = remainder.replace(anchor, '')
    remainder = _RETRIEVAL_FILLER.sub('', _QUESTION_FILLER.sub('', remainder))
    return not re.search(r'[\u4e00-\u9fff]', remainder)


def _safe_plan(raw_question: str, plan: QueryPlan) -> QueryPlan:
    if _CONSTRAINT.search(raw_question) or _CONSTRAINT.search(plan.standard):
        return QueryPlan(standard=raw_question, expansions=[])
    anchors = re.findall(r'[\u4e00-\u9fff]+', _QUESTION_FILLER.sub('', raw_question))
    if not anchors or not _preserves_content(plan.standard, anchors):
        return QueryPlan(standard=raw_question, expansions=[])
    # 扩展也须携带原始内容段，不能引入新的数字、型号或限制。
    expansions = [text for text in plan.expansions
                  if not _CONSTRAINT.search(text) and _preserves_content(text, anchors)]
    return QueryPlan(standard=plan.standard, expansions=expansions)


class QueryPlanner:
    def __init__(self, model: Any, input_budget: int, timeout: float = 15):
        if type(input_budget) is not int or input_budget <= 0:
            raise ValueError('input budget must be a positive integer')
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError('query timeout must be finite and positive')
        self.structured_model = model.with_structured_output(QueryPlan, method='json_mode', include_raw=True)
        self.input_budget, self.timeout = input_budget, timeout

    # 外部注入的模型由调用方关闭；取消不捕获、不重试，超时转换为统一上游错误。
    async def plan(self, raw_question: str) -> QueryPlan:
        if not isinstance(raw_question, str) or not raw_question.strip():
            raise ValueError('raw question must be nonempty text')
        messages = build_query_messages(raw_question)
        if len(raw_question) > 512 or estimate_tokens(messages) > self.input_budget:
            raise InputTooLong()
        try:
            async with asyncio.timeout(self.timeout):
                output = await self.structured_model.ainvoke(messages)
        except (LengthFinishReasonError, ContentFilterFinishReasonError) as exc:
            raise invalid_output() from exc
        except (TimeoutError, httpx.TimeoutException, APITimeoutError) as exc:
            raise ServiceError('upstream_timeout', '模型响应超时，请稍后重试。', 504) from exc
        except Exception as exc:
            raise ServiceError('upstream_error', '模型服务暂时不可用，请稍后重试。', 502) from exc
        raw = output.get('raw') if isinstance(output, dict) else None
        if not isinstance(raw, AIMessage) or raw.response_metadata.get('finish_reason') != 'stop':
            raise invalid_output()
        result = validate_structured_output(output, QueryPlan)
        return _safe_plan(raw_question, result)
