"""Explicit incremental migrations; no migration is run during module import."""
import argparse
import asyncio

from app.config import load_settings
from app.db.session import Database
from app.flywheel.migration import migrate_flywheel, verify_flywheel


def database_url(settings, target):
    if target == 'test':
        return settings.database_url.set(host='127.0.0.1', port=3308, database='customer_service_test')
    if target == 'configured':
        return settings.database_url
    raise ValueError('Choose test or configured database explicitly')


async def run(args):
    database = Database(database_url(load_settings(), args.database))
    try:
        if args.action == 'migrate':
            await migrate_flywheel(database)
        else:
            await verify_flywheel(database)
        print(f'flywheel {args.action}: schema verified ({args.database})')
    finally:
        await database.dispose()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('migrate', 'verify'))
    parser.add_argument('--database', choices=('test', 'configured'), required=True)
    args = parser.parse_args(argv)
    try:
        asyncio.run(run(args))
    except RuntimeError as exc:
        parser.exit(1, f'flywheel schema operation stopped: {exc}\n')
    except Exception as exc:
        parser.exit(1, f'flywheel schema operation failed: {type(exc).__name__}\n')


if __name__ == '__main__':
    main()
