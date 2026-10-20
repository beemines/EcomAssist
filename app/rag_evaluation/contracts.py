"""评估模块共用的不可变契约；资源会话不进入跨模块数据结构。"""

from dataclasses import dataclass
from typing import Literal

from app.knowledge.types import ChunkDraft

Strategy = Literal["dense", "bm25", "hybrid", "hybrid_rerank"]
Scope = Literal["pilot", "full"]


@dataclass(frozen=True)
class CorpusChunk:
    """稳定逻辑块及其完整入库草稿，物理主键由每次运行另行分配。"""
    chunk_key: str
    document: str
    ordinal: int
    draft: ChunkDraft


@dataclass(frozen=True)
class GoldGroup:
    """外层候选组合为或，每个内层组合必须全部命中。"""
    group_id: str
    alternatives: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class MappedGroup:
    """本次运行物理主键表示的证据组，保留完整 AND/OR 结构。"""
    group_id: str
    alternatives: tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class AnswerPoint:
    """需逐项判定的事实、适用条件和可接受的同义表述。"""
    point_id: str
    text: str
    condition: str | None
    aliases: tuple[str, ...]


@dataclass(frozen=True)
class EvalCase:
    """审定题面及金标；生成模块只能取得题面和实际检索证据。"""
    eval_id: str
    bucket: str
    difficulty: str
    query: str
    category: str | None
    should_refuse: bool
    groups: tuple[GoldGroup, ...]
    points: tuple[AnswerPoint, ...]
    ledger_eval_id: str


@dataclass(frozen=True)
class FrozenDataset:
    """完成离线验证的材料快照及固定试运行题号。"""
    dataset_id: str
    fingerprint: str
    corpus_hash: str
    cases_hash: str
    annotation_hash: str
    chunks: tuple[CorpusChunk, ...]
    cases: tuple[EvalCase, ...]
    pilot_ids: tuple[str, ...]
    regression_links: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class PointVerdict:
    """裁判对一个标准要点的覆盖判断及理由。"""
    point_id: str
    covered: bool
    reason: str


@dataclass(frozen=True)
class ClaimVerdict:
    """裁判对回答中一个事实断言的证据支持判断。"""
    claim: str
    supported: bool
    reason: str


@dataclass(frozen=True)
class GenerationJudgment:
    """完整联合裁判结果；原始响应仅供本地私有失败审计。"""
    points: tuple[PointVerdict, ...]
    claims: tuple[ClaimVerdict, ...]
    raw_response: str
    finish_reason: str
    prompt_version: str


@dataclass(frozen=True)
class CleanupResult:
    """已证明归属资源的清理结果；未知归属不能算成功。"""
    ok: bool
    errors: tuple[str, ...]
    unverified: tuple[str, ...]


# 可变 JSON 的字段校验由 report/store 所属任务负责，禁止任意对象序列化。
CaseRecord = dict[str, object]
RunConfig = dict[str, object]
RunManifest = dict[str, object]
