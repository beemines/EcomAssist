"""Recovery and scene contracts catch the actual missing signal before any training."""
import json
from pathlib import Path
import pytest
from app.topics.reviews import digest
from app.topics.types import LabelledSample
from app.topics.taxonomy import default_taxonomy


def sample(i,text,labels):
    return LabelledSample(id=i,text=text,labels=labels,origin='synthetic',group_id=i,source_question_ids=[],pilot=False)


def record(path,data,kind):
    path.parent.mkdir(parents=True,exist_ok=True)
    value=dict(state='complete',intent_hash='a'*64,data=data,receipt=dict(attempt_id=kind+'-fixture',
        payload_hash='b'*64,prompt_hash='c'*64,prompt_version='fixture',model='glm-5.3-flash',request_id='fixture'))
    path.write_text(json.dumps(value|{'record_hash':digest(value)},ensure_ascii=False),encoding='utf-8')


def cached(root,*,text='鞋挤得脚疼,换双宽点的',label_text=None,labels=('退换货','尺码'),id='syn-unused'):
    gen=dict(id=id,text=text,family_id='family-'+id,requested_labels=['商品信息'])
    label=dict(id=id,cleaned_text=label_text or text,labels=list(labels),notes='unit synthetic fixture only')
    record(root/'corpus/journal/generate-0000.json',[gen],'generate')
    record(root/'corpus/journal/label-0000.json',[label],'label')


def test_recovery_requires_complete_matching_inputs_but_does_not_discard_a_valid_label_plan_disagreement(tmp_path):
    from app.topics.coverage_repair import recover_candidates
    cached(tmp_path)
    rows,proof,excluded=recover_candidates(tmp_path)
    assert len(rows)==1 and rows[0].labels==('退换货','尺码') and rows[0].text=='鞋挤得脚疼,换双宽点的'
    assert rows[0].group_id=='family-syn-unused'
    assert proof[rows[0].id]['generate_file'].endswith('generate-0000.json')
    assert len(proof[rows[0].id]['label_sha256'])==64 and not excluded


@pytest.mark.parametrize('kind',['changed_text','missing_generate','already_used','tampered_record'])
def test_recovery_refuses_unproven_or_previously_exposed_rows(tmp_path,kind):
    from app.topics.coverage_repair import recover_candidates
    cached(tmp_path,label_text='另一个完全不同的问题' if kind=='changed_text' else None)
    if kind=='missing_generate':(tmp_path/'corpus/journal/generate-0000.json').unlink()
    if kind=='already_used':
        p=tmp_path/'negation-v4/dataset/train.jsonl';p.parent.mkdir(parents=True)
        p.write_text(sample('syn-unused','鞋挤得脚疼,换双宽点的',['退换货','尺码']).model_dump_json()+'\n',encoding='utf-8')
    if kind=='tampered_record':
        p=tmp_path/'corpus/journal/label-0000.json';value=json.loads(p.read_text(encoding='utf-8'));value['data'][0]['labels']=['其他'];p.write_text(json.dumps(value),encoding='utf-8')
        with pytest.raises(ValueError,match='checkpoint'):recover_candidates(tmp_path)
    else:
        rows,proof,excluded=recover_candidates(tmp_path)
        assert not rows and not proof and excluded


@pytest.mark.parametrize('text,labels,scene,protected',[
    ('鞋挤得脚疼,换双宽点的',['退换货','尺码'],'A',False),
    ('不退了,给我换双宽点的',['退换货','尺码'],'A',False),
    ('别办退货,先看衣长多少',['尺码'],'B',False),
    ('换货先别办,我肩宽选哪款',['尺码'],'B',False),
    ('买大了想退',['退换货','尺码'],'A',True),
    ('不退货,只问尺码',['尺码'],'B',True),
    ('不退了,给我换个码',['退换货','尺码'],None,False)])
def test_protection_is_for_known_probe_families_not_an_entire_business_behavior(text,labels,scene,protected):
    from app.topics.coverage_repair import scene_of,protected_probe
    row=sample('synthetic',text,labels)
    assert scene_of(row)==scene
    assert bool(protected_probe(row)) is protected


def test_training_and_validation_coverage_gate_reject_the_actual_zero_pair_regression():
    from app.topics.coverage_repair import audit_scene_coverage
    rows=[sample(str(i),'尺码是多少',['尺码']) for i in range(64)]
    with pytest.raises(ValueError,match='scene'):audit_scene_coverage(rows,partition='train')
    with pytest.raises(ValueError,match='scene'):audit_scene_coverage(rows[:32],partition='validation')


def test_scene_plans_explicitly_request_the_missing_positive_and_negated_requests():
    from app.topics.coverage_repair import scene_plan
    a=scene_plan(8,{},0,partition='train-a')
    b=scene_plan(8,{},0,partition='validation-b')
    assert all(labels==('退换货','尺码') for labels in a.scenario_labels)
    assert all(labels==('尺码',) for labels in b.scenario_labels)
    assert all('取消' in hint and '退换' in hint for hint in b.scenario_hints)
    assert a.taxonomy_hash==b.taxonomy_hash==default_taxonomy().digest
    with pytest.raises(ValueError):scene_plan(8,{},0,partition='not-a-known-stage')


def test_cached_text_family_in_old_dataset_is_not_recovered_under_a_new_id(tmp_path):
    from app.topics.coverage_repair import recover_candidates
    cached(tmp_path)
    p=tmp_path/'dataset/train.jsonl';p.parent.mkdir()
    p.write_text(sample('old-id','鞋挤得脚疼,换双宽点的',['退换货','尺码']).model_dump_json()+'\n',encoding='utf-8')
    rows,proof,excluded=recover_candidates(tmp_path)
    assert not rows and not proof and any(x['reason']=='previously_exposed_text_family' for x in excluded)


def test_reviewed_scene_labels_are_rechecked_after_human_changes_or_exclusions():
    from app.topics.coverage_repair import audit_scene_coverage
    a=[sample('a'+str(i),'脚挤'+str(i)+'想换宽点的',['退换货','尺码']) for i in range(32)]
    b=[sample('b'+str(i),'别办退货先问衣长'+str(i),['尺码']) for i in range(32)]
    assert audit_scene_coverage(a+b,partition='train')==dict(groups=64,scene_a=32,scene_b=32,short=64)
    b[0]=b[0].model_copy(update={'labels':('退换货','尺码')})
    with pytest.raises(ValueError,match='scene'):audit_scene_coverage(a+b,partition='train')
    with pytest.raises(ValueError,match='scene'):audit_scene_coverage(a+b[1:],partition='train')


@pytest.mark.asyncio
async def test_verified_cache_seed_finishes_without_new_teacher_calls_and_is_scope_bound(tmp_path):
    from app.topics.remediation import collect_short,load_short
    from app.topics.coverage_repair import scene_plan,protected_probe
    class NoNetworkTeacher:
        async def generate(self,*a,**k):pytest.fail('cache-complete scope called a teacher')
        async def label(self,*a,**k):pytest.fail('cache-complete scope called a teacher')
    seeds=[sample('cache','鞋挤脚想换宽点的',['退换货','尺码'])]
    kwargs=dict(output=tmp_path/'part',blocked=(),scope={'source':'fixture'},partition='train-a',target=1,
        minima={'退换货':1,'尺码':1},planner=scene_plan,row_guard=protected_probe,profile={'version':'fixture-cache'},seeds=seeds)
    await collect_short(NoNetworkTeacher(),**kwargs)
    status,rows=load_short(tmp_path/'part')
    assert status['status']=='complete' and len(rows)==1 and rows[0].text=='鞋挤脚想换宽点的'
    with pytest.raises(ValueError,match='scope'):
        await collect_short(NoNetworkTeacher(),**(kwargs|{'seeds':[seeds[0].model_copy(update={'text':'另外一条新句子'})]}))
    with pytest.raises(ValueError):await collect_short(NoNetworkTeacher(),**(kwargs|{'output':tmp_path/'unbound','profile':None,'planner':None,'row_guard':None}))
