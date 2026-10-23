"""Bounded side-channel rounds: no teacher or real-time chat dependencies."""
import time
import asyncio

from app.flywheel.leases import processing_lease
from app.topics.client import TopicClientError
from app.topics.receipts import FailureKey
from app.topics.repository import make_receipt,verify_preview
from app.topics.reviews import digest
from app.topics.snapshot import write_new_json
from app.topics.types import ClassifyItem,Prediction


async def _wait_stop(stop,seconds):
    try:await asyncio.wait_for(stop.wait(),timeout=seconds)
    except TimeoutError:pass


def validate_predictions(preview,predictions):
    preview=verify_preview(preview)
    rows=tuple(Prediction.model_validate_json(row.model_dump_json()) for row in predictions)
    allowed={item.id for item in preview.items if item.status=='ready'}
    if (len({row.id for row in rows})!=len(rows) or any(row.id not in allowed
            or row.model_version!=preview.identity.model_version
            or row.taxonomy_version!=preview.identity.taxonomy_version for row in rows)):
        raise ValueError('Predictions do not match the frozen batch identities')
    return rows


class BatchRunner:
    def __init__(self,repository,client,receipts,*,clock=time.time):
        self.repository,self.client,self.receipts,self.clock=repository,client,receipts,clock

    async def watch(self,*,stop,identity,from_id=1,to_id=None,limit=100,interval=60):
        if type(interval) is not int or not 60<=interval<=300 or type(limit) is not int or not 20<=limit<=100:
            raise ValueError('Watch requires20..100 items and polling60..300 seconds')
        while not stop.is_set():
            if self.receipts.round_failures()==3:return dict(status='paused',failed_rounds=3)
            preview=verify_preview(await self.repository.preview_pending(from_id=from_id,to_id=to_id,
                limit=limit,identity=identity,reclassify=False))
            if preview.identity!=identity or preview.database_identity!=self.receipts.database_identity:
                raise ValueError('Watch selection identity changed')
            eligible=sum(self.receipts.eligible(FailureKey(question_id=item.id,input_hash=item.input_hash,
                model_version=identity.model_version),now=self.clock()) for item in preview.items)
            delay=interval
            if eligible>=20:
                try:result=await self.run_once(preview)
                except Exception:
                    self.receipts.record_round(success=False,now=self.clock())
                    # An unexpected guard/DB failure needs diagnosis, not an implicit loop.
                    return dict(status='failed',reason='round_guard_failed')
                failed=any(value in ('temporary_failure','permanent_failure') for value in result.problems.values())
                if failed or result.written:
                    failures=self.receipts.record_round(success=not failed,now=self.clock())
                    if failures==3:return dict(status='paused',failed_rounds=3)
                    delay=max(interval,min(240,60*2**max(0,failures-1))) if failed else interval
            await _wait_stop(stop,delay)
        return dict(status='stopped')

    async def run_once(self,preview,*,reclassify=False):
        preview=verify_preview(preview)
        if type(reclassify) is not bool or reclassify!=preview.reclassify:
            raise ValueError('Reclassification must be explicitly requested for this frozen preview')
        if self.receipts.database_identity!=preview.database_identity:
            raise ValueError('Batch receipts target a different database')
        def key(item):
            return FailureKey(question_id=item.id,input_hash=item.input_hash,model_version=preview.identity.model_version)
        problems,delayed,outputs={},{},[]
        retry_available=True
        async def request(call):
            nonlocal retry_available
            try:
                return await call()
            except TopicClientError as exc:
                if not exc.temporary or not retry_available:
                    raise
                retry_available=False
                return await call()
        async with processing_lease(self.repository.database,prefix='ch10-topic:') as lease:
            if lease is None:
                return make_receipt(preview,problems={'batch':'busy'})
            selected=await self.repository.select_locked(preview,lease)
            ready=[]
            for item in selected:
                if not self.receipts.eligible(key(item),now=self.clock()):
                    delayed[item.id]='waiting_retry'
                elif item.status=='cleaning_failed':
                    self.receipts.record_failure(key(item),'cleaning_failed',now=self.clock())
                    problems[item.id]='cleaning_failed'
                else:
                    ready.append(item)
            if ready:
                try:
                    if await request(self.client.health)!=preview.identity:
                        raise TopicClientError('topic_response_identity_invalid')
                except TopicClientError as exc:
                    code='temporary_failure' if exc.temporary else 'permanent_failure'
                    for item in ready:
                        self.receipts.record_failure(key(item),code,now=self.clock())
                        problems[item.id]=code
                    ready=[]
            for start in range(0,len(ready),64):
                items=ready[start:start+64]
                try:
                    chunk=await request(lambda:self.client.classify(
                        [ClassifyItem(id=item.id,text=item.text) for item in items],preview.identity,
                        request_id=f'{preview.batch_id}-{start}'))
                    chunk=validate_predictions(preview,chunk)
                    if tuple(row.id for row in chunk)!=tuple(item.id for item in items):
                        raise TopicClientError('topic_prediction_identity_invalid')
                except TopicClientError as exc:
                    code='temporary_failure' if exc.temporary else 'permanent_failure'
                    for item in items:
                        self.receipts.record_failure(key(item),code,now=self.clock())
                        problems[item.id]=code
                else:
                    outputs.extend(chunk)
            if outputs and await request(self.client.health)!=preview.identity:
                raise RuntimeError('Topic identity changed before commit; round paused')
            result=await self.repository.commit_predictions(preview,outputs,lease)
            by_id={item.id:item for item in preview.items}
            for identifier in result.written:
                self.receipts.record_success(key(by_id[identifier]),now=self.clock())
            for identifier,status in result.problems.items():
                self.receipts.record_failure(key(by_id[identifier]),status,now=self.clock())
            result=result.model_copy(update={'problems':problems | delayed | result.problems})
            value=result.model_dump(mode='json')
            path=self.receipts.path.parent/'batches'/f'{preview.batch_id}-{digest(value)}.json'
            if not path.exists():
                write_new_json(path,value)
            return result
