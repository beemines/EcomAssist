"""A resumed data scope must not hide its stop or rewrite prior evidence."""
import json
import pytest
from app.topics.reviews import digest
from tests.test_topic_remediation import sample


def test_partial_seed_load_checks_actual_samples_and_does_not_rewrite_status(tmp_path):
    from app.topics.coverage_recovery import partial_seeds
    row=sample('b','先别换,问问袖长',('尺码',));content=row.model_dump_json()+'\n'
    (tmp_path/'samples.jsonl').write_text(content,encoding='utf-8')
    fields=dict(status='budget_paused',samples_hash=digest(content),independent_groups=1)
    (tmp_path/'status.json').write_text(json.dumps(fields|dict(status_hash=digest(fields))),encoding='utf-8')
    before=(tmp_path/'status.json').read_bytes()
    assert partial_seeds(tmp_path)==(row,)
    assert (tmp_path/'status.json').read_bytes()==before
    (tmp_path/'samples.jsonl').write_text(content+'\n',encoding='utf-8')
    with pytest.raises(ValueError):partial_seeds(tmp_path)


def test_b_plan_is_short_and_does_not_suggest_reopening_cancelled_requests():
    from app.topics.coverage_recovery import cancellation_plan
    plan=cancellation_plan(16,{},0,partition='test-b')
    assert len(plan.scenario_labels)==16 and set(plan.scenario_labels)=={('尺码',)}
    assert all('最多16字' in hint and '实际只问' in hint and '风格' not in hint for hint in plan.scenario_hints)


async def test_stopped_recovery_returns_actual_stage_without_merging_or_later_calls(tmp_path,monkeypatch):
    from app.topics import coverage_recovery as module
    # Source validation is separate; exercise real stop propagation at the collector boundary.
    class Paused:
        async def generate(self,*a,**k):pytest.fail('Stopped preparation called teacher')
    async def stopped(*args,**kwargs):
        path=kwargs['output'];path.mkdir(parents=True)
        fields=dict(status='diagnosis_required',independent_groups=14,samples_hash=digest(''))
        (path/'samples.jsonl').write_text('',encoding='utf-8')
        (path/'status.json').write_text(json.dumps(fields|dict(status_hash=digest(fields))),encoding='utf-8')
    monkeypatch.setattr(module,'collect_short',stopped)
    result=await module.collect_part(Paused(),path=tmp_path/'part',scope={},blocked=(),seeds=(),stage='validation-b',
        target=16,max_chars=16,minima={'尺码':16},multi_fraction=0,baseline={},scene='B',provenance={})
    assert result['status']=='diagnosis_required' and result['groups']==14


def test_recovery_cli_preview_is_free_and_selects_the_new_600_scope(tmp_path,monkeypatch,capsys):
    from app.topics import data_cli,budget,teacher,coverage_recovery
    from tests.test_topic_budget_amendment import prepared
    from tests.test_topic_coverage_budget import previous,amend
    from tests.test_topic_recovery_budget import recover
    path,_=prepared(tmp_path);previous(path);amend(path);recover(path)
    monkeypatch.setattr(budget,'BUDGET_PATH',path)
    monkeypatch.setattr(coverage_recovery,'preview_recovery',lambda *a,**k:dict(mode='preview',teacher_calls=0),raising=False)
    monkeypatch.setattr(teacher,'configured_teacher',lambda *a,**k:pytest.fail('Preview created paid teacher'))
    monkeypatch.setattr('sys.argv',['data','recover-coverage','--source','unused','--output',str(tmp_path/'out')])
    data_cli.main();value=json.loads(capsys.readouterr().out)
    assert value['teacher_calls']==0 and value['budget']['attempt_limit']==600
    assert not (tmp_path/'out').exists()


async def test_complete_validation_recovery_keeps_previous_members_and_reuses_completed_http(tmp_path,monkeypatch):
    from app.topics import coverage_recovery as module
    from app.topics.reviews import make_review_pack
    from app.topics.review_submission import TopicReviewService,ReviewSubmission
    from app.topics.teacher import GeneratedQuestion,Prelabel
    from tests.test_topic_review_submission import payload
    from tests.test_topic_coverage_preparation import complete_part
    root=tmp_path/'coverage-v5';scope={'source_manifest':'a'*64}
    monkeypatch.setattr(module,'source_context',lambda source:(tmp_path,scope))
    monkeypatch.setattr(module,'old_rows',lambda base:())
    train_a=[sample('ta'+str(i),'挤脚'+str(i)+'换宽点',('退换货','尺码')) for i in range(32)]
    train_b=[sample('tb'+str(i),'不用退问厚'+str(i),('尺码',)) for i in range(32)]
    for name,rows in (('train-a',train_a),('train-b',train_b)):
        complete_part(root/'parts'/name,rows)
    train=train_a+train_b;complete_part(root/'train-corpus',train)
    status=json.loads((root/'train-corpus/status.json').read_text(encoding='utf-8'))
    pack=make_review_pack(train,snapshot_hash=status['status_hash'],teacher_receipts=(),purpose='pilot')
    review=root/'train-review';review.mkdir();(review/'pack.json').write_text(pack.model_dump_json(),encoding='utf-8')
    TopicReviewService(review).save(ReviewSubmission.model_validate(payload(pack)))
    a=[sample('va'+str(i),'罩太窄'+str(i)+'换',('退换货','尺码')) for i in range(16)]
    b=[sample('vb'+str(i),'不退问长'+str(i),('尺码',)) for i in range(14)]
    complete_part(root/'parts/validation-a',a);complete_part(root/'parts/validation-b',b)
    b_status=root/'parts/validation-b/status.json';value=json.loads(b_status.read_text(encoding='utf-8'))
    value.pop('status_hash');value['status']='budget_paused';b_status.write_text(json.dumps(value|dict(status_hash=digest(value))),encoding='utf-8')
    before=b_status.read_bytes()
    (root/'cache-snapshot.json').write_text(json.dumps(dict(source=scope,samples=[])),encoding='utf-8')
    class Boundary:
        last_receipt=None
        def __init__(self):self.calls=0;self.generated={}
        async def generate(self,plan,**kwargs):
            assert plan.count==16;self.calls+=1;self.last_receipt={'attempt_id':'gen-fixture','model':'glm-5.3-flash'}
            rows=tuple(GeneratedQuestion(id='fresh'+str(i),text='不换问宽'+str(i),family_id='f'+str(i),requested_labels=['尺码']) for i in range(16))
            self.generated={r.id:r for r in rows};return rows
        async def label(self,cleaned,**kwargs):
            self.calls+=1;self.last_receipt={'attempt_id':'label-fixture','model':'glm-5.3-flash'}
            return tuple(Prelabel(id=r.sample_id,cleaned_text=r.text,labels=['尺码'],notes='') for r in cleaned)
    teacher=Boundary()
    result=await module.prepare_recovery(tmp_path/'source',teacher,output=root,partition='validation')
    assert result['rows']==32 and result['scene_a']==result['scene_b']==16
    _,rows=module.load_short(root/'validation-corpus')
    assert {r.id for r in a+b}<={r.id for r in rows}
    assert b_status.read_bytes()==before and teacher.calls==2
    assert await module.prepare_recovery(tmp_path/'source',teacher,output=root,partition='validation')==result
    assert teacher.calls==2
