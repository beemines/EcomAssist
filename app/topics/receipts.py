"""Local failure receipts bound to a database, input hash and model identity."""
from contextlib import closing, contextmanager
import json
import math
from pathlib import Path
import sqlite3
from typing import Literal, Sequence
from uuid import uuid4

from pydantic import Field, model_validator

from app.topics.types import StrictRecord


FailureStatus = Literal['needs_review', 'input_too_long', 'invalid_input', 'cleaning_failed',
                        'temporary_failure', 'permanent_failure']
STATUSES = frozenset(('needs_review', 'input_too_long', 'invalid_input', 'cleaning_failed',
                      'temporary_failure', 'permanent_failure'))


class ReceiptError(RuntimeError):
    """Missing, foreign or corrupt receipts are unknown, never an empty summary."""


class FailureKey(StrictRecord):
    question_id: str = Field(pattern=r'^[1-9][0-9]{0,19}$')
    input_hash: str = Field(pattern=r'^[a-f0-9]{64}$')
    model_version: str = Field(min_length=1, max_length=128)

    @model_validator(mode='after')
    def bounded_id(self):
        if int(self.question_id) > 2**64-1:
            raise ValueError('Question ID exceeds unsigned BIGINT')
        return self


class FailureState(StrictRecord):
    key: FailureKey
    status: FailureStatus
    failures: int = Field(ge=1, le=3)
    next_attempt_at: float | None
    paused: bool
    updated_at: float

    @model_validator(mode='after')
    def consistent(self):
        if self.paused != (self.status != 'temporary_failure' or self.failures == 3):
            raise ValueError('Failure pause contradicts policy')
        if self.paused != (self.next_attempt_at is None):
            raise ValueError('Failure deadline contradicts pause')
        return self


def _clock(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError('Receipt time must be a finite nonnegative epoch')
    return float(value)


def _identity(value):
    import re
    if type(value) is not str or re.fullmatch('[a-f0-9]{64}', value) is None:
        raise ValueError('Database identity must be a SHA256 digest')
    return value


class ReceiptStore:
    def __init__(self, path: Path, *, database_identity: str):
        self.path = path.resolve()
        self.database_identity = _identity(database_identity)

    @staticmethod
    def initialize(path: Path, *, database_identity: str):
        identity = _identity(database_identity)
        path = path.resolve()
        marker = path.with_suffix('.identity.json')
        if path.exists() or marker.exists():
            raise ReceiptError('Receipt store already initialized or requires recovery')
        path.parent.mkdir(parents=True, exist_ok=True)
        header = dict(schema_version=1, store_id=uuid4().hex, database_identity=identity)
        with marker.open('x', encoding='utf-8') as stream:
            json.dump(header, stream, sort_keys=True)
        try:
            with path.open('xb'):
                pass
            with closing(sqlite3.connect(path, isolation_level=None)) as connection:
                connection.execute('PRAGMA synchronous=FULL')
                connection.execute('BEGIN IMMEDIATE')
                connection.execute('CREATE TABLE metadata(header TEXT NOT NULL)')
                connection.execute('INSERT INTO metadata VALUES(?)', (json.dumps(header, sort_keys=True),))
                connection.execute('CREATE TABLE failures(question_id TEXT NOT NULL,input_hash TEXT NOT NULL,'
                    'model_version TEXT NOT NULL,payload TEXT NOT NULL,PRIMARY KEY(question_id,input_hash,model_version))')
                connection.execute('CREATE TABLE events(id INTEGER PRIMARY KEY AUTOINCREMENT,'
                    'question_id TEXT NOT NULL,input_hash TEXT NOT NULL,model_version TEXT NOT NULL,'
                    'action TEXT NOT NULL,created_at REAL NOT NULL)')
                connection.commit()
        except (OSError, sqlite3.Error):
            raise ReceiptError('Receipt initialization failed; identity marker preserved') from None

    @contextmanager
    def _open(self, *, write=False):
        marker = self.path.with_suffix('.identity.json')
        try:
            with closing(sqlite3.connect(self.path.as_uri()+'?mode=rw', uri=True, timeout=5,
                                        isolation_level=None)) as connection:
                expected = json.loads(marker.read_text(encoding='utf-8'))
                headers = connection.execute('SELECT header FROM metadata').fetchall()
                if (len(headers) != 1 or json.loads(headers[0][0]) != expected
                        or set(expected) != {'schema_version', 'store_id', 'database_identity'}
                        or expected['schema_version'] != 1 or expected['database_identity'] != self.database_identity
                        or connection.execute('PRAGMA quick_check').fetchone() != ('ok',)):
                    raise ReceiptError('Receipt identity or integrity mismatch')
                connection.execute('PRAGMA synchronous=FULL')
                connection.execute('BEGIN IMMEDIATE' if write else 'BEGIN')
                try:
                    yield connection
                    connection.commit()
                except BaseException:
                    connection.rollback()
                    raise
        except (OSError, sqlite3.Error, ValueError, KeyError):
            raise ReceiptError('Receipt store unavailable or invalid') from None

    @staticmethod
    def _key(key):
        return FailureKey.model_validate(key.model_dump())

    @staticmethod
    def _read(connection, key):
        row = connection.execute('SELECT payload FROM failures WHERE question_id=? AND input_hash=? AND model_version=?',
            (key.question_id, key.input_hash, key.model_version)).fetchone()
        if row is None:
            return None
        state = FailureState.model_validate_json(row[0])
        if state.key != key:
            raise ReceiptError('Receipt payload identity mismatch')
        return state

    def states(self, keys: Sequence[FailureKey]) -> tuple[FailureState, ...]:
        if len(keys) > 10000:
            raise ValueError('Receipt summary exceeds the bounded 10000-input window')
        checked = tuple(self._key(key) for key in keys)
        with self._open() as connection:
            return tuple(state for key in dict.fromkeys(checked) if (state := self._read(connection, key)) is not None)

    def eligible(self, key: FailureKey, *, now: float) -> bool:
        moment = _clock(now)
        states = self.states([key])
        return not states or (not states[0].paused and states[0].next_attempt_at <= moment)

    def record_failure(self, key: FailureKey, status: FailureStatus, *, now: float) -> FailureState:
        key, moment = self._key(key), _clock(now)
        if status not in STATUSES:
            raise ValueError('Unknown failure status; raw error messages are not receipt codes')
        with self._open(write=True) as connection:
            prior = self._read(connection, key)
            failures = min(3, (prior.failures if prior else 0)+1)
            paused = status != 'temporary_failure' or failures == 3
            state = FailureState(key=key, status=status, failures=failures, paused=paused,
                next_attempt_at=None if paused else moment+min(240, 60*2**(failures-1)), updated_at=moment)
            connection.execute('INSERT INTO failures VALUES(?,?,?,?) ON CONFLICT(question_id,input_hash,model_version) '
                'DO UPDATE SET payload=excluded.payload',
                (key.question_id, key.input_hash, key.model_version, state.model_dump_json()))
            self._event(connection, key, status, moment)
            return state

    @staticmethod
    def _event(connection, key, action, moment):
        connection.execute('INSERT INTO events(question_id,input_hash,model_version,action,created_at) VALUES(?,?,?,?,?)',
            (key.question_id, key.input_hash, key.model_version, action, moment))

    def _clear(self, key, action, now):
        key, moment = self._key(key), _clock(now)
        with self._open(write=True) as connection:
            connection.execute('DELETE FROM failures WHERE question_id=? AND input_hash=? AND model_version=?',
                (key.question_id, key.input_hash, key.model_version))
            self._event(connection, key, action, moment)

    def retry(self, key: FailureKey, *, now: float):
        self._clear(key, 'explicit_retry', now)

    def record_success(self, key: FailureKey, *, now: float):
        self._clear(key, 'classified', now)
