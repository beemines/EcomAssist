"""A wrong family is rejected, never guessed, while valid siblings are saved offline."""
import json
import pytest
from app.topics.revalidation import revalidate_generation_checkpoint
from app.topics.reviews import digest
from app.topics.teacher import GenerationPlan
from app.topics.taxonomy import default_taxonomy
from tests.test_topic_offline_revalidation import failed


def fixture(tmp_path):
    plan=GenerationPlan(count=2,scenario_labels=[['物流'],['发票']],taxonomy_hash=default_taxonomy().digest)
    scope={'approved_fixture':True}
    content=json.dumps(dict(items=[
        dict(id='g00',family_id='f00',requested_labels=['物流'],text='物流在哪里?'),
        dict(id='g01',family_id='f00',requested_labels=['发票'],text='怎样开发票?')]))
    path,_=failed(tmp_path,content=content)
    renamed=path.with_name('generate-0000.json');path.rename(renamed);path=renamed
    for target in (path,tmp_path/'diagnostics/abc.json'):
        value=json.loads(target.read_text(encoding='utf-8'))
        value['receipt'].update(id_map={'g00':'syn-x','g01':'syn-y'},family_map={'f00':'family-x','f01':'family-y'})
        if target==path:value['intent_hash']=digest(dict(scope=scope,plan=plan.model_dump(mode='json')))
        target.write_text(json.dumps(value),encoding='utf-8')
    return path,plan,scope


def test_generation_recovery_keeps_original_attempt_and_quarantines_wrong_family(tmp_path):
    path,plan,scope=fixture(tmp_path);prior=json.loads(path.read_text(encoding='utf-8'))
    rows=revalidate_generation_checkpoint(path,plan,scope=scope,reason='Diagnosed wrong family; keep strict valid siblings only')
    assert len(rows)==1 and rows[0].id=='syn-x' and rows[0].family_id=='family-x'
    saved=json.loads(path.read_text(encoding='utf-8'))
    assert saved['receipt']==prior['receipt']
    assert saved['offline_revalidation']['quarantine']==[dict(sample_id='syn-y',reason='generated_item_invalid')]


@pytest.mark.parametrize('kind',['scope','unknown_id','family_map','all_invalid'])
def test_generation_recovery_rejects_unbound_or_fully_invalid_diagnostics(tmp_path,kind):
    path,plan,scope=fixture(tmp_path);prior=json.loads(path.read_text(encoding='utf-8'))
    artifact=tmp_path/'diagnostics/abc.json';value=json.loads(artifact.read_text(encoding='utf-8'))
    if kind=='scope':scope={'different':True}
    elif kind=='family_map':value['receipt']['family_map']['f00']='different'
    else:
        content=json.loads(value['content'])
        if kind=='unknown_id':content['items'][1]['id']='foreign'
        else:content['items'][0]['family_id']='f01'
        value['content']=json.dumps(content)
    artifact.write_text(json.dumps(value),encoding='utf-8')
    with pytest.raises(ValueError):revalidate_generation_checkpoint(path,plan,scope=scope,reason='Must stay failed')
    assert json.loads(path.read_text(encoding='utf-8'))==prior
