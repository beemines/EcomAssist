"""A single durable authorization ledger counts money before physical requests."""

from contextlib import closing, contextmanager
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from uuid import uuid4

from pydantic import Field, model_validator

from app.topics.types import StrictRecord


APPROVAL_ID = 'ch10-topic-20261021'
EVIDENCE_ROOT = Path('D:/shixi/ecommerce-customer-service/.cache/ch10-evidence')
BUDGET_PATH = EVIDENCE_ROOT / 'budget.sqlite3'
LIMIT_MICRO = 10_000_000
MAX_ATTEMPTS = 300
ATTEMPT_EXTENSION_ID = 'ch10-topic-20261022-attempts-400'
ATTEMPT_EXTENSION_TEXT = '允许400次，费用仍最多10元'
EXTENDED_ATTEMPTS = 400
REMEDIATION_APPROVAL_ID='ch10-topic-20261023-attempts-450'
REMEDIATION_APPROVAL_TEXT='批准第二轮修复，累计450次、仍最多10元'
NEGATION_APPROVAL_ID='ch10-topic-20261023-attempts-500'
NEGATION_APPROVAL_TEXT='批准该范围，累计500次仍最多10元'
RESERVATION_MICRO = 1_205_863


class BudgetError(RuntimeError):
    """Fail closed; errors never include credentials or request text."""


class Usage(StrictRecord):
    prompt_tokens: int = Field(ge=0, le=1048576)
    completion_tokens: int = Field(ge=0, le=131072)
    total_tokens: int = Field(ge=0, le=1179648)
    reasoning_tokens: int | None = Field(default=None, ge=0, le=131072)
    reasoning_included: bool = True

    @property
    def billable_completion(self):
        return self.completion_tokens + (0 if self.reasoning_included else (self.reasoning_tokens or 0))

    @model_validator(mode='after')
    def complete_counts(self):
        if (not self.reasoning_included and self.reasoning_tokens is None
                or self.reasoning_included and self.reasoning_tokens is not None
                and self.reasoning_tokens > self.completion_tokens
                or self.billable_completion > 131072
                or self.total_tokens != self.prompt_tokens + self.billable_completion):
            raise ValueError('Usage token counts are incomplete or contradictory')
        return self


class Reservation(StrictRecord):
    attempt_id: str
    reserved_micro: int


class BudgetSummary(StrictRecord):
    approval_id: str
    limit_micro: int
    used_micro: int
    remaining_micro: int
    attempts: int
    unknown_attempts: int
    consecutive_failures: int
    paused: bool
    attempt_limit: int = MAX_ATTEMPTS
    approval_revision: str | None = None


def _now():
    return datetime.now(timezone.utc).isoformat()


def _marker(path):
    return path.with_suffix('.approval.json')


def _extension_identity(path,marker):
    return dict(schema_version='1',ledger_id=marker['ledger_id'],base_approval_id=APPROVAL_ID,
        revision_id=ATTEMPT_EXTENSION_ID,original_attempt_limit=str(MAX_ATTEMPTS),attempt_limit=str(EXTENDED_ATTEMPTS),
        limit_micro=str(LIMIT_MICRO),base_marker_sha256=hashlib.sha256(_marker(path).read_bytes()).hexdigest(),
        approval_text=ATTEMPT_EXTENSION_TEXT)


def _attempt_limit(path,marker):
    extension=path.with_suffix('.attempt-approval.json')
    remediation=path.with_suffix('.remediation-approval.json')
    negation=path.with_suffix('.negation-approval.json')
    if extension.is_symlink(): raise BudgetError('Attempt authorization cannot be a symlink')
    if not extension.exists():
        if remediation.exists() or remediation.is_symlink() or negation.exists() or negation.is_symlink():raise BudgetError('Missing prior authorization')
        return MAX_ATTEMPTS,None
    if not extension.is_file() or extension.stat().st_size>4096:
        raise BudgetError('Attempt authorization is unavailable or corrupt')
    value=json.loads(extension.read_text(encoding='utf-8'))
    if (type(value) is not dict or set(value)!=set(_extension_identity(path,marker))|{'approved_at'}
            or {key:item for key,item in value.items() if key!='approved_at'}!=_extension_identity(path,marker)
            or type(value.get('approved_at')) is not str
            or datetime.fromisoformat(value['approved_at']).utcoffset() is None):
        raise BudgetError('Attempt authorization identity mismatch')
    if remediation.is_symlink():raise BudgetError('Remediation authorization cannot be a symlink')
    if not remediation.exists():
        if negation.exists() or negation.is_symlink():raise BudgetError('Missing prior remediation authorization')
        return EXTENDED_ATTEMPTS,ATTEMPT_EXTENSION_ID
    if not remediation.is_file() or remediation.stat().st_size>4096:raise BudgetError('Invalid remediation authorization')
    value=json.loads(remediation.read_text(encoding='utf-8'))
    expected=_remediation_identity(path,marker)
    if (type(value) is not dict or set(value)!=set(expected)|{'approved_at'}
            or {k:v for k,v in value.items() if k!='approved_at'}!=expected
            or type(value.get('approved_at')) is not str or datetime.fromisoformat(value['approved_at']).utcoffset() is None):
        raise BudgetError('Remediation authorization identity mismatch')
    if negation.is_symlink():raise BudgetError('Negation authorization cannot be a symlink')
    if not negation.exists():return 450,REMEDIATION_APPROVAL_ID
    if not negation.is_file() or negation.stat().st_size>4096:raise BudgetError('Invalid negation authorization')
    value=json.loads(negation.read_text(encoding='utf-8'));expected=_negation_identity(path,marker)
    if (type(value) is not dict or set(value)!=set(expected)|{'approved_at'}
            or {k:v for k,v in value.items() if k!='approved_at'}!=expected
            or type(value.get('approved_at')) is not str or datetime.fromisoformat(value['approved_at']).utcoffset() is None):
        raise BudgetError('Negation authorization identity mismatch')
    return 500,NEGATION_APPROVAL_ID


def _remediation_identity(path,marker):
    return dict(schema_version='1',ledger_id=marker['ledger_id'],base_approval_id=APPROVAL_ID,
        revision_id=REMEDIATION_APPROVAL_ID,previous_revision_id=ATTEMPT_EXTENSION_ID,
        previous_marker_sha256=hashlib.sha256(path.with_suffix('.attempt-approval.json').read_bytes()).hexdigest(),
        base_marker_sha256=hashlib.sha256(_marker(path).read_bytes()).hexdigest(),
        original_attempt_limit='300',previous_attempt_limit='400',attempt_limit='450',limit_micro=str(LIMIT_MICRO),
        approval_text=REMEDIATION_APPROVAL_TEXT)


def _negation_identity(path,marker):
    return dict(schema_version='1',ledger_id=marker['ledger_id'],base_approval_id=APPROVAL_ID,
        revision_id=NEGATION_APPROVAL_ID,previous_revision_id=REMEDIATION_APPROVAL_ID,
        previous_marker_sha256=hashlib.sha256(path.with_suffix('.remediation-approval.json').read_bytes()).hexdigest(),
        base_marker_sha256=hashlib.sha256(_marker(path).read_bytes()).hexdigest(),
        original_attempt_limit='300',previous_attempt_limit='450',attempt_limit='500',limit_micro=str(LIMIT_MICRO),
        approval_text=NEGATION_APPROVAL_TEXT)


def initialize_budget(path: Path, approval_id: str) -> None:
    """Only this explicit one-time operation may create files; never reset them."""
    path = path.absolute()
    if approval_id != APPROVAL_ID:
        raise BudgetError('Unrecognized budget authorization')
    path.parent.mkdir(parents=True, exist_ok=True)
    marker = _marker(path)
    extension=path.with_suffix('.attempt-approval.json')
    remediation=path.with_suffix('.remediation-approval.json')
    negation=path.with_suffix('.negation-approval.json')
    if (path.exists() or marker.exists() or path.is_symlink() or marker.is_symlink() or extension.exists()
            or extension.is_symlink() or remediation.exists() or remediation.is_symlink() or negation.exists() or negation.is_symlink()):
        raise BudgetError('Budget or authorization marker already exists; reset is forbidden')
    identity = dict(schema_version='1', ledger_id=uuid4().hex, approval_id=approval_id,
        limit_micro=str(LIMIT_MICRO), attempt_limit=str(MAX_ATTEMPTS), reservation_micro=str(RESERVATION_MICRO))
    try:
        with marker.open('x', encoding='utf-8') as stream:
            json.dump(identity, stream, sort_keys=True)
        with path.open('xb'):
            pass
        with closing(sqlite3.connect(path, isolation_level=None)) as connection:
            connection.execute('PRAGMA journal_mode=DELETE')
            connection.execute('PRAGMA synchronous=FULL')
            connection.execute('BEGIN IMMEDIATE')
            connection.execute('CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL)')
            connection.execute('CREATE TABLE attempts('
                'id TEXT PRIMARY KEY,stage TEXT NOT NULL,payload_hash TEXT NOT NULL,'
                'reserved_micro INTEGER NOT NULL CHECK(reserved_micro=1205863),'
                'charged_micro INTEGER CHECK(charged_micro>=0 AND charged_micro<=reserved_micro),'
                "state TEXT NOT NULL CHECK(state IN ('reserved','unknown','settled')),"
                'usage_json TEXT,outcome INTEGER CHECK(outcome IN (0,1)),error_code TEXT,'
                'created_at TEXT NOT NULL,finished_at TEXT)')
            connection.executemany('INSERT INTO metadata VALUES(?,?)',
                list(identity.items()) + [('consecutive_failures', '0'), ('paused', '0')])
            connection.commit()
    except (OSError, sqlite3.Error) as exc:
        raise BudgetError('Budget initialization incomplete; authorization marker retained') from exc


class BudgetLedger:
    def __init__(self, path: Path, approval_id: str):
        self.path, self.approval_id = path.absolute(), approval_id
        self.summary()

    @contextmanager
    def _connection(self):
        connection = None
        try:
            if (not self.path.is_file() or self.path.is_symlink() or not _marker(self.path).is_file()
                    or _marker(self.path).is_symlink() or _marker(self.path).stat().st_size > 4096):
                raise BudgetError('Existing budget and authorization marker are required')
            marker = json.loads(_marker(self.path).read_text(encoding='utf-8'))
            expected = dict(schema_version='1', ledger_id=marker.get('ledger_id'), approval_id=APPROVAL_ID,
                limit_micro=str(LIMIT_MICRO), attempt_limit=str(MAX_ATTEMPTS), reservation_micro=str(RESERVATION_MICRO))
            if (self.approval_id != APPROVAL_ID or marker != expected
                    or type(marker['ledger_id']) is not str or not re.fullmatch('[0-9a-f]{32}', marker['ledger_id'])):
                raise BudgetError('Budget authorization identity mismatch')
            connection = sqlite3.connect(self.path.as_uri() + '?mode=rw', uri=True, isolation_level=None, timeout=10)
            connection.row_factory = sqlite3.Row
            connection.execute('PRAGMA synchronous=FULL')
            connection.execute('BEGIN IMMEDIATE')
            if connection.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
                raise BudgetError('Budget database integrity check failed')
            metadata = dict(connection.execute('SELECT key,value FROM metadata').fetchall())
            if (set(metadata) != set(expected) | {'consecutive_failures', 'paused'}
                    or any(metadata.get(key) != value for key, value in expected.items())
                    or metadata['paused'] not in ('0', '1') or not metadata['consecutive_failures'].isdigit()):
                raise BudgetError('Budget metadata is missing or corrupt')
            effective,revision=_attempt_limit(self.path,marker)
            metadata['_effective_attempt_limit']=effective
            metadata['_approval_revision']=revision
            yield connection, metadata
            connection.commit()
        except (sqlite3.Error, OSError, ValueError, AttributeError, TypeError) as exc:
            if connection is not None:
                connection.rollback()
            raise BudgetError('Budget ledger unavailable or corrupt') from exc
        finally:
            if connection is not None:
                connection.close()

    def _summary(self, connection, metadata):
        count, used, unknown = connection.execute('SELECT COUNT(*),COALESCE(SUM(COALESCE(charged_micro,reserved_micro)),0),'
            'COALESCE(SUM(charged_micro IS NULL),0) FROM attempts').fetchone()
        attempt_limit=metadata['_effective_attempt_limit']
        if not 0 <= used <= LIMIT_MICRO or count > attempt_limit:
            raise BudgetError('Budget accounting exceeds authorization')
        return BudgetSummary(approval_id=self.approval_id, limit_micro=LIMIT_MICRO, used_micro=used,
            remaining_micro=LIMIT_MICRO-used, attempts=count, unknown_attempts=unknown,
            consecutive_failures=int(metadata['consecutive_failures']),
            paused=metadata['paused'] == '1' or count >= attempt_limit or LIMIT_MICRO-used < RESERVATION_MICRO,
            attempt_limit=attempt_limit,approval_revision=metadata['_approval_revision'])

    def summary(self) -> BudgetSummary:
        with self._connection() as (connection, metadata):
            return self._summary(connection, metadata)

    def resume_after_diagnosis(self,*,expected_failure_ids:tuple[str,...],reason:str,evidence_sha256:str) -> BudgetSummary:
        """Explicit operator recovery of the circuit only; hard quotas never change."""
        if (type(reason) is not str or not reason.strip() or len(reason)>512
                or type(evidence_sha256) is not str or not re.fullmatch('[0-9a-f]{64}',evidence_sha256)
                or type(expected_failure_ids) is not tuple or len(expected_failure_ids)!=3
                or any(type(item) is not str or not re.fullmatch('[0-9a-f]{32}',item) for item in expected_failure_ids)):
            raise BudgetError('A bounded diagnosis, evidence hash and exact three failure identities are required')
        with self._connection() as (connection,metadata):
            current=self._summary(connection,metadata)
            latest=connection.execute('SELECT id,outcome FROM attempts ORDER BY created_at DESC,id DESC LIMIT 3').fetchall()
            if (metadata['paused']!='1' or current.consecutive_failures<3
                    or current.attempts>=current.attempt_limit or current.remaining_micro<RESERVATION_MICRO
                    or connection.execute('SELECT COUNT(*) FROM attempts WHERE outcome IS NULL').fetchone()[0]
                    or tuple(row['id'] for row in latest)!=expected_failure_ids
                    or any(row['outcome']!=0 for row in latest)):
                raise BudgetError('Only the diagnosed completed failure streak can be rearmed within existing hard quotas')
            connection.execute('CREATE TABLE IF NOT EXISTS diagnostic_resumes('
                'id TEXT PRIMARY KEY,failure_ids TEXT NOT NULL UNIQUE,reason TEXT NOT NULL,'
                'evidence_sha256 TEXT NOT NULL,prior_failures INTEGER NOT NULL,'
                'attempts INTEGER NOT NULL,used_micro INTEGER NOT NULL,created_at TEXT NOT NULL)')
            connection.execute('INSERT INTO diagnostic_resumes VALUES(?,?,?,?,?,?,?,?)',
                (uuid4().hex,json.dumps(expected_failure_ids),reason,evidence_sha256,
                    current.consecutive_failures,current.attempts,current.used_micro,_now()))
            connection.execute("UPDATE metadata SET value='0' WHERE key IN ('paused','consecutive_failures')")
            metadata.update(paused='0',consecutive_failures='0')
            return self._summary(connection,metadata)

    def reserve(self, stage: str, payload_hash: str) -> Reservation:
        if stage not in ('generate', 'label', 'augment', 'repair') or type(payload_hash) is not str or not re.fullmatch('[0-9a-f]{64}', payload_hash):
            raise BudgetError('Invalid request authorization metadata')
        with self._connection() as (connection, metadata):
            current = self._summary(connection, metadata)
            if current.paused:
                raise BudgetError('Teacher budget is paused or cannot cover the full reservation')
            attempt_id = uuid4().hex
            connection.execute('INSERT INTO attempts(id,stage,payload_hash,reserved_micro,state,created_at) '
                "VALUES(?,?,?,?,'reserved',?)", (attempt_id, stage, payload_hash, RESERVATION_MICRO, _now()))
        return Reservation(attempt_id=attempt_id, reserved_micro=RESERVATION_MICRO)

    @staticmethod
    def _attempt(connection, attempt_id):
        row = connection.execute('SELECT * FROM attempts WHERE id=?', (attempt_id,)).fetchone()
        if row is None:
            raise BudgetError('No matching pre-request reservation')
        return row

    def settle(self, attempt_id: str, usage: Usage) -> None:
        if not isinstance(usage, Usage):
            raise BudgetError('Complete validated usage is required')
        usage_json = usage.model_dump_json()
        charged = (8 * usage.prompt_tokens + 28 * usage.billable_completion + 9) // 10
        with self._connection() as (connection, metadata):
            row = self._attempt(connection, attempt_id)
            if row['charged_micro'] is not None:
                if row['usage_json'] != usage_json:
                    raise BudgetError('Conflicting settlement cannot alter a prior bill')
                return
            if charged > row['reserved_micro']:
                raise BudgetError('Usage exceeds the full authorized reservation')
            connection.execute("UPDATE attempts SET charged_micro=?,usage_json=?,state='settled' WHERE id=?",
                               (charged, usage_json, attempt_id))

    def mark_unknown(self, attempt_id: str, reason: str) -> None:
        if type(reason) is not str or not re.fullmatch('[a-z][a-z0-9_]{0,63}', reason):
            raise BudgetError('Only safe error codes may enter the ledger')
        with self._connection() as (connection, metadata):
            row = self._attempt(connection, attempt_id)
            if row['charged_micro'] is None:
                connection.execute("UPDATE attempts SET state='unknown',error_code=? WHERE id=?", (reason, attempt_id))

    def record_outcome(self, attempt_id: str, *, success: bool) -> None:
        if type(success) is not bool:
            raise BudgetError('Outcome must be explicit')
        with self._connection() as (connection, metadata):
            row = self._attempt(connection, attempt_id)
            if row['outcome'] is not None:
                if row['outcome'] != int(success):
                    raise BudgetError('Conflicting attempt outcome')
                return
            failures = 0 if success else int(metadata['consecutive_failures']) + 1
            connection.execute('UPDATE metadata SET value=? WHERE key=?', (str(failures), 'consecutive_failures'))
            if failures >= 3:
                connection.execute("UPDATE metadata SET value='1' WHERE key='paused'")
            connection.execute('UPDATE attempts SET outcome=?,finished_at=? WHERE id=?',
                               (int(success), _now(), attempt_id))


def amend_budget_attempt_limit(path:Path,*,revision_id:str,approval_text:str) -> BudgetSummary:
    """Append the explicit human amendment; original marker and SQL rows stay intact."""
    if revision_id!=ATTEMPT_EXTENSION_ID or approval_text!=ATTEMPT_EXTENSION_TEXT:
        raise BudgetError('An exact recognized human authorization amendment is required')
    ledger=BudgetLedger(path,APPROVAL_ID)
    with ledger._connection() as (connection,metadata):
        extension=ledger.path.with_suffix('.attempt-approval.json')
        if not extension.exists():
            marker=json.loads(_marker(ledger.path).read_text(encoding='utf-8'))
            identity=_extension_identity(ledger.path,marker)|dict(approved_at=_now())
            with extension.open('x',encoding='utf-8') as stream:
                json.dump(identity,stream,ensure_ascii=False,sort_keys=True)
                stream.flush()
                import os
                os.fsync(stream.fileno())
            effective,revision=_attempt_limit(ledger.path,marker)
            metadata['_effective_attempt_limit']=effective
            metadata['_approval_revision']=revision
        return ledger._summary(connection,metadata)


def amend_remediation_limit(path:Path,*,revision_id:str,approval_text:str)->BudgetSummary:
    """Second explicit additive approval; never rewrites the original400 amendment."""
    if revision_id!=REMEDIATION_APPROVAL_ID or approval_text!=REMEDIATION_APPROVAL_TEXT:
        raise BudgetError('An exact recognized remediation authorization is required')
    ledger=BudgetLedger(path,APPROVAL_ID)
    with ledger._connection() as (connection,metadata):
        if metadata['_effective_attempt_limit'] not in (400,450):raise BudgetError('The prior400 authorization is required')
        target=ledger.path.with_suffix('.remediation-approval.json')
        marker=json.loads(_marker(ledger.path).read_text(encoding='utf-8'))
        if not target.exists():
            with target.open('x',encoding='utf-8') as stream:
                json.dump(_remediation_identity(ledger.path,marker)|dict(approved_at=_now()),stream,ensure_ascii=False,sort_keys=True)
                stream.flush()
                import os
                os.fsync(stream.fileno())
        limit,revision=_attempt_limit(ledger.path,marker)
        metadata['_effective_attempt_limit']=limit;metadata['_approval_revision']=revision
        return ledger._summary(connection,metadata)


def amend_negation_limit(path:Path,*,revision_id:str,approval_text:str)->BudgetSummary:
    """Append the explicit500 authorization while preserving all previous approvals."""
    if revision_id!=NEGATION_APPROVAL_ID or approval_text!=NEGATION_APPROVAL_TEXT:
        raise BudgetError('An exact recognized negation authorization is required')
    ledger=BudgetLedger(path,APPROVAL_ID)
    with ledger._connection() as (connection,metadata):
        if metadata['_effective_attempt_limit'] not in (450,500):raise BudgetError('The prior450 authorization is required')
        target=ledger.path.with_suffix('.negation-approval.json')
        marker=json.loads(_marker(ledger.path).read_text(encoding='utf-8'))
        if not target.exists():
            with target.open('x',encoding='utf-8') as stream:
                json.dump(_negation_identity(ledger.path,marker)|dict(approved_at=_now()),stream,ensure_ascii=False,sort_keys=True)
                stream.flush()
                import os
                os.fsync(stream.fileno())
        limit,revision=_attempt_limit(ledger.path,marker)
        metadata['_effective_attempt_limit']=limit;metadata['_approval_revision']=revision
        return ledger._summary(connection,metadata)
