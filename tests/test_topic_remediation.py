"""Fixture data checks for the approved second iteration, no model-quality claims."""
from types import SimpleNamespace
import pytest
from app.topics.types import LabelledSample
from app.topics.teacher import GeneratedQuestion,Prelabel
from app.topics.taxonomy import default_taxonomy

def sample(id,text,labels=('物流',),group=None):
    return LabelledSample(id=id,text=text,labels=labels,origin='synthetic',group_id=group or id,
        source_question_ids=[],pilot=False)

def test_short_filter_excludes_old_family_probe_and_overlength():
    from app.topics.remediation import filter_short
    blocked=[sample('old','这个包裹什么时候能到')]
    candidates=[sample('same','这个包裹什么时候能到'),sample('probe','买大了想退',('退换货','尺码')),
        sample('long','这是一个远远超过十六个字的物流运输进度问题请回答'),sample('ok','明天还能送到吗')]
    retained,excluded=filter_short(candidates,blocked)
    assert [row.id for row in retained]==['ok']
    assert {row['sample_id'] for row in excluded}=={'same','probe','long'}

def test_short_plans_are_frozen_deterministic_and_keep_other_exclusive():
    from app.topics.remediation import short_plan
    first=short_plan(16,{},0,partition='train')
    assert first==short_plan(16,{},0,partition='train')
    assert all(not ('其他' in labels and len(labels)>1) for labels in first.scenario_labels)
    assert all('4至16' in hint for hint in first.scenario_hints)
    assert first!=short_plan(16,{},0,partition='test')

async def test_short_collection_resumes_paid_stages_without_repeat_or_old_text_transmission(tmp_path):
    from app.topics.remediation import collect_short
    calls=[]
    class Teacher:
        last_receipt=None
        async def generate(self,plan,**kwargs):
            assert kwargs==dict(short=True,isolate_invalid_items=True)
            assert plan.count==1
            calls.append('generate');self.last_receipt=dict(attempt_id='fixture')
            return (GeneratedQuestion(id='new',text='这件我想退货',family_id='new-family',requested_labels=plan.scenario_labels[0]),)
        async def label(self,rows,**kwargs):
            assert rows[0].sample_id=='new' and rows[0].text=='这件我想退货'
            calls.append('label');self.last_receipt=dict(attempt_id='fixture')
            return (Prelabel(id='new',cleaned_text=rows[0].text,labels=['退换货'],notes=''),)
    minima={label:0 for label in default_taxonomy().ordered_names}
    teacher=Teacher();scope=dict(source_hash='a'*64)
    await collect_short(teacher,output=tmp_path,blocked=[],scope=scope,partition='train',target=1,minima=minima,multi_fraction=0)
    assert calls==['generate','label']
    await collect_short(teacher,output=tmp_path,blocked=[],scope=scope,partition='train',target=1,minima=minima,multi_fraction=0)
    assert calls==['generate','label']


@pytest.mark.parametrize('text,expected',[
    ('大了一码,给我退了吧',True),('尺码偏大,退款多久到账',True),
    ('裤子码小了,想换个号',False),('不退了,帮我换个大一码的',False),('尺码拍小了,能换大一码吗',False)])
def test_reserved_probe_semantic_paraphrases_are_data_exclusions_only(text,expected):
    from app.topics.remediation import probe_semantic_family
    assert probe_semantic_family(sample('q',text,('退换货','尺码')))==expected


def test_short_filter_protects_blocked_ids_even_when_dedup_would_keep_a_new_lexical_id():
    from app.topics.remediation import filter_short
    retained,excluded=filter_short([sample('a-new','这个包裹什么时候到')],[sample('z-old','这个包裹什么时候到')])
    assert not retained
    assert any(row['sample_id']=='a-new' for row in excluded)


def test_conflicting_blocked_rows_cannot_hide_their_family_from_new_candidates():
    from app.topics.remediation import filter_short
    blocked=[sample('old1','包裹在哪',group='shared'),sample('old2','包裹在哪',('退换货',))]
    retained,_=filter_short([sample('new','哪天能够送到',group='shared')],blocked)
    assert not retained
