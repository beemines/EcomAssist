import argparse
import asyncio
import sys
from app.config import load_settings
from app.db.session import Database
from app.tool_audit.migration import migrate_tool_audit, verify_tool_audit


async def run(command):
    database = Database(load_settings().database_url)
    try:
        action = migrate_tool_audit if command == 'init' else verify_tool_audit
        await action(database)
        print('Tool audit schema ready')
    finally:
        await database.dispose()


def main():
    parser = argparse.ArgumentParser(description='Explicit tool audit schema migration')
    parser.add_argument('command', choices=['init', 'verify'])
    args = parser.parse_args()
    try:
        asyncio.run(run(args.command))
    except Exception as exc:
        print(f'Tool audit schema failed ({type(exc).__name__}); check target/schema', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
