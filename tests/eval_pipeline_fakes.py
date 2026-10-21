"""CPU pipeline fixtures; never represent paid model evaluation."""
from pathlib import Path
from datetime import datetime, timezone
from tests.fakes import fake_settings
from app.quality.evidence_confidence import canonical_hash, evidence_budget_fingerprint


def dataset_and_rule():
    from app.rag_evaluation.dataset import load_dataset, DATASET_ID
    from tests.flywheel_confidence_fakes import rule
    from app.quality.evidence_confidence import ConfidenceRule
    dataset = load_dataset(DATASET_ID, root=Path('evals/datasets'))
    settings = fake_settings()
    raw = rule(top_k=settings.rerank_top_k, budget_fingerprint=evidence_budget_fingerprint(
        top_k=settings.rerank_top_k, token_budget=min(6000,(settings.model_context_window+7)//8))).model_dump(mode='json')
    raw['source'].update(dataset_id=dataset.dataset_id, dataset_fingerprint=dataset.fingerprint, corpus_hash=dataset.corpus_hash)
    raw.pop('rule_version')
    raw['rule_version'] = canonical_hash(raw)
    return dataset, ConfidenceRule.model_validate_json(__import__('json').dumps(raw)), settings


def seed_report(run_key, *, status='failed'):
    from app.eval_pipeline.types import new_report
    dataset, rule, settings = dataset_and_rule()
    result = new_report(run_key, 'smoke_20', '手动', dataset, settings, rule, provider_scope='mock')
    result.status = status
    result.finished_at = datetime.now(timezone.utc) if status in ('failed','interrupted','completed') else None
    return result


class MockPipelineResources:
    provider_scope='mock'
    instances=[]
    def __init__(self,report,*,settings,store,**kwargs):
        self.report,self.settings,self.pipeline_store=report,settings,store
        self.calls=[]; self.closed=False
        MockPipelineResources.instances.append(self)
        from contextlib import contextmanager
        from contextvars import ContextVar
        current=ContextVar('mock_pipeline_stage',default=None)
        self.current_stage=current
        class Requests:
            @contextmanager
            def stage(self,name):
                token=current.set(name)
                try: yield
                finally: current.reset(token)
        self.requests=Requests()
    async def prepare(self,dataset):
        from dataclasses import asdict
        from app.knowledge.types import ChunkRecord, VectorHit
        from app.retrieval.types import RerankHit
        id_map={chunk.chunk_key:i for i,chunk in enumerate(dataset.chunks,1)}
        records={i:ChunkRecord(**asdict(chunk.draft),id=i,vector_id=str(i),vectorize_status='done')
            for i,chunk in enumerate(dataset.chunks,1)}
        class Repository:
            async def get_done(self,ids): return [records[i] for i in ids if i in records]
        class Embedder:
            async def embed(self,texts): return [[.1]*1024 for _ in texts]
        class Index:
            async def recall(self,vector,query,**kwargs): return [VectorHit(i,.9) for i in records][:50]
        class Reranker:
            async def rank(self,question,texts,*,top_n):
                return [RerankHit(index=i,score=.95-i*.001) for i in range(min(top_n,len(texts)))]
        self.repository,self.embedder,self.index,self.reranker=Repository(),Embedder(),Index(),Reranker()
        return id_map
    def phase_model(self,output_tokens):
        from app.eval_pipeline.resources import UsageCollector
        return PipelineModel(self),UsageCollector()
    async def cleanup(self):
        from app.rag_evaluation.contracts import CleanupResult
        self.closed=True
        return CleanupResult(True,(),())


class PipelineModel:
    def __init__(self,resources,schema=None): self.resources,self.schema=resources,schema
    def with_structured_output(self,schema,**kwargs): return PipelineModel(self.resources,schema)
    async def ainvoke(self,messages,**kwargs):
        import json
        from langchain_core.messages import AIMessage
        self.resources.calls.append(self.resources.current_stage.get())
        body=json.loads(messages[-1].content) if messages[-1].content.startswith('{') else {}
        fields=set(self.schema.model_fields)
        if fields=={'standard','expansions'}:
            # QueryPlanner provides a JSON question envelope.
            question=body.get('question') or body.get('raw_question') or messages[-1].content
            value={'standard':question,'expansions':[]}
        elif fields=={'useful','reason','response_kind'}:
            value={'useful':True,'reason':'离线固定内容自评','response_kind':'knowledge'}
        else:
            value={'points':[{'point_id':item['point_id'],'covered':True,'reason':'离线固定裁判'}
                for item in body['coverage_rubric']],
                'claims':[{'claim':'离线固定事实','supported':True,'reason':'受控样例，不是语义质量结论'}]}
        raw=AIMessage(json.dumps(value,ensure_ascii=False),response_metadata={'finish_reason':'stop'})
        return {'raw':raw,'parsed':self.schema.model_validate_json(raw.content),'parsing_error':None}
    async def astream(self,messages,**kwargs):
        from langchain_core.messages import AIMessageChunk
        self.resources.calls.append(self.resources.current_stage.get())
        yield AIMessageChunk('离线固定事实[1]')
        yield AIMessageChunk('',response_metadata={'finish_reason':'stop'})
