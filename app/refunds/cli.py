"""退款表的显式init与只读verify；异常输出不含配置或凭据。"""
import argparse
import asyncio
import sys

from app.config import load_settings
from app.db.session import Database
from app.refunds.migration import migrate_refunds, verify_refunds


async def run(args):
    """使用现有配置目标并始终释放连接，init只能由显式命令选择。"""
    database = Database(load_settings().database_url)
    try:
        await (migrate_refunds(database) if args.command == 'init' else verify_refunds(database))
        print('Refund schema ready')
    finally:
        await database.dispose()


def main(argv=None):
    """解析命令并将内部异常映射为不泄密的非零退出码。"""
    parser = argparse.ArgumentParser(description='待审核退款表管理')
    parser.add_argument('command', choices=['init', 'verify'])
    args = parser.parse_args(argv)
    try:
        asyncio.run(run(args))
    except Exception as exc:
        print(f'Refund job failed ({type(exc).__name__}); check configuration', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
