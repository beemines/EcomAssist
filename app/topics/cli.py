"""Explicit operational commands; migrations default to read-only preview."""

import argparse
import asyncio
import os

from app.config import load_settings
from app.db.session import Database
from app.topics.migration import migrate_topics, verify_topics


async def run(args):
    settings = load_settings(env_file=os.environ.get('CH10_ENV_FILE', '.env'))
    url = settings.database_url
    if args.database == 'test':
        url = url.set(host='127.0.0.1', port=3308, database='customer_service_test', username='customer_service')
    database = Database(url)
    try:
        if args.command == 'verify':
            await verify_topics(database)
            print('{"verified":true,"read_only":true}')
        else:
            result = await migrate_topics(database, preview=not args.execute)
            print(result.model_dump_json())
    finally:
        await database.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    migrate = commands.add_parser('migrate', help='Preview by default; explicit --execute changes the schema')
    migrate.add_argument('--database', choices=['configured', 'test'], required=True)
    migrate.add_argument('--execute', action='store_true')
    verify = commands.add_parser('verify', help='Verify the exact known schema without writes')
    verify.add_argument('--database', choices=['configured', 'test'], required=True)
    asyncio.run(run(parser.parse_args()))


if __name__ == '__main__':
    main()
