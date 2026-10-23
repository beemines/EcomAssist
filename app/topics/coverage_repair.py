"""Versioned data-only scene contracts and recovery; never imported by inference."""
from collections import Counter
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import re

from app.topics.cleaning import clean_question
from app.topics.grouping import group_samples
from app.topics.negation import DIAGNOSTICS
from app.topics.reviews import digest
from app.topics.taxonomy import default_taxonomy
from app.topics.teacher import GeneratedQuestion,Prelabel,GenerationPlan
from app.topics.types import LabelledSample

VERSION='ch10-coverage-v5'
SOURCE_FOLDERS=('corpus','remediation-v2/train-corpus','remediation-v2/test-corpus',
    'negation-v4/train-corpus','negation-v4/validation-corpus','negation-v4/test-corpus')
_NEGATION=re.compile(r'(?:不(?:要|用|想|需要)?|别|无需).{0,4}(?:退|换)|(?:退|换).{0,5}(?:先别|不用|不要|不办|不走|先不|取消)')


def protected_probe(row):
    value=re.sub(r'[\W_]+','',row.text)
    for text,_ in DIAGNOSTICS:
        reference=re.sub(r'[\W_]+','',text)
        if value==reference or SequenceMatcher(None,value,reference,autojunk=False).ratio()>=.82:
            return 'reserved_known_probe_near_family'
    return None


def scene_of(row):
    """Audit existing prelabels and text forms, never predict a business label."""
    labels=set(row.labels)
    if {'退换货','尺码'}<=labels and '码' not in row.text and '尺寸' not in row.text:return 'A'
    if labels=={'尺码'} and _NEGATION.search(row.text):return 'B'
    return None


def audit_scene_coverage(rows,*,partition):
    rows=tuple(rows);counts=Counter(scene_of(row) for row in rows)
    if partition not in ('train','validation','test'):raise ValueError('Unknown scene partition')
    required={'train':(64,32,32),'validation':(32,16,16),'test':(187,12,12)}[partition]
    total,a,b=required
    if (len(rows)!=total or len({r.group_id for r in rows})!=total or counts['A']<a or counts['B']<b
            or any(protected_probe(row) for row in rows)):
        raise ValueError('Required scene coverage or independent families are missing; do not train')
    if partition=='test':
        if sum(len(r.text)<=16 for r in rows)<75:raise ValueError('Independent test short scene coverage is missing')
        by_group={r.group_id:set(r.labels) for r in rows}
        for label in default_taxonomy().ordered_names:
            positive=sum(label in labels for labels in by_group.values())
            if min(positive,total-positive)<10:raise ValueError('Independent test class scene coverage is missing')
    return dict(groups=total,scene_a=counts['A'],scene_b=counts['B'],short=sum(len(r.text)<=16 for r in rows))


def scene_plan(count,positives,batch,*,partition):
    if partition not in tuple(f'{p}-{s}' for p in ('train','validation','test') for s in ('a','b')):
        raise ValueError('Unknown scene stage')
    scene=partition[-1];labels=('退换货','尺码') if scene=='a' else ('尺码',)
    domains={'train':'衣物长短、鞋的松紧、物品放不下',
        'validation':'窗帘垂地、罩子套不进、餐具摆不下',
        'test':'宠物用品容纳不下、箱包穿戴不合适、支架宽窄'}
    styles=('先说原因再提要求','先提要求再说原因','短促口语','犹豫后明确最终要求',
        '否定一种操作但明确最终诉求','询问具体办理方式','说明使用受阻','直接向客服求助')
    hints=[]
    for i in range(count):
        hint=f'{partition}独立情境{batch}-{i}；4至16字；{domains[partition.split("-")[0]]}，{styles[(batch*16+i)%8]}；'
        if scene=='a':hint+='实际要退或换且有大小适配诉求；不要出现“码”“尺寸”；用不同原因表达挤、松、长短或放不下；'
        else:hint+='明确取消退换操作，实际只问大小适配；不要出现仍然要换或退的要求；'
        hints.append(hint+'改变语序和情境，不循环替换商品名，不复写常见验收短句')
    return GenerationPlan(count=count,scenario_labels=[labels]*count,scenario_hints=hints,taxonomy_hash=default_taxonomy().digest)


def old_rows(root):
    root=Path(root);mapping={}
    paths=[root/folder/'samples.jsonl' for folder in ('pilot',)+SOURCE_FOLDERS]
    paths += [root/folder/(part+'.jsonl') for folder in ('dataset','remediation-v2/dataset','negation-v4/dataset')
        for part in ('train','validation','test','train-augmentations')]
    for path in paths:
        if not path.exists():continue
        if path.is_symlink():raise ValueError('Old data source cannot be linked')
        for line in path.read_text(encoding='utf-8').splitlines():
            if line.strip():
                row=LabelledSample.model_validate_json(line);mapping[row.id]=row
    return tuple(mapping.values())


def recover_candidates(evidence_root):
    """Inspect existing completed GLM journals without constructing a teacher."""
    root=Path(evidence_root).resolve();blocked=old_rows(root);used={r.id for r in blocked}
    generated={};labelled={};excluded=[];hashes={}
    for folder in SOURCE_FOLDERS:
        journal=root/folder/'journal'
        if journal.is_symlink():raise ValueError('Source checkpoint directory cannot be linked')
        for path in sorted(journal.glob('*.json')):
            if not re.fullmatch(r'(?:(?:train|validation|test)-)?(?:generate|label)-\d{4}',path.stem):continue
            if path.is_symlink():raise ValueError('Source checkpoint cannot be linked')
            content=path.read_bytes();saved=json.loads(content)
            if saved.get('state')!='complete':continue
            if saved.get('record_hash')!=digest({k:v for k,v in saved.items() if k!='record_hash'}):
                raise ValueError('Source checkpoint was modified')
            receipt=saved.get('receipt') or {}
            if receipt.get('model')!='glm-5.3-flash' or not receipt.get('attempt_id'):
                raise ValueError('Source checkpoint has no independent teacher receipt')
            hashes[str(path.relative_to(root))]=hashlib.sha256(content).hexdigest()
            is_generate='generate-' in path.stem
            destination=generated if is_generate else labelled
            record_type=GeneratedQuestion if is_generate else Prelabel
            for value in saved['data']:
                try:row=record_type.model_validate(value)
                except ValueError:
                    excluded.append(dict(sample_id=value.get('id','unknown'),reason='invalid_cached_item'));continue
                if not row.id.startswith('syn-'):continue
                if row.id in destination and destination[row.id][0]!=row:
                    raise ValueError('Conflicting source checkpoint identity')
                destination[row.id]=(row,str(path.relative_to(root)))
    used_families={row.family_id for identifier,(row,_) in generated.items() if identifier in used}
    samples=[];provenance={}
    for identifier,(label,label_path) in sorted(labelled.items()):
        reason=None;parent=generated.get(identifier)
        if identifier in used:reason='previously_exposed_id'
        elif parent is None:reason='missing_generation_proof'
        else:
            gen,gen_path=parent;cleaned=clean_question(gen.text,sample_id=gen.id)
            if cleaned.quarantine_reasons or any('redacted' in edit for edit in cleaned.edits):reason='unsafe_cached_text'
            elif cleaned.text!=label.cleaned_text:reason='cached_input_mismatch'
            elif gen.family_id in used_families:reason='previously_exposed_family'
        if reason:
            excluded.append(dict(sample_id=identifier,reason=reason));continue
        row=LabelledSample(id=identifier,text=label.cleaned_text,labels=label.labels,origin='synthetic',
            group_id=gen.family_id,source_question_ids=[],pilot=False)
        if protected_probe(row):
            excluded.append(dict(sample_id=identifier,reason='reserved_known_probe_near_family'));continue
        samples.append(row)
        provenance[identifier]=dict(generate_file=gen_path,generate_sha256=hashes[gen_path],
            label_file=label_path,label_sha256=hashes[label_path],requested_labels=list(gen.requested_labels),
            recovered_labels=list(label.labels),human_review='pending')
    grouped=group_samples(blocked+tuple(samples))
    crossing={i for ids in grouped.component_ids.values() if set(ids)&used for i in ids if i not in used}
    invalid={r['sample_id'] for r in grouped.excluded}
    for row in samples:
        if row.id in crossing:excluded.append(dict(sample_id=row.id,reason='previously_exposed_text_family'))
        elif row.id in invalid:excluded.append(dict(sample_id=row.id,reason='cached_duplicate_or_probe_family'))
    samples=tuple(row for row in samples if row.id not in crossing|invalid)
    provenance={row.id:provenance[row.id] for row in samples}
    return samples,provenance,tuple(excluded)
