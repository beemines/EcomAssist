"""原样两步DDL；先核验已存在部分，逐项恢复隐式提交后的缺失结构。"""
from pathlib import Path
import re

from sqlalchemy import text

from app.db.session import Database
from app.quality.migration import _statements, _verify


_SQL = Path(__file__).resolve().parents[2] / 'sql'
_COLUMN_QUERY = ('SELECT COLUMN_NAME,COLUMN_TYPE,IS_NULLABLE,COLUMN_DEFAULT,EXTRA,'
                 'COLUMN_COMMENT,CHARACTER_SET_NAME FROM information_schema.COLUMNS '
                 'WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:table ORDER BY ORDINAL_POSITION')


def _column(definition: str) -> tuple:
    """仅解析用户本章固定DDL语法，以SQL原文而非ORM推导核验契约。"""
    match = re.fullmatch(
        r'(\w+)\s+(BIGINT UNSIGNED|INT|TEXT|DATETIME)\s+(NOT NULL|NULL)'
        r'(?:\s+DEFAULT (CURRENT_TIMESTAMP))?(?:\s+(AUTO_INCREMENT))?'
        r"(?:\s+COMMENT '([^']*)')?", definition.strip())
    if match is None:
        raise RuntimeError('invalid context DDL column')
    name, kind, nullable, default, extra, comment = match.groups()
    return (name, kind.lower(), 'YES' if nullable == 'NULL' else 'NO',
            default.lower() if default else None, 'auto_increment' if extra else '',
            comment or '', 'utf8mb4' if kind == 'TEXT' else None)


def _contracts():
    steps = [_statements((_SQL / name).read_text(encoding='utf-8'))
             for name in ('ch07.sql', 'ch07-layers.sql')]
    if [len(step) for step in steps] != [2, 3] or any(step[0] != 'SET NAMES utf8mb4' for step in steps):
        raise RuntimeError('invalid context DDL steps')
    additions = []
    for statement in (steps[0][1], steps[1][1]):
        if not statement.startswith('ALTER TABLE conversations'):
            raise RuntimeError('invalid context DDL target')
        clauses = re.findall(r'ADD COLUMN\s+(.*?)\s+AFTER\s+(\w+)(?:,|$)', statement, re.S)
        for definition, after in clauses:
            additions.append((_column(definition), after, f'ALTER TABLE conversations ADD COLUMN {definition} AFTER {after}'))
    if [item[0][0] for item in additions] != ['summary', 'summary_upto_msg_id', 'layer1_from_msg_id']:
        raise RuntimeError('invalid context DDL anchors')
    table = re.fullmatch(r"CREATE TABLE IF NOT EXISTS conversation_summaries \(\s*(.*?)\s*\) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='([^']*)'", steps[1][2], re.S)
    if table is None:
        raise RuntimeError('invalid context DDL summary table')
    body, comment = table.groups()
    columns, indexes = [], set()
    for line in body.splitlines():
        line = line.strip().rstrip(',')
        index = re.fullmatch(r'(PRIMARY KEY|UNIQUE KEY (\w+)|KEY (\w+)) \((\w+(?:,\s*\w+)*)\)', line)
        if index:
            declaration, unique_name, name, fields = index.groups()
            index_name = unique_name or name or 'PRIMARY'
            indexes.update((index_name, field.strip(), seq, 1 if declaration.startswith('KEY ') else 0, None, 'BTREE')
                           for seq, field in enumerate(fields.split(','), 1))
        else:
            columns.append(_column(line))
    return steps, additions, {'comment': comment, 'columns': columns, 'indexes': indexes, 'foreign_keys': set()}


def _actual(row) -> tuple:
    default = None if row.COLUMN_DEFAULT is None else str(row.COLUMN_DEFAULT)
    if row.COLUMN_TYPE.lower() == 'datetime' and default is not None:
        default = default.lower().replace('()', '')
    return (row.COLUMN_NAME, row.COLUMN_TYPE.lower(), row.IS_NULLABLE, default,
            row.EXTRA.lower().replace('default_generated', '').strip(), row.COLUMN_COMMENT, row.CHARACTER_SET_NAME)


async def _existing(connection, additions, summary_contract, target):
    tables = set((await connection.scalars(text('SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE()'))).all())
    if not {'conversations', 'messages'} <= tables:
        raise RuntimeError('context base schema missing; apply original conversations/messages DDL first')
    rows = (await connection.execute(text(_COLUMN_QUERY), {'table': 'conversations'})).all()
    by_name = {row.COLUMN_NAME: row for row in rows}
    actual_order = [row.COLUMN_NAME for row in rows]
    # 已存在列先全部核验，不能先补列再发现另一处结构漂移。
    predecessors = ['status']
    for expected, after, statement in additions:
        name = expected[0]
        if name in by_name:
            if _actual(by_name[name]) != expected:
                raise RuntimeError(f'context schema mismatch: conversations.{name}')
            # 前驱列未成功时仍须位于最近已存在前驱后，避免先补DDL才发现位置漂移。
            previous = next((field for field in reversed(predecessors) if field in by_name), None)
            if previous is None or actual_order.index(name) != actual_order.index(previous) + 1:
                raise RuntimeError(f'context schema mismatch: conversations.{name} position')
        predecessors.append(name)
    if 'conversation_summaries' in tables:
        try:
            await _verify(connection, 'conversation_summaries', summary_contract, target)
        except RuntimeError as exc:
            raise RuntimeError('context schema mismatch: conversation_summaries; explicit repair required') from exc
    return set(by_name), 'conversation_summaries' in tables


async def _check(database: Database, *, initialize: bool) -> None:
    steps, additions, summary_contract = _contracts()
    # MySQL DDL隐式提交；begin仅管理连接，不承诺整个迁移能回滚。
    async with database.engine.begin() as connection:
        target = await connection.scalar(text('SELECT DATABASE()'))
        if not target or target != database.engine.url.database:
            raise RuntimeError('context target database mismatch')
        columns, table_exists = await _existing(connection, additions, summary_contract, target)
        missing = [item for item in additions if item[0][0] not in columns]
        if not initialize and (missing or not table_exists):
            raise RuntimeError('context schema missing; explicit migration required')
        if initialize and (missing or not table_exists):
            await connection.exec_driver_sql(steps[0][0])
            first_missing = [item for item in additions[:2] if item[0][0] not in columns]
            if len(first_missing) == 2:
                await connection.exec_driver_sql(steps[0][1])
            else:
                for expected, after, statement in first_missing:
                    await connection.exec_driver_sql(statement)
            if additions[2][0][0] not in columns:
                await connection.exec_driver_sql(steps[1][1])
            if not table_exists:
                await connection.exec_driver_sql(steps[1][2])
            await _existing(connection, additions, summary_contract, target)


async def verify_context(database: Database) -> None:
    """仅SELECT核验；缺失结构和漂移都明确拒绝。"""
    await _check(database, initialize=False)


async def migrate_context(database: Database) -> None:
    """已有定义必须匹配；只补用户DDL中尚未成功的列/表。"""
    await _check(database, initialize=True)
