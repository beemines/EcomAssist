"""Explicit operational commands; migrations default to read-only preview."""

import argparse
import asyncio
import os
import json
from pathlib import Path

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
        elif args.command=='migrate':
            result = await migrate_topics(database, preview=not args.execute)
            print(result.model_dump_json())
        else:
            from app.topics.operations import operate
            print(json.dumps(await operate(args,database),ensure_ascii=False))
    finally:
        await database.dispose()


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest='command', required=True)
    migrate = commands.add_parser('migrate', help='Preview by default; explicit --execute changes the schema')
    migrate.add_argument('--database', choices=['configured', 'test'], required=True)
    migrate.add_argument('--execute', action='store_true')
    verify = commands.add_parser('verify', help='Verify the exact known schema without writes')
    verify.add_argument('--database', choices=['configured', 'test'], required=True)
    for name in ('preview','run-once','watch','retry','reclassify'):
        command=commands.add_parser(name)
        command.add_argument('--database',choices=['configured','test'],required=True)
        command.add_argument('--profile',type=Path,required=True)
        command.add_argument('--execute',action='store_true')
        if name in ('preview','watch'):
            command.add_argument('--from-id',type=int,default=1)
            command.add_argument('--to-id',type=int)
            command.add_argument('--limit',type=int,choices=range(1,101),default=100)
            if name=='preview':
                command.add_argument('--output',type=Path)
                command.add_argument('--reclassify',action='store_true')
            else:command.add_argument('--poll-seconds',type=int,choices=range(60,301),default=60)
        else:command.add_argument('--preview-file',type=Path,required=True)
    return result


def main():asyncio.run(run(parser().parse_args()))


if __name__ == '__main__':
    main()
