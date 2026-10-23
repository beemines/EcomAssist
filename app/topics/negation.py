"""Synthetic-only negation remediation with independent prelabels and real human gates."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from app.topics.remediation import collect_short,load_short,original_source,probe_semantic_family
from app.topics.reviews import digest,make_review_pack
from app.topics.taxonomy import default_taxonomy
from app.topics.teacher import GenerationPlan
from app.topics.types import LabelledSample

PROFILE_VERSION='ch10-negation-scenes-v1'
DIAGNOSTICS=(('买大了',('尺码',)),('尺码买大了',('尺码',)),('买大了想退',('退换货','尺码')),
    ('尺码大了想退',('退换货','尺码')),('买小了想退',('退换货','尺码')),('太大了想换',('退换货','尺码')),
    ('尺寸不合适想退',('退换货','尺码')),('不退货,只问尺码',('尺码',)))


def protected_family(row):
    """Data exclusion only: never call this function from an inference decoder."""
    if probe_semantic_family(row):return 'reserved_size_return_diagnostic_family'
    if '尺码' in row.labels and '退换货' not in row.labels and re.search(r'不(?:要|用|想)?退|别退',row.text):
        return 'reserved_negated_return_size_diagnostic_family'
    return None


def negation_plan(count,positives,batch,*,partition):
    if partition not in ('train','validation','test'):raise ValueError('Unknown negation partition')
    taxonomy=default_taxonomy();names=taxonomy.ordered_names;projected=Counter(positives);labels=[];hints=[]
    for i in range(count):
        slot=batch*16+i
        ordered=sorted(names,key=lambda name:(projected[name],names.index(name)))
        selected=[ordered[0]]
        if slot%4 in (0,3) and selected[0]!='其他':selected.append(next(name for name in ordered[1:] if name!='其他'))
        selected=taxonomy.canonical_labels(selected);labels.append(selected);projected.update(selected)
        hint=f'{partition}独立新场景{batch}-{i}，4至16字短口语；'
        if slot%2:
            denied=next(name for name in ('退换货','物流','发票','账号','保修维修','优惠活动') if name not in selected
                and not (name=='退换货' and '尺码' in selected))
            hint+=f'撤销诉求={denied}；明确说不要该操作，只肯定表达指定诉求，否定项不计标签；'
        else:hint+='肯定对照；明确表达指定诉求，省略背景也保留每个实际诉求；'
        if selected==('其他',):hint+='只谈一般客服沟通或情绪，不加入具体业务要求；'
        hint+='使用新语序和不同业务情境，不复写常见模板，不靠换名词凑数'
        hints.append(hint)
    return GenerationPlan(count=count,scenario_labels=labels,scenario_hints=hints,taxonomy_hash=taxonomy.digest)


def source_context(source):
    from app.topics.augmentation import _read_dataset
    source=Path(source).resolve();base=source.parent.parent
    if source!=base/'remediation-v2'/'dataset':raise ValueError('Use the frozen second-iteration source dataset')
    original,blocked,pilot=original_source(base/'dataset')
    manifest,parts=_read_dataset(source)
    lineage=json.loads((source.parent/'lineage.json').read_text(encoding='utf-8'))
    if lineage['base_manifest_hash']!=original['manifest_hash']:raise ValueError('Source lineage changed')
    all_rows={row.id:row for row in blocked}
    for rows in parts.values():
        for row in rows:all_rows[row.id]=row
    for folder in ('train-corpus','test-corpus'):
        _,rows=load_short(source.parent/folder)
        for row in rows:all_rows.setdefault(row.id,row)
    for i,(text,labels) in enumerate(DIAGNOSTICS):
        identifier='protected-diagnostic-'+str(i)
        all_rows[identifier]=LabelledSample(id=identifier,text=text,labels=labels,origin='synthetic',
            group_id=identifier,source_question_ids=[],pilot=False)
    scope=dict(source_manifest_hash=manifest['manifest_hash'],original_manifest_hash=original['manifest_hash'],
        original_pilot_receipt_hash=pilot.receipt_hash,iteration='negation-v4',external_data='new_synthetic_only')
    return scope,tuple(all_rows.values())


async def prepare_partition(source,teacher,*,output,partition,recovery=None):
    scope,blocked=source_context(source);output=Path(output)
    if partition not in ('train','validation','test'):raise ValueError('Unknown preparation partition')
    for preceding in {'train':(), 'validation':('train',), 'test':('train','validation')}[partition]:
        state,rows=load_short(output/(preceding+'-corpus'))
        scope[preceding+'_status_hash']=state['status_hash'];blocked+=rows
    minima={label:10 if partition=='test' else 1 for label in default_taxonomy().ordered_names}
    await collect_short(teacher,output=output/(partition+'-corpus'),blocked=blocked,scope=scope,partition=partition,
        target=187 if partition=='test' else 64,minima=minima,multi_fraction=.25,recovery=recovery,
        planner=negation_plan,row_guard=protected_family,
        profile=dict(version=PROFILE_VERSION,code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
    status,rows=load_short(output/(partition+'-corpus'))
    if partition=='train':build_training_review(output)
    return dict(partition=partition,status=status['status'],rows=len(rows),status_hash=status['status_hash'])


def _freeze(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if path.read_text(encoding='utf-8')!=text:raise ValueError('Refuse to replace frozen negation evidence')
    else:
        with path.open('x',encoding='utf-8',newline='\n') as stream:stream.write(text)


def build_training_review(output):
    output=Path(output);status,rows=load_short(output/'train-corpus')
    if len(rows)<64:raise ValueError('The target64 training review is incomplete')
    ordered=sorted(rows,key=lambda row:digest(dict(seed=20261023,id=row.id)))
    chosen=[];selected=set()
    for label in default_taxonomy().ordered_names:
        if not any(label in row.labels for row in chosen):
            match=next((row for row in ordered if row.id not in selected and label in row.labels),None)
            if match is None:raise ValueError('Training review does not cover all17 topics')
            chosen.append(match);selected.add(match.id)
    for row in ordered:
        if len(chosen)==64:break
        if row.id not in selected:chosen.append(row);selected.add(row.id)
    receipts=[]
    for path in sorted((output/'train-corpus/journal').glob('*.json')):
        value=json.loads(path.read_text(encoding='utf-8'))
        if value.get('state')=='complete':receipts.append(dict(journal_file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),attempt_id=value.get('receipt',{}).get('attempt_id')))
    pack=make_review_pack(chosen,snapshot_hash=status['status_hash'],teacher_receipts=receipts,purpose='pilot',
        annotation_notes={row.id:'本轮新合成训练对照。请核对真正肯定的诉求，否定或取消的操作不计标签；疑难可排除。通过前不会用于重训。' for row in chosen})
    _freeze(output/'train-review/pack.json',pack.model_dump_json(indent=2)+'\n')
    return pack
