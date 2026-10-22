"""Corpus expansion uses actual human receipts and bounded independent teacher stages."""
import json
from types import SimpleNamespace
import pytest
from app.topics.corpus import expand_corpus, corpus_status
from app.topics.cleaning import clean_question
from app.topics.reviews import apply_review
from app.topics.teacher import GeneratedQuestion,Prelabel
from tests.test_topic_review_receipts import pack,decision


class Teacher:
    def __init__(self):
        self.calls=[];self.last_receipt=None;self.intents={};self.mismatch=False
        self.ledger=SimpleNamespace(summary=lambda:SimpleNamespace(model_dump=lambda:dict(attempts=len(self.calls))))
    async def generate(self,plan):
        self.calls.append('generate');self.last_receipt={'attempt_id':str(len(self.calls))}
        self.intents={f'gen-{i}':labels for i,labels in enumerate(plan.scenario_labels)}
        return tuple(GeneratedQuestion(id=f'gen-{i}',text=f'独立界面测试场景{i}，需要了解业务规则。',
            family_id=f'fam-{i}',requested_labels=labels) for i,labels in enumerate(plan.scenario_labels))
    async def label(self,rows):
        self.calls.append('label');self.last_receipt={'attempt_id':str(len(self.calls))}
        return tuple(Prelabel(id=row.sample_id,cleaned_text=row.text,
            labels=['发票'] if self.mismatch and i==len(rows)-1 else self.intents[row.sample_id],
            notes='transport fixture, not model quality') for i,row in enumerate(rows))


def reviewed():
    p=pack()
    return apply_review(p,[decision(p,s.id) for s in p.samples])


async def test_expansion_requires_receipt_and_never_relabels_or_resends_pool(tmp_path):
    human=reviewed();teacher=Teacher()
    result=await expand_corpus(None,human,teacher,output=tmp_path,target_groups=3,minimum_per_class=0,multi_fraction=0)
    assert teacher.calls==['generate','label']
    rows=[json.loads(line) for line in (result/'samples.jsonl').read_text(encoding='utf-8').splitlines()]
    assert {s.id for s in human.samples}<={row['id'] for row in rows}
    assert corpus_status(result)['scope']['review_receipt_hash']==human.receipt_hash
    await expand_corpus(None,human,teacher,output=tmp_path,target_groups=3,minimum_per_class=0,multi_fraction=0)
    assert teacher.calls==['generate','label']
    changed=human.model_copy(update={'receipt_hash':'0'*64})
    with pytest.raises(ValueError):
        await expand_corpus(None,changed,teacher,output=tmp_path,target_groups=3,minimum_per_class=0,multi_fraction=0)


async def test_scenario_mismatch_is_quarantined_not_used_as_truth(tmp_path):
    human=reviewed();teacher=Teacher();teacher.mismatch=True
    # The second generated scenario is a different category but receives invoice from the independent fixture teacher.
    result=await expand_corpus(None,human,teacher,output=tmp_path,target_groups=4,minimum_per_class=0,
        multi_fraction=0,max_batches=1)
    state=corpus_status(result)
    assert state['status']=='incomplete'
    assert any(row['reason']=='scenario_label_mismatch' for row in state['quarantine'])
    assert state['budget']['attempts']==2


async def test_failed_checkpoint_does_not_repeat_automatically(tmp_path):
    teacher=Teacher();human=reviewed()
    async def failed(plan):
        teacher.calls.append('failed_generate');teacher.last_receipt={'attempt_id':'failed-fixture'}
        raise RuntimeError('fixture stage failure')
    teacher.generate=failed
    with pytest.raises(RuntimeError):
        await expand_corpus(None,human,teacher,output=tmp_path,target_groups=3,minimum_per_class=0,multi_fraction=0)
    with pytest.raises(ValueError):
        await expand_corpus(None,human,teacher,output=tmp_path,target_groups=3,minimum_per_class=0,multi_fraction=0)
    assert teacher.calls==['failed_generate']
