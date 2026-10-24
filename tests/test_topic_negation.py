"""Program contracts for a new synthetic-only, human-gated data iteration."""
from collections import Counter
import json
import pytest
from app.topics.types import LabelledSample
from app.topics.teacher import GeneratedQuestion,Prelabel,GenerationPlan
from app.topics.taxonomy import default_taxonomy
from app.topics.reviews import digest


def row(id,text,labels):
    return LabelledSample(id=id,text=text,labels=labels,origin='synthetic',group_id=id,source_question_ids=[],pilot=False)


def test_plans_balance_all_topics_and_never_count_the_cancelled_topic():
    from app.topics.negation import negation_plan
    counts=Counter();all_labels=[];negative=0
    for batch in range(4):
        plan=negation_plan(16,counts,batch,partition='train')
        assert plan==negation_plan(16,counts,batch,partition='train')
        for labels,hint in zip(plan.scenario_labels,plan.scenario_hints):
            counts.update(labels);all_labels.extend(labels)
            if '撤销诉求=' in hint:
                denied=hint.split('撤销诉求=')[1].split('；')[0]
                assert denied not in labels;negative+=1
            assert not ('其他' in labels and len(labels)>1)
    assert set(all_labels)==set(default_taxonomy().ordered_names) and negative==32
    assert negation_plan(2,{},0,partition='validation')!=negation_plan(2,{},0,partition='test')


@pytest.mark.parametrize('text,labels,excluded',[
    ('不退货,只问尺码',['尺码'],True),('别退款了只看尺寸',['尺码'],True),
    ('买大了想退',['退换货','尺码'],True),('不退货了只查物流',['物流'],False),
    ('不要发票只问尺码',['尺码'],False)])
def test_known_diagnostic_semantic_families_are_data_exclusions(text,labels,excluded):
    from app.topics.negation import protected_family
    assert bool(protected_family(row('x',text,labels)))==excluded


async def test_profiled_collector_guards_rows_and_reuses_paid_stage_checkpoints(tmp_path,monkeypatch):
    from app.topics.remediation import collect_short
    from app.topics.negation import protected_family
    calls=[]
    def planner(count,positive,batch,*,partition):
        return GenerationPlan(count=1,scenario_labels=[['尺码'] if batch==0 else ['发票']],
            taxonomy_hash=default_taxonomy().digest,scenario_hints=['只造新合成句，不发送旧数据'])
    class Teacher:
        last_receipt=None
        async def generate(self,plan,**kwargs):
            b=len(calls)//2;calls.append('generate');self.last_receipt={'attempt_id':'fixture'}
            assert kwargs['short']==(b==0)
            return (GeneratedQuestion(id='new-'+str(b),family_id='family-'+str(b),
                text='不退货只问尺码' if b==0 else '别催物流我只要发票请告诉我开具流程',requested_labels=plan.scenario_labels[0]),)
        async def label(self,cleaned,**kwargs):
            calls.append('label');self.last_receipt={'attempt_id':'fixture'}
            r=cleaned[0]
            return (Prelabel(id=r.sample_id,cleaned_text=r.text,labels=['尺码'] if r.sample_id=='new-0' else ['发票'],notes=''),)
    kwargs=dict(output=tmp_path,blocked=[],scope={'fixture':True},partition='train',target=1,
        minima={label:0 for label in default_taxonomy().ordered_names},multi_fraction=0,max_batches=2,
        planner=planner,row_guard=protected_family,profile={'version':'fixture-v1','generation_profile':'mixed','max_chars':45})
    teacher=Teacher()
    await collect_short(teacher,**kwargs)
    assert calls==['generate','label','generate','label']
    status=json.loads((tmp_path/'status.json').read_text(encoding='utf-8'))
    assert status['status']=='complete' and status['rows']==1
    assert any(q['sample_id']=='new-0' for q in status['quarantine'])
    await collect_short(teacher,**kwargs)
    assert len(calls)==4
    from app.topics import remediation
    original_prompt=remediation.system_prompt
    monkeypatch.setattr(remediation,'system_prompt',lambda stage:original_prompt(stage)+(' changed' if stage=='generate' else ''))
    with pytest.raises(ValueError):await collect_short(teacher,**kwargs)
    monkeypatch.setattr(remediation,'system_prompt',original_prompt)
    with pytest.raises(ValueError):await collect_short(teacher,**(kwargs|{'profile':{'version':'changed'}}))


def test_new_test_length_policy_preserves_full_sentences_without_changing_old_short_data_gate():
    from app.topics.remediation import filter_short
    sample=row('new','别催物流我只要发票请告诉我开具流程',['发票'])
    assert len(sample.text)>16
    assert not filter_short([sample],[])[0]
    retained=filter_short([sample],[],max_chars=45)[0]
    assert len(retained)==1 and retained[0].id=='new' and retained[0].text==sample.text and retained[0].labels==('发票',)
    with pytest.raises(ValueError):filter_short([sample],[],max_chars=128)


def test_training_pack_contains_64_synthetic_rows_but_no_invented_human_receipt(tmp_path):
    from app.topics.negation import build_training_review
    root=tmp_path/'train-corpus';root.mkdir()
    names=default_taxonomy().ordered_names
    samples=[row('new-'+str(i),'新合成问题第'+str(i)+'条',[names[i%17]]) for i in range(64)]
    content=''.join(r.model_dump_json()+'\n' for r in samples)
    (root/'samples.jsonl').write_text(content,encoding='utf-8')
    fields=dict(status='complete',samples_hash=digest(content),independent_groups=64)
    (root/'status.json').write_text(json.dumps(fields|{'status_hash':digest(fields)}),encoding='utf-8')
    (root/'journal').mkdir()
    pack=build_training_review(tmp_path)
    assert len(pack.samples)==64 and pack.purpose=='pilot' and all(r.origin=='synthetic' for r in pack.samples)
    assert not (tmp_path/'train-review/review-receipt.json').exists()
    assert build_training_review(tmp_path)==pack


def test_negation_cli_preview_reads_existing_budget_without_constructing_a_teacher(tmp_path,monkeypatch,capsys):
    from app.topics import data_cli,budget,negation,teacher
    from tests.test_topic_budget_amendment import prepared,with_450
    path,_=prepared(tmp_path);with_450(path)
    budget.amend_negation_limit(path,revision_id=budget.NEGATION_APPROVAL_ID,approval_text=budget.NEGATION_APPROVAL_TEXT)
    monkeypatch.setattr(budget,'BUDGET_PATH',path)
    monkeypatch.setattr(negation,'source_context',lambda source:({'source_manifest_hash':'a'*64},()))
    monkeypatch.setattr(teacher,'configured_teacher',lambda *a,**k:pytest.fail('preview constructed a paid teacher'))
    monkeypatch.setattr('sys.argv',['data','prepare-negation','--source','unused','--output',str(tmp_path/'out')])
    data_cli.main()
    result=json.loads(capsys.readouterr().out)
    assert result['mode']=='preview' and result['partition']=='train' and result['budget']['attempts']==0
    assert result['budget']['attempt_limit']==500 and result['external_data']=='new_synthetic_questions_and_taxonomy_only'
    assert not (tmp_path/'out').exists()
