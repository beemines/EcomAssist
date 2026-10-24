"""Bounded candidate batches and a real no-progress stop, without model calls."""
from collections import Counter
import json
import pytest
from app.topics.teacher import GeneratedQuestion,Prelabel
from app.topics.remediation import collect_short,load_short
from app.topics.reviews import digest
from app.topics.taxonomy import default_taxonomy
from tests.test_topic_remediation import sample


def test_exact_selection_preserves_rare_labels_and_all_overflow_families():
    from app.topics.coverage_selection import select_exact
    rows=[sample('common'+str(i),'查包裹'+str(i)) for i in range(20)]
    rows += [sample('rare'+str(i),'能否微信付款'+str(i),('支付',)) for i in range(3)]
    chosen,candidates=select_exact(rows,target=5,minima={'支付':3},multi_fraction=0)
    assert len(chosen)==5 and sum('支付' in r.labels for r in chosen)==3
    assert len(candidates)==23 and select_exact(reversed(rows),target=5,minima={'支付':3},multi_fraction=0)==(chosen,candidates)
    with pytest.raises(ValueError):select_exact(rows,target=2,minima={'支付':3},multi_fraction=0)


def planner(count,positives,batch,*,partition):
    from app.topics.teacher import GenerationPlan
    return GenerationPlan(count=count,scenario_labels=[('尺码',)]*count,taxonomy_hash=default_taxonomy().digest)


PROFILE=dict(version='bounded-recovery-v1',max_chars=16,generation_profile='short',batch_floor=16,
    no_gain_limit=2,exact_groups=True)


class Boundary:
    last_receipt=None
    def __init__(self,valid):self.valid=valid;self.calls=[];self.generated={}
    async def generate(self,plan,**kwargs):
        self.calls.append(('generate',plan.count));rows=[]
        for i in range(plan.count):
            identifier='new-'+str(len(self.calls))+'-'+str(i)
            text=('不退问长'+str(i)) if self.valid else '这一条明显超出了十六个字所以必须留在隔离区不能使用'+str(i)
            row=GeneratedQuestion(id=identifier,text=text,family_id=identifier,requested_labels=['尺码'])
            rows.append(row);self.generated[identifier]=row
        self.last_receipt=dict(attempt_id='fixture-'+str(len(self.calls)))
        return tuple(rows)
    async def label(self,cleaned,**kwargs):
        self.calls.append(('label',len(cleaned)));self.last_receipt=dict(attempt_id='fixture-'+str(len(self.calls)))
        return tuple(Prelabel(id=r.sample_id,cleaned_text=r.text,labels=['尺码'],notes='') for r in cleaned)


async def test_tail_deficit_one_requests_a_batch_and_publishes_exact_quota_with_candidate_hash(tmp_path):
    teacher=Boundary(True);seed=sample('seed','不换问宽窄',('尺码',))
    await collect_short(teacher,output=tmp_path,blocked=(),scope={},partition='fixture',target=2,
        minima={'尺码':2},multi_fraction=0,planner=planner,row_guard=lambda r:None,profile=PROFILE,seeds=[seed])
    status,rows=load_short(tmp_path)
    assert teacher.calls==[('generate',16),('label',16)] and len(rows)==2
    content=(tmp_path/'qualified-candidates.jsonl').read_text(encoding='utf-8')
    assert status['candidate_samples_hash']==digest(content) and len(content.splitlines())==17
    (tmp_path/'qualified-candidates.jsonl').write_text(content+'\n',encoding='utf-8')
    with pytest.raises(ValueError,match='candidate'):load_short(tmp_path)
    (tmp_path/'qualified-candidates.jsonl').write_text(content,encoding='utf-8')
    teacher.valid=False
    await collect_short(teacher,output=tmp_path,blocked=(),scope={},partition='fixture',target=2,
        minima={'尺码':2},multi_fraction=0,planner=planner,row_guard=lambda r:None,profile=PROFILE,seeds=[seed])
    assert len(teacher.calls)==2


async def test_two_batches_without_gain_stop_without_consuming_remaining_stage_budget(tmp_path):
    teacher=Boundary(False)
    await collect_short(teacher,output=tmp_path,blocked=(),scope={},partition='fixture',target=2,
        minima={'尺码':2},multi_fraction=0,planner=planner,row_guard=lambda r:None,profile=PROFILE)
    status=json.loads((tmp_path/'status.json').read_text(encoding='utf-8'))
    assert teacher.calls==[('generate',16),('generate',16)]
    assert status['status']=='diagnosis_required' and status['independent_groups']==0
    assert not (tmp_path/'.prepare.lock').exists()


async def test_generated_exact_duplicate_cannot_displace_a_pinned_reviewed_seed(tmp_path):
    class Duplicate(Boundary):
        async def generate(self,plan,**kwargs):
            rows=list(await super().generate(plan,**kwargs))
            rows[0]=rows[0].model_copy(update={'text':'不换问宽窄'})
            return tuple(rows)
    teacher=Duplicate(True);seed=sample('seed','不换问宽窄',('尺码',))
    await collect_short(teacher,output=tmp_path,blocked=(),scope={},partition='fixture',target=2,
        minima={'尺码':2},multi_fraction=0,planner=planner,row_guard=lambda r:None,profile=PROFILE|{'pin_seeds':True},seeds=[seed])
    _,rows=load_short(tmp_path)
    assert seed.id in {r.id for r in rows} and len(rows)==2
