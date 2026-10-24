"""Local human review submissions; no teacher, training worker or business writes."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from uuid import uuid4
from typing import Literal

from pydantic import Field, field_validator

from app.topics.reviews import ReviewPack, ReviewDecision, ReviewReceipt, apply_review, digest, verify_pack
from app.topics.taxonomy import default_taxonomy
from app.topics.types import StrictRecord


class DelegatedAuthority(StrictRecord):
    """Trusted local operator record, never accepted through the human HTTP form."""
    schema_version: Literal[1]
    kind: Literal['user_authorized_ai']
    human_status: Literal['not_performed']
    user_instruction: str = Field(min_length=1, max_length=2048)
    recorded_at: str
    reviewer: Literal['Codex AI（用户授权代审，非人工）']
    model_version: str = Field(pattern=r'^[0-9a-f]{64}$')
    dataset_hash: str = Field(pattern=r'^[0-9a-f]{64}$')
    test_pack_hash: str = Field(pattern=r'^[0-9a-f]{64}$')
    error_pack_hash: str | None = Field(pattern=r'^[0-9a-f]{64}$')

    @field_validator('recorded_at')
    @classmethod
    def aware(cls, value):
        if datetime.fromisoformat(value).utcoffset() is None:
            raise ValueError('Delegation record needs a timezone')
        return value


class DelegatedReview(StrictRecord):
    schema_version: Literal[1]
    human_status: Literal['not_performed']
    review_status: Literal['ai_delegated']
    authority: DelegatedAuthority
    authority_hash: str = Field(pattern=r'^[0-9a-f]{64}$')
    receipt: ReviewReceipt
    record_hash: str = Field(pattern=r'^[0-9a-f]{64}$')


def verify_delegated_review(value, pack):
    record = DelegatedReview.model_validate(value)
    authority = record.authority
    expected_pack = authority.test_pack_hash if pack.purpose=='test' else authority.error_pack_hash
    if (pack.purpose not in ('test','errors') or expected_pack!=pack.pack_hash
            or authority.dataset_hash!=pack.snapshot_hash
            or digest(authority.model_dump(mode='json'))!=record.authority_hash
            or any(row.reviewer!=authority.reviewer or not row.notes.strip() for row in record.receipt.decisions)):
        raise ValueError('Delegated AI review scope or provenance is invalid')
    fields=record.model_dump(mode='json');fields.pop('record_hash')
    if digest(fields)!=record.record_hash:
        raise ValueError('Delegated review integrity check failed')
    receipt=record.receipt
    fields=receipt.model_dump(mode='json');fields.pop('receipt_hash')
    if digest(fields)!=receipt.receipt_hash or datetime.fromisoformat(receipt.created_at).utcoffset() is None:
        raise ValueError('Delegated receipt changed')
    actual=receipt.model_dump(mode='json');expected=apply_review(pack,receipt.decisions).model_dump(mode='json')
    for item in (actual,expected):
        item.pop('created_at');item.pop('receipt_hash')
    if actual!=expected:
        raise ValueError('Delegated receipt differs from the frozen pack')
    return record.model_dump(mode='json')


class ReviewChoice(StrictRecord):
    sample_id: str = Field(min_length=1, max_length=128)
    decision: str = Field(pattern=r'^(accept|correct|exclude)$')
    final_labels: tuple[str, ...]
    notes: str = Field(default='', max_length=1024)

    @field_validator('final_labels', mode='before')
    @classmethod
    def labels(cls, value):
        return default_taxonomy().canonical_labels(value, allow_empty=True)


class ReviewSubmission(StrictRecord):
    pack_hash: str = Field(pattern=r'^[0-9a-f]{64}$')
    reviewer: str = Field(min_length=1, max_length=128)
    attested: bool
    items: tuple[ReviewChoice, ...] = Field(min_length=1, max_length=100)

    @field_validator('reviewer')
    @classmethod
    def named(cls, value):
        if not value.strip():
            raise ValueError('Reviewer cannot be blank')
        return value.strip()

    @field_validator('attested')
    @classmethod
    def affirmative(cls, value):
        if value is not True:
            raise ValueError('Human review must be explicitly attested')
        return value

    @field_validator('items', mode='before')
    @classmethod
    def array(cls, value):
        if type(value) not in (list, tuple):
            raise ValueError('An explicit decision array is required')
        return tuple(value)


class ReviewSubmissionConflict(ValueError):
    """A different human submission already exists or another save owns the lock."""


class TopicReviewService:
    def __init__(self, root: Path):
        self.root = Path(root)

    def pack(self) -> ReviewPack:
        result = ReviewPack.model_validate_json((self.root / 'pack.json').read_text(encoding='utf-8'))
        verify_pack(result)
        return result

    def state(self) -> ReviewReceipt | None:
        path = self.root / 'review-receipt.json'
        if not path.exists():
            return None
        receipt = ReviewReceipt.model_validate_json(path.read_text(encoding='utf-8'))
        fields = receipt.model_dump(mode='json')
        receipt_hash = fields.pop('receipt_hash')
        instant = datetime.fromisoformat(receipt.created_at)
        if digest(fields) != receipt_hash or instant.utcoffset() is None:
            raise ValueError('Review receipt integrity check failed')
        expected = apply_review(self.pack(), receipt.decisions).model_dump(mode='json')
        # Rebuilding validates every decision and retained family without changing the saved timestamp.
        for field in ('created_at', 'receipt_hash'):
            expected.pop(field)
        actual = receipt.model_dump(mode='json')
        for field in ('created_at', 'receipt_hash'):
            actual.pop(field)
        if expected != actual:
            raise ValueError('Review receipt does not match its frozen pack')
        return receipt

    def delegated_state(self):
        path=self.root/'ai-review.json'
        if not path.exists():return None
        return verify_delegated_review(json.loads(path.read_text(encoding='utf-8')),self.pack())

    def save_delegated(self, decisions, *, authority):
        """Explicit AI delegation only; does not attest or save any human decision."""
        authority=DelegatedAuthority.model_validate(authority)
        receipt=apply_review(self.pack(),decisions)
        fields=dict(schema_version=1,human_status='not_performed',review_status='ai_delegated',
            authority=authority.model_dump(mode='json'),authority_hash=digest(authority.model_dump(mode='json')),
            receipt=receipt.model_dump(mode='json'))
        candidate=verify_delegated_review(fields|dict(record_hash=digest(fields)),self.pack())
        lock=self.root/'.review-submit.lock'
        try:descriptor=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        except FileExistsError:raise ReviewSubmissionConflict('Another submission owns the local review lock') from None
        try:
            os.close(descriptor)
            existing=self.delegated_state()
            if existing is not None:
                identity=lambda record:(record['authority_hash'],record['receipt']['decisions'])
                if identity(existing)!=identity(candidate):
                    raise ReviewSubmissionConflict('Delegated decisions cannot be silently replaced')
                return existing
            self._atomic('ai-review.json',json.dumps(candidate,ensure_ascii=False,indent=2)+'\n')
            return candidate
        finally:lock.unlink(missing_ok=True)

    def _atomic(self, name: str, text: str):
        temporary = self.root / ('.' + name + '.' + uuid4().hex + '.tmp')
        try:
            with temporary.open('x', encoding='utf-8', newline='\n') as handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.root / name)
        finally:
            temporary.unlink(missing_ok=True)

    def _publish_decisions(self, receipt: ReviewReceipt):
        self._atomic('decisions.jsonl', ''.join(row.model_dump_json() + '\n' for row in receipt.decisions))

    def save(self, submission: ReviewSubmission) -> dict:
        submission = ReviewSubmission.model_validate(submission.model_dump())
        pack = self.pack()
        if submission.pack_hash != pack.pack_hash:
            raise ValueError('Submission belongs to a different pack')
        now = datetime.now(timezone.utc).isoformat()
        decisions = tuple(ReviewDecision(**choice.model_dump(), pack_hash=pack.pack_hash,
            reviewer=submission.reviewer, reviewed_at=now) for choice in submission.items)
        candidate = apply_review(pack, decisions)
        lock = self.root / '.review-submit.lock'
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            raise ReviewSubmissionConflict('Another submission owns the local review lock') from None
        try:
            os.close(descriptor)
            existing = self.state()
            if existing is not None:
                def identity(receipt):
                    return [row.model_dump(exclude={'reviewed_at'}) for row in receipt.decisions]
                if identity(existing) != identity(candidate):
                    raise ReviewSubmissionConflict('Submitted decisions cannot be silently replaced')
                receipt = existing
            else:
                receipt = candidate
                # The immutable receipt is authoritative; an identical retry can repair the JSONL projection.
                self._atomic('review-receipt.json', receipt.model_dump_json(indent=2) + '\n')
            self._publish_decisions(receipt)
            return dict(status='submitted', receipt_hash=receipt.receipt_hash, accepted=len(receipt.samples),
                corrected=sum(row.decision == 'correct' for row in receipt.decisions),
                excluded=len(receipt.excluded_ids), total=len(receipt.decisions))
        finally:
            lock.unlink(missing_ok=True)

    def render(self) -> str:
        from app.topics.reviews import render_review_html
        human=self.state()
        return render_review_html(self.pack(), hosted=True, submitted=human,
            delegated=self.delegated_state() if human is None else None,
            review_port={'remediation-v2':8008,'negation-v4':8009,'coverage-v5':8010}.get(self.root.parent.name,8007))
