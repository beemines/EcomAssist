"""step04 physical ownership reused with native manifests and truthful model budgets."""
import asyncio
import math
from uuid import UUID
from threading import Lock
import httpx
from langchain_core.callbacks import BaseCallbackHandler
from app.context.acceptance import AcceptanceCallCap
from app.context.tokens import estimate_payload
from app.core.llm import create_model, model_with_output_budget
from app.knowledge.embeddings import SiliconFlowEmbedder
from app.retrieval.rerank import SiliconFlowReranker
from app.rag_evaluation.resources import OwnedResources, REQUEST_STAGES


class UsageCollector(BaseCallbackHandler):
    def __init__(self): self.values=[]; self._diagnostics=[]; self._lock=Lock()
    def on_llm_end(self,response,**kwargs):
        for batch in response.generations:
            for generation in batch:
                message=getattr(generation,'message',None)
                usage=getattr(message,'usage_metadata',None)
                if not isinstance(usage,dict):
                    usage=(getattr(message,'response_metadata',{}) or {}).get('token_usage')
                if isinstance(usage,dict):
                    total=usage.get('total_tokens')
                    if type(total) is int and total>=0:
                        with self._lock: self.values.append(total)
                if message is not None:
                    metadata=getattr(message,'response_metadata',{}) or {}
                    self._record(metadata.get('finish_reason'),getattr(message,'content',''),
                        (getattr(message,'additional_kwargs',{}) or {}).get('reasoning_content'),
                        (usage or {}).get('output_tokens',(usage or {}).get('completion_tokens')))
    def _record(self,finish,content,reasoning,output_tokens):
        value={'finish_reason':finish if finish in ('stop','length','content_filter','tool_calls') else 'unknown',
            'output_characters':len(content) if isinstance(content,str) else 0,
            'reasoning_characters':len(reasoning) if isinstance(reasoning,str) else 0,
            'output_tokens':output_tokens if type(output_tokens) is int and output_tokens>=0 else None}
        with self._lock: self._diagnostics.append(value)
    def on_llm_error(self,error,**kwargs):
        completion=getattr(error,'completion',None)
        choices=getattr(completion,'choices',None)
        if choices:
            choice=choices[0]; message=choice.message
            self._record(choice.finish_reason,getattr(message,'content',None),
                getattr(message,'reasoning_content',None),
                getattr(getattr(completion,'usage',None),'completion_tokens',None))
    def diagnostics(self):
        with self._lock: return [dict(value) for value in self._diagnostics]
    def summary(self,*,estimated_input,output_tokens):
        with self._lock: values=list(self.values)
        return {'actual_tokens':sum(values) if values else None,'actual_calls':len(values),
            'estimated_tokens':0 if values else estimated_input+output_tokens,
            'estimated_calls':0 if values else 1}


class ResourceStore:
    """Adapt only step04's ownership/counter protocol, never its fixed-budget config."""
    def __init__(self,store,key): self.store,self.key=store,key
    async def get(self,run_id):
        if run_id!=UUID(self.key).hex: raise ValueError('Resource owner key mismatch')
        report=await self.store.get(self.key)
        return {'config':{'dataset_id':report.dataset_id,'provenance':{
            key:report.config[key] for key in ('dataset_fingerprint','corpus_hash','cases_hash','annotation_hash')}},
            'ownership':report.ownership,'request_counts':report.usage['physical_calls']}
    async def update(self,run_id,patch):
        if run_id!=UUID(self.key).hex or not set(patch)<={'ownership','cleanup','request_counts'}:
            raise ValueError('Invalid native resource update')
        report=await self.store.get(self.key)
        values={key:value for key,value in patch.items() if key!='request_counts'}
        if 'request_counts' in patch: values['usage']={**report.usage,'physical_calls':patch['request_counts']}
        await self.store.update(self.key,**values)


class PipelineResources(OwnedResources):
    provider_scope='actual'
    def __init__(self,report,*,settings,store,lease,acceptance_call_cap=None,observability=None,cancel_event=None):
        super().__init__(settings,ResourceStore(store,report.run_key),UUID(report.run_key).hex)
        self.report,self.pipeline_store,self.lease=report,store,lease
        self.cap,self.observability=acceptance_call_cap,observability
        self.cancel_event=cancel_event
        count=report.dataset_size
        self.run_cap=AcceptanceCallCap(UUID(report.run_key).hex,
            {'glm':count*4,'embedding':count+math.ceil(report.config['chunk_count']/20),'rerank':count},
            store.root/report.run_key/'call-ledger.sqlite')
        self._dispatch_lock=asyncio.Lock()

    def _open_index(self):
        from app.eval_pipeline.types import endpoint_fingerprints
        if self.report.config['endpoint_hashes']['milvus']!=endpoint_fingerprints(self.settings)['milvus']:
            raise ValueError('Evaluation cleanup endpoint changed; keep owned resources for explicit recovery')
        return super()._open_index()

    async def _before_dispatch(self,provider,request):
        async with self._dispatch_lock:
            if self.cancel_event is not None and self.cancel_event.is_set():
                raise RuntimeError('Evaluation dispatch cancelled before transport')
            if hasattr(self.lease,'transaction'):
                async with self.lease.transaction(): pass
            elif self.provider_scope=='actual':
                raise ValueError('Paid pipeline dispatch needs database ownership')
            if self.cancel_event is not None and self.cancel_event.is_set():
                raise RuntimeError('Evaluation dispatch cancelled before transport')
            self.run_cap.reserve(provider)
            if self.cap is not None: self.cap.reserve(provider)
            if provider=='glm': await self.requests.model_hook(request)
            else: await self.requests.fixed_hook(provider)(request)

    def _provider_client(self,provider):
        async def hook(request): await self._before_dispatch(provider,request)
        return self._http(hook)

    def _models(self):
        # This pipeline is asynchronous. A mistaken synchronous invoke is denied
        # before networking, rather than bypassing the asynchronous owner guard.
        def deny(request): raise RuntimeError('Synchronous evaluation dispatch is disabled')
        sync=httpx.Client(event_hooks={'request':[deny]})
        try:
            from app.eval_pipeline.types import effective_reasoning_effort
            model=create_model(self.settings,http_client=sync,http_async_client=self._provider_client('glm'),
                reasoning_effort=effective_reasoning_effort(self.settings))
        except BaseException:
            sync.close(); raise
        self._register_model(model)
        handler=getattr(self.observability,'handler',None)
        self.model=model.model_copy(update={'callbacks':[handler]} if handler else {},deep=False)
        self.embedder=SiliconFlowEmbedder(self.settings,http_client=self._provider_client('embedding'))
        self.reranker=SiliconFlowReranker(self.settings,http_client=self._provider_client('rerank'))

    def phase_model(self,output_tokens):
        collector=UsageCollector()
        model=model_with_output_budget(self.model,self.settings,output_tokens)
        callbacks=list(model.callbacks or [])+[collector]
        return model.model_copy(update={'callbacks':callbacks},deep=False),collector
