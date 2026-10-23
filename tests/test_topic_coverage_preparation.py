"""Preparation leaves space for missing classes and never invents a human review."""
from collections import Counter
import json
import pytest
from app.topics.reviews import digest
from tests.test_topic_coverage_repair import sample


def complete_part(root,rows):
    root.mkdir(parents=True)
    content=''.join(r.model_dump_json()+'\n' for r in rows)
    (root/'samples.jsonl').write_text(content,encoding='utf-8')
    fields=dict(status='complete',samples_hash=digest(content))
    (root/'status.json').write_text(json.dumps(fields|{'status_hash':digest(fields)}),encoding='utf-8')


def test_cache_selection_reserves_slots_for_unavailable_classes_and_keeps_old_families_out():
    from app.topics.coverage_preparation import select_cache
    rows=[sample('c'+str(i),'盒窄'+str(i)+'想换宽点',['退换货','尺码']) for i in range(8)]
    used=sample('old','盒窄0想换宽点',['退换货','尺码'])
    chosen=select_cache(rows,[used],stage='test-general-mixed',target=4,max_chars=45,
        minima={'退换货':1,'尺码':1,'其他':2},reserve_missing=True)
    assert len(chosen)==2 and not any(r.id=='c0' for r in chosen)
    assert sum('其他' in r.labels for r in chosen)==0


def test_merge_publishes_only_complete_actual_a_b_and_never_writes_a_human_receipt(tmp_path):
    from app.topics.coverage_preparation import merge_partition
    a=[sample('a'+str(i),'挤脚'+str(i)+'换宽点',['退换货','尺码']) for i in range(32)]
    b=[sample('b'+str(i),'不退问长'+str(i),['尺码']) for i in range(32)]
    complete_part(tmp_path/'parts/train-a',a);complete_part(tmp_path/'parts/train-b',b)
    result=merge_partition(tmp_path,'train',[tmp_path/'parts/train-a',tmp_path/'parts/train-b'],scope={'fixture':'1'})
    assert result['rows']==64 and result['scene_a']==32 and result['scene_b']==32
    pack=json.loads((tmp_path/'train-review/pack.json').read_text(encoding='utf-8'))
    assert len(pack['samples'])==64 and pack['purpose']=='pilot'
    assert not (tmp_path/'train-review/review-receipt.json').exists()
    assert merge_partition(tmp_path,'train',[tmp_path/'parts/train-a',tmp_path/'parts/train-b'],scope={'fixture':'1'})==result


def test_missing_scene_prevents_publish_before_dataset_or_review(tmp_path):
    from app.topics.coverage_preparation import merge_partition
    a=[sample('a'+str(i),'挤脚'+str(i)+'换宽点',['退换货','尺码']) for i in range(64)]
    complete_part(tmp_path/'parts/train-a',a)
    with pytest.raises(ValueError,match='scene'):merge_partition(tmp_path,'train',[tmp_path/'parts/train-a'],scope={})
    assert not (tmp_path/'train-corpus').exists() and not (tmp_path/'train-review').exists()


def test_cli_preview_never_constructs_a_teacher(tmp_path,monkeypatch,capsys):
    from app.topics import data_cli,teacher,budget,coverage_preparation
    from tests.test_topic_coverage_budget import previous,amend
    from tests.test_topic_budget_amendment import prepared
    path,_=prepared(tmp_path);previous(path);amend(path)
    monkeypatch.setattr(budget,'BUDGET_PATH',path)
    monkeypatch.setattr(coverage_preparation,'inspect_source',lambda source:dict(source_manifest='a'*64,qualified=3,scene_a=2,scene_b=0))
    monkeypatch.setattr(teacher,'configured_teacher',lambda *a,**k:pytest.fail('preview constructed a paid teacher'))
    monkeypatch.setattr('sys.argv',['data','prepare-coverage','--source','unused','--output',str(tmp_path/'out')])
    data_cli.main();preview=json.loads(capsys.readouterr().out)
    assert preview['mode']=='preview' and preview['budget']['attempt_limit']==560
    assert not (tmp_path/'out').exists()


@pytest.mark.asyncio
async def test_full_train_preparation_binds_journals_and_second_execution_never_calls_teacher(tmp_path,monkeypatch):
    from app.topics import coverage_preparation as module
    from app.topics.teacher import GeneratedQuestion,Prelabel
    monkeypatch.setattr(module,'source_context',lambda source:(tmp_path,{'source_manifest':'a'*64}))
    monkeypatch.setattr(module,'recover_candidates',lambda base:((),{},()))
    monkeypatch.setattr(module,'old_rows',lambda base:())
    class SyntheticHTTPBoundary:
        def __init__(self):self.last_receipt=None;self.counter=0;self.generated={};self.calls=0;self.forbid=False
        async def generate(self,plan,**kwargs):
            assert not self.forbid
            self.calls+=1;rows=[]
            for labels in plan.scenario_labels:
                n=self.counter;self.counter+=1;identifier='syn-fixture-'+str(n)
                text=('鞋挤'+str(n)+'换宽点') if len(labels)==2 else ('不退问长'+str(n))
                row=GeneratedQuestion(id=identifier,text=text,family_id='fam-'+identifier,requested_labels=labels)
                rows.append(row);self.generated[identifier]=row
            self.last_receipt={'attempt_id':'generate-fixture-'+str(self.calls),'model':'glm-5.3-flash'}
            return tuple(rows)
        async def label(self,cleaned,**kwargs):
            assert not self.forbid
            self.calls+=1;self.last_receipt={'attempt_id':'label-fixture-'+str(self.calls),'model':'glm-5.3-flash'}
            return tuple(Prelabel(id=r.sample_id,cleaned_text=r.text,labels=self.generated[r.sample_id].requested_labels,notes='fixture') for r in cleaned)
    teacher=SyntheticHTTPBoundary();output=tmp_path/'coverage-v5'
    first=await module.prepare_coverage(tmp_path/'source',teacher,output=output,partition='train')
    assert first['rows']==64 and (first['scene_a'],first['scene_b'])==(32,32)
    assert len(json.loads((output/'train-review/pack.json').read_text(encoding='utf-8'))['teacher_receipts'])==9
    calls=teacher.calls;teacher.forbid=True
    assert await module.prepare_coverage(tmp_path/'source',teacher,output=output,partition='train')==first
    assert teacher.calls==calls and not (output/'train-review/review-receipt.json').exists()
