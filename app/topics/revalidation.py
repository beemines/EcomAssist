"""Explicit offline repair of a diagnosed, already charged label completion."""
import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4

from app.topics.reviews import digest
from app.topics.teacher import MODEL,_strict_json,parse_prelabels


def revalidate_label_checkpoint(path:Path,samples,*,reason:str):
    path=Path(path)
    if not isinstance(reason,str) or not reason.strip() or len(reason)>512:
        raise ValueError('An explicit bounded diagnosis is required')
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
                ('attempt_id','payload_hash','prompt_hash','model','request_id'))):
        raise ValueError('Diagnostic receipt or completion is not bound to this attempt')
    rows=parse_prelabels(_strict_json(source['content']),samples)
    archive=path.with_name(path.stem+'.offline-'+uuid4().hex+'.json')
    with archive.open('x',encoding='utf-8') as stream:
        json.dump(dict(original=saved,reason=reason,diagnostic_sha256=hashlib.sha256(content).hexdigest()),stream,ensure_ascii=False,indent=2)
    fields=dict(state='complete',intent_hash=saved['intent_hash'],data=[row.model_dump(mode='json') for row in rows],
        receipt=receipt,offline_revalidation=dict(reason=reason,archive=archive.name,
            diagnostic_sha256=hashlib.sha256(content).hexdigest()))
    temporary=path.with_name('.'+path.name+'.'+uuid4().hex+'.tmp')
    try:
        with temporary.open('x',encoding='utf-8') as stream:
            json.dump(fields|{'record_hash':digest(fields)},stream,ensure_ascii=False,indent=2)
            stream.flush();os.fsync(stream.fileno())
        os.replace(temporary,path)
    finally: temporary.unlink(missing_ok=True)
    return rows
