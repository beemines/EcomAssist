"""Deterministically augment only frozen train groups, using the existing budget."""
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path

from app.topics.corpus import _atomic
from app.topics.grouping import exact_text_key,validate_augmentation
from app.topics.prompts import PROMPT_VERSION,system_prompt
from app.topics.reviews import digest
from app.topics.taxonomy import default_taxonomy
from app.topics.types import LabelledSample


def _read_dataset(root):
    root=Path(root)
    manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    fields={key:value for key,value in manifest.items() if key!='manifest_hash'}
    if (digest(fields)!=manifest.get('manifest_hash') or manifest.get('seed')!=20261021
            or manifest.get('taxonomy_hash')!=default_taxonomy().digest
            or set(manifest.get('splits',{}))!={'train','validation','test'}):
        raise ValueError('Frozen dataset identity changed')
    rows={};seen=set()
    for name in ('train','validation','test'):
        content=(root/(name+'.jsonl')).read_text(encoding='utf-8')
        if hashlib.sha256(content.encode()).hexdigest()!=manifest['file_hashes'][name]:
            raise ValueError('Frozen split content changed')
        rows[name]=[LabelledSample.model_validate_json(line) for line in content.splitlines() if line.strip()]
        ids=[row.id for row in rows[name]]
        if ids!=manifest['splits'][name] or len(ids)!=len(set(ids)) or set(ids)&seen:
            raise ValueError('Frozen split memberships overlap or changed')
        seen.update(ids)
    return manifest,rows


def select_train_parents(root):
    manifest,rows=_read_dataset(root)
    groups=defaultdict(list)
    for row in rows['train']: groups[row.group_id].append(row)
    if not groups: raise ValueError('No frozen train groups')
    strata=defaultdict(list)
    for group,members in groups.items():
        labels=tuple(label for label in default_taxonomy().ordered_names if any(label in row.labels for row in members))
        strata[labels].append(group)
    rank=lambda group:digest(dict(seed=20261021,group=group))
    selected=set()
    target=max(1,round(len(groups)*.25))
    for bucket in strata.values(): selected.update(sorted(bucket,key=rank)[:round(len(bucket)*.25)])
    if len(selected)>target: selected=set(sorted(selected,key=rank)[:target])
    if len(selected)<target:
        selected.update(sorted(set(groups)-selected,key=rank)[:target-len(selected)])
    parents=tuple(min(groups[group],key=lambda row:row.id) for group in sorted(selected,key=rank))
    return parents,manifest


def load_augmentations(root):
    root=Path(root)
    status=json.loads((root/'status.json').read_text(encoding='utf-8'))
    content=(root/'samples.jsonl').read_text(encoding='utf-8')
    if (status.get('status')!='complete' or digest({k:v for k,v in status.items() if k!='status_hash'})!=status.get('status_hash')
            or digest(content)!=status.get('samples_hash')):
        raise ValueError('Training augmentation is incomplete or changed')
    return status,tuple(LabelledSample.model_validate_json(line) for line in content.splitlines() if line.strip())


async def augment_training(dataset,teacher,*,output,recovery=None):
    from app.topics.data_cli import _checkpoint
    parents,manifest=select_train_parents(dataset)
    _,all_rows=_read_dataset(dataset)
    scope=dict(base_manifest_hash=manifest['manifest_hash'],parent_ids=[row.id for row in parents],
        prompt_version=PROMPT_VERSION,prompt_hash=digest(system_prompt('augment')))
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    lock=output/'.prepare.lock'
    try: descriptor=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    except FileExistsError: raise ValueError('Another augmentation preparation owns the lock') from None
    try:
        os.close(descriptor)
        scope_file=output/'run.json'
        if scope_file.exists():
            if json.loads(scope_file.read_text(encoding='utf-8'))!=scope: raise ValueError('Augmentation scope changed')
        else:
            with scope_file.open('x',encoding='utf-8') as stream: json.dump(scope,stream,ensure_ascii=False)
        journal=output/'journal';journal.mkdir(exist_ok=True)
        accepted=[];quarantine=[];seen={exact_text_key(row.text) for rows in all_rows.values() for row in rows}
        for start in range(0,len(parents),16):
            batch=parents[start:start+16]
            children,receipt=await _checkpoint(f'augment-{start:04}',dict(scope=scope,samples=[row.model_dump(mode='json') for row in batch]),
                lambda batch=batch:teacher.augment(batch,isolate_invalid_items=True),teacher,journal,LabelledSample,recovery=recovery)
            by_id={parent.id+'-aug':parent for parent in batch}
            rejected=receipt.get('item_quarantine',[])
            rejected_ids={row.get('sample_id') for row in rejected}
            accepted_ids={row.id for row in children}
            if (len(accepted_ids)!=len(children) or len(rejected_ids)!=len(rejected) or accepted_ids & rejected_ids
                    or accepted_ids | rejected_ids!=set(by_id)
                    or any(set(row)!={'sample_id','reason'} or row['reason']!='augmentation_item_invalid' for row in rejected)):
                raise ValueError('Augmentation child membership mismatch')
            quarantine.extend(rejected)
            for child in children:
                validate_augmentation(by_id[child.id],child)
                key=exact_text_key(child.text)
                if key in seen: quarantine.append(dict(sample_id=child.id,reason='duplicate_augmentation'));continue
                seen.add(key);accepted.append(child)
        content=''.join(row.model_dump_json()+'\n' for row in sorted(accepted,key=lambda row:row.id))
        status=dict(status='complete',base_manifest_hash=manifest['manifest_hash'],selected=len(parents),
            accepted=len(accepted),quarantine=quarantine,samples_hash=digest(content))
        _atomic(output/'samples.jsonl',content)
        _atomic(output/'status.json',json.dumps(status|dict(status_hash=digest(status)),ensure_ascii=False,indent=2))
        return output
    finally: lock.unlink(missing_ok=True)
