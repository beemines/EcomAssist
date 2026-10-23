"""Cache-first, separately quota-bound A/B preparation. No import starts a request."""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

from app.topics.coverage_repair import (VERSION,recover_candidates,old_rows,scene_of,protected_probe,
    scene_plan,audit_scene_coverage)
from app.topics.grouping import group_samples
from app.topics.remediation import filter_short,collect_short,load_short
from app.topics.reviews import digest,make_review_pack
from app.topics.taxonomy import default_taxonomy
from app.topics.teacher import GenerationPlan
from app.topics.review_submission import TopicReviewService

STAGES=('train-a','train-b','validation-a','validation-b','test-a','test-b','test-general-short','test-general-mixed')


def freeze_text(path,text):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if path.read_text(encoding='utf-8')!=text:raise ValueError('Refuse to change frozen coverage evidence')
    else:
        with path.open('x',encoding='utf-8',newline='\n') as stream:stream.write(text)


def freeze_json(path,value):freeze_text(path,json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n')


def source_context(source):
    from app.topics.augmentation import _read_dataset
    source=Path(source).resolve();base=source.parent.parent
    if source!=base/'negation-v4/dataset':raise ValueError('Use the frozen v4 source')
    manifest,_=_read_dataset(source)
    receipt=TopicReviewService(base/'negation-v4/train-review').state()
    prior=json.loads((base/'negation-v4/corpus/run.json').read_text(encoding='utf-8'))
    if receipt is None or prior['review_receipt_hash']!=receipt.receipt_hash:raise ValueError('Prior human training source changed')
    if not {r.id for r in receipt.samples}<=set(manifest['splits']['train']):raise ValueError('Prior human rows are not in source training')
    return base,dict(source_manifest=manifest['manifest_hash'],source_files=manifest['file_hashes'],
        source_human_receipt_hash=receipt.receipt_hash,version=VERSION)


def inspect_source(source):
    base,scope=source_context(source);rows,_,_=recover_candidates(base)
    return scope|dict(qualified=len(rows),scene_a=sum(scene_of(r)=='A' for r in rows),
        scene_b=sum(scene_of(r)=='B' for r in rows),short=sum(len(r.text)<=16 for r in rows),teacher_calls=0)


def select_cache(rows,blocked,*,stage,target,max_chars,minima=None,reserve_missing=False):
    used={r.id for r in blocked}
    eligible=tuple(r for r in rows if r.id not in used and not protected_probe(r))
    if stage.endswith('-a'):eligible=tuple(r for r in eligible if scene_of(r)=='A')
    elif stage.endswith('-b'):eligible=tuple(r for r in eligible if scene_of(r)=='B')
    eligible,_=filter_short(eligible,tuple(blocked),max_chars=max_chars)
    ordered=sorted(eligible,key=lambda r:digest(dict(seed=20261023,stage=stage,id=r.id)))
    candidates=[];groups=set()
    for row in ordered:
        if row.group_id not in groups:candidates.append(row);groups.add(row.group_id)
    minimum=Counter(minima or {});counts=Counter();chosen=[]
    def remaining():return sum(max(0,n-counts[label]) for label,n in minimum.items())
    while candidates and len(chosen)<target:
        gains={r.id:sum(counts[label]<minimum[label] for label in r.labels) for r in candidates}
        best=max(candidates,key=lambda r:(gains[r.id],len(r.labels)>1,-candidates.index(r)))
        if not gains[best.id]:break
        candidates.remove(best);chosen.append(best);counts.update(best.labels)
    limit=max(0,target-remaining()) if reserve_missing else target
    if len(chosen)>limit:raise ValueError('Cached classes leave insufficient independent slots')
    for row in candidates:
        if len(chosen)>=limit:break
        chosen.append(row);counts.update(row.labels)
    return tuple(chosen)


def representatives(rows):
    chosen={}
    for row in sorted(rows,key=lambda r:digest(dict(seed=20261023,id=r.id))):chosen.setdefault(row.group_id,row)
    return tuple(chosen.values())


def merge_partition(output,partition,parts,*,scope):
    output=Path(output);raw=[];statuses=[];receipts=[]
    for path in parts:
        path=Path(path)
        if path.resolve().parent!=(output/'parts').resolve():raise ValueError('Part is outside this coverage iteration')
        status,rows=load_short(path);raw.extend(rows);statuses.append(dict(stage=path.name,status_hash=status['status_hash']))
        for journal in sorted((path/'journal').glob('*.json')):
            value=json.loads(journal.read_text(encoding='utf-8'))
            if value.get('state')=='complete':receipts.append(dict(file=str(journal.relative_to(output)),sha256=hashlib.sha256(journal.read_bytes()).hexdigest()))
    grouped=group_samples(raw)
    if grouped.excluded:raise ValueError('Unexpected duplicate/probe in completed scene parts')
    rows=representatives(grouped.samples)
    coverage=audit_scene_coverage(rows,partition=partition)
    content=''.join(r.model_dump_json()+'\n' for r in sorted(rows,key=lambda r:r.id))
    fields=dict(status='complete',scope_hash=digest(scope),parts=statuses,independent_groups=len(rows),rows=len(rows),
        scene_a=coverage['scene_a'],scene_b=coverage['scene_b'],short=coverage['short'],samples_hash=digest(content),
        omitted_same_new_family=sorted({r.id for r in raw}-{r.id for r in rows}))
    status=fields|dict(status_hash=digest(fields));corpus=output/(partition+'-corpus')
    freeze_text(corpus/'samples.jsonl',content);freeze_json(corpus/'status.json',status)
    if partition=='train':
        cache=output/'cache-snapshot.json'
        if cache.exists():receipts.append(dict(file=cache.name,sha256=hashlib.sha256(cache.read_bytes()).hexdigest()))
        pack=make_review_pack(rows,snapshot_hash=status['status_hash'],teacher_receipts=receipts,purpose='pilot',
            annotation_notes={r.id:('场景A：大小适配并实际要求退或换；逐条核对全部诉求。' if scene_of(r)=='A' else
                '场景B：取消退换，实际仅咨询大小适配；若仍要求换货，标签必须含退换货。') for r in rows})
        freeze_text(output/'train-review/pack.json',pack.model_dump_json(indent=2)+'\n')
    return status


def general_planner(baseline):
    def plan(count,positives,batch,*,partition):
        names=default_taxonomy().ordered_names;projected=Counter(baseline)+Counter(positives);labels=[];hints=[]
        for i in range(count):
            ordered=sorted(names,key=lambda n:(projected[n],names.index(n)));chosen=[ordered[0]]
            if i%2 and chosen[0]!='其他':chosen.append(next(n for n in ordered[1:] if n!='其他'))
            chosen=default_taxonomy().canonical_labels(chosen);labels.append(chosen);projected.update(chosen)
            length='4至16字' if partition.endswith('short') else '4至45字'
            hints.append(f'{partition}全新独立情境{batch}-{i}；{length}；明确每个字面诉求，改变原因和语序，不以替换商品名凑家族；取消操作不要当肯定要求')
        return GenerationPlan(count=count,scenario_labels=labels,scenario_hints=hints,taxonomy_hash=default_taxonomy().digest)
    return plan


async def prepare_coverage(source,teacher,*,output,partition,recovery=None):
    base,scope=source_context(source);output=Path(output).resolve()
    if output!=(base/'coverage-v5').resolve():raise ValueError('Use the independent coverage-v5 output')
    if partition not in ('train','validation','test'):raise ValueError('Unknown coverage partition')
    cache,provenance,excluded=recover_candidates(base)
    snapshot=dict(source=scope,samples=[r.model_dump(mode='json') for r in cache],provenance=provenance,exclusions=excluded)
    freeze_json(output/'cache-snapshot.json',snapshot)
    scope=scope|dict(cache_snapshot_hash=digest(snapshot),partition=partition)
    for prior in {'train':(), 'validation':('train',), 'test':('train','validation')}[partition]:
        status,_=load_short(output/(prior+'-corpus'));scope[prior+'_status_hash']=status['status_hash']
    blocked=list(old_rows(base));paths=[];preceding=[]
    first={'train':'train-a','validation':'validation-a','test':'test-a'}[partition]
    for stage in STAGES[:STAGES.index(first)]:
        status,rows=load_short(output/'parts'/stage);blocked.extend(rows)
    async def part(stage,target,*,scene=None,max_chars=16,baseline=None,minima=None,multi_fraction=0):
        nonlocal blocked
        if target==0:return
        minimum=minima or {n:0 for n in default_taxonomy().ordered_names}
        seeds=select_cache(cache,blocked,stage=stage,target=target,max_chars=max_chars,minima=minimum,
            reserve_missing=stage=='test-general-mixed')
        def guard(row):
            protected=protected_probe(row)
            return protected or ('target_scene_not_present' if scene and scene_of(row)!=scene else None)
        profile=dict(version=VERSION,stage=stage,max_chars=max_chars,generation_profile='mixed' if max_chars==45 else 'short',
            preparation_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            scene_code_sha256=hashlib.sha256(Path(__file__).with_name('coverage_repair.py').read_bytes()).hexdigest())
        path=output/'parts'/stage
        await collect_short(teacher,output=path,blocked=tuple(blocked),scope=scope,partition=stage,target=target,
            minima=minimum,multi_fraction=multi_fraction,recovery=recovery,planner=scene_plan if scene else general_planner(baseline or {}),
            row_guard=guard,profile=profile,seeds=seeds)
        status,rows=load_short(path)
        blocked.extend(rows);paths.append(path);preceding.extend(representatives(rows))
    if partition in ('train','validation'):
        quota=32 if partition=='train' else 16
        for scene in ('a','b'):
            minimum={n:0 for n in default_taxonomy().ordered_names};minimum['尺码']=quota
            if scene=='a':minimum['退换货']=quota
            await part(partition+'-'+scene,quota,scene=scene.upper(),minima=minimum)
    else:
        await part('test-a',12,scene='A',max_chars=45,minima={'退换货':12,'尺码':12})
        await part('test-b',12,scene='B',minima={'尺码':12})
        short_needed=max(0,75-sum(len(r.text)<=16 for r in preceding))
        baseline=Counter(l for r in preceding for l in r.labels)
        await part('test-general-short',short_needed,baseline=baseline,multi_fraction=.25)
        baseline=Counter(l for r in preceding for l in r.labels);remaining=187-len(preceding)
        minima={n:max(0,10-baseline[n]) for n in default_taxonomy().ordered_names}
        needed_multi=max(0,math.ceil(.25*187)-sum(len(r.labels)>1 for r in preceding))
        await part('test-general-mixed',remaining,max_chars=45,baseline=baseline,minima=minima,
            multi_fraction=needed_multi/remaining if remaining else 0)
    return merge_partition(output,partition,paths,scope=scope)
