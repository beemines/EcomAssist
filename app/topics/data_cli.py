"""Explicit preparation commands; no imports start paid calls or background workers."""

import argparse
import asyncio
from collections import Counter
import json
import os
from pathlib import Path

from app.topics.snapshot import SnapshotPreview, export_pool, preview_pool, write_new_json


async def snapshot_command(args):
    from app.config import load_settings
    from app.db.session import Database
    settings = load_settings(env_file=os.environ.get('CH10_ENV_FILE', '.env'))
    database = Database(settings.database_url)
    try:
        if args.execute:
            if args.preview_file is None or args.preview:
                raise ValueError('Execute needs --preview-file and no --preview')
            if args.from_id != 1 or args.to_id is not None or args.limit != 100:
                raise ValueError('Execute uses the exact saved preview; omit new range flags')
            preview = SnapshotPreview.model_validate_json(args.preview_file.read_text(encoding='utf-8'))
            snapshot = await export_pool(database, preview, args.output)
            summary = dict(rows=len(snapshot.rows), unique_texts=len({row.cleaned.input_hash for row in snapshot.rows}),
                origins=dict(Counter(row.origin for row in snapshot.rows)),
                sources=dict(Counter(row.source for row in snapshot.rows)),
                quarantined=sum(bool(row.cleaned.quarantine_reasons) for row in snapshot.rows),
                snapshot_hash=snapshot.snapshot_hash)
        else:
            if args.preview_file is not None:
                raise ValueError('--preview-file is used only with --execute')
            preview = await preview_pool(database, from_id=args.from_id, to_id=args.to_id, limit=args.limit)
            write_new_json(args.output, preview.model_dump(mode='json'))
            summary = dict(rows=len(preview.ids), from_id=preview.from_id, high_water=preview.high_water,
                           fingerprint=preview.fingerprint, mode='preview')
        print(json.dumps(summary, ensure_ascii=False))
    finally:
        await database.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    budget_init = commands.add_parser('budget-init', help='Preview or initialize the single approved CNY10 ledger')
    budget_init.add_argument('--execute', action='store_true')
    commands.add_parser('budget-status', help='Read existing budget; never create or reset it')
    snapshot = commands.add_parser('snapshot', help='Preview, then export a bounded read-only pool snapshot')
    snapshot.add_argument('--database', choices=['configured'], default='configured')
    snapshot.add_argument('--from-id', type=int, default=1)
    snapshot.add_argument('--to-id', type=int)
    snapshot.add_argument('--limit', type=int, default=100)
    snapshot.add_argument('--preview', action='store_true')
    snapshot.add_argument('--execute', action='store_true')
    snapshot.add_argument('--preview-file', type=Path)
    snapshot.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.command.startswith('budget-'):
        from app.topics.budget import APPROVAL_ID, BUDGET_PATH, LIMIT_MICRO, MAX_ATTEMPTS, BudgetLedger, initialize_budget
        if args.command == 'budget-init':
            if not args.execute:
                print(json.dumps(dict(mode='preview', approval_id=APPROVAL_ID,
                    limit_micro=LIMIT_MICRO, maximum_physical_attempts=MAX_ATTEMPTS,
                    path=str(BUDGET_PATH)), ensure_ascii=False))
                return
            initialize_budget(BUDGET_PATH, APPROVAL_ID)
        print(BudgetLedger(BUDGET_PATH, APPROVAL_ID).summary().model_dump_json())
    else:
        asyncio.run(snapshot_command(args))


if __name__ == '__main__':
    main()
