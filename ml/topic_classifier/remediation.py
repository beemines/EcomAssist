"""Freeze pinned v2 partitions without repurposing the exposed first test set."""
from collections import Counter
import json
from pathlib import Path
from app.topics.grouping import group_samples,GROUPING_VERSION
from app.topics.reviews import digest
from app.topics.types import LabelledSample
from app.topics.taxonomy import default_taxonomy
from app.topics.remediation import load_short,original_source,probe_semantic_family,filter_short
from ml.topic_classifier.data import load_dataset,SplitManifest,SEED,_content,_sha,write_dataset,freeze_augmentations


def pinned_manifest(source,new_train,new_test,tokenizer,*,audit_excluded=()):
    source=Path(source);original=load_dataset(source)
    old={name:tuple(LabelledSample.model_validate_json(line) for line in (source/(name+'.jsonl')).read_text(encoding='utf-8').splitlines())
        for name in ('train','validation','test')}
    new_train=tuple(new_train);new_test=tuple(new_test)
    all_rows=old['train']+old['validation']+old['test']+new_train+new_test
    if len({row.id for row in all_rows})!=len(all_rows):raise ValueError('New IDs overlap original partitions')
    assigned={row.id:name for name,rows in (('train',old['train']+new_train),('validation',old['validation']),('test',new_test)) for row in rows}
    old_ids={row.id for rows in old.values() for row in rows};new_ids={row.id for row in new_train+new_test}
    exposed={row.id for row in old['test']}
    grouped=group_samples(all_rows)
    if grouped.excluded:raise ValueError('Duplicate/conflicting/probe family cannot be silently dropped during freeze')
    for ids in grouped.groups.values():
        if len({assigned[i] for i in ids if i in assigned})>1 or set(ids)&exposed and set(ids)&set(assigned):
            raise ValueError('A family crosses pinned partitions or the exposed test baseline')
        if set(ids)&old_ids and set(ids)&new_ids:raise ValueError('New short family overlaps the original corpus')
    mapping={row.id:row for row in grouped.samples}
    if any(mapping[row.id]!=row for row in old['train']+old['validation']):raise ValueError('Original training/validation identity changed')
    rows={name:sorted((mapping[i] for i,value in assigned.items() if value==name),key=lambda row:row.id)
        for name in ('train','validation','test')}
    total=sum(map(len,rows.values()));taxonomy=default_taxonomy();counts={};origins={};group_ids={}
    for name,fraction in (('train',.8),('validation',.1),('test',.1)):
        current=rows[name]
        if not total or abs(len(current)/total-fraction)>.03:raise ValueError('Pinned split proportions exceed80/10/10 tolerance')
        if any(len(tokenizer(row.text,truncation=False,add_special_tokens=True)['input_ids'])>128 for row in current):
            raise ValueError('A pinned row exceeds128 tokens; do not truncate or discard it')
        groups={row.group_id for row in current};positive=Counter(label for row in current for label in row.labels)
        by_group={g:{label for row in current if row.group_id==g for label in row.labels} for g in groups}
        gp=Counter(label for labels in by_group.values() for label in labels)
        if name!='train' and any(min(positive[label],len(current)-positive[label],gp[label],len(groups)-gp[label])<10 for label in taxonomy.ordered_names):
            raise ValueError('Pinned holdout needs10 positive and negative independent groups for each class')
        counts[name]={label:dict(positive=positive[label],negative=len(current)-positive[label]) for label in taxonomy.ordered_names}
        origins[name]=dict(Counter(row.origin for row in current));group_ids[name]=sorted(groups)
    included=tuple(sorted((row for values in rows.values() for row in values),key=lambda row:row.id))
    fields=dict(schema_version=1,seed=SEED,taxonomy_hash=taxonomy.digest,grouping_version=GROUPING_VERSION,
        corpus_hash=digest([row.model_dump(mode='json') for row in included]),
        splits={name:[row.id for row in values] for name,values in rows.items()},group_ids=group_ids,
        label_counts=counts,origins=origins,pilot_ids=sorted(row.id for row in included if row.pilot),
        excluded=[dict(sample_id=i,reason='first_iteration_exposed_test_baseline') for i in sorted(exposed)]+list(audit_excluded),
        file_hashes={name:_sha(_content(values)) for name,values in rows.items()})
    manifest=SplitManifest(**fields,manifest_hash=digest(fields))
    if manifest.file_hashes['validation']!=original.file_hashes['validation']:raise ValueError('Validation bytes changed')
    return manifest,included


def freeze_iteration(source,iteration,base_dir):
    from transformers import AutoTokenizer
    source=Path(source);iteration=Path(iteration)
    original,blocked,pilot=original_source(source)
    train_status,train=load_short(iteration/'train-corpus');test_status,test=load_short(iteration/'test-corpus')
    lineage=json.loads((iteration/'lineage.json').read_text(encoding='utf-8'))
    if (lineage.get('base_manifest_hash')!=original['manifest_hash'] or lineage.get('pilot_receipt_hash')!=pilot.receipt_hash
            or lineage.get('original_source')!=str(source.resolve())
            or lineage.get('train_status_hash')!=train_status['status_hash'] or lineage.get('test_status_hash')!=test_status['status_hash']
            or lineage.get('original_test_policy')!='exposed_baseline_only_excluded_from_v2'):
        raise ValueError('Approved iteration lineage changed')
    tokenizer=AutoTokenizer.from_pretrained(base_dir,local_files_only=True,trust_remote_code=False)
    excluded=[dict(sample_id=row.id,reason='reserved_short_probe_semantic_family',partition=name)
        for name,rows in (('train',train),('test',test)) for row in rows if probe_semantic_family(row)]
    train=tuple(row for row in train if not probe_semantic_family(row))
    test=tuple(row for row in test if not probe_semantic_family(row))
    train,train_excluded=filter_short(train,blocked)
    test,test_excluded=filter_short(test,blocked+train)
    excluded+=list(train_excluded)+list(test_excluded)
    manifest,samples=pinned_manifest(source,train,test,tokenizer,audit_excluded=excluded)
    output=iteration/'dataset';write_dataset(samples,manifest,output)
    children=tuple(LabelledSample.model_validate_json(line) for line in (source/'train-augmentations.jsonl').read_text(encoding='utf-8').splitlines())
    audit=freeze_augmentations(samples,manifest,children,tokenizer,output)
    if audit['augmentation']['accepted']!=len(children):raise ValueError('Original training augmentation no longer passes; do not silently replace it')
    return dict(manifest_hash=manifest.manifest_hash,sizes=audit['sizes'],augmentation=audit['augmentation']['accepted'],
        old_validation_hash_unchanged=True,exposed_first_test_reused=False,pilot_receipt_hash=pilot.receipt_hash)
