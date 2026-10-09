# 将权威 FAQ 整块选择为预算内证据，编号固定后再调整展示位置。
import copy
import json
import math
from collections.abc import Sequence
from dataclasses import dataclass

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage

from app.core.errors import InputTooLong
from app.core.tool_history import build_tool_messages


@dataclass(frozen=True)
class Citation:
    n: int
    chunk_id: str
    section_path: str | None
    question: str
    answer: str


@dataclass(frozen=True)
class EvidencePacket:
    payload: dict
    citations: list[Citation]
    messages: list[BaseMessage]
    best_score: float | None
    strategy: str


# 统一紧凑序列化；字符和数据库 TEXT 字节界限均针对实际工具 JSON。
def _serialize(payload: dict) -> str:
    text = json.dumps(payload, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    if len(text) > 20000 or len(text.encode('utf-8')) > 65535:
        raise InputTooLong()
    return text


# 按相关性编号后两侧交替：最强首位、次强末位，中间证据不重编号。
def _numbered_payload(payload: dict, selected: list[dict]) -> dict:
    ranked = [dict(item, n=n) for n, item in enumerate(selected, 1)]
    shown = ranked[::2] + list(reversed(ranked[1::2]))
    result = copy.deepcopy(payload)
    result.update(found=bool(shown), matches=shown)
    if isinstance(result.get('retrieval'), dict):
        result['retrieval']['match_count'] = len(shown)
    return result


# 校验证据字段并使用字符串主键，避免 JavaScript 消费 BIGINT 时丢失精度。
def _matches(payload: dict) -> list[dict]:
    matches = payload['matches']
    if not isinstance(matches, list):
        raise ValueError('FAQ matches must be a list')
    result, seen = [], set()
    for original in matches:
        item = copy.deepcopy(original)
        identifier = item.get('id')
        if type(identifier) not in (str, int) or not str(identifier).strip() or str(identifier) in seen:
            raise ValueError('evidence identifiers must be nonempty and unique')
        if any(not isinstance(item.get(field), str) or not item[field].strip() for field in ('question', 'answer')):
            raise ValueError('evidence must contain complete question and answer text')
        if item.get('section_path') is not None and not isinstance(item['section_path'], str):
            raise ValueError('section path must be text or null')
        if type(item.get('score')) not in (int, float) or not math.isfinite(item['score']):
            raise ValueError('evidence score must be finite')
        if item.get('score_kind') not in ('rerank', 'cosine', 'bm25', 'rrf'):
            raise ValueError('evidence score kind is required')
        item['id'] = str(identifier)
        seen.add(item['id'])
        result.append(item)
    return sorted(result, key=lambda item: item['score'], reverse=True)


# 复用完整工具轮次校验与结构计费，必需证据优先，历史仅整轮删除。
def build_evidence(*, system: SystemMessage, turns: Sequence[Sequence[BaseMessage]],
                   current: HumanMessage, request: AIMessage | None, payload: dict | None,
                   budget: int) -> EvidencePacket:
    if type(budget) is not int or budget <= 0:
        raise ValueError('input budget must be a positive integer')
    if (request is None) != (payload is None):
        raise ValueError('tool request and payload must be supplied together')
    if request is None:
        messages = build_tool_messages(system, turns, current, budget, tool_schema=[])
        return EvidencePacket({}, [], messages, None, 'none')
    if not isinstance(payload, dict) or not isinstance(request, AIMessage) or len(request.tool_calls) != 1:
        raise ValueError('one valid tool request and object payload are required')
    call_id = request.tool_calls[0]['id']

    # 每次试装都用同一工具预算入口，不能忽略申请参数或关联标识。
    def assemble(data: dict, history: Sequence[Sequence[BaseMessage]]) -> list[BaseMessage]:
        result = ToolMessage(_serialize(data), tool_call_id=call_id)
        return build_tool_messages(system, history, current, budget, tool_schema=[],
                                   current_tool_messages=[request, result])

    if 'matches' not in payload:
        copied = copy.deepcopy(payload)
        return EvidencePacket(copied, [], assemble(copied, turns), None, 'tool')
    candidates = _matches(payload)
    strategy = payload.get('retrieval', {}).get('strategy', 'none')
    # 基础申请与空结果也必须能装下；历史校验在最终组装时仍严格执行。
    assemble(_numbered_payload(payload, []), [])
    selected: list[dict] = []
    for candidate in candidates:
        trial = _numbered_payload(payload, [*selected, candidate])
        try:
            assemble(trial, [])
        except InputTooLong:
            continue
        selected.append(candidate)
    if candidates and not selected:
        raise InputTooLong()
    bounded = _numbered_payload(payload, selected)
    messages = assemble(bounded, turns)
    citations = [Citation(item['n'], item['id'], item.get('section_path'), item['question'], item['answer'])
                 for item in bounded['matches']]
    return EvidencePacket(bounded, citations, messages, selected[0]['score'] if selected else None, strategy)
