"""原样退款DDL与结构核验；在线启动绝不执行DDL。"""
from pathlib import Path
import re

from sqlalchemy import text

from app.db.session import Database
from app.quality.migration import _contract, _statements, _verify


_DDL = Path(__file__).resolve().parents[2] / 'sql' / 'ch06-ddl.sql'


def _refund_contract():
    """复用已验证的DDL解析器，并扩展退款复合身份索引契约。"""
    statements = _statements(_DDL.read_text(encoding='utf-8'))
    if len(statements) != 2 or statements[0] != 'SET NAMES utf8mb4':
        raise RuntimeError('invalid refund DDL')
    statement = statements[1]
    composite = re.findall(r'^\s*KEY (\w+) \((\w+,\w+,\w+)\),\s*$', statement, flags=re.M)
    without_composite = re.sub(r'^\s*KEY \w+ \(\w+,\w+,\w+\),\s*$', '', statement, flags=re.M)
    without_composite = '\n'.join(line for line in without_composite.splitlines() if line.strip())
    name, expected = _contract(without_composite)
    if name != 'refund_requests' or len(composite) != 1:
        raise RuntimeError('invalid refund DDL contract')
    for index, columns in composite:
        expected['indexes'].update((index, column, seq, 1, None, 'BTREE')
            for seq, column in enumerate(columns.split(','), 1))
    return statements, name, expected


async def _check(database, *, initialize):
    """只在显式init且表缺失时创建；存在表必须精确匹配，不自动修复。"""
    statements, name, expected = _refund_contract()
    async with database.engine.begin() as connection:
        target = await connection.scalar(text('SELECT DATABASE()'))
        if target is None or target != database.engine.url.database:
            raise RuntimeError('refund target database mismatch')
        exists = await connection.scalar(text("SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='refund_requests'"))
        if not exists:
            if not initialize:
                raise RuntimeError('refund schema missing; explicit init required')
            for statement in statements:
                await connection.exec_driver_sql(statement)
        try:
            await _verify(connection, name, expected, target)
        except RuntimeError as exc:
            raise RuntimeError('refund schema mismatch; explicit repair required') from exc


async def migrate_refunds(database: Database) -> None:
    """显式init仅建缺表，历史表存在时严格核验。"""
    await _check(database, initialize=True)


async def verify_refunds(database: Database) -> None:
    """启动与verify命令只读核验，缺失和漂移都拒绝。"""
    await _check(database, initialize=False)
