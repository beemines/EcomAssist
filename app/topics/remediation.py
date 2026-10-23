"""Versioned, synthetic-only short-input preparation using the original shared ledger."""
from collections import Counter
import json
import os
import re
from pathlib import Path
from app.topics.cleaning import clean_question
from app.topics.corpus import _atomic,corpus_status
from app.topics.grouping import group_samples,GROUPING_VERSION
from app.topics.prompts import system_prompt,SHORT_PROMPT_VERSION
from app.topics.reviews import digest
from app.topics.taxonomy import default_taxonomy
from app.topics.teacher import GenerationPlan,GeneratedQuestion,Prelabel
from app.topics.types import LabelledSample
from app.topics.budget import BudgetError


def probe_semantic_family(row):
    """Conservatively exclude oversized-and-return paraphrases from data, never infer labels."""
    if not {'退换货','尺码'}<=set(row.labels):return False
    value=re.sub(r'[\W_]+','',row.text)
    positive_return=re.sub(r'不要退|不想退|不退了?','',value)
    return '退' in positive_return and bool(re.search(r'大了|偏大|太大|过大|宽了|肥了',value))


def original_source(dataset):
    from app.topics.augmentation import _read_dataset
    from app.topics.review_submission import TopicReviewService
    import hashlib
    dataset=Path(dataset);manifest,parts=_read_dataset(dataset)
    pilot=TopicReviewService(dataset.parent/'pilot').state()
    corpus_run=json.loads((dataset.parent/'corpus/run.json').read_text(encoding='utf-8'))
    if pilot is None or corpus_run.get('review_receipt_hash')!=pilot.receipt_hash:
        raise ValueError('Actual reviewed original pilot is required')
    content=(dataset/'train-augmentations.jsonl').read_text(encoding='utf-8')
    overlay=json.loads((dataset/'augmentation.json').read_text(encoding='utf-8'))
    if overlay['base_manifest_hash']!=manifest['manifest_hash'] or overlay['content_hash']!=hashlib.sha256(content.encode()).hexdigest():
        raise ValueError('Original training augmentation changed')
    children=tuple(LabelledSample.model_validate_json(line) for line in content.splitlines() if line.strip())
    blocked=tuple(row for name in ('train','validation','test') for row in parts[name])+children
    return manifest,blocked,pilot


async def prepare_remediation(source,teacher,*,output,recovery=None):
    manifest,blocked,pilot=original_source(source)
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    scope=dict(base_manifest_hash=manifest['manifest_hash'],original_source=str(Path(source).resolve()),
        pilot_receipt_hash=pilot.receipt_hash,iteration='short-input-v2')
    names=default_taxonomy().ordered_names
    minima={name:4 for name in names};minima.update({'尺码':20,'退换货':20,'物流':8,'订单修改':8})
    await collect_short(teacher,output=output/'train-corpus',blocked=blocked,scope=scope,partition='train',
        target=128,minima=minima,multi_fraction=.3,recovery=recovery)
    train_status,train=load_short(output/'train-corpus')
    await collect_short(teacher,output=output/'test-corpus',blocked=blocked+train,
        scope=scope|dict(new_train_hash=train_status['samples_hash']),partition='test',target=187,
        minima={name:10 for name in names},multi_fraction=.3,recovery=recovery)
    test_status,test=load_short(output/'test-corpus')
    lineage=scope|dict(train_status_hash=train_status['status_hash'],test_status_hash=test_status['status_hash'],
        original_test_policy='exposed_baseline_only_excluded_from_v2',original_file_hashes=manifest['file_hashes'])
    for path,value in ((output/'lineage.json',lineage),(output/'corpus/run.json',dict(review_receipt_hash=pilot.receipt_hash,lineage_hash=digest(lineage)))):
        path.parent.mkdir(parents=True,exist_ok=True)
        text=json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)
        if path.exists():
            if path.read_text(encoding='utf-8')!=text:raise ValueError('Remediation lineage changed')
        else:
            with path.open('x',encoding='utf-8') as stream:stream.write(text)
    return dict(status='complete',train_groups=train_status['independent_groups'],test_groups=test_status['independent_groups'])


def filter_short(candidates,blocked,*,max_chars=16):
    if type(max_chars) is not int or max_chars not in (16,45):raise ValueError('Only bounded short or mixed-test lengths are supported')
    candidates=tuple(candidates);blocked=tuple(blocked)
    if len({row.id for row in candidates+blocked})!=len(candidates)+len(blocked):
        raise ValueError('New synthetic IDs overlap previously frozen samples')
    invalid={row.id for row in candidates if not 4<=len(row.text)<=max_chars}
    eligible=[row for row in candidates if row.id not in invalid]
    grouped=group_samples(blocked+tuple(eligible))
    old={row.id for row in blocked};new={row.id for row in eligible}
    # Include discarded duplicate/conflicting IDs, not just the dedup winner.
    crossing={i for ids in grouped.component_ids.values() if set(ids)&old for i in ids if i in new}
    excluded=[dict(sample_id=i,reason=f'short_length_outside4_{max_chars}') for i in sorted(invalid)]
    excluded+=list(row for row in grouped.excluded if row['sample_id'] in new)
    excluded+=[dict(sample_id=i,reason='previous_family_overlap') for i in sorted(crossing)]
    return tuple(row for row in grouped.samples if row.id in new-crossing),tuple(excluded)


def _counts(rows):
    groups={}
    for row in rows:groups.setdefault(row.group_id,[]).append(row)
    counts=Counter(label for members in groups.values() for label in {t for row in members for t in row.labels})
    multi=sum(any(len(row.labels)>1 for row in members) for members in groups.values())
    return len(groups),counts,multi


def short_plan(count,positives,batch,*,partition):
    if partition not in ('train','test'):raise ValueError('Only two explicitly assigned remediation partitions exist')
    taxonomy=default_taxonomy();names=taxonomy.ordered_names
    targets={name:10 if partition=='test' else 4 for name in names}
    if partition=='train':targets.update({'尺码':20,'退换货':20,'物流':8,'订单修改':8})
    projected=Counter(positives);labels=[];hints=[]
    styles=('直白请求','条件追问','否定后纠正','操作询问','时间追问','表达困扰','短促追问','结果确认')
    for i in range(count):
        ordered=sorted(names,key=lambda name:(projected[name]/targets[name],names.index(name)))
        chosen=[ordered[0]]
        if (batch*16+i)%2==1 and chosen[0]!='其他':
            chosen.append(next(name for name in ordered[1:] if name!='其他'))
        selected=taxonomy.canonical_labels(chosen);labels.append(selected);projected.update(selected)
        context='训练补充' if partition=='train' else '独立新场景，不复写前面的题'
        hint=f'{context}，4至16字手机短口语，{styles[(batch+i+(3 if partition=="test" else 0))%len(styles)]}；仅明确表达指定诉求，场景{partition}-{batch}-{i}'
        if selected==('其他',):hint+='；只谈一般客服沟通或情绪，不加任何具体业务诉求'
        hints.append(hint)
    return GenerationPlan(count=count,scenario_labels=labels,scenario_hints=hints,taxonomy_hash=taxonomy.digest)


def load_short(root):
    root=Path(root);value=json.loads((root/'status.json').read_text(encoding='utf-8'))
    content=(root/'samples.jsonl').read_text(encoding='utf-8')
    if (value.get('status')!='complete' or value.get('status_hash')!=digest({k:v for k,v in value.items() if k!='status_hash'})
            or value.get('samples_hash')!=digest(content)):
        raise ValueError('Short-input partition is incomplete or modified')
    return value,tuple(LabelledSample.model_validate_json(line) for line in content.splitlines() if line.strip())


async def collect_short(teacher,*,output,blocked,scope,partition,target,minima,multi_fraction=.3,max_batches=29,recovery=None,
                        planner=None,row_guard=None,profile=None):
    from app.topics.data_cli import _checkpoint
    if profile is not None and (type(profile) is not dict or not callable(planner) or not callable(row_guard)):
        raise ValueError('A custom profile must bind both its planner and data guard')
    if profile is None and (planner is not None or row_guard is not None):raise ValueError('Unbound custom planning is forbidden')
    max_chars=profile.get('max_chars',16) if profile else 16
    generation_profile=profile.get('generation_profile','short') if profile else 'short'
    if max_chars not in (16,45) or generation_profile not in ('short','mixed'):raise ValueError('Invalid bounded data profile')
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    scope=dict(source=scope,partition=partition,target=target,minima=minima,multi_fraction=multi_fraction,
        taxonomy_hash=default_taxonomy().digest,grouping_version=GROUPING_VERSION,short_prompt_version=SHORT_PROMPT_VERSION,
        prompt_hashes={stage:digest(system_prompt(stage)) for stage in ('generate_short','label')},
        blocked_hash=digest([row.model_dump(mode='json') for row in blocked]))
    if generation_profile=='mixed':scope['prompt_hashes']['generate']=digest(system_prompt('generate'))
    if profile is not None:scope['custom_profile']=profile
    if (output/'status.json').exists():
        prior=json.loads((output/'status.json').read_text(encoding='utf-8'))
        if prior.get('scope_hash')!=digest(scope):raise ValueError('Remediation partition scope changed')
        if prior.get('status')=='complete':load_short(output);return output
    lock=output/'.prepare.lock'
    try:descriptor=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    except FileExistsError:raise ValueError('Another short-input preparation owns the scope') from None
    try:
        os.close(descriptor);run=output/'run.json'
        if run.exists():
            if json.loads(run.read_text(encoding='utf-8'))!=scope:raise ValueError('Remediation generation scope changed')
        else:
            with run.open('x',encoding='utf-8') as stream:json.dump(scope,stream,ensure_ascii=False,sort_keys=True)
        journal=output/'journal';journal.mkdir(exist_ok=True)
        raw=[];quarantine=[]
        def publish(status):
            rows,excluded=filter_short(raw,blocked,max_chars=max_chars)
            if row_guard is not None:
                excluded=list(excluded)+[dict(sample_id=row.id,reason=reason) for row in rows if (reason:=row_guard(row))]
                rows=tuple(row for row in rows if not row_guard(row))
            groups,counts,multi=_counts(rows)
            content=''.join(row.model_dump_json()+'\n' for row in rows)
            result=dict(status=status,scope_hash=digest(scope),independent_groups=groups,rows=len(rows),
                label_groups={label:counts[label] for label in default_taxonomy().ordered_names},multi_groups=multi,
                quarantine=quarantine+list(excluded),samples_hash=digest(content))
            _atomic(output/'samples.jsonl',content)
            _atomic(output/'status.json',json.dumps(result|dict(status_hash=digest(result)),ensure_ascii=False,indent=2))
            return rows,groups,counts,multi
        def enough(groups,counts,multi):
            return groups>=target and all(counts[label]>=value for label,value in minima.items()) and multi>=groups*multi_fraction
        for batch in range(max_batches):
            rows,groups,counts,multi=publish('preparing')
            if enough(groups,counts,multi):publish('complete');return output
            plan_path=journal/f'plan-{batch:04}.json'
            if plan_path.exists():
                bound=json.loads(plan_path.read_text(encoding='utf-8'))
                if bound.get('record_hash')!=digest({k:v for k,v in bound.items() if k!='record_hash'}):raise ValueError('Short plan modified')
                plan=GenerationPlan.model_validate_json(json.dumps(bound['plan'],ensure_ascii=False))
            else:
                plan=(planner or short_plan)(min(16,max(1,target-groups)),counts,batch,partition=partition)
                fields=dict(scope_hash=digest(scope),plan=plan.model_dump(mode='json'))
                with plan_path.open('x',encoding='utf-8') as stream:json.dump(fields|dict(record_hash=digest(fields)),stream,ensure_ascii=False)
            if json.loads(plan_path.read_text(encoding='utf-8'))['scope_hash']!=digest(scope):raise ValueError('Short plan scope modified')
            try:
                generated,receipt=await _checkpoint(f'{partition}-generate-{batch:04}',dict(scope=scope,plan=plan.model_dump(mode='json')),
                    lambda:teacher.generate(plan,short=generation_profile!='mixed' or batch%2==0,isolate_invalid_items=True),teacher,journal,GeneratedQuestion,recovery=recovery)
                rejected=receipt.get('item_quarantine',[])
                if len(generated)+len(rejected)!=plan.count:raise ValueError('Incomplete generation item accounting')
                quarantine.extend(rejected)
                eligible=[]
                for parent in generated:
                    if not 4<=len(parent.text)<=max_chars:quarantine.append(dict(sample_id=parent.id,reason=f'short_length_outside4_{max_chars}'))
                    else:eligible.append(parent)
                if eligible:
                    cleaned=tuple(clean_question(row.text,sample_id=row.id) for row in eligible)
                    labelled,receipt=await _checkpoint(f'{partition}-label-{batch:04}',dict(scope=scope,samples=[row.model_dump(mode='json') for row in cleaned]),
                        lambda:teacher.label(cleaned,isolate_invalid_items=True),teacher,journal,Prelabel,recovery=recovery)
                    rejected=receipt.get('item_quarantine',[]);rejected_ids={row['sample_id'] for row in rejected}
                    by_id={row.id:row for row in labelled};parents={row.id:row for row in eligible}
                    if (len(by_id)!=len(labelled) or len(rejected_ids)!=len(rejected) or set(by_id)&rejected_ids
                            or set(by_id)|rejected_ids!=set(parents)):
                        raise ValueError('Incomplete independent prelabel accounting')
                    quarantine.extend(rejected)
                    for identifier,row in by_id.items():
                        parent=parents[identifier]
                        if row.cleaned_text!=parent.text:raise ValueError('Prelabel changed exact input')
                        if row.labels!=parent.requested_labels:
                            quarantine.append(dict(sample_id=identifier,reason='scenario_label_mismatch'));continue
                        raw.append(LabelledSample(id=identifier,text=row.cleaned_text,labels=row.labels,origin='synthetic',
                            group_id=parent.family_id,source_question_ids=[],pilot=False))
            except BudgetError:publish('budget_paused');return output
            except BaseException:publish('stage_failed');raise
            rows,groups,counts,multi=publish('preparing')
            print(json.dumps(dict(partition=partition,batch=batch,groups=groups,multi=multi,min_class=min(counts.values(),default=0))),flush=True)
        publish('complete' if enough(groups,counts,multi) else 'incomplete')
        return output
    finally:lock.unlink(missing_ok=True)
