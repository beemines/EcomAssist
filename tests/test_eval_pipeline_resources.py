import asyncio
from contextlib import asynccontextmanager
from uuid import uuid4
import httpx
import pytest
from langchain_core.messages import HumanMessage
from tests.eval_pipeline_fakes import seed_report
from tests.fakes import fake_settings


class Lease:
    def __init__(self,event=None): self.checks=0; self.event=event
    @asynccontextmanager
    async def transaction(self):
        self.checks+=1
        yield None
        if self.event is not None: self.event.set()


class GlobalCap:
    def __init__(self,deny=False): self.used=[]; self.deny=deny
    def reserve(self,provider):
        from app.context.acceptance import AcceptanceLimitExceeded
        if self.deny: raise AcceptanceLimitExceeded('controlled global ceiling')
        self.used.append(provider)


async def resources(tmp_path,*,cap=None,event=None,lease=None):
    from app.eval_pipeline.resources import PipelineResources,ResourceStore
    from app.eval_pipeline.store import PipelineStore
    from app.rag_evaluation.resources import RequestCounter,REQUEST_STAGES
    store=PipelineStore(tmp_path); report=seed_report(str(uuid4()),status='preparing')
    await store.create(report)
    value=PipelineResources(report,settings=fake_settings(
        siliconflow_api_key='unit-test-only'),store=store,lease=lease or Lease(),
        acceptance_call_cap=cap,cancel_event=event)
    value.requests=RequestCounter(value.store,value.run_id,dict.fromkeys(REQUEST_STAGES,0))
    requests=[]
    async def respond(request):
        requests.append(request)
        if request.url.path.endswith('/embeddings'):
            return httpx.Response(200,json={'data':[{'index':0,'embedding':[.1]*1024}]})
        if request.url.path.endswith('/rerank'):
            return httpx.Response(200,json={'results':[{'index':0,'relevance_score':.9}]})
        return httpx.Response(200,json={'id':'mock-completion','object':'chat.completion','created':1,
            'model':'mock','choices':[{'index':0,'message':{'role':'assistant','content':'离线答案'},'finish_reason':'stop'}],
            'usage':{'prompt_tokens':7,'completion_tokens':3,'total_tokens':10}})
    def client(hook):
        result=httpx.AsyncClient(transport=httpx.MockTransport(respond),event_hooks={'request':[hook]})
        value._closers.append(('mock-http',result.aclose))
        return result
    value._http=client
    value._models()
    return value,store,requests


async def test_actual_sdk_and_embedding_rerank_clients_share_owner_and_both_caps(tmp_path):
    cap=GlobalCap(); value,store,requests=await resources(tmp_path,cap=cap)
    try:
        with value.requests.stage('rewrite'):
            phase,usage=value.phase_model(100)
            await phase.ainvoke([HumanMessage('离线计数验证')])
        await value.embedder.embed(['模拟知识'])
        await value.reranker.rank('模拟问题',['模拟知识'])
        assert cap.used==['glm','embedding','rerank'] and value.lease.checks==3
        assert value.run_cap.status()['counts']=={'glm':1,'embedding':1,'rerank':1}
        row=await store.get(value.report.run_key)
        assert row.usage['physical_calls']['rewrite']==1
        assert len(requests)==3
        assert usage.summary(estimated_input=99,output_tokens=50)=={
            'actual_tokens':10,'actual_calls':1,'estimated_tokens':0,'estimated_calls':0}
        with pytest.raises(Exception): value.model.invoke([HumanMessage('同步旁路应拒绝')])
        assert len(requests)==3 and len(cap.used)==3
    finally: await value.cleanup()


async def test_changed_milvus_address_cannot_cleanup_another_endpoint(tmp_path):
    value,store,requests=await resources(tmp_path)
    try:
        value.settings=value.settings.model_copy(update={'milvus_uri':'http://127.0.0.1:19531'})
        with pytest.raises(ValueError,match='endpoint'):
            value._open_index()
        assert value.index is None and not requests
    finally: await value.cleanup()


async def test_exhausted_global_cap_never_reaches_transport_or_sdk_retry(tmp_path):
    value,store,requests=await resources(tmp_path,cap=GlobalCap(deny=True))
    try:
        with value.requests.stage('rewrite'):
            with pytest.raises(Exception): await value.model.ainvoke([HumanMessage('离线预算拒绝')])
        assert not requests and (await store.get(value.report.run_key)).usage['physical_calls']['rewrite']==0
    finally: await value.cleanup()


async def test_cancellation_during_owner_check_prevents_dispatch(tmp_path):
    event=asyncio.Event(); cap=GlobalCap()
    value,store,requests=await resources(tmp_path,cap=cap,event=event,lease=Lease(event))
    try:
        with value.requests.stage('rewrite'):
            with pytest.raises(Exception): await value.model.ainvoke([HumanMessage('离线取消')])
        assert not requests and not cap.used
    finally: await value.cleanup()
