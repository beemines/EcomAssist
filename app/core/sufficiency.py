# 对本轮问题和当前证据做严格 JSON 充分性自评，外部故障始终是错误。
import asyncio
import math
import re
from contextvars import ContextVar
from typing import Any, Literal

import httpx
from langchain_core.messages import AIMessage
from openai import APITimeoutError, ContentFilterFinishReasonError, LengthFinishReasonError
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.errors import InputTooLong, ServiceError
from app.core.evidence import EvidencePacket
from app.core.extraction import invalid_output, validate_structured_output
from app.core.memory import estimate_tokens
from app.core.prompts import build_sufficiency_messages
from app.agent.controls import UsageLedger, estimate_call_input, record_usage
from app.workflow.context_budget import stage_packet, standalone_packet
from app.context.logging import log_model_call, log_calibration


_SUFFICIENCY_USAGE: ContextVar[dict[int, dict[str, int]] | None] = ContextVar('sufficiency_usage', default=None)


class _Assessment(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    useful: bool
    reason: str = Field(min_length=1, max_length=256)
    response_kind: Literal['knowledge', 'social', 'clarification']

    # 原始 JSON 必须给出非空理由，不把空白自评解释为合法拒答。
    @field_validator('reason')
    @classmethod
    def reason_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError('reason must not be blank')
        return value


class QualityDecision(_Assessment):
    source: Literal['retrieval_low_conf', 'self_check'] | None


_SOCIAL = re.compile(r'(?:你好|您好|嗨|哈喽|谢谢(?:你|您)?|多谢|辛苦了|再见|拜拜|早上好|下午好|晚上好)[！!。.?？\s]*')
_CLARIFICATION = re.compile(
    r'(?:请问)?(?:我的)?(?:订单|包裹|快递|物流)(?:到哪了|到哪里了|什么时候到|怎么还没到|状态如何|状态是什么|帮我查(?:一下)?)[啊呢吗？?！!。\s]*'
    r'|(?:帮我|请)?(?:查(?:一下)?)(?:订单|物流|快递)[？?！!。\s]*'
    r'|(?:请问)?(?:可以|能)(?:退货|退款|换货|维修)(?:吗|么)[？?！!。\s]*'
)


# 只允许明确问候或未提供标识/条件的窄问法绕开事实回答；未知问法保守归知识。
def _safe_kind(question: str, kind: str) -> Literal['knowledge', 'social', 'clarification']:
    if kind == 'social' and _SOCIAL.fullmatch(question.strip()):
        return 'social'
    if kind == 'clarification' and _CLARIFICATION.fullmatch(question.strip()):
        return 'clarification'
    return 'knowledge'


class SufficiencyService:
    @property
    def usage(self) -> dict[str, int]:
        """读取当前调用任务的独立成本副本，不能借用其他会话的最后响应。"""
        values = (_SUFFICIENCY_USAGE.get() or {}).get(id(self))
        return dict(values) if values is not None else {
            'actual': 0, 'estimated': 0, 'actual_calls': 0, 'estimated_calls': 0}

    @usage.setter
    def usage(self, value: dict[str, int]) -> None:
        """整体替换上下文映射，避免子任务继承的可变对象被并发原地修改。"""
        _SUFFICIENCY_USAGE.set({**(_SUFFICIENCY_USAGE.get() or {}), id(self): dict(value)})

    # 依赖由调用方拥有；服务不关闭模型，明确使用 SDK JSON 模式与原始输出。
    def __init__(self, model: Any, *, input_budget: int, timeout: float = 20,
                 minimum_rerank_score: float | None,
                 mode: Literal['calibrated_score', 'content_ablation'] = 'calibrated_score'):
        if mode not in ('calibrated_score', 'content_ablation'):
            raise ValueError('unknown sufficiency mode')
        if type(input_budget) is not int or input_budget <= 0:
            raise ValueError('input budget must be a positive integer')
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError('sufficiency timeout must be finite and positive')
        if minimum_rerank_score is not None and (type(minimum_rerank_score) not in (int, float)
                                                or not math.isfinite(minimum_rerank_score)):
            raise ValueError('rerank threshold must be finite')
        self.structured_model = model.with_structured_output(_Assessment, method='json_mode', include_raw=True)
        self.input_budget, self.timeout, self.minimum_rerank_score = input_budget, timeout, minimum_rerank_score
        self.mode = mode
        self.usage = {'actual': 0, 'estimated': 0, 'actual_calls': 0, 'estimated_calls': 0}

    # 无工具问题也必须判定；合法自评后再执行知识空集及真实重排分的硬门槛。
    async def check(self, raw_question: str, evidence: EvidencePacket, *, order_context: dict | None = None,
                    snapshot=None, original_question=None, context_logger=None, on_packet=None,
                    on_calibration=None, output_tokens=2048) -> QualityDecision:
        """判断政策可否支持事实或条件答复，订单事实不替代政策。"""
        self.usage = dict.fromkeys(self.usage, 0)
        if not isinstance(raw_question, str) or not raw_question.strip():
            raise ValueError('raw question must be nonempty text')
        if self.mode == 'calibrated_score' and evidence.strategy == 'hybrid_rerank':
            if self.minimum_rerank_score is None:
                raise ValueError('online hybrid_rerank requires a calibrated threshold')
            if any(item['score_kind'] != 'rerank' for item in evidence.payload.get('matches', [])):
                raise ValueError('hybrid_rerank requires authoritative rerank scores')
        messages = build_sufficiency_messages(raw_question, evidence.payload, order_context=order_context)
        packet = (stage_packet(snapshot, system=messages[0], raw_question=original_question or raw_question,
            attachment={'resolved_question': raw_question, 'evidence': evidence.payload, 'order_context': order_context},
            output_tokens=output_tokens) if snapshot is not None else standalone_packet(messages, output_tokens=output_tokens))
        messages = packet.messages
        if snapshot is None and packet.estimated_tokens > self.input_budget:
            raise InputTooLong()
        cost = packet.estimated_tokens
        ledger = UsageLedger()
        record_usage(None, ledger, estimated_input=cost, output_limit=output_tokens)
        self.usage = {key: getattr(ledger, key) for key in self.usage}
        log_model_call(context_logger, packet, phase='sufficiency', on_packet=on_packet,
            conversation_id=snapshot.conversation_id if snapshot else None,
            user_message_id=snapshot.user_message_id if snapshot else None)
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
                            phase='sufficiency', on_calibration=on_calibration)
        raw = output.get('raw') if isinstance(output, dict) else None
        ledger = UsageLedger()
        record_usage(raw, ledger, estimated_input=cost, output_limit=output_tokens)
        self.usage = {key: getattr(ledger, key) for key in self.usage}
        if (not isinstance(raw, AIMessage) or raw.response_metadata.get('finish_reason') != 'stop'
                or raw.tool_calls or raw.invalid_tool_calls):
            raise invalid_output()
        result = validate_structured_output(output, _Assessment)
        kind = _safe_kind(raw_question, result.response_kind)
        # 内容消融保留空事实证据门槛；校准分仅属于默认线上重排路径。
        low = not evidence.citations or (self.mode == 'calibrated_score' and evidence.strategy == 'hybrid_rerank'
            and (evidence.best_score is None or evidence.best_score < self.minimum_rerank_score))
        if kind == 'knowledge' and low:
            return QualityDecision(useful=False, reason='当前知识证据为空或低于已校准重排门槛。',
                                   response_kind='knowledge', source='retrieval_low_conf')
        if kind != result.response_kind:
            return QualityDecision(useful=False, reason='业务事实问题不能按社交或澄清放行。',
                                   response_kind='knowledge', source='self_check')
        return QualityDecision(useful=result.useful, reason=result.reason, response_kind=kind,
                               source=None if result.useful else 'self_check')
