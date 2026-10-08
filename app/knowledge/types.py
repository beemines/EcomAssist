from dataclasses import dataclass
from typing import Protocol

from app.repositories.records import MessageRecord


def validate_text(name: str, value: str | None, limit: int, *, nullable: bool = False, utf8: bool = False) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, str) or (len(value.encode("utf-8")) if utf8 else len(value)) > limit:
        raise ValueError(f"{name} exceeds its MySQL {'UTF-8 byte' if utf8 else 'character'} limit or is not text")


def validate_id(value: int) -> None:
    if type(value) is not int or not 1 <= value <= 9223372036854775807:
        raise ValueError("knowledge id must fit positive INT64")


@dataclass(frozen=True)
class ChunkDraft:
    category: str
    questions: str
    answer: str
    section_path: str | None = None
    content_type: str | None = None
    is_key_clause: bool = False

    def __post_init__(self) -> None:
        validate_text("category", self.category, 255)
        validate_text("questions", self.questions, 65535, utf8=True)
        validate_text("answer", self.answer, 65535, utf8=True)
        validate_text("section_path", self.section_path, 512, nullable=True)
        validate_text("content_type", self.content_type, 32, nullable=True)
        if type(self.is_key_clause) is not bool:
            raise ValueError("is_key_clause must be bool")


@dataclass(frozen=True)
class ChunkRecord(ChunkDraft):
    id: int = 0
    prev_chunk_id: int | None = None
    next_chunk_id: int | None = None
    vector_id: str | None = None
    vectorize_status: str = "pending"


@dataclass(frozen=True)
class VectorHit:
    id: int
    score: float


@dataclass(frozen=True)
class ExtractedQA:
    source_ref: str
    question: str
    answer: str

    def __post_init__(self) -> None:
        validate_text("source_ref", self.source_ref, 255, nullable=True)
        validate_text("question", self.question, 65535, utf8=True)
        validate_text("answer", self.answer, 65535, utf8=True)


@dataclass(frozen=True)
class StagedQA(ExtractedQA):
    id: int = 0
    batch_no: str = ""
    status: str = "extracted"


@dataclass(frozen=True)
class ConversationTranscript:
    id: int
    last_message_id: int
    messages: list[MessageRecord]


def embedding_text(chunk: ChunkDraft | ChunkRecord) -> str:
    return f"category: {chunk.category}\nquestions: {chunk.questions}\nanswer: {chunk.answer}"


class Embedder(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class VectorIndex(Protocol):
    async def upsert(self, rows: list[tuple[int, list[float]]]) -> list[int]: ...
    async def search(self, vector: list[float], limit: int = 3) -> list[VectorHit]: ...
