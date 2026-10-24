"""Bounded, read-only pool snapshots with explicit preview and frozen provenance."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator
from sqlalchemy import text

from app.db.session import Database
from app.topics.cleaning import CleanQuestion, clean_question
from app.topics.types import StrictRecord


def _digest(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode('utf-8')).hexdigest()


class SnapshotPreview(StrictRecord):
    schema_version: int = Field(default=1, ge=1, le=1)
    database_identity: str = Field(pattern=r'^[0-9a-f]{64}$')
    from_id: int = Field(ge=1, lt=2**64)
    to_id: int | None = Field(default=None, ge=1, lt=2**64)
    limit: int = Field(ge=1, le=100)
    high_water: str = Field(pattern=r'^(0|[1-9][0-9]*)$')
    ids: tuple[str, ...]
    rows_hash: str = Field(pattern=r'^[0-9a-f]{64}$')
    captured_at: str = Field(min_length=1, max_length=40)
    fingerprint: str = Field(pattern=r'^[0-9a-f]{64}$')

    @field_validator('ids', mode='before')
    @classmethod
    def ids_array(cls, value):
        if type(value) not in (list, tuple):
            raise ValueError('IDs must be an array')
        return tuple(value)

    @model_validator(mode='after')
    def check_bounds(self):
        if self.to_id is not None and self.to_id < self.from_id:
            raise ValueError('Invalid snapshot range')
        if len(self.ids) > self.limit or len(set(self.ids)) != len(self.ids):
            raise ValueError('Invalid frozen row IDs')
        if any(not identifier.isascii() or not identifier.isdecimal()
               or not 0 < int(identifier) < 2**64 or str(int(identifier)) != identifier for identifier in self.ids):
            raise ValueError('Expected positive BIGINT strings')
        if not 0 <= int(self.high_water) < 2**64:
            raise ValueError('Invalid high water ID')
        return self


class PoolRow(StrictRecord):
    id: str
    conversation_id: str | None
    user_message_id: str | None
    assistant_message_id: str | None
    raw_question: str
    source: Literal['retrieval_low_conf', 'self_check', 'user_feedback']
    origin: Literal['unverified'] = 'unverified'
    created_at: str
    cleaned: CleanQuestion


class PoolSnapshot(StrictRecord):
    schema_version: int = Field(default=1, ge=1, le=1)
    preview: SnapshotPreview
    rows: tuple[PoolRow, ...]
    snapshot_hash: str = Field(pattern=r'^[0-9a-f]{64}$')

    @field_validator('rows', mode='before')
    @classmethod
    def rows_array(cls, value):
        if type(value) not in (list, tuple):
            raise ValueError('Rows must be an array')
        return tuple(value)


def write_new_json(output: Path, value) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


async def _identity(database, session):
    name, server = (await session.execute(text('SELECT DATABASE(), @@server_uuid'))).one()
    url = database.engine.url
    return _digest(dict(database=name, server=server, host=url.host, port=url.port))


async def _rows(session, *, from_id, upper, limit):
    rows = (await session.execute(text('SELECT id,conversation_id,user_message_id,assistant_message_id,'
        'raw_question,source,created_at FROM low_confidence_questions '
        'WHERE id>=:lower AND id<=:upper ORDER BY id LIMIT :limit'),
        dict(lower=from_id, upper=upper, limit=limit))).mappings().all()
    result = []
    for row in rows:
        value = dict(row)
        for key in ('id', 'conversation_id', 'user_message_id', 'assistant_message_id'):
            value[key] = str(value[key]) if value[key] is not None else None
        value['created_at'] = value['created_at'].isoformat()
        result.append(value)
    return result


async def preview_pool(database: Database, *, from_id: int, to_id: int | None, limit: int) -> SnapshotPreview:
    if (type(from_id) is not int or not 0 < from_id < 2**64 or type(limit) is not int
            or not 1 <= limit <= 100 or to_id is not None
            and (type(to_id) is not int or not from_id <= to_id < 2**64)):
        raise ValueError('Snapshot requires a valid ID range and limit 1..100')
    async with database.session() as session:
        identity = await _identity(database, session)
        high_water = int(await session.scalar(text('SELECT COALESCE(MAX(id),0) FROM low_confidence_questions')))
        upper = min(high_water, to_id) if to_id is not None else high_water
        rows = await _rows(session, from_id=from_id, upper=upper, limit=limit)
    values = dict(schema_version=1, database_identity=identity, from_id=from_id, to_id=to_id,
        limit=limit, high_water=str(high_water), ids=tuple(row['id'] for row in rows),
        rows_hash=_digest(rows), captured_at=datetime.now(timezone.utc).isoformat())
    return SnapshotPreview(**values, fingerprint=_digest(values))


async def export_pool(database: Database, preview: SnapshotPreview, output: Path) -> PoolSnapshot:
    values = preview.model_dump()
    fingerprint = values.pop('fingerprint')
    if fingerprint != _digest(values):
        raise ValueError('Preview scope was modified')
    async with database.session() as session:
        identity = await _identity(database, session)
        if identity != preview.database_identity:
            raise ValueError('Preview database identity changed')
        upper = min(int(preview.high_water), preview.to_id) if preview.to_id is not None else int(preview.high_water)
        rows = await _rows(session, from_id=preview.from_id, upper=upper, limit=preview.limit)
    if tuple(row['id'] for row in rows) != preview.ids or _digest(rows) != preview.rows_hash:
        raise ValueError('Frozen rows changed; create and inspect a new preview')
    output_rows = tuple(PoolRow(**row, cleaned=clean_question(row['raw_question'], sample_id='pool-' + row['id']))
                        for row in rows)
    snapshot = PoolSnapshot(preview=preview, rows=output_rows,
                            snapshot_hash=_digest([row.model_dump(mode='json') for row in output_rows]))
    write_new_json(output, snapshot.model_dump(mode='json'))
    return snapshot
