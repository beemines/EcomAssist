# 混合索引行保存知识主键、固定维度向量、三栏拼接正文和分类元数据。
from dataclasses import dataclass

from app.knowledge.embeddings import validate_vector
from app.knowledge.types import validate_id, validate_text


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
        validate_text('category', self.category, 255)
