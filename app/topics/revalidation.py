"""Explicit offline repair of a diagnosed, already charged label completion."""
import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4

from app.topics.reviews import digest
from app.topics.teacher import MODEL,Prelabel,_strict_json,_items,parse_prelabels,parse_mapped_prelabels,parse_generated,isolate_items


def _diagnostic(path):
    saved=json.loads(path.read_text(encoding='utf-8'))
    if saved.get('state')!='failed' or not isinstance(saved.get('receipt'),dict):
        raise ValueError('Only a diagnosed failed completion may be revalidated')
    receipt=saved['receipt']
    attempt=receipt.get('attempt_id')
    if not isinstance(attempt,str) or not attempt.isalnum(): raise ValueError('Invalid attempt identity')
    diagnostic=Path(receipt['diagnostic_file']).resolve()
    if diagnostic!=(path.parent.parent/'diagnostics'/(attempt+'.json')).resolve():
        raise ValueError('Diagnostic must be the original bounded local artifact')
    content=diagnostic.read_bytes()
    source=json.loads(content)
    if (source.get('finish_reason')!='stop' or source.get('attempt_id')!=attempt
            or not isinstance(source.get('receipt'),dict) or receipt.get('model')!=MODEL
            or any(source['receipt'].get(key)!=receipt.get(key) for key in
                ('attempt_id','payload_hash','prompt_hash','model','request_id','id_map','family_map'))):
        raise ValueError('Diagnostic receipt or completion is not bound to this attempt')
    return saved,content,_strict_json(source['content'])


def _reason(reason):
    if not isinstance(reason,str) or not reason.strip() or len(reason)>512:
        raise ValueError('An explicit bounded diagnosis is required')


def revalidate_label_checkpoint(path:Path,samples,*,reason:str,quarantine_text_mismatch:bool=False):
    path=Path(path);_reason(reason)
    saved,content,value=_diagnostic(path);receipt=saved['receipt']
    quarantine=[]
    if quarantine_text_mismatch:
        mapping={sample.sample_id:sample for sample in samples}
        id_map=receipt.get('id_map',{identifier:identifier for identifier in mapping})
        if (type(id_map) is not dict or len(id_map)!=len(samples) or len(set(id_map.values()))!=len(samples)
                or set(id_map.values())!=set(mapping)
                or 'id_map' in receipt and set(id_map)!={f'r{i:02d}' for i in range(len(samples))}):
            raise ValueError('Transport ID map does not match immutable inputs')
        wire={alias:mapping[identifier].model_copy(update={'sample_id':alias}) for alias,identifier in id_map.items()}
        retained=[]
        for item in _items(value,wire):
            checked=item.copy()
            if 'text' in checked:
                if type(checked['text']) is not str:raise ValueError('Copied text must be a string')
                if 'cleaned_text' not in checked:checked['cleaned_text']=checked['text']
                del checked['text']
            Prelabel.model_validate(checked)
            try:
                parsed=parse_prelabels({'items':[item]},[wire[item['id']]])[0]
            except ValueError as exc:
                if str(exc) not in ('Prelabel must not alter the question','Redundant text aliases must both equal the exact input'):
                    raise
                quarantine.append(dict(sample_id=id_map[item['id']],reason='prelabel_text_mismatch'))
            else:retained.append(parsed.model_copy(update={'id':id_map[parsed.id]}))
        if not retained:raise ValueError('No exact-input rows remain; do not promote an empty stage')
        rows=tuple(retained)
    else:
        rows=parse_mapped_prelabels(value,samples,receipt['id_map']) if 'id_map' in receipt else parse_prelabels(value,samples)
    _promote(path,saved,rows,quarantine,content,reason)
    return rows


def _promote(path,saved,rows,quarantine,content,reason):
    archive=path.with_name(path.stem+'.offline-'+uuid4().hex+'.json')
    with archive.open('x',encoding='utf-8') as stream:
        json.dump(dict(original=saved,reason=reason,diagnostic_sha256=hashlib.sha256(content).hexdigest()),stream,ensure_ascii=False,indent=2)
    fields=dict(state='complete',intent_hash=saved['intent_hash'],data=[row.model_dump(mode='json') for row in rows],
        receipt=saved['receipt'],offline_revalidation=dict(reason=reason,archive=archive.name,
            diagnostic_sha256=hashlib.sha256(content).hexdigest(),quarantine=quarantine))
    temporary=path.with_name('.'+path.name+'.'+uuid4().hex+'.tmp')
    try:
        with temporary.open('x',encoding='utf-8') as stream:
            json.dump(fields|{'record_hash':digest(fields)},stream,ensure_ascii=False,indent=2)
            stream.flush();os.fsync(stream.fileno())
        os.replace(temporary,path)
    finally: temporary.unlink(missing_ok=True)


def revalidate_generation_checkpoint(path:Path,plan,*,scope,reason:str):
    path=Path(path);_reason(reason)
    saved,content,value=_diagnostic(path);receipt=saved['receipt']
    if saved.get('intent_hash')!=digest(dict(scope=scope,plan=plan.model_dump(mode='json'))):
        raise ValueError('The generation plan is not bound to this frozen checkpoint')
    ids=receipt.get('id_map');families=receipt.get('family_map')
    if (type(ids) is not dict or type(families) is not dict
            or set(ids)!={f'g{i:02d}' for i in range(plan.count)}
            or set(families)!={f'f{i:02d}' for i in range(plan.count)}
            or len(set(ids.values()))!=plan.count or len(set(families.values()))!=plan.count):
        raise ValueError('Immutable generation transport maps are incomplete')
    expected={f'g{i:02d}':dict(family_id=f'f{i:02d}',requested_labels=list(labels))
        for i,labels in enumerate(plan.scenario_labels)}
    rows,quarantine=isolate_items(value,expected,
        lambda item:parse_generated({'items':[item]},{item['id']:expected[item['id']]}),
        id_map=ids,reason='generated_item_invalid')
    rows=tuple(row.model_copy(update={'id':ids[row.id],'family_id':families[row.family_id]}) for row in rows)
    _promote(path,saved,rows,quarantine,content,reason)
    return rows
