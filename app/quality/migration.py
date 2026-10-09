# 原 DDL 同时决定执行语句与核验契约；不借 ORM 建表，也不自动修复已有结构。
from pathlib import Path
import re

from sqlalchemy import text

from app.db.session import Database


_DDL = Path(__file__).resolve().parents[2] / "sql" / "ch04-ddl.sql"
_TABLE_NAMES = {"low_confidence_questions", "faith_cases"}


# 仅在字符串外切分语句，保留中文 COMMENT 内原有的分号和全部字面量。
def _statements(ddl: str) -> list[str]:
    sql = re.sub(r"(?m)^\s*--[^\n]*$", "", ddl)
    result, buffer = [], []
    quoted = False
    escaped = False
    for char in sql:
        if char == ";" and not quoted:
            if "".join(buffer).strip():
                result.append("".join(buffer).strip())
            buffer = []
            continue
        buffer.append(char)
        if escaped:
            escaped = False
        elif char == "\\" and quoted:
            escaped = True
        elif char == "'":
            quoted = not quoted
    if quoted:
        raise RuntimeError("invalid quality DDL: unclosed literal")
    if "".join(buffer).strip():
        result.append("".join(buffer).strip())
    return result


# 规范 SQL 类型拼写但保留 ENUM 字面量大小写与中文原值。
def _type(value: str) -> str:
    if value.upper().startswith("ENUM("):
        return "enum" + value[value.index("("):]
    return re.sub(r"\s+", " ", value.lower()).strip()


# 从固定原样 CREATE 语句读取核验契约，避免映射与数据库一起漂移仍被误判为一致。
def _contract(statement: str) -> tuple[str, dict]:
    table = re.fullmatch(r"CREATE TABLE (\w+) \(\s*(.*?)\s*\) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='([^']*)'", statement, re.S)
    if table is None:
        raise RuntimeError("invalid quality DDL: unsupported table definition")
    name, body, comment = table.groups()
    columns, indexes, foreign_keys = [], set(), set()
    for line in body.splitlines():
        line = line.strip().rstrip(",")
        column = re.fullmatch(r"(\w+)\s+((?:BIGINT|INT) UNSIGNED|VARCHAR\(\d+\)|ENUM\('[^)]*'\)|TEXT|JSON|DATETIME)\s+(NOT NULL|NULL)(?:\s+DEFAULT ('[^']*'|CURRENT_TIMESTAMP|\d+))?(?:\s+(AUTO_INCREMENT))?\s+COMMENT '([^']*)'", line)
        index = re.fullmatch(r"(PRIMARY KEY|UNIQUE KEY \w+|KEY \w+) \((\w+)\)", line)
        foreign = re.fullmatch(r"CONSTRAINT (\w+) FOREIGN KEY \((\w+)\) REFERENCES (\w+) \((\w+)\)", line)
        if column:
            col_name, col_type, nullable, default, extra, col_comment = column.groups()
            if default is not None:
                default = default.strip("'")
                if col_type == "DATETIME":
                    default = default.lower()
            charset = "utf8mb4" if col_type.startswith(("VARCHAR", "ENUM", "TEXT")) else None
            columns.append((col_name, _type(col_type), "NO" if nullable == "NOT NULL" else "YES", default, "auto_increment" if extra else "", col_comment, charset))
        elif index:
            declaration, col_name = index.groups()
            idx_name = "PRIMARY" if declaration == "PRIMARY KEY" else declaration.split()[-1]
            unique = declaration.startswith(("PRIMARY", "UNIQUE"))
            indexes.add((idx_name, col_name, 1, 0 if unique else 1, None, "BTREE"))
        elif foreign:
            fk_name, col_name, target, target_col = foreign.groups()
            foreign_keys.add((fk_name, col_name, target, target_col, "RESTRICT", "RESTRICT"))
            indexes.add((fk_name, col_name, 1, 1, None, "BTREE"))
        else:
            raise RuntimeError(f"invalid quality DDL: unsupported definition in {name}")
    return name, {"comment": comment, "columns": columns, "indexes": indexes, "foreign_keys": foreign_keys}


# 获取数据库实际结构并与 DDL 直接解析的契约比较，拒绝缺列、多列和规则漂移。
async def _verify(connection, name: str, expected: dict, schema: str) -> None:
    parameters = {"table": name}
    options = (await connection.execute(text("SELECT ENGINE,TABLE_COLLATION,TABLE_COMMENT,TABLE_TYPE FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:table"), parameters)).one()
    if options.ENGINE != "InnoDB" or not options.TABLE_COLLATION.startswith("utf8mb4_") or options.TABLE_COMMENT != expected["comment"] or options.TABLE_TYPE != "BASE TABLE":
        raise RuntimeError(f"quality schema mismatch: {name} table options")
    rows = (await connection.execute(text("SELECT COLUMN_NAME,COLUMN_TYPE,IS_NULLABLE,COLUMN_DEFAULT,EXTRA,COLUMN_COMMENT,CHARACTER_SET_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:table ORDER BY ORDINAL_POSITION"), parameters)).all()
    actual_columns = []
    for row in rows:
        default = None if row.COLUMN_DEFAULT is None else str(row.COLUMN_DEFAULT)
        if row.COLUMN_TYPE.lower() == "datetime" and default is not None:
            default = default.lower().replace("()", "")
        extra = row.EXTRA.lower().replace("default_generated", "").strip()
        actual_columns.append((row.COLUMN_NAME, _type(row.COLUMN_TYPE), row.IS_NULLABLE, default, extra, row.COLUMN_COMMENT, row.CHARACTER_SET_NAME))
    if actual_columns != expected["columns"]:
        raise RuntimeError(f"quality schema mismatch: {name} columns")
    indexes = (await connection.execute(text("SELECT INDEX_NAME,COLUMN_NAME,SEQ_IN_INDEX,NON_UNIQUE,SUB_PART,INDEX_TYPE FROM information_schema.STATISTICS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:table"), parameters)).all()
    if {tuple(row) for row in indexes} != expected["indexes"]:
        raise RuntimeError(f"quality schema mismatch: {name} indexes")
    foreign_keys = (await connection.execute(text("SELECT k.CONSTRAINT_NAME,k.COLUMN_NAME,k.REFERENCED_TABLE_SCHEMA,k.REFERENCED_TABLE_NAME,k.REFERENCED_COLUMN_NAME,r.DELETE_RULE,r.UPDATE_RULE FROM information_schema.KEY_COLUMN_USAGE k JOIN information_schema.REFERENTIAL_CONSTRAINTS r ON r.CONSTRAINT_SCHEMA=k.CONSTRAINT_SCHEMA AND r.TABLE_NAME=k.TABLE_NAME AND r.CONSTRAINT_NAME=k.CONSTRAINT_NAME WHERE k.TABLE_SCHEMA=DATABASE() AND k.TABLE_NAME=:table AND k.REFERENCED_TABLE_NAME IS NOT NULL"), parameters)).all()
    # MySQL 的默认 NO ACTION 与 RESTRICT 等价，但跨库引用始终拒绝。
    actual_fks = {(r.CONSTRAINT_NAME, r.COLUMN_NAME, r.REFERENCED_TABLE_NAME, r.REFERENCED_COLUMN_NAME, r.DELETE_RULE.replace("NO ACTION", "RESTRICT"), r.UPDATE_RULE.replace("NO ACTION", "RESTRICT")) for r in foreign_keys}
    if any(r.REFERENCED_TABLE_SCHEMA != schema for r in foreign_keys) or actual_fks != expected["foreign_keys"]:
        raise RuntimeError(f"quality schema mismatch: {name} foreign keys")


# 仅两表都缺失时执行原 DDL；已有两表只做核验，部分存在必须显式修复。
async def migrate_quality(database: Database) -> None:
    statements = _statements(_DDL.read_text(encoding="utf-8"))
    contracts = dict(_contract(s) for s in statements if s.startswith("CREATE TABLE "))
    if set(contracts) != _TABLE_NAMES or statements[0] != "SET NAMES utf8mb4":
        raise RuntimeError("invalid quality DDL: tables or character set")
    async with database.engine.begin() as connection:
        target = await connection.scalar(text("SELECT DATABASE()"))
        if target is None or target != database.engine.url.database:
            raise RuntimeError("quality migration target database mismatch")
        existing = set((await connection.scalars(text("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME IN ('low_confidence_questions','faith_cases')"))).all())
        if existing and existing != _TABLE_NAMES:
            raise RuntimeError("partial quality schema; explicit repair required")
        if not existing:
            for statement in statements:
                await connection.exec_driver_sql(statement)
        for name, expected in contracts.items():
            await _verify(connection, name, expected, target)


# 在线启动只读取原 DDL 契约和实际结构，缺表或漂移都拒绝，不执行任何 DDL。
async def verify_quality(database: Database) -> None:
    statements = _statements(_DDL.read_text(encoding='utf-8'))
    contracts = dict(_contract(s) for s in statements if s.startswith('CREATE TABLE '))
    if set(contracts) != _TABLE_NAMES or statements[0] != 'SET NAMES utf8mb4':
        raise RuntimeError('invalid quality DDL: tables or character set')
    async with database.engine.connect() as connection:
        target = await connection.scalar(text('SELECT DATABASE()'))
        if target is None or target != database.engine.url.database:
            raise RuntimeError('quality verification target database mismatch')
        existing = set((await connection.scalars(text("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME IN ('low_confidence_questions','faith_cases')"))).all())
        if existing != _TABLE_NAMES:
            raise RuntimeError('quality schema missing; explicit migration required')
        for name, expected in contracts.items():
            await _verify(connection, name, expected, target)
