"""Freeze the approved append-only training/validation update after actual human review."""
import json
from pathlib import Path
from app.topics.negation import source_context,protected_family
from app.topics.remediation import load_short,filter_short
from app.topics.review_submission import TopicReviewService
from app.topics.reviews import digest
from app.topics.types import LabelledSample
from ml.topic_classifier.data import load_dataset,write_dataset,freeze_augmentations
from ml.topic_classifier.remediation import pinned_manifest
from ml.topic_classifier.doctor import file_hash


def freeze_negation(source,iteration,base_dir):
    source=Path(source);iteration=Path(iteration)
    service=TopicReviewService(iteration/'train-review')
    receipt=service.state()
    if receipt is None:raise ValueError('Actual human training review is still pending')
    if service.pack().purpose!='pilot' or not receipt.samples:raise ValueError('Retained actual human training review required')
    train_status,raw_train=load_short(iteration/'train-corpus')
    if service.pack().snapshot_hash!=train_status['status_hash']:raise ValueError('Human review belongs to another training corpus')
    val_status,raw_val=load_short(iteration/'validation-corpus');test_status,raw_test=load_short(iteration/'test-corpus')
    scope,blocked=source_context(source)
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(base_dir,local_files_only=True,trust_remote_code=False)
    human_train=tuple(row.model_copy(update={'pilot':True}) for row in receipt.samples)
    if any(protected_family(row) for row in human_train):raise ValueError('A diagnostic family cannot enter training')
    train,excluded_train=filter_short(human_train,blocked)
    if excluded_train:raise ValueError('Reviewed training rows overlap a protected family; inspect before freeze')
    train_boundary={row.id:row for row in raw_train};train_boundary.update({row.id:row for row in train})
    validation,excluded_val=filter_short(raw_val,blocked+tuple(train_boundary.values()))
    validation=tuple(row for row in validation if not protected_family(row))
    if len(validation)!=len(raw_val):raise ValueError('A frozen validation family changed; inspect before freeze')
    test,excluded_test=filter_short(raw_test,blocked+tuple(train_boundary.values())+raw_val,max_chars=45)
    if len(test)!=len(raw_test) or any(protected_family(row) for row in test):raise ValueError('A frozen independent test family changed')
    manifest,samples=pinned_manifest(source,train,test,tokenizer,new_validation=validation,
        audit_excluded=[dict(sample_id=i,reason='human_excluded_training') for i in receipt.excluded_ids])
    output=iteration/'dataset'
    overlay=json.loads((source/'augmentation.json').read_text(encoding='utf-8'))
    if overlay['base_manifest_hash']!=scope['source_manifest_hash'] or overlay['content_hash']!=file_hash(source/'train-augmentations.jsonl'):
        raise ValueError('Original augmentation changed')
    children=tuple(LabelledSample.model_validate_json(line) for line in (source/'train-augmentations.jsonl').read_text(encoding='utf-8').splitlines())
    write_dataset(samples,manifest,output)
    audit=freeze_augmentations(samples,manifest,children,tokenizer,output)
    if audit['augmentation']['accepted']!=len(children):raise ValueError('Do not silently replace original augmentation')
    from ml.topic_classifier.artifacts import freeze_json
    lineage=scope|dict(train_status_hash=train_status['status_hash'],validation_status_hash=val_status['status_hash'],
        test_status_hash=test_status['status_hash'],training_review_receipt_hash=receipt.receipt_hash,
        retained_reviewed_training=len(train),validation_appended=len(validation),old_validation_members_retained=True,
        source_test_policy='exposed_regression_only',manifest_hash=manifest.manifest_hash)
    freeze_json(iteration/'lineage.json',lineage)
    (iteration/'corpus').mkdir(exist_ok=True)
    freeze_json(iteration/'corpus/run.json',dict(review_receipt_hash=receipt.receipt_hash,lineage_hash=digest(lineage)))
    return dict(manifest_hash=manifest.manifest_hash,sizes=audit['sizes'],augmentation=audit['augmentation']['accepted'],
        new_training_human_receipt=receipt.receipt_hash,old_validation_members_retained=True,validation_appended=len(validation))
