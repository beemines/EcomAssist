"""Explicit incremental migrations; no migration is run during module import."""
import argparse
import asyncio
import json
from datetime import datetime, timezone
from sqlalchemy import text

from app.config import load_settings
from app.db.session import Database
from app.flywheel.migration import migrate_flywheel, verify_flywheel
from app.flywheel.types import database_id


def database_url(settings, target):
    if target == 'test':
        return settings.database_url.set(host='127.0.0.1', port=3308, database='customer_service_test')
    if target == 'configured':
        return settings.database_url
    raise ValueError('Choose test or configured database explicitly')


async def run(args):
    settings = load_settings()
    if args.action == 'calibrate':
        from app.flywheel.acceptance import acceptance_cap
        from app.quality.calibration import run_calibration
        result = await run_calibration(settings, args.output,
            acceptance_cap(args.acceptance_run) if args.acceptance_run else None)
        print(json.dumps({'rule_version': result.rule.rule_version,
            'calibration': result.calibration, 'held_out': result.held_out}, ensure_ascii=False))
        return
    database = Database(database_url(settings, args.database))
    try:
        if args.action == 'migrate':
            await migrate_flywheel(database)
        elif args.action == 'verify':
            await verify_flywheel(database)
        else:
            await verify_flywheel(database)
            from app.flywheel.repository import FlywheelRepository, row_dict
            repository = FlywheelRepository(database)
            if args.action == 'status':
                async with database.session() as session:
                    row = (await session.execute(text('SELECT id,processing,matched_review_id FROM '
                        'low_confidence_questions WHERE id=:id'), {'id': int(args.pool_id)})).mappings().one_or_none()
                    result = row_dict(row) if row else {'id': args.pool_id, 'found': False}
            elif args.action == 'process':
                from app.flywheel.runtime import FlywheelRuntime
                from app.flywheel.acceptance import acceptance_cap
                cap = acceptance_cap(args.acceptance_run) if args.acceptance_run else None
                runtime = await FlywheelRuntime.create(settings, database=database, acceptance_call_cap=cap)
                try:
                    receipt = await runtime.processor.process(args.pool_id)
                    result = receipt.model_dump() if receipt else {'id': args.pool_id, 'matched': False}
                finally:
                    await runtime.close()
            else:
                result = await repository.manage_processing(args.pool_id, action=args.action, now=datetime.now(timezone.utc))
            print(json.dumps(result, ensure_ascii=False))
            return
        print(f'flywheel {args.action}: schema verified ({args.database})')
    finally:
        await database.dispose()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('migrate', 'verify', 'process', 'status', 'initialize', 'retry', 'recover', 'calibrate'))
    parser.add_argument('--database', choices=('test', 'configured'), required=True)
    parser.add_argument('--pool-id', type=database_id, help='仅管理此指定问题ID，不扫描旧记录')
    parser.add_argument('--execute', action='store_true', help='显式执行处理或管理；缺省仅显示dry-run')
    parser.add_argument('--acceptance-run', choices=('ch09-local-20261019',))
    parser.add_argument('--output', type=__import__('pathlib').Path)
    args = parser.parse_args(argv)
    if args.action == 'calibrate':
        if args.database != 'test' or args.output is None:
            parser.error('Calibration requires --database test and --output')
        if not args.execute:
            from pathlib import Path
            from app.rag_evaluation.dataset import DATASET_ID, load_dataset
            from app.quality.calibration import build_calibration_split
            dataset = load_dataset(DATASET_ID, root=Path(__file__).parents[2] / 'evals/datasets')
            split = build_calibration_split(dataset)
            print(f'dry-run: {len(dataset.cases)} retrievals; calibration={len(split.calibration_ids)}; '
                f'held_out={len(split.held_out_ids)}; no credentials, database, models or upstream connections')
            return
    elif args.action not in ('migrate', 'verify') and args.pool_id is None:
        parser.error('This action requires one --pool-id')
    if args.action in ('process', 'initialize', 'retry', 'recover') and not args.execute:
        print(f'dry-run: {args.action} pool_id={args.pool_id}; no database writes or model calls')
        return
    try:
        asyncio.run(run(args))
    except (RuntimeError, ValueError) as exc:
        parser.exit(1, f'flywheel schema operation stopped: {exc}\n')
    except Exception as exc:
        parser.exit(1, f'flywheel schema operation failed: {type(exc).__name__}\n')


if __name__ == '__main__':
    main()
