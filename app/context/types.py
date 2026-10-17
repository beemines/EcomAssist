"""各上下文任务共用的不可变预算载体。"""
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
import json
from types import MappingProxyType
from typing import Any


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, (tuple, list)):
        return tuple(_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class PhaseOverheads:
    """真实阶段开销；tool_peak_tokens 已含单步参数、结果和全部包装。

    tools 是实际绑定 schema 的冻结副本。FAQ 正文由 E 负担，其 P
    只包含申请及回执；调用方必须证明单步峰值，不能再加一次结果额度。
    """

    name: str
    system: str
    tools: tuple[Mapping, ...]
    output_tokens: int
    attachment_tokens: int
    tool_peak_tokens: int
    uses_evidence: bool

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip() or not isinstance(self.system, str):
            raise ValueError('Phase requires a name and actual system text.')
        for name in ('output_tokens', 'attachment_tokens', 'tool_peak_tokens'):
            value = getattr(self, name)
            if type(value) is not int or value < (1 if name == 'output_tokens' else 0):
                raise ValueError('Phase costs must be finite integers within their bounds.')
        if type(self.uses_evidence) is not bool:
            raise ValueError('Phase evidence flag must be boolean.')
        if not isinstance(self.tools, (list, tuple)) or any(not isinstance(tool, Mapping) for tool in self.tools):
            raise ValueError('Phase tools must be actual schema mappings.')
        object.__setattr__(self, 'tools', _freeze(self.tools))


@dataclass(frozen=True)
class ContextBudget:
    window: int
    phases: Mapping[str, Mapping[str, int]]
    desired: int
    history: int
    layer1: int
    layer2: int
    evidence: int
    summary: int
    safety: int
    estimator_version: str

    def __post_init__(self):
        object.__setattr__(self, 'phases', _freeze(self.phases))


@dataclass(frozen=True)
class ContextAnchors:
    summary_upto: int | None
    layer1_from: int | None


@dataclass(frozen=True)
class SummarySegment:
    seq: int
    from_msg_id: int
    upto_msg_id: int
    content: str
    created_at: datetime


@dataclass(frozen=True)
class FrozenMessage:
    """JSON为序列化文本，避免后台任务共享可变工具参数。"""
    id: str
    role: str
    content: str | None
    tool_calls_json: str | None
    tool_call_id: str | None


@dataclass(frozen=True)
class SummaryBatch:
    conversation_id: str
    expected_summary_upto: int | None
    expected_seq: int
    from_msg_id: int
    upto_msg_id: int
    source_rows: tuple[FrozenMessage, ...]
    source_hash: str

    def __post_init__(self):
        object.__setattr__(self, 'source_rows', tuple(self.source_rows))


@dataclass(frozen=True)
class SummaryRequest:
    """In-memory admission record; target SQL boundary is frozen at task start."""
    task_id: str
    conversation_id: str
    layer2_tokens: int
    budget: ContextBudget
    created_at: float


@dataclass(frozen=True)
class LayerPlan:
    anchors: ContextAnchors
    layer1: tuple[FrozenMessage, ...]
    layer2: tuple[FrozenMessage, ...]
    raw_layer2_rows: tuple[FrozenMessage, ...]
    layer1_tokens: int
    layer2_tokens: int
    downgrade_ranges: tuple[tuple[int, int], ...]

    def __post_init__(self):
        for name in ('layer1', 'layer2', 'raw_layer2_rows'):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        object.__setattr__(self, 'downgrade_ranges', tuple(tuple(pair) for pair in self.downgrade_ranges))


@dataclass(frozen=True)
class ContextSnapshot:
    snapshot_id: str
    conversation_id: str
    user_message_id: str
    anchors: ContextAnchors
    summaries: tuple[SummarySegment, ...]
    omitted_summary_seqs: tuple[int, ...]
    layer1: tuple[FrozenMessage, ...]
    layer2: tuple[FrozenMessage, ...]
    budget: ContextBudget

    def __post_init__(self):
        for name in ('summaries', 'omitted_summary_seqs', 'layer1', 'layer2'):
            object.__setattr__(self, name, tuple(getattr(self, name)))


@dataclass(frozen=True, init=False)
class ModelContextPacket:
    """内部仅存序列化文本；每次出站取值均重建可变对象的防御性副本。"""
    _messages_json: str
    _tools_json: str
    estimated_tokens: int
    output_tokens: int
    prefix_hash: str
    snapshot_id: str

    def __init__(self, messages, tools, estimated_tokens, output_tokens, prefix_hash, snapshot_id):
        from langchain_core.messages import message_to_dict
        from app.context.tokens import _plain_json

        values = dict(_messages_json=json.dumps([message_to_dict(message) for message in messages],
                      ensure_ascii=False, allow_nan=False),
                      _tools_json=json.dumps(_plain_json(tools), ensure_ascii=False, allow_nan=False),
                      estimated_tokens=estimated_tokens, output_tokens=output_tokens,
                      prefix_hash=prefix_hash, snapshot_id=snapshot_id)
        for name, value in values.items():
            object.__setattr__(self, name, value)

    @property
    def messages(self):
        from langchain_core.messages import messages_from_dict
        return tuple(messages_from_dict(json.loads(self._messages_json)))

    @property
    def tools(self):
        return tuple(json.loads(self._tools_json))
