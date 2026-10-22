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
