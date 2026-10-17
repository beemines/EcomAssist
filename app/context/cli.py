"""显式迁移或只读核验：python -m app.context.cli migrate|verify。"""
import argparse
import asyncio
import sys
import json
from pathlib import Path

from app.config import load_settings
from app.context.migration import migrate_context, verify_context
from app.db.session import Database


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description='Layered conversation context schema')
    commands = result.add_subparsers(dest='command', required=True)
    commands.add_parser('migrate', help='Resume supplied context DDL, refusing structure drift')
    commands.add_parser('verify', help='Read-only verification; never execute DDL')
    for name in ('budget', 'replay'):
        command = commands.add_parser(name, help='Fully offline acceptance '+name)
        command.add_argument('--profile', choices=('default', 'demo'), required=True)
        if name == 'replay':
            command.add_argument('--output', type=Path, required=True)
    return result


async def run(args: argparse.Namespace) -> None:
    if args.command == 'budget':
        from app.context.acceptance import profile_budget
        print(json.dumps(profile_budget(args.profile), ensure_ascii=False, indent=2))
        return
    if args.command == 'replay':
        from app.context.replay import replay
        result = await replay(args.profile, args.output.parent/'replays')
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps({'profile': args.profile, 'output': str(args.output), 'turns': len(result['turns']),
                          'recall': result['final_recall']['source_present']}, ensure_ascii=False))
        return
    database = Database(load_settings().database_url)
    try:
        action = migrate_context if args.command == 'migrate' else verify_context
        await action(database)
        print('Context schema ready')
    finally:
        await database.dispose()


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        asyncio.run(run(args))
    except Exception as exc:
        # 驱动和配置异常可能携带URL/密码，不回显异常正文。
        print(f'Context schema failed ({type(exc).__name__}); check configuration and schema', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
