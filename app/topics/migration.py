"""Explicit step10 migration with read-only preview and exact known schema stages."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from typing import Literal

from sqlalchemy import text

from app.flywheel.migration import _apply_alter
from app.quality.migration import _contract, _statements, _verify
from app.topics.types import StrictRecord


ROOT = Path(__file__).resolve().parents[2]
TABLE = 'topic_classifications'


class MigrationReceipt(StrictRecord):
    database_identity: str
    stage: Literal['missing', 'base', 'complete']
    preview: bool
    statements: tuple[str, ...]
    applied_count: int
    complete: bool


def contracts():
    original = _statements((ROOT/'sql/ch10-ddl.sql').read_text(encoding='utf-8'))
    runtime = _statements((ROOT/'sql/ch10-runtime.sql').read_text(encoding='utf-8'))
    if len(original) != 2 or len(runtime) != 2 or original[0] != runtime[0] or original[0] != 'SET NAMES utf8mb4':
        raise RuntimeError('Invalid topic DDL statements or character set')
    name, base = _contract(original[1])
    if name != TABLE:
        raise RuntimeError('Invalid topic DDL table')
    # MySQL reuses the already defined unique question index for the FK; the
    # older generic parser assumes an implicit FK index even when one exists.
    base['indexes'].discard(('fk_topic_question', 'question_id', 1, 1, None, 'BTREE'))
    complete = deepcopy(base)
    parsed = re.sub(r'\bCHAR\((64|36)\)', r'VARCHAR(\1)', runtime[1])
    _apply_alter({TABLE: complete}, parsed)
    complete['columns'] = [(column[0], {'input_hash': 'char(64)', 'batch_id': 'char(36)'}.get(column[0], column[1]),
                            *column[2:]) for column in complete['columns']]
    if [column[0] for column in complete['columns'][-4:]] != ['model_version', 'taxonomy_version', 'input_hash', 'batch_id']:
        raise RuntimeError('Invalid topic tracking columns')
    return base, complete, original, runtime


async def migrate_topics(database, *, preview: bool) -> MigrationReceipt:
    if type(preview) is not bool:
        raise ValueError('Migration mode must be explicit')
    base, complete, original, runtime = contracts()
    async with database.engine.connect() as connection:
        schema = await connection.scalar(text('SELECT DATABASE()'))
        if not schema or schema != database.engine.url.database:
            raise RuntimeError('Topic migration database identity mismatch')
        parent = (await connection.execute(text('SELECT c.COLUMN_TYPE,c.IS_NULLABLE,c.COLUMN_KEY,t.ENGINE '
            'FROM information_schema.COLUMNS c JOIN information_schema.TABLES t '
            'ON t.TABLE_SCHEMA=c.TABLE_SCHEMA AND t.TABLE_NAME=c.TABLE_NAME '
            "WHERE c.TABLE_SCHEMA=DATABASE() AND c.TABLE_NAME='low_confidence_questions' AND c.COLUMN_NAME='id'"))).one_or_none()
        if parent is None or tuple(parent) != ('bigint unsigned', 'NO', 'PRI', 'InnoDB'):
            raise RuntimeError('Topic schema requires the existing unsigned question primary key')
        exists = await connection.scalar(text('SELECT COUNT(*) FROM information_schema.TABLES '
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='topic_classifications'"))
        if not exists:
            stage, planned = 'missing', original + runtime
        else:
            names = list((await connection.scalars(text('SELECT COLUMN_NAME FROM information_schema.COLUMNS '
                'WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:table ORDER BY ORDINAL_POSITION'), {'table': TABLE})).all())
            if names == [column[0] for column in complete['columns']]:
                await _verify(connection, TABLE, complete, schema)
                stage, planned = 'complete', []
            elif names == [column[0] for column in base['columns']]:
                await _verify(connection, TABLE, base, schema)
                stage, planned = 'base', runtime
            else:
                raise RuntimeError('Partial or conflicting topic schema; explicit repair required')
        url = database.engine.url
        identity = hashlib.sha256(json.dumps(dict(schema=schema, host=url.host, port=url.port),
            sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        if not preview and planned:
            for statement in planned:
                await connection.exec_driver_sql(statement)
            await connection.commit()
            await _verify(connection, TABLE, complete, schema)
            stage = 'complete'
        return MigrationReceipt(database_identity=identity, stage=stage, preview=preview,
            statements=tuple(planned), applied_count=0 if preview else len(planned), complete=stage == 'complete')


async def verify_topics(database):
    if not (await migrate_topics(database, preview=True)).complete:
        raise RuntimeError('Topic schema missing; explicitly migrate first')
