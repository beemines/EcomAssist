"""Reviewed, bounded sidecar operations. Importing this module never starts a job."""
import asyncio
from pathlib import Path
import time
from app.topics.manifest import verify_release
from app.topics.profile import load_profile
from app.topics.repository import BatchPreview,TopicRepository,verify_preview
from app.topics.receipts import ReceiptStore,FailureKey
from app.topics.snapshot import write_new_json
from app.topics.client import TopicClient
from app.topics.batch import BatchRunner
from app.topics.migration import migrate_topics


def read_scope(path,identity,*,database_identity,reclassify):
    path=Path(path)
    if path.stat().st_size>256*1024:raise ValueError('Preview exceeds the bounded100-question scope')
    preview=verify_preview(BatchPreview.model_validate_json(path.read_text(encoding='utf-8')))
    if (preview.identity!=identity or preview.database_identity!=database_identity or preview.reclassify!=reclassify):
        raise ValueError('Frozen scope belongs to a different model/database/operation')
    return preview


async def operate(args,database):
    profile=load_profile(args.profile)
    identity=verify_release(profile.manifest_path.parent if profile.manifest_path.is_file() else profile.manifest_path)
    schema=await migrate_topics(database,preview=True)
    if not schema.complete:raise ValueError('Run the explicit topic migration before selecting any batch')
    repository=TopicRepository(database,runtime_root=profile.runtime_root)
    if args.command in ('preview','watch'):
        preview=await repository.preview_pending(from_id=args.from_id,to_id=args.to_id,limit=args.limit,
            identity=identity,reclassify=getattr(args,'reclassify',False))
        if args.command=='preview':
            if args.output:write_new_json(args.output,preview.model_dump(mode='json'))
            return dict(mode='preview',preview=preview.model_dump(mode='json'))
    else:
        preview=read_scope(args.preview_file,identity,database_identity=schema.database_identity,
            reclassify=args.command=='reclassify' or args.command=='retry' and getattr(args,'reclassify',False))
    if not args.execute:return dict(mode='preview',command=args.command,preview_hash=preview.preview_hash,items=len(preview.items))
    path=profile.runtime_root/'receipts.sqlite3'
    if not path.exists() and not path.with_suffix('.identity.json').exists():
        ReceiptStore.initialize(path,database_identity=schema.database_identity)
    receipts=ReceiptStore(path,database_identity=schema.database_identity)
    if args.command=='retry':
        for item in preview.items:
            receipts.retry(FailureKey(question_id=item.id,input_hash=item.input_hash,model_version=identity.model_version),now=time.time())
        receipts.retry_rounds(now=time.time())
        return dict(mode='executed',retried_ids=[row.id for row in preview.items],preview_hash=preview.preview_hash)
    if receipts.round_failures()==3:raise ValueError('Worker paused; explicit retry with the reviewed scope is required')
    async with TopicClient(profile.service_url) as client:
        runner=BatchRunner(repository,client,receipts)
        if args.command=='watch':
            return await runner.watch(stop=asyncio.Event(),identity=identity,from_id=args.from_id,to_id=args.to_id,
                limit=args.limit,interval=args.poll_seconds)
        result=await runner.run_once(preview,reclassify=preview.reclassify)
        service_failure=any(value in ('temporary_failure','permanent_failure') for value in result.problems.values())
        if service_failure or result.written:receipts.record_round(success=not service_failure,now=time.time())
        return dict(mode='executed',receipt=result.model_dump(mode='json'))
