import asyncio
from types import SimpleNamespace
import httpx
import pytest
from tests.test_review_queue_api import review_app


@pytest.mark.parametrize('kind',['processing','publication'])
async def test_explicit_api_retry_resumes_quota_paused_consumer(kind):
    from app.flywheel.worker import FlywheelWorker
    from app.flywheel.processing import PauseWorker
    from app.flywheel.runtime import FlywheelRuntime
    class Processor:
        pending=True;calls=0;allow=False
        def __init__(self):self.repository=self;self.done=asyncio.Event()
        async def next_pending_id(self,now):return '1' if self.pending else None
        async def recover(self):return True
        async def process(self,identifier):
            self.calls+=1;self.pending=False
            if not self.allow:raise PauseWorker('quota_exhausted')
            self.done.set()
    processor=Processor();worker=FlywheelWorker(processor,poll_seconds=.01)
    runtime=FlywheelRuntime.__new__(FlywheelRuntime)
    runtime.worker=worker;runtime.publication_worker=SimpleNamespace(resume=lambda:worker.resume())
    runtime.acceptance_call_cap=None
    app=review_app();app.state.flywheel_runtime=runtime
    class Pool:
        async def manage_processing(self,*args,**kwargs):
            processor.pending=True;return {'id':'1','processing':{'status':'pending','attempt_count':1}}
    app.state.flywheel_repository=Pool()
    original=app.state.review_service.retry_publication
    async def retry(identifier):processor.pending=True;return await original(identifier)
    app.state.review_service.retry_publication=retry
    worker.start()
    try:
        async with asyncio.timeout(1):
            while worker.paused_reason is None:await asyncio.sleep(.005)
        processor.allow=True
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app),base_url='http://127.0.0.1:8006') as client:
            path='/api/low-confidence-questions/1/retry' if kind=='processing' else '/api/review-queue/1/retry-publication'
            assert (await client.post(path,json={})).status_code==200
        await asyncio.wait_for(processor.done.wait(),.3)
        assert processor.calls==2
    finally:await worker.close(.1)


async def test_explicit_retry_cannot_reset_exhausted_physical_allowance(tmp_path):
    from app.flywheel.runtime import FlywheelRuntime
    from app.context.acceptance import AcceptanceCallCap
    runtime=FlywheelRuntime.__new__(FlywheelRuntime)
    runtime.acceptance_call_cap=AcceptanceCallCap('unit-hard-cap',{'glm':0,'embedding':0,'rerank':0},tmp_path/'cap.sqlite')
    calls=[]
    async def resume():calls.append('unsafe')
    runtime.worker=SimpleNamespace(resume=resume);runtime.publication_worker=None
    app=review_app();app.state.flywheel_runtime=runtime
    class Pool:
        async def manage_processing(self,*args,**kwargs):return {'id':'1'}
    app.state.flywheel_repository=Pool()
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app),base_url='http://127.0.0.1:8006') as client:
        response=await client.post('/api/low-confidence-questions/1/retry',json={})
    assert response.status_code==409 and response.json()['code']=='acceptance_budget'
    assert not calls and runtime.acceptance_call_cap.status()['counts']['glm']==0
