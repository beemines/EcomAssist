"""Incremental, exact DDL contracts; never rebuild or repair a partial schema."""
from copy import deepcopy
from pathlib import Path
import re

from sqlalchemy import text

from app.quality.migration import _contract, _statements, _verify

ROOT = Path(__file__).resolve().parents[2]
TABLES = {'review_queue', 'eval_runs'}


def _create_contract(statement):
    updates = set(re.findall(r'(?m)^\s*(\w+)[^\n]*ON UPDATE CURRENT_TIMESTAMP', statement))
    name, contract = _contract(re.sub(r'\s+ON UPDATE CURRENT_TIMESTAMP', '', statement))
    contract['columns'] = [(*column[:4], 'on update current_timestamp', *column[5:])
                           if column[0] in updates else column for column in contract['columns']]
    return name, contract


def _clauses(source):
    result, start, depth, quoted = [], 0, 0, False
    for index, char in enumerate(source):
        if char == "'":
            quoted = not quoted
        elif not quoted:
            depth += (char == '(') - (char == ')')
            if char == ',' and depth == 0:
                result.append(source[start:index].strip())
                start = index + 1
    result.append(source[start:].strip())
    return result


def _apply_alter(contracts, statement):
    match = re.fullmatch(r'ALTER TABLE (\w+)\s+(.*)', statement, re.S)
    if match is None or match[1] not in contracts:
        raise RuntimeError('invalid flywheel DDL ALTER target')
    contract = contracts[match[1]]
    for clause in _clauses(match[2]):
        if clause.startswith('ADD COLUMN '):
            column_source = clause[len('ADD COLUMN '):]
            position = re.search(r'\s+AFTER (\w+)$', column_source)
            if position:
                column_source = column_source[:position.start()]
            _, parsed = _contract("CREATE TABLE temporary (\n" + column_source +
                "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='temporary'")
            [column] = parsed['columns']
            if column[0] in [item[0] for item in contract['columns']]:
                raise RuntimeError('invalid flywheel DDL duplicate column')
            if position:
                names = [item[0] for item in contract['columns']]
                if position[1] not in names:
                    raise RuntimeError('invalid flywheel DDL AFTER target')
                contract['columns'].insert(names.index(position[1]) + 1, column)
            else:
                contract['columns'].append(column)
        else:
            index = re.fullmatch(r'ADD (UNIQUE KEY|KEY) (\w+) \(([^)]+)\)', clause)
            foreign = re.fullmatch(r'ADD CONSTRAINT (\w+) FOREIGN KEY \((\w+)\) REFERENCES (\w+) \((\w+)\) ON DELETE SET NULL', clause)
            if index:
                for seq, name in enumerate(index[3].split(','), 1):
                    contract['indexes'].add((index[2], name.strip(), seq,
                        0 if index[1] == 'UNIQUE KEY' else 1, None, 'BTREE'))
            elif foreign:
                name, column, target, target_column = foreign.groups()
                contract['foreign_keys'].add((name, column, target, target_column, 'SET NULL', 'RESTRICT'))
                if not any(item[1] == column and item[2] == 1 for item in contract['indexes']):
                    contract['indexes'].add((name, column, 1, 1, None, 'BTREE'))
            else:
                raise RuntimeError('invalid flywheel DDL addition')


def _contracts():
    original = _statements((ROOT / 'sql/ch09-ddl.sql').read_text(encoding='utf-8'))
    runtime = _statements((ROOT / 'sql/ch09-runtime.sql').read_text(encoding='utf-8'))
    if original[0] != 'SET NAMES utf8mb4' or runtime[0] != original[0]:
        raise RuntimeError('invalid flywheel DDL charset')
    quality = dict(_contract(stmt) for stmt in _statements(
        (ROOT / 'sql/ch04-ddl.sql').read_text(encoding='utf-8')) if stmt.startswith('CREATE TABLE '))
    baseline = {'low_confidence_questions': quality['low_confidence_questions']}
    base = deepcopy(baseline)
    for statement in original[1:]:
        if statement.startswith('CREATE TABLE '):
            name, contract = _create_contract(statement)
            if name not in TABLES:
                raise RuntimeError('invalid flywheel DDL table')
            base[name] = contract
        else:
            _apply_alter(base, statement)
    if set(base) != TABLES | {'low_confidence_questions'}:
        raise RuntimeError('invalid flywheel DDL table set')
    complete = deepcopy(base)
    for statement in runtime[1:]:
        _apply_alter(complete, statement)
    return baseline, base, complete, original, runtime


def quality_extension_contracts(expected):
    """Only exact known additions are accepted by the old quality verifier."""
    baseline, base, complete, _, _ = _contracts()
    if expected != baseline['low_confidence_questions']:
        return []
    return [base['low_confidence_questions'], complete['low_confidence_questions']]


async def _columns(connection, table):
    return list((await connection.scalars(text(
        'SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() '
        'AND TABLE_NAME=:table ORDER BY ORDINAL_POSITION'), {'table': table})).all())


async def _verify_set(connection, contracts, schema):
    for table, expected in contracts.items():
        await _verify(connection, table, expected, schema)


async def _check(database, *, initialize):
    baseline, base, complete, original, runtime = _contracts()
    async with database.engine.begin() as connection:
        schema = await connection.scalar(text('SELECT DATABASE()'))
        if not schema or schema != database.engine.url.database:
            raise RuntimeError('flywheel migration target database mismatch')
        existing = set((await connection.scalars(text(
            "SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() "
            "AND TABLE_NAME IN ('review_queue','eval_runs','low_confidence_questions')"))).all())
        if 'low_confidence_questions' not in existing:
            raise RuntimeError('flywheel schema requires ch02/ch04 prerequisites')
        new_tables = existing & TABLES
        if new_tables and new_tables != TABLES:
            raise RuntimeError('partial flywheel schema; explicit repair required')
        if not new_tables:
            await _verify_set(connection, baseline, schema)
            if not initialize:
                raise RuntimeError('flywheel schema missing; explicitly migrate')
            for statement in original:
                await connection.exec_driver_sql(statement)
            await _verify_set(connection, base, schema)
            stage = 'base'
        else:
            names = {table: await _columns(connection, table) for table in complete}
            if all(names[table] == [col[0] for col in expected['columns']]
                   for table, expected in complete.items()):
                await _verify_set(connection, complete, schema)
                return
            if all(names[table] == [col[0] for col in expected['columns']]
                   for table, expected in base.items()):
                await _verify_set(connection, base, schema)
                stage = 'base'
            else:
                raise RuntimeError('partial or conflicting flywheel schema; explicit repair required')
        if stage == 'base':
            if not initialize:
                raise RuntimeError('flywheel runtime schema missing; explicitly migrate')
            for statement in runtime:
                await connection.exec_driver_sql(statement)
        await _verify_set(connection, complete, schema)


async def migrate_flywheel(database):
    await _check(database, initialize=True)


async def verify_flywheel(database):
    await _check(database, initialize=False)
