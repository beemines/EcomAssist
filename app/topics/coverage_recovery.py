"""Approved cache-first recovery in new scopes; original interrupted parts stay intact."""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
from app.topics.coverage_preparation import source_context,freeze_json,select_cache,merge_partition,general_planner
from app.topics.coverage_repair import old_rows,scene_of,protected_probe,scene_plan
from app.topics.coverage_selection import candidate_rows,VERSION as SELECTION_VERSION
from app.topics.remediation import collect_short,load_short
from app.topics.review_submission import TopicReviewService
from app.topics.reviews import digest
from app.topics.types import LabelledSample
from app.topics.teacher import GenerationPlan
from app.topics.taxonomy import default_taxonomy

VERSION='bounded-recovery-01'


def preview_recovery(source,*,output,partition):
    base,scope=source_context(source);output=Path(output).resolve()
    if output!=base/'coverage-v5' or partition not in ('validation','test'):raise ValueError('Unknown recovery scope')
    receipt=TopicReviewService(output/'train-review').state()
    if receipt is None:raise ValueError('Actual64 training human review is required')
    return dict(mode='preview',partition=partition,teacher_calls=0,source_manifest=scope['source_manifest'],
        training_human_receipt=receipt.receipt_hash,partial_validation_b=len(partial_seeds(output/'parts/validation-b')),
        generation_scope='recovery-01',old_stage_not_rewritten=True)


def partial_seeds(path):
    path=Path(path);status=json.loads((path/'status.json').read_text(encoding='utf-8'))
    content=(path/'samples.jsonl').read_text(encoding='utf-8')
    if (status.get('status')!='budget_paused' or status.get('status_hash')!=digest({k:v for k,v in status.items() if k!='status_hash'})
            or status.get('samples_hash')!=digest(content)):raise ValueError('Partial source changed')
    return tuple(LabelledSample.model_validate_json(line) for line in content.splitlines())


def cancellation_plan(count,positives,batch,*,partition):
    domains=('窗帘长度、桌布宽度、收纳盒容积、门垫厚度、花盆口径、手机套宽窄、枕套长度、床罩大小'
        if partition.startswith('validation') else '猫窝内径、狗衣胸围、宠物箱高度、鸟笼宽度、水壶底径、书包容量、眼镜腿长度、护具松紧')
    hints=[f'独立B情境{batch}-{i}；总长最多16字含标点，尽量6至12字；{domains}；明确表示不退也不换，实际只问大小适配；不要申请取消已建售后，不要修改订单，不得随后又要换货；省掉客服称呼与犹豫铺垫；不复写常见测试句'
        for i in range(count)]
    return GenerationPlan(count=count,scenario_labels=[('尺码',)]*count,scenario_hints=hints,taxonomy_hash=default_taxonomy().digest)


def validate_recovery_sources(iteration):
    iteration=Path(iteration);file=iteration/'recovery-01/source.json'
    if not file.exists():return
    value=json.loads(file.read_text(encoding='utf-8'))
    if value.get('record_hash')!=digest({k:v for k,v in value.items() if k!='record_hash'}):raise ValueError('Recovery source identity changed')
    for name,sha in value['files'].items():
        path=iteration/name
        if path.is_symlink() or not path.resolve().is_relative_to(iteration.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest()!=sha:
            raise ValueError('Original interrupted source changed')
    receipt=TopicReviewService(iteration/'train-review').state()
    if receipt is None or receipt.receipt_hash!=value['actual_human_receipt']:raise ValueError('Actual training human review changed')


async def collect_part(teacher,*,path,scope,blocked,seeds,stage,target,max_chars,minima,multi_fraction,baseline,scene,provenance):
    path=Path(path)
    def guard(row):return protected_probe(row) or ('target_scene_not_present' if scene and scene_of(row)!=scene else None)
    if scene=='B':planner=cancellation_plan
    elif scene=='A':planner=scene_plan
    else:planner=general_planner(baseline)
    def plan(count,positives,batch,*,partition):return planner(count,positives,batch,partition=stage)
    profile=dict(version=VERSION,stage=stage,max_chars=max_chars,generation_profile='mixed' if max_chars==45 else 'short',
        batch_floor=16,no_gain_limit=2,exact_groups=True,pin_seeds=True,source_provenance=provenance,
        recovery_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),selection_version=SELECTION_VERSION,
        selection_code_sha256=hashlib.sha256(Path(__file__).with_name('coverage_selection.py').read_bytes()).hexdigest())
    await collect_short(teacher,output=path,blocked=tuple(blocked),scope=scope,partition=stage+'-recovery-01',target=target,
        minima=minima,multi_fraction=multi_fraction,planner=plan,row_guard=guard,profile=profile,seeds=seeds)
    status=json.loads((path/'status.json').read_text(encoding='utf-8'))
    if status['status']!='complete':return dict(status=status['status'],stage=stage,groups=status['independent_groups'])
    actual,rows=load_short(path)
    return dict(status='complete',rows=rows,candidates=candidate_rows(path,actual,rows))


async def prepare_recovery(source,teacher,*,output,partition):
    output=Path(output).resolve();base,source_scope=source_context(source)
    if output!=base/'coverage-v5' or partition not in ('validation','test'):raise ValueError('Unknown approved recovery target')
    snapshot=json.loads((output/'cache-snapshot.json').read_text(encoding='utf-8'))
    if snapshot['source']!=source_scope:raise ValueError('Original cache source changed')
    cache=tuple(LabelledSample.model_validate(r) for r in snapshot['samples'])
    train_status,_=load_short(output/'train-corpus');receipt=TopicReviewService(output/'train-review').state()
    if receipt is None:raise ValueError('Actual64 training human review is required')
    source_paths=[output/'train-corpus/status.json',output/'train-review/review-receipt.json']
    for stage in ('validation-a','validation-b'):
        source_paths += [p for p in (output/'parts'/stage).rglob('*') if p.is_file() and p.suffix in ('.json','.jsonl')]
    fields=dict(version=VERSION,actual_human_receipt=receipt.receipt_hash,
        files={str(p.relative_to(output)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths})
    freeze_json(output/'recovery-01/source.json',fields|dict(record_hash=digest(fields)))
    validate_recovery_sources(output)
    scope=source_scope|dict(cache_snapshot_hash=digest(snapshot),partition=partition,train_status_hash=train_status['status_hash'])
    if partition=='test':scope['validation_status_hash']=load_short(output/'validation-corpus')[0]['status_hash']
    blocked=list(old_rows(base))
    for stage in ('train-a','train-b'):
        status,rows=load_short(output/'parts'/stage);blocked.extend(candidate_rows(output/'parts'/stage,status,rows))
    paths=[];preceding=[]
    async def run(stage,target,*,scene=None,max_chars=16,minima=None,multi_fraction=0,seeds=None):
        if target==0:return None
        minimum=minima or {n:0 for n in default_taxonomy().ordered_names}
        baseline=Counter(label for r in preceding for label in r.labels)
        selected=select_cache(cache,blocked,stage=stage,target=target,max_chars=max_chars,minima=minimum,
            reserve_missing=stage=='test-general-mixed') if seeds is None else tuple(seeds)
        path=output/'parts'/(stage+'-recovery-01')
        result=await collect_part(teacher,path=path,scope=scope,blocked=blocked,seeds=selected,stage=stage,target=target,
            max_chars=max_chars,minima=minimum,multi_fraction=multi_fraction,baseline=baseline,scene=scene,
            provenance={'source_record_hash':digest(fields)})
        if result['status']!='complete':return result
        paths.append(path);preceding.extend(result['rows']);blocked.extend(result['candidates'])
        return None
    if partition=='validation':
        old_path=output/'parts/validation-a';status,a=load_short(old_path)
        paths.append(old_path);preceding.extend(a);blocked.extend(candidate_rows(old_path,status,a))
        b=partial_seeds(output/'parts/validation-b')
        if len(b)!=14 or any(scene_of(r)!='B' for r in b):raise ValueError('Diagnosed14 B source changed')
        stopped=await run('validation-b',16,scene='B',minima={'尺码':16},seeds=b)
        if stopped:return stopped
    else:
        status,_=load_short(output/'validation-corpus')
        for item in status['parts']:
            path=output/'parts'/item['stage'];part,rows=load_short(path);blocked.extend(candidate_rows(path,part,rows))
        for stage,scene,limit in (('test-a','A',45),('test-b','B',16)):
            minimum={'尺码':12}|({'退换货':12} if scene=='A' else {})
            stopped=await run(stage,12,scene=scene,max_chars=limit,minima=minimum)
            if stopped:return stopped
        short=max(0,75-sum(len(r.text)<=16 for r in preceding))
        stopped=await run('test-general-short',short,multi_fraction=.25)
        if stopped:return stopped
        baseline=Counter(label for r in preceding for label in r.labels);remaining=187-len(preceding)
        minimum={n:max(0,10-baseline[n]) for n in default_taxonomy().ordered_names}
        needed=max(0,math.ceil(.25*187)-sum(len(r.labels)>1 for r in preceding))
        stopped=await run('test-general-mixed',remaining,max_chars=45,minima=minimum,multi_fraction=needed/remaining)
        if stopped:return stopped
    return merge_partition(output,partition,paths,scope=scope)
