"""A budget guard before reservation must not poison a never-sent stage."""
import json
from types import SimpleNamespace
import pytest
from app.topics.budget import BudgetError
from app.topics.data_cli import _checkpoint
from app.topics.teacher import Prelabel


async def test_never_sent_budget_pause_can_resume_without_deleting_history(tmp_path):
    teacher=SimpleNamespace(last_receipt=None);calls=[]
    async def blocked():raise BudgetError('No reservation allocated')
    with pytest.raises(BudgetError):
        await _checkpoint('label-0',{'fixture':True},blocked,teacher,tmp_path,Prelabel)
    path=tmp_path/'label-0.json';saved=json.loads(path.read_text(encoding='utf-8'))
    assert saved['state']=='not_sent' and saved['receipt'] is None
    async def allowed():
        calls.append('one physical fixture');teacher.last_receipt={'attempt_id':'new-fixture'}
        return (Prelabel(id='x',cleaned_text='物流?',labels=['物流'],notes=''),)
    rows,_=await _checkpoint('label-0',{'fixture':True},allowed,teacher,tmp_path,Prelabel)
    assert len(calls)==1 and rows[0].id=='x'
    assert len(list(tmp_path.glob('label-0.unsent-*.json')))==1
    await _checkpoint('label-0',{'fixture':True},allowed,teacher,tmp_path,Prelabel)
    assert len(calls)==1


async def test_unsent_checkpoint_still_cannot_change_frozen_scope(tmp_path):
    teacher=SimpleNamespace(last_receipt=None)
    async def blocked():raise BudgetError('No reservation')
    with pytest.raises(BudgetError):await _checkpoint('label-0',{'old':True},blocked,teacher,tmp_path,Prelabel)
    with pytest.raises(ValueError):await _checkpoint('label-0',{'new':True},blocked,teacher,tmp_path,Prelabel)
