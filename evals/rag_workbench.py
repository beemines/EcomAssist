"""固定数据集与运行目录的评估入口；validate全离线，run与HTTP共用生命周期。"""

import argparse
import asyncio
import json

from app.config import load_settings
from app.rag_evaluation import manager as lifecycle
from app.rag_evaluation.dataset import DatasetError, load_dataset
from app.rag_evaluation.export import report_envelope
from app.rag_evaluation.locking import RunBusy
from app.rag_evaluation.store import RunStore, StoreError


async def _command(args) -> dict:
    """历史展示只投影真实检查点，新运行则由相同 manager 拥有锁和清理。"""
    store = RunStore(lifecycle.RUNTIME_ROOT)
    if args.command == 'show':
        return report_envelope(await store.get(args.run_id), await store.records(args.run_id))
    manager = lifecycle.RunManager(store, load_settings(), lifecycle.DATASET_ROOT)
    try:
        await manager.startup()
        run_id = await manager.start(args.dataset, args.scope)
        await manager.wait(run_id)
        return report_envelope(await store.get(run_id), await store.records(run_id))
    finally:
        await manager.shutdown()


def main(argv=None) -> int:
    """严格解析三个命令，不开放任意数据库、模型或输出落点参数。"""
    parser = argparse.ArgumentParser(description='RAG评估工作台')
    commands = parser.add_subparsers(dest='command', required=True)
    validate = commands.add_parser('validate')
    validate.add_argument('--dataset', required=True)
    run = commands.add_parser('run')
    run.add_argument('--dataset', required=True)
    run.add_argument('--scope', choices=('pilot', 'full'), required=True)
    show = commands.add_parser('show')
    show.add_argument('--run-id', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'validate':
            dataset = load_dataset(args.dataset, root=lifecycle.DATASET_ROOT)
            result = dict(dataset_id=dataset.dataset_id, fingerprint=dataset.fingerprint,
                          cases=len(dataset.cases), chunks=len(dataset.chunks), pilot_ids=dataset.pilot_ids)
        else:
            result = asyncio.run(_command(args))
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        if args.command == 'run' and result['run']['state'] != 'completed':
            return 1
        return 0
    except (DatasetError, lifecycle.PilotRequired, RunBusy, StoreError) as exc:
        print(json.dumps({'error': type(exc).__name__, 'message': '评估请求未完成'}, ensure_ascii=False))
        return 2
    except KeyboardInterrupt:
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
