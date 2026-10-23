"""Human-first frozen data and training contracts for the approved coverage repair."""
import hashlib
import json
from pathlib import Path
import re
from app.topics.coverage_repair import VERSION,audit_scene_coverage,old_rows,scene_of
from app.topics.coverage_preparation import source_context,freeze_json
from app.topics.remediation import load_short,filter_short
from app.topics.review_submission import TopicReviewService
from app.topics.reviews import digest
from app.topics.types import LabelledSample
from ml.topic_classifier.data import write_dataset,freeze_augmentations
from ml.topic_classifier.remediation import pinned_manifest
from ml.topic_classifier.doctor import file_hash


def read_contract(dataset):
    dataset=Path(dataset);path=dataset/'coverage.json'
    if not path.is_file() or path.is_symlink():raise ValueError('A frozen coverage contract is required')
    content=path.read_bytes();value=json.loads(content)
    keys={'version','manifest_hash','training_status_hash','review_receipt_hash','new_train_ids',
        'new_validation_ids','test_scene_hash','contract_hash'}
    if (type(value) is not dict or set(value)!=keys or value['version']!=VERSION
            or value['contract_hash']!=digest({k:v for k,v in value.items() if k!='contract_hash'})):
        raise ValueError('Frozen coverage contract changed')
    for key in ('manifest_hash','training_status_hash','review_receipt_hash','test_scene_hash'):
        if type(value[key]) is not str or not re.fullmatch('[0-9a-f]{64}',value[key]):raise ValueError('Invalid coverage identity')
    for key,count in (('new_train_ids',64),('new_validation_ids',32)):
        ids=value[key]
        if type(ids) is not list or len(ids)!=count or any(type(i) is not str for i in ids) or len(set(ids))!=count:
            raise ValueError('Coverage scene memberships changed')
    service=TopicReviewService(dataset.parent/'train-review');receipt=service.state()
    if (receipt is None or receipt.receipt_hash!=value['review_receipt_hash']
            or service.pack().purpose!='pilot' or service.pack().snapshot_hash!=value['training_status_hash']
            or {r.id for r in receipt.samples}!=set(value['new_train_ids'])):
        raise ValueError('Actual human coverage training review changed')
    for proof in service.pack().teacher_receipts:
        if 'file' not in proof or 'sha256' not in proof:raise ValueError('Incomplete coverage teacher provenance')
        source=dataset.parent/proof['file']
        if (source.is_symlink() or not source.resolve().is_relative_to(dataset.parent.resolve())
                or file_hash(source)!=proof['sha256']):raise ValueError('Frozen coverage teacher provenance changed')
    return value,hashlib.sha256(content).hexdigest()


def validate_training_contract(dataset,manifest_hash,train,validation):
    contract,sha=read_contract(dataset)
    if contract['manifest_hash']!=manifest_hash:raise ValueError('Coverage contract belongs to another dataset')
    by_train={r.id:r for r in train};by_val={r.id:r for r in validation}
    if not set(contract['new_train_ids'])<=set(by_train) or not set(contract['new_validation_ids'])<=set(by_val):
        raise ValueError('Required coverage rows are missing')
    new_train=tuple(by_train[i] for i in contract['new_train_ids']);new_val=tuple(by_val[i] for i in contract['new_validation_ids'])
    human=TopicReviewService(Path(dataset).parent/'train-review').state()
    actual={r.id:(r.text,r.labels,r.origin) for r in human.samples}
    if any(actual[r.id]!=(r.text,r.labels,r.origin) for r in new_train):raise ValueError('Human coverage labels or text changed')
    audit_scene_coverage(new_train,partition='train');audit_scene_coverage(new_val,partition='validation')
    return sha


def freeze_coverage(source,iteration,base_dir):
    source=Path(source).resolve();iteration=Path(iteration).resolve()
    service=TopicReviewService(iteration/'train-review');receipt=service.state()
    if receipt is None:raise ValueError('Actual human coverage training review is still pending')
    train_status,raw_train=load_short(iteration/'train-corpus')
    if service.pack().purpose!='pilot' or service.pack().snapshot_hash!=train_status['status_hash']:
        raise ValueError('Actual human review belongs to another coverage corpus')
    human_train=tuple(r.model_copy(update={'pilot':True}) for r in receipt.samples)
    audit_scene_coverage(human_train,partition='train')
    val_status,validation=load_short(iteration/'validation-corpus');test_status,test=load_short(iteration/'test-corpus')
    audit_scene_coverage(validation,partition='validation');audit_scene_coverage(test,partition='test')
    base,scope=source_context(source)
    if iteration!=(base/'coverage-v5').resolve():raise ValueError('Use the separate approved coverage directory')
    snapshot=json.loads((iteration/'cache-snapshot.json').read_text(encoding='utf-8'))
    if snapshot['source']!=scope:raise ValueError('Frozen cache source changed')
    statuses={'train':train_status,'validation':val_status,'test':test_status}
    raw_parts={};part_records=[]
    for partition,status in statuses.items():
        expected=scope|dict(cache_snapshot_hash=digest(snapshot),partition=partition)
        for prior in {'train':(), 'validation':('train',), 'test':('train','validation')}[partition]:
            expected[prior+'_status_hash']=statuses[prior]['status_hash']
        if status['scope_hash']!=digest(expected):raise ValueError('Coverage partition source changed')
        for item in status['parts']:
            path=iteration/'parts'/item['stage'];actual,rows=load_short(path)
            run=json.loads((path/'run.json').read_text(encoding='utf-8'))
            if actual['status_hash']!=item['status_hash'] or actual['scope_hash']!=digest(run) or run['source']!=expected:
                raise ValueError('Coverage scene part identity changed')
            raw_parts[item['stage']]=rows;part_records.append(item)
    blocked={r.id:r for r in old_rows(base)}
    train,excluded=filter_short(human_train,tuple(blocked.values()))
    if excluded:raise ValueError('Reviewed coverage training overlaps a protected old family')
    for stage,rows in raw_parts.items():
        if stage.startswith('train-'):blocked.update({r.id:r for r in rows})
    blocked.update({r.id:r for r in train})
    validation,val_excluded=filter_short(validation,tuple(blocked.values()))
    if val_excluded:raise ValueError('New coverage validation overlaps a protected family')
    for stage,rows in raw_parts.items():
        if stage.startswith('validation-'):blocked.update({r.id:r for r in rows})
    blocked.update({r.id:r for r in validation})
    test,test_excluded=filter_short(test,tuple(blocked.values()),max_chars=45)
    if test_excluded:raise ValueError('Independent coverage test overlaps a protected family')
    audit_scene_coverage(train,partition='train');audit_scene_coverage(validation,partition='validation');audit_scene_coverage(test,partition='test')
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(base_dir,local_files_only=True,trust_remote_code=False)
    manifest,samples=pinned_manifest(source,train,test,tokenizer,new_validation=validation)
    overlay=json.loads((source/'augmentation.json').read_text(encoding='utf-8'))
    if overlay['base_manifest_hash']!=scope['source_manifest'] or overlay['content_hash']!=file_hash(source/'train-augmentations.jsonl'):
        raise ValueError('Original coverage augmentation source changed')
    children=tuple(LabelledSample.model_validate_json(line) for line in (source/'train-augmentations.jsonl').read_text(encoding='utf-8').splitlines())
    output=iteration/'dataset';write_dataset(samples,manifest,output)
    audit=freeze_augmentations(samples,manifest,children,tokenizer,output)
    if audit['augmentation']['accepted']!=len(children):raise ValueError('Do not silently drop original training augmentation')
    scenes={s:sorted(r.id for r in test if scene_of(r)==s) for s in ('A','B')}
    freeze_json(output/'test-scenes.json',scenes)
    fields=dict(version=VERSION,manifest_hash=manifest.manifest_hash,training_status_hash=train_status['status_hash'],
        review_receipt_hash=receipt.receipt_hash,new_train_ids=sorted(r.id for r in train),
        new_validation_ids=sorted(r.id for r in validation),test_scene_hash=file_hash(output/'test-scenes.json'))
    freeze_json(output/'coverage.json',fields|dict(contract_hash=digest(fields)))
    lineage=scope|dict(manifest_hash=manifest.manifest_hash,training_human_receipt_hash=receipt.receipt_hash,
        partition_statuses={k:v['status_hash'] for k,v in statuses.items()},parts=part_records,
        coverage_contract_hash=file_hash(output/'coverage.json'),all_previous_tests_excluded=True,
        old_train_and_validation_retained=True,original_augmentations_retained=len(children))
    freeze_json(iteration/'lineage.json',lineage)
    freeze_json(iteration/'corpus/run.json',dict(review_receipt_hash=receipt.receipt_hash,lineage_hash=digest(lineage)))
    validate_training_contract(output,manifest.manifest_hash,tuple(r for r in samples if r.id in manifest.splits['train']),
        tuple(r for r in samples if r.id in manifest.splits['validation']))
    return dict(manifest_hash=manifest.manifest_hash,sizes=audit['sizes'],augmentation=len(children),human_receipt=receipt.receipt_hash,
        training_scenes=audit_scene_coverage(train,partition='train'),validation_scenes=audit_scene_coverage(validation,partition='validation'))
