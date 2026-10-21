"""Read-only topic distribution; absent model/receipts never become fake zeroes."""
from datetime import datetime,timezone
import json
from typing import Literal

from pydantic import Field,field_validator,model_validator
from sqlalchemy import text

from app.topics.cleaning import clean_question
from app.topics.migration import migrate_topics
from app.topics.receipts import FailureKey,ReceiptError,ReceiptStore
from app.topics.taxonomy import default_taxonomy
from app.topics.types import ModelIdentity,StrictRecord


class TopicFilters(StrictRecord):
    source: Literal['retrieval_low_conf','self_check','user_feedback'] | None=None
    since: datetime | None=None
    until: datetime | None=None

    @field_validator('since','until')
    @classmethod
    def aware(cls,value):
        if value is not None and value.utcoffset() is None:
            raise ValueError('Topic dates require an explicit timezone')
        return value.astimezone(timezone.utc) if value else None

    @model_validator(mode='after')
    def ordered(self):
        if self.since is not None and self.until is not None and self.since>=self.until:
            raise ValueError('Topic date range must be positive and half open')
        return self


class TopicCount(StrictRecord):
    name: str
    count: int | None
    share: float | None


class TopicSummary(StrictRecord):
    status: Literal['ready','unconfigured']
    identity: ModelIdentity | None
    pool_total: int
    effective: int | None
    unclassified: int | None
    stale: int | None
    unknown: int
    pending_review: int | None
    receipts_status: Literal['available','unknown','window_exceeded']
    latest: str | None
    topics: tuple[TopicCount,...]


class TopicQuestion(StrictRecord):
    question_id: str
    text: str
    labels: tuple[str,...]
    source: str
    classified_at: str
    model_version: str
    matched_review_id: str | None


class TopicQuestionPage(StrictRecord):
    status: Literal['ready','unconfigured']
    total: int | None
    offset: int
    limit: int
    items: tuple[TopicQuestion,...]


def _where(filters):
    clauses,values=['1=1'],{}
    if filters.source is not None:
        clauses.append('q.source=:source'); values['source']=filters.source
    for name,operator in (('since','>='),('until','<')):
        value=getattr(filters,name)
        if value is not None:
            clauses.append(f'q.created_at{operator}:{name}')
            values[name]=value.replace(tzinfo=None)  # Existing admin treats naive DATETIME as UTC.
    return ' AND '.join(clauses),values


def _valid(identity,values):
    names=default_taxonomy().ordered_names
    for index,name in enumerate(names): values[f'label_{index}']=json.dumps(name,ensure_ascii=False)
    flags=[f'JSON_CONTAINS(t.labels,:label_{index})' for index in range(17)]
    shape="JSON_TYPE(t.labels)='ARRAY' AND JSON_LENGTH(t.labels)>0 AND JSON_LENGTH(t.labels)=("+'+'.join(flags)+')'
    shape+=' AND NOT (JSON_CONTAINS(t.labels,:label_16) AND JSON_LENGTH(t.labels)>1)'
    known=f't.model_version IS NOT NULL AND t.taxonomy_version IS NOT NULL AND t.input_hash IS NOT NULL AND ({shape})'
    if identity is None:
        return 'FALSE',known
    values.update(model=identity.model_version,taxonomy=identity.taxonomy_version)
    current=(f'({known}) AND BINARY t.model_version=BINARY :model AND BINARY t.taxonomy_version=BINARY :taxonomy '
             'AND BINARY t.input_hash=BINARY SHA2(q.raw_question,256)')
    return current,known


async def fetch_summary(database,filters,identity):
    where,values=_where(filters)
    schema=await migrate_topics(database,preview=True)
    async with database.session() as session:
        if not schema.complete:
            if schema.stage!='missing' or identity is not None:
                raise RuntimeError('Topic schema requires explicit migration')
            total=int(await session.scalar(text('SELECT COUNT(*) FROM low_confidence_questions q WHERE '+where),values))
            return dict(pool_total=total,effective=0,stale=0,unknown=0,latest=None,label_counts={},pending_inputs=[],
                        database_identity=schema.database_identity)
        current,known=_valid(identity,values)
        columns=['COUNT(*) AS pool_total',f'COALESCE(SUM({current}),0) AS effective',
            f'COALESCE(SUM(t.id IS NOT NULL AND NOT ({known})),0) AS unknown',
            f'COALESCE(SUM(t.id IS NOT NULL AND ({known}) AND NOT ({current})),0) AS stale',
            f'MAX(CASE WHEN ({current}) THEN t.classified_at ELSE NULL END) AS latest']
        columns += [f'COALESCE(SUM(({current}) AND JSON_CONTAINS(t.labels,:label_{index})),0) AS label_count_{index}'
                    for index in range(17)]
        join=' FROM low_confidence_questions q LEFT JOIN topic_classifications t ON t.question_id=q.id WHERE '+where
        row=(await session.execute(text('SELECT '+','.join(columns)+join),values)).mappings().one()
        pending=[]
        if identity is not None:
            pending=(await session.execute(text('SELECT q.id,SHA2(q.raw_question,256) AS input_hash'+join+
                f' AND NOT COALESCE(({current}),FALSE) ORDER BY q.id LIMIT 10001'),values)).mappings().all()
        return dict(pool_total=int(row['pool_total']),effective=int(row['effective']),stale=int(row['stale']),
            unknown=int(row['unknown']),latest=row['latest'].isoformat() if row['latest'] else None,
            label_counts={name:int(row[f'label_count_{index}']) for index,name in enumerate(default_taxonomy().ordered_names)},
            pending_inputs=[dict(question_id=str(item['id']),input_hash=item['input_hash'],model_version=identity.model_version)
                            for item in pending],database_identity=schema.database_identity)


async def fetch_questions(database,label,filters,identity,*,offset,limit):
    where,values=_where(filters)
    current,_=_valid(identity,values)
    values['selected_label']=json.dumps(label,ensure_ascii=False)
    join=(' FROM low_confidence_questions q JOIN topic_classifications t ON t.question_id=q.id WHERE '+where+
          f' AND ({current}) AND JSON_CONTAINS(t.labels,:selected_label)')
    async with database.session() as session:
        total=int(await session.scalar(text('SELECT COUNT(*)'+join),values))
        rows=(await session.execute(text('SELECT q.id,q.raw_question,q.source,q.matched_review_id,t.labels,'
            't.classified_at,t.model_version'+join+' ORDER BY q.id DESC LIMIT :limit OFFSET :offset'),
            values | dict(limit=limit,offset=offset))).mappings().all()
    return dict(total=total,items=[dict(row) for row in rows])


class TopicStatisticsService:
    def __init__(self,repository,profile,receipts,*,identity_provider=None):
        self.repository,self.profile,self.receipts=repository,profile,receipts
        self.identity_provider=identity_provider

    def _identity(self):
        if self.identity_provider is not None:
            return self.identity_provider()  # Trusted application/test injection, never a query parameter.
        if self.profile is None or not self.profile.manifest_path.is_file():
            return None
        from app.topics.manifest import verify_manifest
        return verify_manifest(self.profile.manifest_path)

    async def summary(self,filters: TopicFilters) -> TopicSummary:
        filters=TopicFilters.model_validate(filters.model_dump())
        identity=self._identity()
        row=await self.repository.read_summary(filters,identity)
        pending,status=None,'unknown'
        if identity is not None and len(row['pending_inputs'])>10000:
            status='window_exceeded'
        elif identity is not None:
            receipts=self.receipts
            if receipts is None and self.profile is not None:
                receipts=ReceiptStore(self.profile.runtime_root/'receipts.sqlite3',database_identity=row['database_identity'])
            if receipts is not None:
                try:
                    states=receipts.states([FailureKey.model_validate(item) for item in row['pending_inputs']])
                    pending=sum(state.status in ('needs_review','input_too_long','invalid_input','cleaning_failed') for state in states)
                    status='available'
                except ReceiptError:
                    pass
        effective=row['effective'] if identity is not None else None
        topics=tuple(TopicCount(name=name,count=row['label_counts'].get(name,0) if identity is not None else None,
            share=(float(row['label_counts'].get(name,0)/effective) if effective else 0.) if identity is not None else None)
            for name in default_taxonomy().ordered_names)
        return TopicSummary(status='ready' if identity else 'unconfigured',identity=identity,pool_total=row['pool_total'],
            effective=effective,unclassified=row['pool_total']-effective if effective is not None else None,
            stale=row['stale'] if identity else None,unknown=row['unknown'],pending_review=pending,
            receipts_status=status,latest=row['latest'] if identity else None,topics=topics)

    async def questions(self,label,filters,offset=0,limit=20):
        if (label not in default_taxonomy().ordered_names or type(offset) is not int or offset<0
                or type(limit) is not int or not 1<=limit<=100):
            raise ValueError('Invalid topic question label or pagination')
        filters=TopicFilters.model_validate(filters.model_dump())
        identity=self._identity()
        if identity is None:
            return TopicQuestionPage(status='unconfigured',total=None,offset=offset,limit=limit,items=())
        data=await self.repository.read_questions(label,filters,identity,offset=offset,limit=limit)
        items=[]
        for row in data['items']:
            cleaned=clean_question(row['raw_question'],sample_id=str(row['id']))
            labels=json.loads(row['labels']) if isinstance(row['labels'],str) else row['labels']
            items.append(TopicQuestion(question_id=str(row['id']),text=cleaned.text if not cleaned.quarantine_reasons
                else '[该问题含待人工脱敏信息，暂不展示]',labels=default_taxonomy().canonical_labels(labels),source=row['source'],
                classified_at=row['classified_at'].isoformat(),model_version=row['model_version'],
                matched_review_id=str(row['matched_review_id']) if row['matched_review_id'] is not None else None))
        return TopicQuestionPage(status='ready',total=data['total'],offset=offset,limit=limit,items=tuple(items))
