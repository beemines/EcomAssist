# 混合索引行保存知识主键、固定维度向量、三栏拼接正文和分类元数据。
from dataclasses import dataclass
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.knowledge.embeddings import validate_vector
from app.knowledge.types import ChunkRecord, VectorHit, validate_id, validate_text


# 检索分类沿用HTTP契约；通用数据库文本校验仍可接收合法空存储字段。
def validate_category(category: str | None) -> None:
    validate_text('category', category, 255, nullable=True)
    if category is not None and not category.strip():
        raise ValueError('retrieval category must be nonblank text')


@dataclass(frozen=True)
class IndexedChunk:
    id: int
    embedding: list[float]
    text: str
    category: str

    # 复用旧索引数据校验；TEXT 无固定字节上限，分类保持 MySQL 的 255 字符契约。
    def __post_init__(self) -> None:
        validate_id(self.id)
        object.__setattr__(self, 'embedding', validate_vector(self.embedding))
        if not isinstance(self.text, str):
            raise ValueError('indexed text must be text')
        validate_category(self.category)
        if self.category is None:
            raise ValueError('indexed category must be text')


class QueryPlan(BaseModel):
    # 查询对象严格拒绝额外字段和类型转换，长度契约同时约束原始 JSON。
    model_config = ConfigDict(strict=True, extra='forbid')
    standard: str = Field(min_length=1, max_length=512)
    expansions: list[Annotated[str, Field(min_length=1, max_length=64)]] = Field(max_length=4)

    @field_validator('standard', 'expansions')
    @classmethod
    def reject_blank_text(cls, value):
        """拒绝标准问法或扩展词中的纯空白，保证每个查询片段有效。"""
        texts = [value] if isinstance(value, str) else value
        if any(not text.strip() for text in texts):
            raise ValueError('query text must not be blank')
        return value


class RerankHit(BaseModel):
    # 只返回输入位置与有限相关分数，不接收云端返回的正文替代知识原文。
    model_config = ConfigDict(strict=True, extra='forbid', allow_inf_nan=False)
    index: int = Field(ge=0)
    score: float


# 分数必须保留其来源标签，禁止把余弦、BM25、融合和重排分数当成同一量纲。
@dataclass(frozen=True)
class ScoredChunk:
    chunk: ChunkRecord
    score: float
    score_kind: Literal['cosine', 'bm25', 'rrf', 'rerank']


# 候选只保留主键和原召回分数，正文仅由最终权威匹配持有。
@dataclass(frozen=True)
class RetrievalBundle:
    query: QueryPlan
    strategy: str
    candidates: list[VectorHit]
    matches: list[ScoredChunk]
