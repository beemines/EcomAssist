"""A redundant verbatim alias can be recovered without any new HTTP request."""
import json
import pytest
from app.topics.revalidation import revalidate_label_checkpoint
from app.topics.cleaning import clean_question
from app.topics.reviews import digest


def failed(tmp_path,**changes):
    journal=tmp_path/'journal';journal.mkdir()
    diagnostics=tmp_path/'diagnostics';diagnostics.mkdir()
    receipt=dict(attempt_id='abc',payload_hash='a'*64,prompt_hash='b'*64,model='glm-5.3-flash')
    diagnostic=dict(attempt_id='abc',receipt=receipt,finish_reason='stop',
        content=json.dumps(dict(items=[dict(id='x',text='物流?',cleaned_text='物流?',labels=['物流'],notes='')]),ensure_ascii=False))|changes
    artifact=diagnostics/'abc.json';artifact.write_text(json.dumps(diagnostic),encoding='utf-8')
    record=dict(state='failed',intent_hash='c'*64,receipt=receipt|dict(diagnostic_file=str(artifact.resolve())))
    path=journal/'label-0000.json';path.write_text(json.dumps(record),encoding='utf-8')
    return path,record


def test_revalidation_archives_failed_record_and_keeps_original_receipt(tmp_path):
    path,prior=failed(tmp_path)
    rows=revalidate_label_checkpoint(path,[clean_question('物流?',sample_id='x')],reason='Identical verbatim aliases')
    assert rows[0].labels==('物流',)
    saved=json.loads(path.read_text(encoding='utf-8'))
    assert saved['receipt']==prior['receipt'] and saved['state']=='complete'
    assert saved['record_hash']==digest({k:v for k,v in saved.items() if k!='record_hash'})
    assert len(list(path.parent.glob('label-0000.offline-*.json')))==1
    with pytest.raises(ValueError):
        revalidate_label_checkpoint(path,[clean_question('物流?',sample_id='x')],reason='Repeat')


@pytest.mark.parametrize('kind',['length','wrong_attempt','changed_text','extra_field'])
def test_ambiguous_or_unbound_diagnostic_cannot_be_promoted(tmp_path,kind):
    path,prior=failed(tmp_path)
    artifact=tmp_path/'diagnostics/abc.json';raw=json.loads(artifact.read_text(encoding='utf-8'))
    if kind=='length': raw['finish_reason']='length'
    elif kind=='wrong_attempt': raw['receipt']['attempt_id']='different'
    else:
        value=json.loads(raw['content'])
        if kind=='changed_text': value['items'][0]['text']='运费多少?'
        else: value['items'][0]['ignore_rules']=True
        raw['content']=json.dumps(value)
    artifact.write_text(json.dumps(raw),encoding='utf-8')
    with pytest.raises(ValueError):
        revalidate_label_checkpoint(path,[clean_question('物流?',sample_id='x')],reason='Must stay failed')
    assert json.loads(path.read_text(encoding='utf-8'))==prior


def test_explicit_partial_recovery_quarantines_changed_text_without_editing_it(tmp_path):
    content=json.dumps(dict(items=[
        dict(id='r00',text='物流?',labels=['物流'],notes=''),
        dict(id='r01',text='退退货?',labels=['退换货'],notes='')]),ensure_ascii=False)
    path,prior=failed(tmp_path,content=content)
    for target in (path,tmp_path/'diagnostics/abc.json'):
        value=json.loads(target.read_text(encoding='utf-8'))
        value['receipt']['id_map']={'r00':'x','r01':'y'}
        target.write_text(json.dumps(value),encoding='utf-8')
    prior=json.loads(path.read_text(encoding='utf-8'))
    rows=revalidate_label_checkpoint(path,[clean_question('物流?',sample_id='x'),clean_question('退货?',sample_id='y')],
        reason='Explicitly quarantine a copied-text mismatch, retain independently valid siblings',quarantine_text_mismatch=True)
    assert [row.id for row in rows]==['x']
    saved=json.loads(path.read_text(encoding='utf-8'))
    assert saved['receipt']==prior['receipt']
    assert saved['offline_revalidation']['quarantine']==[dict(sample_id='y',reason='prelabel_text_mismatch')]
    assert saved['record_hash']==digest({k:v for k,v in saved.items() if k!='record_hash'})


@pytest.mark.parametrize('kind',['unknown_id','duplicate_id','extra_field','unknown_label','all_changed'])
def test_partial_recovery_still_rejects_global_or_non_text_schema_failures(tmp_path,kind):
    items=[dict(id='x',text='物流?',labels=['物流'],notes=''),dict(id='y',text='退退货?',labels=['退换货'],notes='')]
    if kind=='unknown_id':items[1]['id']='z'
    elif kind=='duplicate_id':items[1]['id']='x'
    elif kind=='extra_field':items[1]['new_rule']='unsafe'
    elif kind=='unknown_label':items[1]['labels']=['投诉']
    else:items[0]['text']='物流物流?'
    path,prior=failed(tmp_path,content=json.dumps(dict(items=items)))
    with pytest.raises(ValueError):
        revalidate_label_checkpoint(path,[clean_question('物流?',sample_id='x'),clean_question('退货?',sample_id='y')],
            reason='Must not relax identity or schema',quarantine_text_mismatch=True)
    assert json.loads(path.read_text(encoding='utf-8'))==prior
