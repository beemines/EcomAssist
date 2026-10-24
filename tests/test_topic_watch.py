"""Watch uses no scheduler/teacher and stops durably after three failed rounds."""
import asyncio
from types import SimpleNamespace
import pytest
from app.topics.batch import BatchRunner
from app.topics.repository import make_preview,make_receipt,PreparedQuestion
from app.topics.receipts import ReceiptStore
from tests.test_topic_batch import identity

@pytest.mark.parametrize('count',[19,20])
async def test_watch_waits_for_twenty_and_pauses_on_third_failed_round(tmp_path,monkeypatch,count):
    import app.topics.batch as module
    stop=asyncio.Event();delays=[];calls=[]
    frozen=make_preview(database_identity='a'*64,identity=identity(),from_id='1',to_id=str(count),high_water=str(count),
        reclassify=False,items=[PreparedQuestion(id=str(i),text='物流在哪',input_hash='b'*64,status='ready') for i in range(1,count+1)])
    class Repository:
        async def preview_pending(self,**kwargs):return frozen
    path=tmp_path/'r.sqlite3';ReceiptStore.initialize(path,database_identity='a'*64)
    receipts=ReceiptStore(path,database_identity='a'*64);runner=BatchRunner(Repository(),None,receipts)
    async def run(preview,**kwargs):
        calls.append(preview)
        return make_receipt(preview,problems={row.id:'temporary_failure' for row in preview.items})
    async def wait(event,seconds):
        delays.append(seconds)
        if count==19:stop.set()
    runner.run_once=run
    monkeypatch.setattr(module,'_wait_stop',wait,raising=False)
    result=await runner.watch(stop=stop,identity=identity(),from_id=1,to_id=count,limit=100,interval=60)
    if count==19:
        assert not calls and result['status']=='stopped' and delays==[60]
    else:
        assert len(calls)==3 and result['status']=='paused' and delays==[60,120]
        assert ReceiptStore(path,database_identity='a'*64).round_failures()==3
