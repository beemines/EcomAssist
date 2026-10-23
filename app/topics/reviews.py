"""Frozen review packs and explicit human decisions, never inferred acceptance."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from string import Template
from typing import Literal, Sequence

from pydantic import Field, field_validator, model_validator

from app.topics.cleaning import CLEANING_VERSION
from app.topics.prompts import PROMPT_VERSION, system_prompt
from app.topics.taxonomy import default_taxonomy
from app.topics.types import LabelledSample, StrictRecord


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode('utf-8')).hexdigest()


def _array(value):
    if type(value) not in (list, tuple):
        raise ValueError('Expected an explicit array')
    return tuple(value)


def _timestamp(value):
    instant = datetime.fromisoformat(value)
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError('Review timestamp needs an explicit timezone')
    return instant.astimezone(timezone.utc).isoformat()


class ReviewPack(StrictRecord):
    schema_version: int = Field(default=1, ge=1, le=1)
    purpose: Literal['pilot', 'test', 'errors'] = 'pilot'
    snapshot_hash: str = Field(pattern=r'^[0-9a-f]{64}$')
    taxonomy_hash: str = Field(pattern=r'^[0-9a-f]{64}$')
    taxonomy_version: str
    cleaning_version: str
    prompt_version: str
    prompt_hashes: dict[str, str]
    annotation_notes: dict[str, str]
    scenario_labels: dict[str, tuple[str, ...]]
    teacher_receipts: tuple[dict, ...]
    samples: tuple[LabelledSample, ...]
    pack_hash: str = Field(pattern=r'^[0-9a-f]{64}$')

    @field_validator('samples', 'teacher_receipts', mode='before')
    @classmethod
    def explicit_array(cls, value):
        return _array(value)

    @field_validator('scenario_labels', mode='before')
    @classmethod
    def scenario_arrays(cls, value):
        if type(value) is not dict:
            raise ValueError('Expected scenario mapping')
        return {key: default_taxonomy().canonical_labels(labels) for key, labels in value.items()}


class ReviewDecision(StrictRecord):
    sample_id: str = Field(min_length=1, max_length=128)
    pack_hash: str = Field(pattern=r'^[0-9a-f]{64}$')
    decision: Literal['accept', 'correct', 'exclude']
    final_labels: tuple[str, ...]
    reviewer: str = Field(min_length=1, max_length=128)
    reviewed_at: str
    notes: str = Field(default='', max_length=1024)

    @field_validator('final_labels', mode='before')
    @classmethod
    def checked_labels(cls, value):
        return default_taxonomy().canonical_labels(value, allow_empty=True)

    @field_validator('reviewer')
    @classmethod
    def named_reviewer(cls, value):
        if not value.strip():
            raise ValueError('A reviewer must explicitly identify themselves')
        return value

    @field_validator('reviewed_at')
    @classmethod
    def timezone_required(cls, value):
        return _timestamp(value)

    @model_validator(mode='after')
    def explicit_truth(self):
        if self.decision == 'exclude' and self.final_labels or self.decision != 'exclude' and not self.final_labels:
            raise ValueError('Accepted/corrected rows need explicit labels; excluded rows need none')
        return self


class ReviewReceipt(StrictRecord):
    pack_hash: str = Field(pattern=r'^[0-9a-f]{64}$')
    taxonomy_hash: str = Field(pattern=r'^[0-9a-f]{64}$')
    prompt_hashes: dict[str, str]
    decisions: tuple[ReviewDecision, ...]
    samples: tuple[LabelledSample, ...]
    excluded_ids: tuple[str, ...]
    created_at: str
    receipt_hash: str = Field(pattern=r'^[0-9a-f]{64}$')

    @field_validator('decisions', 'samples', 'excluded_ids', mode='before')
    @classmethod
    def arrays(cls, value):
        return _array(value)


def make_review_pack(samples, *, snapshot_hash, teacher_receipts, annotation_notes=None, scenario_labels=None,
                     purpose='pilot') -> ReviewPack:
    taxonomy = default_taxonomy()
    fields = dict(schema_version=1, purpose=purpose, snapshot_hash=snapshot_hash, taxonomy_hash=taxonomy.digest,
        taxonomy_version=taxonomy.version, cleaning_version=CLEANING_VERSION, prompt_version=PROMPT_VERSION,
        prompt_hashes={stage: hashlib.sha256(system_prompt(stage).encode('utf-8')).hexdigest()
                       for stage in ('generate', 'label')},
        annotation_notes=annotation_notes or {}, scenario_labels=scenario_labels or {},
        teacher_receipts=list(teacher_receipts), samples=[sample.model_dump(mode='json') for sample in samples])
    return ReviewPack(**fields, pack_hash=digest(fields))


def verify_pack(pack: ReviewPack):
    fields = pack.model_dump(mode='json')
    pack_hash = fields.pop('pack_hash')
    if (digest(fields) != pack_hash or pack.taxonomy_hash != default_taxonomy().digest
            or pack.taxonomy_version != default_taxonomy().version or pack.cleaning_version != CLEANING_VERSION
            or not pack.samples or len({sample.id for sample in pack.samples}) != len(pack.samples)):
        raise ValueError('Review pack identity or frozen contents changed')
    if set(pack.annotation_notes) - {sample.id for sample in pack.samples}:
        raise ValueError('Unknown sample note')


def apply_review(pack: ReviewPack, decisions: Sequence[ReviewDecision]) -> ReviewReceipt:
    verify_pack(pack)
    decisions = tuple(decisions)
    ids = {sample.id for sample in pack.samples}
    if (any(not isinstance(decision, ReviewDecision) for decision in decisions)
            or len(decisions) != len(ids) or {decision.sample_id for decision in decisions} != ids):
        raise ValueError('Every frozen sample needs one explicit human decision')
    mapping = {decision.sample_id: decision for decision in decisions}
    if len(mapping) != len(decisions):
        raise ValueError('Duplicate review decision')
    samples, excluded, ordered = [], [], []
    for sample in pack.samples:
        # Revalidation also rejects invalid model_copy mutations by local callers.
        decision = ReviewDecision.model_validate(mapping[sample.id].model_dump())
        if decision.pack_hash != pack.pack_hash:
            raise ValueError('Decision belongs to a different frozen review pack')
        ordered.append(decision)
        if decision.decision == 'exclude':
            excluded.append(sample.id)
        else:
            if decision.decision == 'accept' and decision.final_labels != sample.labels:
                raise ValueError('Label changes must be an explicit correction')
            samples.append(LabelledSample(**(sample.model_dump() | {'labels': decision.final_labels})))
    fields = dict(pack_hash=pack.pack_hash, taxonomy_hash=pack.taxonomy_hash, prompt_hashes=pack.prompt_hashes,
        decisions=[decision.model_dump(mode='json') for decision in ordered],
        samples=[sample.model_dump(mode='json') for sample in samples], excluded_ids=excluded,
        created_at=datetime.now(timezone.utc).isoformat())
    return ReviewReceipt(**fields, receipt_hash=digest(fields))


def load_decisions(path: Path) -> tuple[ReviewDecision, ...]:
    def strict_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate decision JSON key')
            result[key] = value
        return result
    rows = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        json.loads(line, object_pairs_hook=strict_pairs)
        rows.append(ReviewDecision.model_validate_json(line))
    return tuple(rows)


def render_review_html(pack: ReviewPack, *, hosted=False, submitted: ReviewReceipt | None = None,review_port=8007) -> str:
    verify_pack(pack)
    if type(review_port) is not int or review_port not in (8007,8008,8009):raise ValueError('Unknown local review surface')
    samples = []
    for index, sample in enumerate(pack.samples, 1):
        scenario = pack.scenario_labels.get(sample.id)
        samples.append(dict(index=index, id=sample.id, text=sample.text, origin=sample.origin,
            labels=list(sample.labels), mismatch=scenario is not None and scenario != sample.labels,
            note=pack.annotation_notes.get(sample.id, '')))
    bootstrap = dict(pack_hash=pack.pack_hash, purpose=pack.purpose, hosted=hosted, samples=samples,
        hosted_origin=f'http://127.0.0.1:{review_port}',round_label={8008:'第二轮',8009:'否定语义修复'}.get(review_port,''),
        taxonomy=[dict(name=topic.name, boundary=topic.boundary) for topic in default_taxonomy().topics],
        submitted=submitted.model_dump(mode='json') if submitted else None)
    # Even a local pack is untrusted text: keep JSON from closing its script element.
    encoded = json.dumps(bootstrap, ensure_ascii=False).replace('&', '\\u0026').replace('<', '\\u003c')
    encoded = encoded.replace('>', '\\u003e').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    folder = Path(__file__).parent
    return Template((folder / 'review_ui.html').read_text(encoding='utf-8')).substitute(
        css=(folder / 'review_ui.css').read_text(encoding='utf-8'),
        script=(folder / 'review_ui.js').read_text(encoding='utf-8'), bootstrap=encoded)
