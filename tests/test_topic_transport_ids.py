"""Short wire IDs are strictly checked, then mapped back to immutable local IDs."""
import json
import httpx
from pydantic import SecretStr
from app.topics.cleaning import clean_question
from app.topics.teacher import TeacherClient
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
