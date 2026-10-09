# 验证最终文字结束状态与本轮引用，非知识输出限于纯问候和必要追问。
import asyncio
import re

import anyio

from app.core.errors import ServiceError
from app.core.evidence import EvidencePacket
from app.core.sufficiency import QualityDecision


REFUSAL_TEXT = '目前的知识资料不足以确认这个问题，我无法给出可靠答案。请补充具体商品或适用条件，或联系人工客服确认。'
_CITATION = re.compile(r'\[(\d+)\]')
_NUMERIC_BRACKET = re.compile(r'\[([\d\s,，\-]+)\]')
_SOCIAL_CLAUSE = re.compile(
    r'(?:你好|您好|嗨|哈喽|不客气|不用谢|感谢您的(?:理解|支持|咨询)|谢谢(?:您|你)?|再见|祝您生活愉快|'
    r'(?:请问)?有什么(?:可以|需要)(?:帮助|帮到|帮)(?:您|你)(?:的吗)?|很高兴为您服务|很高兴能帮到您|'
    r'例如查询订单、物流进度|或了解售后流程等|如后续还有订单、物流或其他售后方面的疑问|'
    r'欢迎随时联系我们|祝您购物愉快)'
)
_DETAIL = r'(?:订单号|商品(?:型号|名称|类别)?|型号|品牌|购买时间|购买日期|收货时间|收货日期|拆封情况|是否拆封|具体问题|适用条件|问题描述|售后诉求)'
_DETAILS = _DETAIL + r'(?:(?:和|、|及|与|以及)' + _DETAIL + r')*'
_CLARIFY_CONTEXT = '为了帮您查询订单的物流情况'
_CLARIFY_CLAUSE = re.compile(
    r'(?:(?:请|麻烦)(?:您)?(?:提供|补充|告知)(?:一下|具体的)?(?:您的|你的)?' + _DETAILS + r'|'
    r'请问(?:您的)?' + _DETAILS + r'(?:是什么|是何时|是多久|呢)?|'
    r'(?:请问)?(?:您)?(?:是否|有没有)(?:拆封|收货)|(?:请问)?(?:您)?(?:什么时候|何时)(?:购买|收货)(?:的)?)'
)


# 下层即使吞掉取消或阻塞事件循环，也不能在已取消或绝对期限后继续成功链路。
def ensure_answer_active(deadline: float | None = None) -> None:
    task = asyncio.current_task()
    if task is not None and task.cancelling():
        raise asyncio.CancelledError()
    if deadline is not None and asyncio.get_running_loop().time() >= deadline:
        raise TimeoutError('answer deadline expired')


class FinalAnswerStream:
    """线上与评估共用最终流协议、可保存长度及完整结束保护。"""

    def __init__(self):
        """累计字符与UTF-8字节，保存实际流中的结束状态和正文片段。"""
        self.parts, self.reasons = [], set()
        self.characters = self.utf8_bytes = 0

    def accept(self, chunk) -> str:
        """拒绝所有形式的工具申请与超限正文，合法片段才交给消费者展示。"""
        if (chunk.tool_calls or chunk.invalid_tool_calls or getattr(chunk, 'tool_call_chunks', None)
                or chunk.additional_kwargs.get('tool_calls')):
            raise ServiceError('upstream_error', '最终回复再次申请工具，无法完成本次回答。', 502)
        reason = chunk.response_metadata.get('finish_reason')
        if reason is not None:
            self.reasons.add(reason)
        text = chunk.text
        if text:
            self.characters += len(text)
            self.utf8_bytes += len(text.encode('utf-8'))
            if self.characters > 20000 or self.utf8_bytes > 65535:
                raise ServiceError('upstream_error', '模型回复超出可保存长度。', 502)
            self.parts.append(text)
        return text

    def complete(self, deadline: float | None = None) -> str:
        """只有完整stop、非空正文且未取消超期的流才能进入持久化或裁判。"""
        ensure_answer_active(deadline)
        answer = ''.join(self.parts)
        if self.reasons != {'stop'} or not answer.strip():
            raise ServiceError('upstream_error', '模型回复未正常完成，请稍后重试。', 502)
        return answer


async def close_answer_stream(upstream) -> None:
    """提前失败或正常结束均显式回收流，在独立五秒屏蔽范围内限制清理等待。"""
    close = getattr(upstream, 'aclose', None)
    if close is not None:
        with anyio.move_on_after(5, shield=True):
            try:
                await close()
            except Exception:
                pass


# 各分句必须完整符合允许的形式，不能在追问后附加政策、状态或承诺。
def _nonfactual_form(answer: str, kind: str) -> bool:
    # 已观察到的纯表情装饰可忽略；不删除任意未知文字或业务短语。
    answer = answer.replace('😊', '').replace('🙂', '')
    clauses = [part.strip() for part in re.split(r'[，,。.!！?？；;～~\n]+', answer) if part.strip()]
    if not clauses:
        return False
    if kind == 'social':
        return all(_SOCIAL_CLAUSE.fullmatch(part) for part in clauses)
    return (any(_CLARIFY_CLAUSE.fullmatch(part) for part in clauses)
            and all(_CLARIFY_CLAUSE.fullmatch(part) or _SOCIAL_CLAUSE.fullmatch(part)
                    or part == _CLARIFY_CONTEXT for part in clauses))


# 仅允许完整 stop 和本轮编号；Task7 还须检查实际 AIMessage 工具字段并且不绑定工具。
def validate_answer(answer: str, finish_reasons: set[str], evidence: EvidencePacket,
                    decision: QualityDecision) -> None:
    if not isinstance(answer, str) or not answer.strip() or finish_reasons != {'stop'}:
        raise ServiceError('invalid_answer', '模型回复未正常完成，请稍后重试。', 502)
    if not decision.useful:
        if answer != REFUSAL_TEXT:
            raise ServiceError('invalid_answer', '模型回复未遵循证据判定，请稍后重试。', 502)
        return
    references = _CITATION.findall(answer)
    known = {str(citation.n) for citation in evidence.citations}
    # 数字列表、空格或前导零不能掩盖未知引用，只支持规范的单个 [n]。
    if (any(reference not in known for reference in references)
            or any(reference not in known for reference in _NUMERIC_BRACKET.findall(answer))):
        raise ServiceError('invalid_answer_citations', '模型回复引用无效，请稍后重试。', 502)
    if decision.response_kind == 'knowledge':
        if not references:
            raise ServiceError('invalid_answer_citations', '模型回复缺少知识引用，请稍后重试。', 502)
    elif references or not _nonfactual_form(answer, decision.response_kind):
        raise ServiceError('invalid_answer', '社交或澄清回复包含未验证内容，请稍后重试。', 502)
