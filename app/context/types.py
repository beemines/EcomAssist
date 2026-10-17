"""各上下文任务共用的不可变预算载体。"""
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
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
