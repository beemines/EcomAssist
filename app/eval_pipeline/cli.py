"""Explicitly run a frozen scope; dry-run never reads credentials or calls upstream."""
import argparse
import asyncio
import json
from pathlib import Path
from app.config import load_settings
from app.eval_pipeline.types import run_key

ROOT=Path(__file__).resolve().parents[2]


def rule_for_settings(settings):
    from app.quality.evidence_confidence import load_online_rule,evidence_budget_fingerprint
    path=settings.evidence_confidence_rule_path or ROOT/'runtime/ch09-evidence/calibration/rule.json'
    return load_online_rule(path,top_k=settings.rerank_top_k,rerank_model=settings.rerank_model,
        budget_fingerprint=evidence_budget_fingerprint(top_k=settings.rerank_top_k,
            token_budget=min(6000,(settings.model_context_window+7)//8)))


async def run(args):
    from app.db.session import Database
    from app.flywheel.migration import verify_flywheel
    from app.flywheel.acceptance import acceptance_cap
    from app.eval_pipeline.store import PipelineStore,EvalRunRepository
    from app.eval_pipeline.manager import EvalPipelineManager
    from app.observability.runtime import LangfuseRuntime
    settings=load_settings()
    rule=rule_for_settings(settings)
    database=Database(settings.database_url)
    observability=LangfuseRuntime.from_settings(settings)
    manager=None
    try:
        await verify_flywheel(database)
        cap=acceptance_cap(args.acceptance_run) if args.acceptance_run else None
        manager=EvalPipelineManager(PipelineStore(ROOT/'runtime/eval-pipeline'),EvalRunRepository(database),
            settings,rule,acceptance_call_cap=cap,observability=observability)
        await manager.startup()
        if args.action=='run':
            await manager.start(run_key=args.run_key,scope=args.scope,triggered_by='手动')
            while manager.tasks: await asyncio.gather(*set(manager.tasks),return_exceptions=True)
            result=(await manager.get_run(args.run_key)).model_dump(mode='json')
        elif args.action=='status': result=(await manager.get_run(args.run_key)).model_dump(mode='json')
        else: result=await manager.list_runs()
        print(json.dumps(result,ensure_ascii=False,allow_nan=False))
    finally:
        try:
            if manager is not None: await manager.close()
        finally:
            await observability.close()
            await database.dispose()


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('run','status','recover'))
    parser.add_argument('--scope',choices=('smoke_20','full_300'),default='smoke_20')
    parser.add_argument('--run-key',type=run_key)
    parser.add_argument('--acceptance-run',choices=('ch09-local-20261019',))
    parser.add_argument('--execute',action='store_true')
    args=parser.parse_args(argv)
    if args.action in ('run','status') and args.run_key is None: parser.error('This action requires --run-key')
    if args.action in ('run','recover') and not args.execute:
        from app.rag_evaluation.dataset import DATASET_ID,load_dataset
        from app.eval_pipeline.runner import select_case_ids
        dataset=load_dataset(DATASET_ID,root=ROOT/'evals/datasets')
        count=len(select_case_ids(dataset,args.scope))
        print(f'dry-run: scope={args.scope}; dataset_size={count}; glm ceiling={4*count}; no credentials/database/upstream')
        return
    try: asyncio.run(run(args))
    except Exception as exc: parser.exit(1,f'evaluation stopped: {type(exc).__name__}\n')


if __name__=='__main__': main()
