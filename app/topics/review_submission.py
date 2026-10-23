"""Local human review submissions; no teacher, training worker or business writes."""
from datetime import datetime, timezone
import os
from pathlib import Path
from uuid import uuid4

from pydantic import Field, field_validator

from app.topics.reviews import ReviewPack, ReviewDecision, ReviewReceipt, apply_review, digest, verify_pack
from app.topics.taxonomy import default_taxonomy
from app.topics.types import StrictRecord


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
        return render_review_html(self.pack(), hosted=True, submitted=self.state(),
            review_port={'remediation-v2':8008,'negation-v4':8009}.get(self.root.parent.name,8007))
