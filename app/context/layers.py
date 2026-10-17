"""只生成模型视图；不改SQL/checkpoint，也不等待或调度摘要。"""
from collections.abc import Sequence
from dataclasses import asdict, replace
import json

from langchain_core.messages import BaseMessage, HumanMessage, trim_messages

from app.context.tokens import estimate_payload
from app.context.types import ContextAnchors, ContextBudget, FrozenMessage, LayerPlan
from app.core.errors import InputTooLong
from app.core.tool_history import _validate_turn, completed_boundaries
from app.repositories.records import MessageRecord, decode_tool_calls, message_from_record


class ContextCapacityError(InputTooLong):
    def __init__(self, reason: str):
        super().__init__()
        self.message = f'Context capacity exceeded: {reason}.'
        self.args = (self.message,)


def freeze_record(row: MessageRecord) -> FrozenMessage:
    message_from_record(row)
    return FrozenMessage(str(row.id), row.role, row.content,
        json.dumps(row.tool_calls, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
        if row.tool_calls is not None else None, row.tool_call_id)


def thaw_message(row: FrozenMessage) -> BaseMessage:
    message = message_from_record(MessageRecord(int(row.id), row.role, row.content,
        json.loads(row.tool_calls_json) if row.tool_calls_json is not None else None, row.tool_call_id))
    message.id = row.id
    return message


def _groups(rows):
    group = []
    for row in rows:
        if row.role == 'user' and group:
            yield group
            group = []
        group.append(row)
    if group:
        yield group


def history_projection(rows: Sequence[FrozenMessage]) -> tuple[list[BaseMessage], list[dict]]:
    """合法轮次原生重放；取消残留只把user原话原生保留，其余全字段审计。"""
    native, audit = [], []
    for group in _groups(rows):
        messages = [thaw_message(row) for row in group]
        try:
            _validate_turn(messages)
        except ValueError:
            for row, message in zip(group, messages):
                if row.role == 'user':
                    native.append(message)
                else:
                    audit.append({'kind': 'interrupted', **asdict(row)})
        else:
            native.extend(messages)
    return native, audit


def history_tokens(rows: Sequence[FrozenMessage]) -> int:
    native, audit = history_projection(rows)
    # 审计仍属历史额度；完整JSON及user包装不可作为免费附件绕过H。
    return estimate_payload(native) + (estimate_payload([HumanMessage(json.dumps(
        {'history_audit': audit}, ensure_ascii=False, separators=(',', ':'), allow_nan=False))]) if audit else 0)


def _compact_layer2(rows: Sequence[FrozenMessage]) -> tuple[FrozenMessage, ...]:
    result = []
    for group in _groups(rows):
        try:
            _validate_turn([thaw_message(row) for row in group])
        except ValueError:
            result.extend(group)  # 取消残留的审计必须仍保留原始字段。
            continue
        request = None
        for row in group:
            if row.tool_calls_json is not None:
                request = decode_tool_calls(json.loads(row.tool_calls_json))[0]
            elif row.role == 'assistant' and len(row.content) > 80:
                row = replace(row, content=row.content[:80] + '后文已截短')
            elif row.role == 'tool' and len(row.content) > 160:
                row = replace(row, content=_archive_result(row, request))
            result.append(row)
    return tuple(result)


def _archive_result(row: FrozenMessage, request: dict) -> str:
    try:
        payload = json.loads(row.content)
    except (ValueError, TypeError):
        payload = None
    # 只有真实结构字段能证明成功；非JSON正文不能杜撰成功状态。
    status = 'unknown'
    if isinstance(payload, dict):
        failed = ('error' in payload or payload.get('status') == 'error' or payload.get('success') is False)
        status = 'error' if failed else 'success'
    data = {'archived': True, 'tool': request['name'], 'status': status,
            'sql_id': row.id, 'tool_call_id': row.tool_call_id}
    for key in ('order_id', 'product_id', 'model', 'mock'):
        value = payload.get(key) if isinstance(payload, dict) else None
        if value is None and key in ('order_id', 'product_id'):
            value = request['args'].get(key)
        if value is not None:
            # 身份不截断；异常大字段明确拒绝，而非生成可能指向另一实体的短串。
            if (key == 'mock' and type(value) is not bool) or (key != 'mock' and
                    (not isinstance(value, str) or len(value) > (64 if key != 'model' else 128))):
                raise ValueError('Invalid archived tool identity field.')
            data[key] = value
    return json.dumps(data, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def plan_layers(rows: Sequence[MessageRecord], anchors: ContextAnchors, budget: ContextBudget,
                *, current_user_id: int) -> LayerPlan:
    s, old_l = anchors.summary_upto or 0, anchors.layer1_from or 0
    if not 0 <= s <= old_l < current_user_id:
        raise ValueError('Invalid context anchors or current user id.')
    history = sorted((row for row in rows if s < row.id < current_user_id), key=lambda row: row.id)
    if len({row.id for row in history}) != len(history):
        raise ValueError('Duplicate SQL message ids.')
    frozen = tuple(freeze_record(row) for row in history)
    boundaries = completed_boundaries(history)
    if old_l > s and old_l not in boundaries:
        raise ValueError('Layer1 anchor must end a complete turn.')
    l = old_l
    layer1 = tuple(row for row in frozen if int(row.id) > l)
    ranges = []
    if history_tokens(layer1) > budget.layer1:
        # 候选只决定边界目标；之后按最旧完整轮逐步推进，未完成尾部保留。
        native, _ = history_projection(layer1)
        candidate = trim_messages(native, max_tokens=budget.layer1, token_counter=estimate_payload,
                                  strategy='last', allow_partial=False, start_on='human')
        first = int(candidate[0].id) if candidate else current_user_id
        for boundary in sorted(boundaries):
            if boundary <= l:
                continue
            # trim的原生候选不包含审计JSON；实际审计仍可能要求推进更远。
            if boundary >= first and history_tokens(layer1) <= budget.layer1:
                break
            prefix = [int(row.id) for row in layer1 if int(row.id) <= boundary]
            ranges.append((prefix[0], boundary))
            l = boundary
            layer1 = tuple(row for row in layer1 if int(row.id) > l)
            if history_tokens(layer1) <= budget.layer1:
                break
    raw_layer2 = tuple(row for row in frozen if int(row.id) <= l)
    layer2 = _compact_layer2(raw_layer2)
    t1, t2 = history_tokens(layer1), history_tokens(layer2)
    # 单层是软线；只可借另一历史层的剩余额度。
    if history_tokens((*layer2, *layer1)) > budget.history:
        raise ContextCapacityError('history hard limit; raw user input cannot be removed')
    return LayerPlan(ContextAnchors(anchors.summary_upto, l or None), layer1, layer2,
                     raw_layer2, t1, t2, tuple(ranges))
