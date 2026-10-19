"""Strict metadata and turn-bound DTOs; models never own processing state."""
from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def database_id(value: str) -> str:
    if (type(value) is not str or not value.isascii() or not value.isdecimal()
            or not 0 < int(value) < 2**64 or value != str(int(value))):
        raise ValueError('Expected canonical positive unsigned BIGINT decimal string')
    return value


def utc_time(value):
    if value is not None:
        if value.utcoffset() is None:
            raise ValueError('Task timestamp requires an explicit timezone')
        return value.astimezone(timezone.utc)
    return None


class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid', allow_inf_nan=False,
                              hide_input_in_errors=True, validate_default=True)


class NormalizedDraft(StrictModel):
    normalized_question: str = Field(min_length=1, max_length=512)
    ai_suggested_answer: str = Field(min_length=1, max_length=16000)

    @field_validator('normalized_question', 'ai_suggested_answer')
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError('FAQ draft text must not be blank')
        return value


class ReviewCandidate(StrictModel):
    id: str
    normalized_question: str = Field(min_length=1, max_length=512)

    @field_validator('id')
    @classmethod
    def identifier(cls, value):
        return database_id(value)


class SemanticMatch(StrictModel):
    matched_review_id: str | None

    @field_validator('matched_review_id')
    @classmethod
    def identifier(cls, value):
        return database_id(value) if value is not None else None


class TaskError(StrictModel):
    code: str = Field(min_length=1, max_length=64, pattern=r'^[a-z][a-z0-9_]*$')
    stage: str = Field(min_length=1, max_length=64, pattern=r'^[a-z][a-z0-9_]*$')
    message: str = Field(min_length=1, max_length=512)


class Versioned(StrictModel):
    schema_version: Literal[1] = 1

    @field_validator('schema_version', mode='before')
    @classmethod
    def exact_version(cls, value):
        if type(value) is not int or value != 1:
            raise ValueError('Unsupported metadata schema version')
        return value


class TaskMetadata(Versioned):
    attempt_count: int = Field(default=0, ge=0, le=3)
    next_attempt_at: datetime | None = None
    last_error: TaskError | None = None

    @field_validator('next_attempt_at')
    @classmethod
    def next_time(cls, value):
        return utc_time(value)


class ProcessingState(TaskMetadata):
    status: Literal['pending', 'running', 'retry_wait', 'matched', 'failed'] = 'pending'
    prompt_versions: dict[str, str] = Field(default_factory=dict)
    normalized_draft: NormalizedDraft | None = None
    dedup_cursor: str | None = None
    candidate_fingerprint: str | None = Field(default=None, pattern=r'^[0-9a-f]{64}$')

    @field_validator('dedup_cursor')
    @classmethod
    def cursor(cls, value):
        return database_id(value) if value is not None else None

    @model_validator(mode='after')
    def consistent(self):
        if self.status == 'running' and self.attempt_count == 0:
            raise ValueError('Running task must reserve an attempt first')
        if self.status == 'retry_wait' and self.next_attempt_at is None:
            raise ValueError('Retry task needs an aware due time')
        if self.status == 'failed' and self.last_error is None:
            raise ValueError('Failed task needs a safe reason')
        return self


class PublicationState(TaskMetadata):
    status: Literal['pending', 'running', 'ready', 'failed'] = 'pending'
    published_at: datetime | None = None

    @field_validator('published_at')
    @classmethod
    def publish_time(cls, value):
        return utc_time(value)

    @model_validator(mode='after')
    def consistent(self):
        if self.status == 'running' and self.attempt_count == 0:
            raise ValueError('Running publication must reserve an attempt')
        if self.status == 'ready' and self.published_at is None:
            raise ValueError('Ready publication needs a verified timestamp')
        if self.status == 'failed' and self.last_error is None:
            raise ValueError('Failed publication needs a safe reason')
        return self


class RetrievedChunk(StrictModel):
    chunk_id: str
    question: str
    answer: str
    section_path: str | None
    score: float
    score_kind: Literal['rerank', 'rrf', 'cosine', 'bm25']
    rank: int = Field(ge=1, le=10)
    in_prompt: bool

    @field_validator('chunk_id')
    @classmethod
    def identifier(cls, value):
        return database_id(value)


class SnapshotPayload(Versioned):
    strategy: str = Field(min_length=1, max_length=64)
    retrieved_at: datetime
    versions: dict[str, str] = Field(default_factory=dict)
    chunks: list[RetrievedChunk] = Field(max_length=10)
    reason: Literal['legacy_payload_missing'] | None = None

    @field_validator('retrieved_at')
    @classmethod
    def captured_time(cls, value):
        return utc_time(value)

    @model_validator(mode='after')
    def unique_chunks(self):
        if len({chunk.chunk_id for chunk in self.chunks}) != len(self.chunks):
            raise ValueError('Snapshot chunk IDs must be unique')
        return self


class RetrievalSnapshot(StrictModel):
    status: Literal['captured', 'not_retrieved', 'unavailable']
    payload: SnapshotPayload | None

    @model_validator(mode='after')
    def consistent(self):
        if (self.status == 'not_retrieved') != (self.payload is None):
            raise ValueError('Only a verified nonretrieval may have NULL snapshot')
        if self.status == 'unavailable' and (self.payload.chunks or self.payload.reason != 'legacy_payload_missing'):
            raise ValueError('Unavailable snapshot must declare missing legacy payload')
        if self.status == 'captured' and self.payload.reason is not None:
            raise ValueError('Captured evidence cannot be marked unavailable')
        return self


class PoolInput(StrictModel):
    conversation_id: str | None
    user_message_id: str | None
    assistant_message_id: str | None
    raw_question: str = Field(min_length=1)
    source: Literal['retrieval_low_conf', 'self_check', 'user_feedback']
    reason: str | None = None
    snapshot: RetrievalSnapshot

    @field_validator('conversation_id', 'user_message_id', 'assistant_message_id')
    @classmethod
    def identifier(cls, value):
        return database_id(value) if value is not None else None

    @field_validator('raw_question', 'reason')
    @classmethod
    def text_capacity(cls, value):
        if value is not None and (not value.strip() or len(value.encode('utf-8')) > 65535):
            raise ValueError('Text must fit the original MySQL TEXT column')
        return value


class PoolReceipt(StrictModel):
    id: str
    created: bool


class ReviewAssignment(StrictModel):
    pool_id: str
    review_id: str
    occurrence_count: int = Field(ge=1, le=2**32-1)
    created: bool


class ReviewChanged(RuntimeError):
    """The proposed dedup target is no longer pending; rescan rather than mismerge."""
