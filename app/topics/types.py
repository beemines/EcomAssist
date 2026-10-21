"""Strict, immutable wire records shared without Torch or database dependencies."""

import math
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.topics.taxonomy import default_taxonomy


class StrictRecord(BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid', frozen=True,
        allow_inf_nan=False, hide_input_in_errors=True, validate_default=True)


def _sequence(value):
    if type(value) not in (tuple, list):
        raise ValueError('Expected a JSON array or tuple')
    return tuple(value)


def _nonblank(value: str) -> str:
    if not value.strip():
        raise ValueError('Text must not be blank')
    return value


class LabelledSample(StrictRecord):
    id: str = Field(min_length=1, max_length=128, pattern=r'^[A-Za-z0-9][A-Za-z0-9_.:-]*$')
    text: str = Field(min_length=1, max_length=512)
    labels: tuple[str, ...]
    origin: Literal['real', 'demo', 'synthetic', 'unverified']
    group_id: str = Field(min_length=1, max_length=128, pattern=r'^[A-Za-z0-9][A-Za-z0-9_.:-]*$')
    source_question_ids: tuple[str, ...]
    pilot: bool

    @field_validator('labels', mode='before')
    @classmethod
    def check_labels(cls, value):
        return default_taxonomy().canonical_labels(value)

    @field_validator('source_question_ids', mode='before')
    @classmethod
    def check_sources(cls, value):
        result = _sequence(value)
        for identifier in result:
            if (type(identifier) is not str or not identifier.isascii() or not identifier.isdecimal()
                    or not 0 < int(identifier) < 2**64 or identifier != str(int(identifier))):
                raise ValueError('Source ID must be a canonical unsigned BIGINT string')
        if len(set(result)) != len(result):
            raise ValueError('Source IDs must be unique')
        return result

    @field_validator('text')
    @classmethod
    def text_not_blank(cls, value):
        return _nonblank(value)


class Prediction(StrictRecord):
    id: str = Field(min_length=1, max_length=128, pattern=r'^[A-Za-z0-9][A-Za-z0-9_.:-]*$')
    labels: tuple[str, ...]
    probabilities: tuple[float, ...] | None
    status: Literal['classified', 'needs_review', 'input_too_long', 'invalid_input']
    model_version: str = Field(min_length=1, max_length=128)
    taxonomy_version: str = Field(min_length=1, max_length=96)

    @field_validator('labels', mode='before')
    @classmethod
    def check_labels(cls, value):
        return default_taxonomy().canonical_labels(value, allow_empty=True)

    @field_validator('probabilities', mode='before')
    @classmethod
    def check_probabilities(cls, value):
        if value is None:
            return None
        values = _sequence(value)
        if len(values) != 17 or any(type(item) not in (float, int) or not 0 <= item <= 1
                                   or not math.isfinite(item) for item in values):
            raise ValueError('Expected exactly 17 finite numeric probabilities in [0,1]')
        return tuple(float(item) for item in values)

    @field_validator('model_version', 'taxonomy_version')
    @classmethod
    def version_not_blank(cls, value):
        return _nonblank(value)

    @model_validator(mode='after')
    def consistent(self):
        if self.status == 'classified':
            if not self.labels or self.probabilities is None:
                raise ValueError('Classified output needs labels and probabilities')
        elif self.status == 'needs_review':
            if self.labels or self.probabilities is None:
                raise ValueError('Uncertainty has probabilities and no asserted labels')
        elif self.labels or self.probabilities is not None:
            raise ValueError('Input errors have no labels or fabricated probabilities')
        return self


class ModelIdentity(StrictRecord):
    model_version: str = Field(min_length=1, max_length=128)
    taxonomy_version: str = Field(min_length=1, max_length=96)
    taxonomy_hash: str = Field(pattern=r'^[0-9a-f]{64}$')
    cleaning_version: str = Field(min_length=1, max_length=96)
    max_tokens: int = Field(ge=128, le=128)

    @field_validator('model_version', 'taxonomy_version', 'cleaning_version')
    @classmethod
    def version_not_blank(cls, value):
        return _nonblank(value)


class ClassifyItem(StrictRecord):
    id: str = Field(min_length=1, max_length=128, pattern=r'^[A-Za-z0-9][A-Za-z0-9_.:-]*$')
    text: str = Field(min_length=1, max_length=512)

    @field_validator('text')
    @classmethod
    def question_not_blank(cls, value):
        return _nonblank(value)


class ClassifyRequest(StrictRecord):
    request_id: str = Field(min_length=1, max_length=64, pattern=r'^[A-Za-z0-9][A-Za-z0-9_.:-]*$')
    items: tuple[ClassifyItem, ...] = Field(min_length=1, max_length=64)

    @field_validator('items', mode='before')
    @classmethod
    def item_array(cls, value):
        return _sequence(value)

    @model_validator(mode='after')
    def unique_ids(self):
        if len({item.id for item in self.items}) != len(self.items):
            raise ValueError('Classification IDs must be unique within a request')
        return self


class ClassifyResponse(StrictRecord):
    request_id: str = Field(min_length=1, max_length=64, pattern=r'^[A-Za-z0-9][A-Za-z0-9_.:-]*$')
    identity: ModelIdentity
    items: tuple[Prediction, ...] = Field(min_length=1, max_length=64)

    @field_validator('items', mode='before')
    @classmethod
    def prediction_array(cls, value):
        return _sequence(value)

    @model_validator(mode='after')
    def same_model(self):
        if (len({item.id for item in self.items}) != len(self.items)
                or any(item.model_version != self.identity.model_version
                       or item.taxonomy_version != self.identity.taxonomy_version for item in self.items)):
            raise ValueError('Prediction identities must agree with the response model')
        return self
