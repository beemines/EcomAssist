from datetime import datetime, timezone
from typing import Literal
from uuid import UUID
from pydantic import Field, field_validator
from app.flywheel.types import Versioned, StrictModel, TaskError, utc_time
from app.quality.evidence_confidence import canonical_hash, verify_rule, evidence_budget_fingerprint, model_fingerprint

EvalScope = Literal['smoke_20', 'full_300']
RunStatus = Literal['preparing','running','completed','completed_with_errors','failed','interrupted','cancelled']
TERMINAL = {'completed','completed_with_errors','failed','interrupted','cancelled'}


def endpoint_fingerprints(settings):
    from app.rag_evaluation.manager import _endpoint
    from app.knowledge.embeddings import EMBEDDING_ENDPOINT
    from app.retrieval.rerank import RERANK_ENDPOINT
    return {name:_endpoint(str(value),suffix)[1] for name,value,suffix in (
        ('llm',settings.llm_base_url,'/chat/completions'),
        ('embedding',EMBEDDING_ENDPOINT,''),('rerank',RERANK_ENDPOINT,''),
        ('milvus',settings.milvus_uri,''))}


def run_key(value):
    if type(value) is not str or str(UUID(value)) != value:
        raise ValueError('Expected canonical UUID run_key')
    return value


class PipelineCaseResult(StrictModel):
    # Keep the validated public step04 stage contract intact, adding audit/usage
    # beside it. Unattempted gold IDs are explicitly frozen ordinals, not DB IDs.
    record: dict
    id_space: Literal['frozen_ordinal','mysql'] = 'mysql'
    evidence_decision: dict | None = None
    usage: dict = Field(default_factory=dict)

    @field_validator('record')
    @classmethod
    def checked_record(cls, value):
        from app.rag_evaluation.report import validate_case_record
        return validate_case_record(value)

    @property
    def eval_id(self): return self.record['eval_id']
    @property
    def status(self): return self.record['status']


class PipelineReport(Versioned):
    run_key: str
    scope: EvalScope
    triggered_by: Literal['手动','定时']
    dataset_size: int = Field(gt=0, le=300)
    dataset_id: str
    dataset_fingerprint: str = Field(pattern=r'^[0-9a-f]{64}$')
    corpus_hash: str = Field(pattern=r'^[0-9a-f]{64}$')
    config_fingerprint: str = Field(pattern=r'^[0-9a-f]{64}$')
    config: dict
    case_ids: list[str]
    status: RunStatus = 'preparing'
    records: list[PipelineCaseResult]
    metrics: dict
    usage: dict = Field(default_factory=dict)
    ownership: dict | None = None
    id_map: dict[str,int] = Field(default_factory=dict)
    cleanup: dict | None = None
    created_at: datetime
    finished_at: datetime | None = None
    published_id: str | None = None
    error: TaskError | None = None

    _key = field_validator('run_key')(run_key)
    _time = field_validator('created_at', 'finished_at')(utc_time)

    def metric_payload(self):
        from app.eval_pipeline.runner import aggregate_metrics
        terminal = self.status in TERMINAL
        usage=dict(self.usage)
        if terminal:
            tokens={'actual_tokens':0,'estimated_tokens':0,'actual_calls':0,'estimated_calls':0}
            for row in self.records:
                for phase in row.usage.values():
                    for name in tokens: tokens[name]+=phase.get(name) or 0
            usage['tokens']=tokens
        return {'schema_version':1, 'metric_version':'ch04-complete-groups-v2', 'run_key':self.run_key,
            'scope':self.scope, 'dataset_id':self.dataset_id, 'dataset_fingerprint':self.dataset_fingerprint,
            'corpus_hash':self.corpus_hash, 'config_fingerprint':self.config_fingerprint, 'config':self.config,
            'status':self.status, 'dataset_size':self.dataset_size,
            'scores':aggregate_metrics(self.records) if terminal else None,
            'completed':sum(row.status=='completed' for row in self.records),
            'errors':sum(row.status.endswith('_error') for row in self.records),
            'usage':usage, 'created_at':self.created_at.isoformat(),
            'elapsed_ms':(self.finished_at-self.created_at).total_seconds()*1000 if self.finished_at else None,
            'finished_at':self.finished_at.isoformat() if self.finished_at else None,
            'error':self.error.model_dump(mode='json') if self.error else None,
            'report_locator':f'/api/eval-runs/{self.run_key}/report'}


class RunView(StrictModel):
    run_key: str
    scope: EvalScope
    status: RunStatus
    dataset_size: int
    progress: dict
    metrics: dict | None
    config_fingerprint: str
    persisted: bool
    report_locator: str


def report_view(report):
    payload = report.metric_payload()
    return RunView(run_key=report.run_key, scope=report.scope, status=report.status,
        dataset_size=report.dataset_size, progress={'total':report.dataset_size,
            'finished':sum(row.status not in ('running','not_attempted') for row in report.records)},
        metrics=payload['scores'], config_fingerprint=report.config_fingerprint,
        persisted=report.published_id is not None, report_locator=payload['report_locator'])


def stored_view(row):
    payload=row['metrics']
    return RunView(run_key=payload['run_key'],scope=payload['scope'],status=payload['status'],
        dataset_size=payload['dataset_size'], progress={'total':payload['dataset_size'],
            'finished':payload.get('completed',0)+payload.get('errors',0)},
        metrics=payload.get('scores'),config_fingerprint=payload['config_fingerprint'],persisted=True,
        report_locator=payload['report_locator'])


def effective_reasoning_effort(settings):
    return settings.rag_evaluation_reasoning_effort or settings.online_reasoning_effort


def new_report(key, scope, triggered_by, dataset, settings, rule, *, provider_scope='actual'):
    from app.eval_pipeline.runner import select_case_ids, aggregate_metrics
    from app.rag_evaluation.runner import _seed
    from app.rag_evaluation.resources import REQUEST_STAGES
    from app.core.prompts import build_query_messages, build_sufficiency_messages, build_grounded_answer_system_prompt
    from app.rag_evaluation.judgment import JUDGE_PROMPT, PROMPT_VERSION
    key=run_key(key)
    ids=select_case_ids(dataset,scope)
    budget=min(6000,(settings.model_context_window+7)//8)
    verify_rule(rule,top_k=settings.rerank_top_k,
        budget_fingerprint=evidence_budget_fingerprint(top_k=settings.rerank_top_k,token_budget=budget),
        model_fingerprint=model_fingerprint(settings.rerank_model),dataset_fingerprint=dataset.fingerprint,
        corpus_hash=dataset.corpus_hash)
    config={'pipeline_version':'ch09-single-strategy-v1','metric_version':'ch04-complete-groups-v2',
        'provider_scope':provider_scope,'endpoint_hashes':endpoint_fingerprints(settings),
        'dataset_id':dataset.dataset_id,'dataset_fingerprint':dataset.fingerprint,
        'corpus_hash':dataset.corpus_hash,'cases_hash':dataset.cases_hash,'annotation_hash':dataset.annotation_hash,
        'models':{'answer':settings.llm_model,'embedding':settings.embedding_model,'rerank':settings.rerank_model},
        'prompt_hashes':{'rewrite':canonical_hash(build_query_messages('')[0].content),
            'self_check':canonical_hash(build_sufficiency_messages('',{})[0].content),
            'answer':canonical_hash(build_grounded_answer_system_prompt()),'judge':canonical_hash(JUDGE_PROMPT)},
        'prompt_versions':{'rewrite':'query-v1','self_check':'sufficiency-v1','answer':'grounded-answer-v1','judge':PROMPT_VERSION},
        'reasoning_effort':effective_reasoning_effort(settings),
        'rule_version':rule.rule_version,'rule_source':rule.source.source_kind,
        'scope':scope,'case_ids':list(ids),'chunk_count':len(dataset.chunks),
        'top_k':settings.rerank_top_k,'evidence_token_budget':budget,
        'model_context_window':settings.model_context_window,'answer_output_tokens':settings.max_output_tokens,
        'rewrite_output_tokens':settings.query_max_output_tokens,'self_check_output_tokens':settings.sufficiency_max_output_tokens,
        'judge_output_tokens':settings.faith_judge_max_output_tokens,'model_retries':0,'case_concurrency':2}
    logical={chunk.chunk_key:i for i,chunk in enumerate(dataset.chunks,1)}
    records=[PipelineCaseResult(record=_seed(case,'hybrid_rerank',logical),id_space='frozen_ordinal')
        for case in dataset.cases if case.eval_id in ids]
    return PipelineReport(run_key=key,scope=scope,triggered_by=triggered_by,dataset_size=len(ids),
        dataset_id=dataset.dataset_id,dataset_fingerprint=dataset.fingerprint,corpus_hash=dataset.corpus_hash,
        config_fingerprint=canonical_hash(config),config=config,case_ids=list(ids),records=records,
        metrics=aggregate_metrics(records),usage={'physical_calls':dict.fromkeys(REQUEST_STAGES,0)},
        created_at=datetime.now(timezone.utc))
