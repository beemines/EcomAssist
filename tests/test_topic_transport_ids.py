"""Short wire IDs are strictly checked, then mapped back to immutable local IDs."""
import json
import httpx
from pydantic import SecretStr
from app.topics.cleaning import clean_question
from app.topics.teacher import TeacherClient,GenerationPlan
from app.topics.taxonomy import default_taxonomy
from app.topics.types import LabelledSample
from tests.test_topic_teacher import ledger_for,response


async def test_short_wire_ids_preserve_stable_ids_and_record_the_mapping(tmp_path):
    ledger=ledger_for(tmp_path)
    samples=[clean_question('物流进度?',sample_id='syn-123456789abcdef123456789abcdef01-0'),
             clean_question('电子发票怎么开?',sample_id='syn-123456789abcdef123456789abcdef01-1')]
    def handler(request):
        items=json.loads(json.loads(request.content)['messages'][1]['content'])['items']
        assert [x['id'] for x in items]==['r00','r01']
        assert all(row.sample_id not in request.content.decode() for row in samples)
        return response(json.dumps(dict(items=[dict(id=row['id'],cleaned_text=row['text'],
            labels=['物流'] if i==0 else ['发票'],notes='') for i,row in enumerate(items)])))
    async with TeacherClient(ledger,api_key=SecretStr('fixture'),transport=httpx.MockTransport(handler)) as teacher:
        rows=await teacher.label(samples)
        assert teacher.last_receipt['id_map']=={'r00':samples[0].sample_id,'r01':samples[1].sample_id}
    assert [row.id for row in rows]==[row.sample_id for row in samples]
    assert ledger.summary().attempts==1


async def test_generation_wire_ids_and_family_ids_are_short_but_local_ids_unique(tmp_path):
    ledger=ledger_for(tmp_path)
    def handler(request):
        items=json.loads(json.loads(request.content)['messages'][1]['content'])['items']
        assert [(row['id'],row['family_id']) for row in items]==[('g00','f00'),('g01','f01')]
        return response(json.dumps(dict(items=[dict(id=row['id'],family_id=row['family_id'],
            requested_labels=row['requested_labels'],text='包裹现在能查到具体位置吗?' if i==0 else '我想开电子发票怎么操作?')
            for i,row in enumerate(items)])))
    plan=GenerationPlan(count=2,scenario_labels=[['物流'],['发票']],taxonomy_hash=default_taxonomy().digest)
    async with TeacherClient(ledger,api_key=SecretStr('fixture'),transport=httpx.MockTransport(handler)) as teacher:
        rows=await teacher.generate(plan)
        assert rows[0].id.startswith('syn-') and rows[0].family_id.startswith('family-')
        assert teacher.last_receipt['id_map']['g00']==rows[0].id
        assert teacher.last_receipt['family_map']['f00']==rows[0].family_id


async def test_augmentation_uses_short_wire_ids_and_keeps_original_parent_family(tmp_path):
    ledger=ledger_for(tmp_path)
    parent=LabelledSample(id='syn-long-parent-abcdef0123456789',text='包裹现在在哪里?',labels=['物流'],
        group_id='frozen-family',origin='synthetic',source_question_ids=[],pilot=False)
    def handler(request):
        items=json.loads(json.loads(request.content)['messages'][1]['content'])['items']
        assert items[0]['id']=='a00'
        return response(json.dumps(dict(items=[dict(id='a00',text='请问包裹现在在哪里?')])))
    async with TeacherClient(ledger,api_key=SecretStr('fixture'),transport=httpx.MockTransport(handler)) as teacher:
        rows=await teacher.augment([parent])
    assert rows[0].id==parent.id+'-aug' and rows[0].group_id==parent.group_id
