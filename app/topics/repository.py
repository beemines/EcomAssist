"""Frozen bounded selections and short writes protected by the same connection."""
import hashlib
import json
from pathlib import Path
from uuid import UUID, uuid4

from pydantic import Field, field_validator, model_validator
from sqlalchemy import text

from app.flywheel.leases import LeaseLost
from app.topics.cleaning import CLEANING_VERSION, clean_question
from app.topics.migration import migrate_topics
from app.topics.reviews import digest
from app.topics.snapshot import write_new_json
from app.topics.taxonomy import default_taxonomy
from app.topics.types import ModelIdentity, StrictRecord, _sequence


class PreviewChanged(RuntimeError):
    pass


def _id(value, *, zero=False):
    if type(value) is str and value.isascii() and value.isdecimal() and value==str(int(value)):
        value=int(value)
    if type(value) is not int or not (0 if zero else 1)<=value<2**64:
        raise ValueError('Expected canonical unsigned question ID')
    return str(value)


class PreparedQuestion(StrictRecord):
    id: str
    input_hash: str = Field(pattern='^[a-f0-9]{64}$')
    text: str | None
    status: str

    @model_validator(mode='after')
    def consistent(self):
        _id(self.id)
        if (self.status not in ('ready','cleaning_failed') or (self.status=='ready') != (self.text is not None)
                or self.text is not None and not 1<=len(self.text)<=512):
            raise ValueError('Invalid locally prepared question')
        return self


class BatchPreview(StrictRecord):
    schema_version: int = Field(ge=1,le=1)
    batch_id: str
    database_identity: str = Field(pattern='^[a-f0-9]{64}$')
    identity: ModelIdentity
    from_id: str
    to_id: str
    high_water: str
    reclassify: bool
    items: tuple[PreparedQuestion,...] = Field(max_length=100)
    preview_hash: str = Field(pattern='^[a-f0-9]{64}$')

    @field_validator('items',mode='before')
    @classmethod
    def array(cls,value): return _sequence(value)

    @model_validator(mode='after')
    def consistent(self):
        if str(UUID(self.batch_id))!=self.batch_id:
            raise ValueError('Batch identity must be a canonical UUID')
        lower,upper,water=int(_id(self.from_id)),int(_id(self.to_id,zero=True)),int(_id(self.high_water,zero=True))
        ids=tuple(int(row.id) for row in self.items)
        if ids!=tuple(sorted(set(ids))) or any(not lower<=i<=min(upper,water) for i in ids):
            raise ValueError('Batch items exceed the frozen scope or contain duplicates')
        taxonomy=default_taxonomy()
        if (self.identity.taxonomy_hash!=taxonomy.digest or self.identity.taxonomy_version!=taxonomy.version
                or self.identity.cleaning_version!=CLEANING_VERSION):
            raise ValueError('Unsupported active taxonomy or cleaner')
        return self


class BatchReceipt(StrictRecord):
    batch_id: str
    preview_hash: str
    model_version: str
    written: tuple[str,...]
    skipped: tuple[str,...]
    problems: dict[str,str]
    previous: dict[str,dict]


def make_preview(**fields):
    value=dict(schema_version=1,batch_id=str(uuid4()),**fields)
    encoded={key:([row.model_dump(mode='json') for row in item] if key=='items' else
                  item.model_dump(mode='json') if key=='identity' else item) for key,item in value.items()}
    return BatchPreview.model_validate(value | {'preview_hash':digest(encoded)})


def verify_preview(preview):
    checked=BatchPreview.model_validate_json(preview.model_dump_json())
    if digest(checked.model_dump(mode='json',exclude={'preview_hash'}))!=checked.preview_hash:
        raise ValueError('Frozen batch preview changed')
    return checked


def make_receipt(preview,*,written=(),skipped=(),problems=None,previous=None):
    return BatchReceipt(batch_id=preview.batch_id,preview_hash=preview.preview_hash,
        model_version=preview.identity.model_version,written=tuple(written),skipped=tuple(skipped),
        problems=problems or {},previous=previous or {})


def _prepared(identifier,raw):
    row=clean_question(raw,sample_id=str(identifier))
    return PreparedQuestion(id=str(identifier),input_hash=hashlib.sha256(raw.encode('utf-8')).hexdigest(),
        text=None if row.quarantine_reasons else row.text,status='cleaning_failed' if row.quarantine_reasons else 'ready')


class TopicRepository:
    def __init__(self,database,*,runtime_root: Path | None=None):
        self.database,self.runtime_root=database,runtime_root

    async def preview_pending(self,*,from_id,to_id,limit,identity,reclassify=False):
        lower=_id(from_id)
        upper=_id(to_id) if to_id is not None else None
        if (upper is not None and int(upper)<int(lower) or type(limit) is not int or not 1<=limit<=100
                or type(reclassify) is not bool):
            raise ValueError('Batch requires a bounded ID range and limit1..100')
        schema=await migrate_topics(self.database,preview=True)
        if not schema.complete:
            raise RuntimeError('Explicit topic migration required before selection')
        async with self.database.session() as session:
            water=int(await session.scalar(text('SELECT COALESCE(MAX(id),0) FROM low_confidence_questions')))
            bound=min(int(upper) if upper is not None else water,water)
            clause='t.question_id IS NULL'
            if reclassify:
                clause+=' OR t.model_version IS NULL OR t.model_version<>:model OR t.taxonomy_version IS NULL '
                clause+='OR t.taxonomy_version<>:taxonomy OR t.input_hash IS NULL OR t.input_hash<>SHA2(q.raw_question,256)'
            rows=(await session.execute(text('SELECT q.id,q.raw_question FROM low_confidence_questions q '
                'LEFT JOIN topic_classifications t ON t.question_id=q.id WHERE q.id>=:lower AND q.id<=:upper AND ('
                +clause+') ORDER BY q.id LIMIT :limit'),dict(lower=int(lower),upper=bound,limit=limit,
                model=identity.model_version,taxonomy=identity.taxonomy_version))).all()
        return make_preview(database_identity=schema.database_identity,identity=identity,from_id=lower,to_id=str(bound),
            high_water=str(water),reclassify=reclassify,items=[_prepared(row[0],row[1]) for row in rows])

    def _check_lease(self,lease):
        if (lease is None or not lease.name.startswith('ch10-topic:')
                or lease.connection.engine is not self.database.engine):
            raise LeaseLost('Topic writes require the owned topic processing connection')

    async def _selection(self,preview,session):
        schema=await session.scalar(text('SELECT DATABASE()'))
        url=self.database.engine.url
        identity=hashlib.sha256(json.dumps(dict(schema=schema,host=url.host,port=url.port),
            sort_keys=True,separators=(',',':')).encode()).hexdigest()
        if schema!=url.database or identity!=preview.database_identity:
            raise PreviewChanged('Batch database identity changed')
        ready,prior,skipped=[],{},[]
        for item in preview.items:
            row=(await session.execute(text('SELECT q.raw_question,t.id AS topic_id,t.labels,t.model_version,'
                't.taxonomy_version,t.input_hash,t.batch_id,t.classified_at FROM low_confidence_questions q '
                'LEFT JOIN topic_classifications t ON t.question_id=q.id WHERE q.id=:id FOR UPDATE'),
                {'id':int(item.id)})).mappings().one_or_none()
            if row is None or _prepared(item.id,row['raw_question'])!=item:
                raise PreviewChanged('Batch source changed; create a new bounded preview')
            if row['topic_id'] is not None:
                current=(row['model_version']==preview.identity.model_version
                    and row['taxonomy_version']==preview.identity.taxonomy_version and row['input_hash']==item.input_hash)
                if current or not preview.reclassify:
                    skipped.append(item.id)
                    continue
                previous={key:row[key] for key in ('model_version','taxonomy_version','input_hash','batch_id')}
                previous['labels']=json.loads(row['labels']) if isinstance(row['labels'],str) else row['labels']
                previous['classified_at']=row['classified_at'].isoformat()
                prior[item.id]=previous
            ready.append(item)
        return tuple(ready),prior,tuple(skipped)

    async def select_locked(self,preview,lease):
        verify_preview(preview)
        self._check_lease(lease)
        async with lease.transaction() as session:
            ready,_,_=await self._selection(preview,session)
        return ready  # The read transaction ends before the inference HTTP.

    async def commit_predictions(self,preview,predictions,lease):
        from app.topics.batch import validate_predictions
        preview=verify_preview(preview)
        predictions=validate_predictions(preview,predictions)
        self._check_lease(lease)
        written,problems=[],{}
        async with lease.transaction() as session:
            ready,prior,skipped=await self._selection(preview,session)
            available={row.id:row for row in ready}
            overwrites={row.id:prior[row.id] for row in predictions
                if row.id in available and row.id in prior and row.status=='classified'}
            if overwrites:
                if self.runtime_root is None:
                    raise RuntimeError('Reclassification requires durable previous-result evidence')
                path=self.runtime_root/'batches'/f'{preview.batch_id}-before.json'
                evidence=dict(preview_hash=preview.preview_hash,previous=overwrites)
                if path.exists():
                    if json.loads(path.read_text(encoding='utf-8'))!=evidence:
                        raise PreviewChanged('Previous-result evidence changed')
                else:
                    write_new_json(path,evidence)
            for prediction in predictions:
                if prediction.id not in available:
                    continue
                if prediction.status!='classified':
                    problems[prediction.id]=prediction.status
                    continue
                item=available[prediction.id]
                values=dict(id=int(item.id),labels=json.dumps(list(prediction.labels),ensure_ascii=False),
                    model=preview.identity.model_version,taxonomy=preview.identity.taxonomy_version,
                    input_hash=item.input_hash,batch=preview.batch_id)
                if item.id in prior:
                    await session.execute(text('UPDATE topic_classifications SET labels=:labels,model_version=:model,'
                        'taxonomy_version=:taxonomy,input_hash=:input_hash,batch_id=:batch,classified_at=CURRENT_TIMESTAMP '
                        'WHERE question_id=:id'),values)
                else:
                    await session.execute(text('INSERT INTO topic_classifications(question_id,labels,model_version,'
                        'taxonomy_version,input_hash,batch_id) VALUES(:id,:labels,:model,:taxonomy,:input_hash,:batch)'),values)
                written.append(item.id)
        return make_receipt(preview,written=written,skipped=skipped,problems=problems,previous=overwrites)
