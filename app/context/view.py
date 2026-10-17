"""冻结本轮段落/消息，统一组装和核验真正出站的完整模型输入。"""
from collections.abc import Sequence
from dataclasses import asdict
import hashlib
import json

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, message_to_dict, messages_from_dict

from app.context.layers import ContextCapacityError, history_projection, history_tokens
from app.context.tokens import _plain_json, estimate_payload
from app.context.types import ContextBudget, ContextSnapshot, LayerPlan, ModelContextPacket, SummarySegment
from app.core.tool_history import _validate_turn
from app.repositories.records import message_from_record, record_from_message


def _json(value) -> str:
    return json.dumps(_plain_json(value), ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def _summaries(segments):
    return [{'seq': segment.seq, 'from_msg_id': str(segment.from_msg_id),
             'upto_msg_id': str(segment.upto_msg_id), 'content': segment.content} for segment in segments]


def _summary_cost(segments):
    return estimate_payload([HumanMessage(_json({'summaries': _summaries(segments)}))]) if segments else 0


def build_snapshot(plan: LayerPlan, segments: Sequence[SummarySegment], *, conversation_id: str,
                   user_message_id: str, budget: ContextBudget) -> ContextSnapshot:
    if int(user_message_id) <= max((int(row.id) for row in (*plan.layer2, *plan.layer1)), default=0):
        raise ValueError('Current user must occur after historical messages.')
    ordered = tuple(sorted(segments, key=lambda segment: segment.seq))
    if (len({segment.seq for segment in ordered}) != len(ordered)
            or any(segment.from_msg_id > segment.upto_msg_id
                   or segment.upto_msg_id > (plan.anchors.summary_upto or 0) for segment in ordered)
            or any(left.upto_msg_id >= right.from_msg_id for left, right in zip(ordered, ordered[1:]))):
        raise ValueError('Summary ranges must be ordered within frozen summary coverage.')
    selected = []
    for segment in reversed(ordered):
        candidate = [segment, *selected]
        if _summary_cost(candidate) > budget.summary:
            break
        selected = candidate
    selected_seqs = {segment.seq for segment in selected}
    omitted = tuple(segment.seq for segment in ordered if segment.seq not in selected_seqs)
    if history_tokens((*plan.layer2, *plan.layer1)) > budget.history:
        raise ContextCapacityError('history hard limit')
    # 不使用asdict(ContextBudget)：嵌套MappingProxy不能deepcopy。
    identity = {'conversation_id': conversation_id, 'user_message_id': user_message_id,
                'anchors': asdict(plan.anchors), 'summaries': [asdict(segment) | {
                    'created_at': segment.created_at.isoformat()} for segment in selected],
                'omitted_summary_seqs': omitted, 'layer1': [asdict(row) for row in plan.layer1],
                'layer2': [asdict(row) for row in plan.layer2],
                'budget': {name: getattr(budget, name) for name in budget.__dataclass_fields__}}
    snapshot_id = hashlib.sha256(_json(identity).encode('utf-8')).hexdigest()
    return ContextSnapshot(snapshot_id, conversation_id, user_message_id, plan.anchors,
                           tuple(selected), omitted, plan.layer1, plan.layer2, budget)


def compose_call(snapshot: ContextSnapshot, *, system: SystemMessage, current: HumanMessage,
                 attachment: dict, pending: Sequence[BaseMessage], tools: Sequence[dict],
                 output_tokens: int) -> ModelContextPacket:
    if not isinstance(system, SystemMessage) or not isinstance(system.content, str):
        raise ValueError('System message must contain text.')
    if not isinstance(current, HumanMessage):
        raise ValueError('Current message must be a user message.')
    if type(output_tokens) is not int or output_tokens <= 0:
        raise ValueError('Output reserve must be a positive integer.')
    if not isinstance(attachment, dict):
        raise ValueError('Attachment must be a JSON object.')
    message_from_record(record_from_message(current))
    if current.id is not None and current.id != snapshot.user_message_id:
        raise ValueError('Current user id differs from frozen snapshot.')
    current = messages_from_dict([message_to_dict(current)])[0]
    current.id = snapshot.user_message_id
    if pending:
        _validate_turn([current, *pending], pending=True)
    historical = (*snapshot.layer2, *snapshot.layer1)
    if history_tokens(historical) > snapshot.budget.history:
        raise ContextCapacityError('history hard limit')
    if _summary_cost(snapshot.summaries) > snapshot.budget.summary:
        raise ContextCapacityError('summary attachment limit')
    native, audit = history_projection(historical)
    body = {'kind': 'context_data', 'summaries': _summaries(snapshot.summaries), 'data': attachment}
    if audit:
        body['history_audit'] = audit
    messages = [system, *native, current, HumanMessage(_json(body)), *pending]
    actual = estimate_payload(messages, tools)
    if actual + output_tokens + snapshot.budget.safety > snapshot.budget.window:
        raise ContextCapacityError('window input + output + safety limit')
    system_prefix = {'role': 'system', 'content': system.content}
    if (name := system.name or system.additional_kwargs.get('name')) is not None:
        system_prefix['name'] = name
    prefix = hashlib.sha256(_json({'system': system_prefix, 'tools': tools}).encode('utf-8')).hexdigest()
    return ModelContextPacket(messages, tools, actual, output_tokens, prefix, snapshot.snapshot_id)
