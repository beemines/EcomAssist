"""Expansion can quarantine invalid items without retrying a paid batch."""
import json
from pathlib import Path
import httpx
from pydantic import SecretStr
import pytest
from app.topics.cleaning import clean_question
from app.topics.teacher import TeacherClient,TeacherError,GenerationPlan
from app.topics.taxonomy import default_taxonomy
from tests.test_topic_teacher import ledger_for,response


async def test_partial_label_batch_keeps_exact_sibling_and_records_diagnostic(tmp_path):
    ledger=ledger_for(tmp_path);calls=[]
    def handler(request):
        calls.append(request)
        return response(json.dumps(dict(items=[
            dict(id='r00',text='物流?',labels=['物流'],notes=''),
            dict(id='r01',text='退退货?',labels=['退换货'],notes='')])))
    async with TeacherClient(ledger,api_key=SecretStr('fixture'),transport=httpx.MockTransport(handler),evidence_dir=tmp_path/'diagnostics') as teacher:
        rows=await teacher.label([clean_question('物流?',sample_id='x'),clean_question('退货?',sample_id='y')],isolate_invalid_items=True)
        assert [row.id for row in rows]==['x']
        assert teacher.last_receipt['item_quarantine']==[dict(sample_id='y',reason='prelabel_item_invalid')]
        evidence=json.loads(Path(teacher.last_receipt['diagnostic_file']).read_text(encoding='utf-8'))
        assert evidence['error_type']=='ItemQuarantine' and json.loads(evidence['content'])['items'][1]['text']=='退退货?'
    assert len(calls)==1 and ledger.summary().attempts==1 and ledger.summary().consecutive_failures==0


async def test_partial_generation_does_not_repair_wrong_family_or_reassign_ids(tmp_path):
    ledger=ledger_for(tmp_path)
    def handler(request):
        items=json.loads(json.loads(request.content)['messages'][1]['content'])['items']
        return response(json.dumps(dict(items=[
            dict(id=row['id'],family_id=row['family_id'] if i==0 else 'f00',requested_labels=row['requested_labels'],
                text='物流在哪里?' if i==0 else '怎样开发票?') for i,row in enumerate(items)])))
    plan=GenerationPlan(count=2,scenario_labels=[['物流'],['发票']],taxonomy_hash=default_taxonomy().digest)
    async with TeacherClient(ledger,api_key=SecretStr('fixture'),transport=httpx.MockTransport(handler)) as teacher:
        rows=await teacher.generate(plan,isolate_invalid_items=True)
        assert len(rows)==1 and rows[0].requested_labels==('物流',)
        assert teacher.last_receipt['item_quarantine']==[dict(sample_id=teacher.last_receipt['id_map']['g01'],reason='generated_item_invalid')]
    assert ledger.summary().attempts==1


@pytest.mark.parametrize('kind',['extra_id','duplicate_id','all_invalid','broken_json'])
async def test_partial_mode_never_accepts_unbound_or_entirely_invalid_batch(tmp_path,kind):
    ledger=ledger_for(tmp_path)
    def handler(request):
        rows=[dict(id='r00',text='物流?',labels=['物流'],notes=''),dict(id='r01',text='退货?',labels=['退换货'],notes='')]
        if kind=='extra_id':rows[1]['id']='foreign'
        elif kind=='duplicate_id':rows[1]['id']='r00'
        elif kind=='all_invalid':
            for row in rows:row['labels']=['不存在']
        return response('bad' if kind=='broken_json' else json.dumps(dict(items=rows)))
    async with TeacherClient(ledger,api_key=SecretStr('fixture'),transport=httpx.MockTransport(handler)) as teacher:
        with pytest.raises(TeacherError):
            await teacher.label([clean_question('物流?',sample_id='x'),clean_question('退货?',sample_id='y')],isolate_invalid_items=True)
    assert ledger.summary().attempts==1 and ledger.summary().consecutive_failures==1
