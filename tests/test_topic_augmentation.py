"""Only frozen training rows may be sent to the teacher for augmentation."""
import hashlib
import json
from types import SimpleNamespace
import pytest
from app.topics.augmentation import augment_training,select_train_parents
from app.topics.reviews import digest
from app.topics.taxonomy import default_taxonomy
from app.topics.types import LabelledSample


def dataset(tmp_path):
    root=tmp_path/'dataset';root.mkdir()
    partitions={name:[] for name in ('train','validation','test')}
    for i in range(16):
        name='train' if i<12 else 'validation' if i<14 else 'test'
        partitions[name].append(LabelledSample(id=f'item-{i}',text=f'请查看包裹在第{i+1}站的物流进度',labels=['物流'],
            group_id=f'family-{i}',origin='synthetic',source_question_ids=[],pilot=False))
    hashes={}
    for name,rows in partitions.items():
        content=''.join(row.model_dump_json()+'\n' for row in rows)
        (root/(name+'.jsonl')).write_text(content,encoding='utf-8')
        hashes[name]=hashlib.sha256(content.encode()).hexdigest()
    value=dict(schema_version=1,seed=20261021,taxonomy_hash=default_taxonomy().digest,
        splits={name:[row.id for row in rows] for name,rows in partitions.items()},file_hashes=hashes)
    (root/'manifest.json').write_text(json.dumps(value|dict(manifest_hash=digest(value))),encoding='utf-8')
    return root,partitions


async def test_only_a_quarter_of_unique_train_groups_reach_teacher_and_resume_is_free(tmp_path):
    root,rows=dataset(tmp_path)
    selected,manifest=select_train_parents(root)
    assert len(selected)==3 and {row.id for row in selected}<={row.id for row in rows['train']}
    calls=[]
    teacher=SimpleNamespace(last_receipt=None)
    async def controlled(batch,**options):
        calls.append([row.id for row in batch]);teacher.last_receipt={'attempt_id':'fixture'}
        return tuple(row.model_copy(update={'id':row.id+'-aug','text':'麻烦了,'+row.text}) for row in batch)
    teacher.augment=controlled
    output=tmp_path/'augmentation'
    await augment_training(root,teacher,output=output)
    await augment_training(root,teacher,output=output)
    assert len(calls)==1
    result=json.loads((output/'status.json').read_text(encoding='utf-8'))
    assert result['accepted']==3 and result['base_manifest_hash']==manifest['manifest_hash']
    assert len((output/'samples.jsonl').read_text(encoding='utf-8').splitlines())==3


async def test_manifest_or_split_tampering_stops_before_teacher(tmp_path):
    root,rows=dataset(tmp_path)
    (root/'test.jsonl').write_text('tampered',encoding='utf-8')
    with pytest.raises(ValueError): select_train_parents(root)


async def test_partial_augmentation_requires_accounting_for_every_missing_child(tmp_path):
    root,_=dataset(tmp_path);teacher=SimpleNamespace(last_receipt=None)
    async def controlled(batch,**options):
        teacher.last_receipt={'attempt_id':'fixture','item_quarantine':[dict(sample_id=batch[-1].id+'-aug',reason='augmentation_item_invalid')]}
        return tuple(row.model_copy(update={'id':row.id+'-aug','text':'麻烦了,'+row.text}) for row in batch[:-1])
    teacher.augment=controlled
    await augment_training(root,teacher,output=tmp_path/'aug')
    status=json.loads((tmp_path/'aug/status.json').read_text(encoding='utf-8'))
    assert status['selected']==3 and status['accepted']==2 and len(status['quarantine'])==1
