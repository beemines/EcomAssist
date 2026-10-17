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
from app.workflow.context_budget import standalone_packet
from app.context.logging import log_model_call, log_calibration


# 只归一已知的完整问句模板，不能用子串替换去猜测任意品牌或限制条件。
_CONDITION = re.compile(r'不|没|未|无|别|只|除|且|并|同时|如果|若|但是|但|才|内|超过|至少|最多')
_ENDING = r'[啊呀呢吗]*[？?。.!！]*'
_LOOKUP = re.compile(
    r'(?:请问)?(?:物流|快递)\s*(?:咋查|怎么查|怎么查询|如何查|如何查询|查询|查询方法|查询流程)' + _ENDING,
)
_APPLICATION = re.compile(
    r'(?:请问)?(?P<topic>退款|退钱|退货)\s*'
    r'(?:咋办|怎么办|如何办理|如何申请|怎么申请|申请|办理|流程|申请流程|申请方式|申请方法|办理流程|办理方式|办理方法)'
    + _ENDING,
)


# Unicode 数字以及非汉字字母都是身份/数值锚点，涵盖全角型号、全角金额和其他数字文字。
def _has_protected_anchor(text: str) -> bool:
    return bool(_CONDITION.search(text)) or any(
        char.isnumeric() or (char.isalpha() and not '\u4e00' <= char <= '\u9fff')
        for char in text
    )


# 仅完整匹配时确认主题与意图；同义词不能把退款申请改成退货或进度查询。
def _phrase_signature(text: str) -> tuple[str, str] | None:
    if _has_protected_anchor(text):
        return None
    text = text.strip()
    if _LOOKUP.fullmatch(text):
        return '物流', '查询'
    match = _APPLICATION.fullmatch(text)
    if match:
        topic = match.group('topic')
        return ('退款' if topic == '退钱' else topic), '办理'
    return None


def _safe_plan(raw_question: str, plan: QueryPlan) -> QueryPlan:
    # 未知身份/条件或模型改变主题意图时回退原话；合法 JSON 才能进入此验证步骤。
    signature = _phrase_signature(raw_question)
    if signature is None or _phrase_signature(plan.standard) != signature:
        return QueryPlan(standard=raw_question, expansions=[])
    topic, intent = signature
    standard = f'{topic}如何{intent}？'
    # 仅检索输出携带口语同义词；原始消息与知识正文都不改动。模型回显也能产生有效归一。
    expansions = [text for text in plan.expansions if _phrase_signature(text) == signature]
    synonym = {'物流': '快递', '退款': '退钱'}.get(topic)
    if synonym:
        expansions.append(f'{synonym}如何{intent}？')
    return QueryPlan(standard=standard, expansions=list(dict.fromkeys(expansions))[:4])


class QueryPlanner:
    # 绑定严格原始 JSON 输出；预算和绝对期限由调用方提供，模型生命周期仍归调用方。
    def __init__(self, model: Any, input_budget: int, timeout: float = 60, *, context_logger=None,
                 output_tokens=2048):
        if type(input_budget) is not int or input_budget <= 0:
            raise ValueError('input budget must be a positive integer')
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or not 0 < timeout <= 60:
            raise ValueError('query timeout must be finite and in (0, 60]')
        self.structured_model = model.with_structured_output(QueryPlan, method='json_mode', include_raw=True)
        self.input_budget, self.timeout = input_budget, timeout
        self.context_logger, self.output_tokens = context_logger, output_tokens

    # 限时理解本轮原话并复核原始 JSON，最后执行主题意图校验与有界同义扩展。
    # 外部模型由调用方关闭；取消不捕获、不重试，超时转换为统一上游错误。
    async def plan(self, raw_question: str, *, context_logger=None, on_packet=None, on_calibration=None) -> QueryPlan:
        if not isinstance(raw_question, str) or not raw_question.strip():
            raise ValueError('raw question must be nonempty text')
        messages = build_query_messages(raw_question)
        packet = standalone_packet(messages, output_tokens=self.output_tokens)
        if len(raw_question) > 512 or packet.estimated_tokens > self.input_budget:
            raise InputTooLong()
        context_logger = context_logger or self.context_logger
        log_model_call(context_logger, packet, phase='query_planner', on_packet=on_packet)
        output = None
        try:
            async with asyncio.timeout(self.timeout):
                output = await self.structured_model.ainvoke(messages)
        except (LengthFinishReasonError, ContentFilterFinishReasonError) as exc:
            raise invalid_output() from exc
        except (TimeoutError, httpx.TimeoutException, APITimeoutError) as exc:
            raise ServiceError('upstream_timeout', '模型响应超时，请稍后重试。', 504) from exc
        except Exception as exc:
            raise ServiceError('upstream_error', '模型服务暂时不可用，请稍后重试。', 502) from exc
        finally:
            log_calibration(context_logger, packet, output.get('raw') if isinstance(output, dict) else None,
                            phase='query_planner', on_calibration=on_calibration)
        raw = output.get('raw') if isinstance(output, dict) else None
        if not isinstance(raw, AIMessage) or raw.response_metadata.get('finish_reason') != 'stop':
            raise invalid_output()
        result = validate_structured_output(output, QueryPlan)
        return _safe_plan(raw_question, result)
