"""Resumable bounded synthetic expansion after an actual pilot review receipt."""
from collections import Counter
import json
import os
from pathlib import Path
from uuid import uuid4

from app.topics.budget import BudgetError
from app.topics.cleaning import clean_question
from app.topics.grouping import GROUPING_VERSION,group_samples,exact_text_key,reserved_probe
from app.topics.prompts import PROMPT_VERSION,system_prompt
from app.topics.reviews import ReviewReceipt,digest
from app.topics.taxonomy import default_taxonomy
from app.topics.teacher import GenerationPlan,GeneratedQuestion,Prelabel
from app.topics.types import LabelledSample

DOMAINS=('家居布艺','厨房收纳','户外运动','办公文具','家用电器','鞋靴服饰','宠物用品','数码配件',
    '灯具家具','母婴用品','图书玩具','清洁日化','园艺用品','旅行箱包','床上用品','美妆护理')
STYLES=('简短口语追问','明确说不要某事只问另一事','带一个具体使用背景','询问操作步骤',
    '询问条件限制','说清希望解决的事情','询问时间或适用范围','用生活化说法表达')


def _atomic(path,value):
    temporary=path.with_name('.'+path.name+'.'+uuid4().hex+'.tmp')
    try:
        with temporary.open('x',encoding='utf-8',newline='\n') as stream:
            stream.write(value);stream.flush();os.fsync(stream.fileno())
        os.replace(temporary,path)
    finally: temporary.unlink(missing_ok=True)


def corpus_status(root):
    value=json.loads((Path(root)/'status.json').read_text(encoding='utf-8'))
    fields={key:item for key,item in value.items() if key!='status_hash'}
    if digest(fields)!=value.get('status_hash'):
        raise ValueError('Corpus status changed')
    content=(Path(root)/'samples.jsonl').read_text(encoding='utf-8')
    if digest(content)!=value['samples_hash']: raise ValueError('Corpus materialization changed')
    return value


def _counts(samples):
    grouped=group_samples(samples)
    mapping={row.id:row for row in grouped.samples}
    positives=Counter(label for ids in grouped.groups.values() for label in {t for i in ids for t in mapping[i].labels})
    multi=sum(any(len(mapping[i].labels)>1 for i in ids) for ids in grouped.groups.values())
    return grouped,positives,multi


def _plan(count,positives,batch):
    taxonomy=default_taxonomy();names=taxonomy.ordered_names
    projected=positives.copy();labels=[];hints=[]
    for i in range(count):
        ordered=sorted(names,key=lambda name:(projected[name],names.index(name)))
        chosen=[ordered[0]]
        if (batch*16+i)%3==0 and chosen[0]!='其他':
            chosen.append(next(name for name in ordered[1:] if name!='其他'))
        labels.append(taxonomy.canonical_labels(chosen))
        projected.update(chosen)
        hints.append(f'围绕{DOMAINS[(batch+i*3)%len(DOMAINS)]}，采用{STYLES[(batch//2+i)%len(STYLES)]}；'
            f'本批场景序号{batch+1}-{i+1}，仅表达指定诉求，不额外增加诉求；创作与常见套话不同的完整问题')
    return GenerationPlan(count=count,scenario_labels=labels,taxonomy_hash=taxonomy.digest,scenario_hints=hints)


async def expand_corpus(snapshot,review:ReviewReceipt,teacher,*,output:Path,target_groups=2040,
        minimum_per_class=100,multi_fraction=.25,max_batches=256,recovery=None,progress=None) -> Path:
    from app.topics.data_cli import _checkpoint,_verify_snapshot
    review=ReviewReceipt.model_validate(review.model_dump())
    fields=review.model_dump(mode='json');fields.pop('receipt_hash')
    if digest(fields)!=review.receipt_hash or not review.samples:
        raise ValueError('An intact human pilot receipt is required')
    if snapshot is not None: _verify_snapshot(snapshot)
    if target_groups<1 or minimum_per_class<0 or not 0<=multi_fraction<=1 or not 1<=max_batches<=256:
        raise ValueError('Invalid bounded expansion target')
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    lock=output/'.prepare.lock'
    try: descriptor=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    except FileExistsError: raise ValueError('Another corpus preparation owns the lock') from None
    try:
        os.close(descriptor)
        scope=dict(review_receipt_hash=review.receipt_hash,pilot_pack_hash=review.pack_hash,
            snapshot_hash=snapshot.snapshot_hash if snapshot else None,taxonomy_hash=default_taxonomy().digest,
            grouping_version=GROUPING_VERSION,prompt_version=PROMPT_VERSION,
            prompt_hashes={stage:digest(system_prompt(stage)) for stage in ('generate','label')},
            target_groups=target_groups,minimum_per_class=minimum_per_class,multi_fraction=multi_fraction)
        run=output/'run.json'
        if run.exists():
            if json.loads(run.read_text(encoding='utf-8'))!=scope: raise ValueError('Frozen corpus scope changed')
        else:
            with run.open('x',encoding='utf-8') as stream: json.dump(scope,stream,ensure_ascii=False)
        journal=output/'journal';journal.mkdir(exist_ok=True)
        samples=list(review.samples);quarantine=[];receipts=[]
        def publish(status):
            grouped,counts,multi=_counts(samples)
            content=''.join(row.model_dump_json()+'\n' for row in sorted(samples,key=lambda row:row.id))
            _atomic(output/'samples.jsonl',content)
            value=dict(scope=scope,status=status,raw_samples=len(samples),independent_groups=len(grouped.groups),
                positive_groups=dict(counts),multi_groups=multi,origins=dict(Counter(row.origin for row in grouped.samples)),
                quarantine=quarantine+list(grouped.excluded),teacher_receipts=receipts,
                samples_hash=digest(content),budget=teacher.ledger.summary().model_dump())
            _atomic(output/'status.json',json.dumps(value|{'status_hash':digest(value)},ensure_ascii=False,indent=2))
            if progress: progress({key:value[key] for key in ('status','raw_samples','independent_groups','multi_groups','budget')})
            return grouped,counts,multi
        for batch in range(max_batches):
            grouped,positives,multi=publish('preparing')
            if (len(grouped.groups)>=target_groups and all(positives[name]>=minimum_per_class for name in default_taxonomy().ordered_names)
                    and multi>=len(grouped.groups)*multi_fraction):
                publish('complete');return output
            count=min(16,max(1,target_groups-len(grouped.groups)))
            plan=_plan(count,positives,batch)
            intent=dict(scope=scope,plan=plan.model_dump(mode='json'))
            try:
                generated,receipt=await _checkpoint(f'generate-{batch:04}',intent,
                    lambda plan=plan:teacher.generate(plan,isolate_invalid_items=True),teacher,journal,GeneratedQuestion,recovery=recovery)
                receipts.append(receipt)
                generation_rejected=receipt.get('item_quarantine',[])+receipt.get('offline_revalidation',{}).get('quarantine',[])
                generation_ids={row.id for row in generated}
                rejected_generation_ids={row.get('sample_id') for row in generation_rejected}
                if (len(generation_ids)!=len(generated) or len(rejected_generation_ids)!=len(generation_rejected)
                        or len(generated)+len(generation_rejected)!=plan.count
                        or generation_ids & rejected_generation_ids
                        or any(set(row)!={'sample_id','reason'} or row['reason']!='generated_item_invalid' for row in generation_rejected)
                        or 'id_map' in receipt and generation_ids | rejected_generation_ids!=set(receipt['id_map'].values())):
                    raise ValueError('Generated rows and explicit quarantine must cover the original plan')
                quarantine.extend(generation_rejected)
                seen={exact_text_key(row.text) for row in samples};eligible=[]
                for row in generated:
                    key=exact_text_key(row.text)
                    reason='reserved_probe' if reserved_probe(row.text) else 'exact_duplicate' if key in seen else None
                    if reason: quarantine.append(dict(sample_id=row.id,reason=reason));continue
                    seen.add(key);eligible.append(row)
                if not eligible: continue
                cleaned=[clean_question(row.text,sample_id=row.id) for row in eligible]
                labelled,receipt=await _checkpoint(f'label-{batch:04}',
                    dict(scope=scope,samples=[row.model_dump(mode='json') for row in cleaned]),
                    lambda cleaned=cleaned:teacher.label(cleaned,isolate_invalid_items=True),teacher,journal,Prelabel,recovery=recovery)
                receipts.append(receipt)
                by_id={row.id:row for row in labelled}
                exact_inputs={row.sample_id:row.text for row in cleaned}
                rejected=receipt.get('offline_revalidation',{}).get('quarantine',[])+receipt.get('item_quarantine',[])
                rejected_ids={row.get('sample_id') for row in rejected}
                expected_ids={row.id for row in eligible}
                if (len(by_id)!=len(labelled) or len(rejected_ids)!=len(rejected)
                        or any(set(row)!={'sample_id','reason'} or row['reason'] not in ('prelabel_text_mismatch','prelabel_item_invalid') for row in rejected)
                        or by_id.keys() & rejected_ids or by_id.keys() | rejected_ids != expected_ids
                        or any(row.cleaned_text!=exact_inputs[row.id] for row in labelled)):
                    raise ValueError('Prelabel identities/text and explicit quarantine must exactly cover eligible inputs')
                quarantine.extend(rejected)
                for parent in eligible:
                    if parent.id in rejected_ids:continue
                    label=by_id[parent.id]
                    if label.labels!=parent.requested_labels:
                        quarantine.append(dict(sample_id=label.id,reason='scenario_label_mismatch',
                            requested=list(parent.requested_labels),observed=list(label.labels)));continue
                    samples.append(LabelledSample(id=label.id,text=label.cleaned_text,labels=label.labels,
                        origin='synthetic',group_id=parent.family_id,source_question_ids=[],pilot=False))
            except BudgetError:
                publish('budget_paused');return output
            except BaseException:
                publish('stage_failed');raise
        grouped,positives,multi=publish('incomplete')
        if (len(grouped.groups)>=target_groups and all(positives[name]>=minimum_per_class for name in default_taxonomy().ordered_names)
                and multi>=len(grouped.groups)*multi_fraction): publish('complete')
        return output
    finally: lock.unlink(missing_ok=True)
