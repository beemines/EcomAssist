"""Identity fixtures verify integrity; fake bytes are never inference evidence."""
import hashlib
import json
import pytest
from app.topics.manifest import verify_manifest
from app.topics.reviews import digest
from app.topics.taxonomy import default_taxonomy
from app.topics.cleaning import CLEANING_VERSION


def model_files(tmp_path):
    taxonomy=default_taxonomy()
    config=dict(model_type='bert',hidden_size=768,num_hidden_layers=12,num_attention_heads=12,
        problem_type='multi_label_classification',id2label={str(i):label for i,label in enumerate(taxonomy.ordered_names)},
        label2id={label:i for i,label in enumerate(taxonomy.ordered_names)})
    content={'config.json':json.dumps(config,ensure_ascii=False).encode(),'model.safetensors':b'fake identity fixture, never a model',
        'tokenizer.json':b'{}','tokenizer_config.json':b'{}','thresholds.json':b'{}'}
    files={}
    for name,data in content.items():
        (tmp_path/name).write_bytes(data);files[name]=dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
    core=dict(schema_version=1,base_model='hfl/chinese-roberta-wwm-ext',base_revision='5c58d0b8ec1d9014354d691c538661bf00bfdb44',
        taxonomy_version=taxonomy.version,taxonomy_hash=taxonomy.digest,labels=list(taxonomy.ordered_names),
        cleaning_version=CLEANING_VERSION,decoder_version='ch10-multilabel-v1',max_tokens=128,seed=20261021,
        dataset_hash='1'*64,augmentation_hash='2'*64,pilot_receipt_hash='3'*64,training_receipt_hash='4'*64,
        training_config_hash='5'*64,dependency_lock_hash='6'*64,files=files)
    value=dict(core=core,model_version=digest(core))
    path=tmp_path/'manifest.json';path.write_text(json.dumps(value,ensure_ascii=False),encoding='utf-8')
    return path,value


def test_valid_core_identity_excludes_report_backreferences(tmp_path):
    path,value=model_files(tmp_path)
    identity=verify_manifest(path)
    assert identity.model_version==value['model_version'] and identity.taxonomy_hash==default_taxonomy().digest
    report=tmp_path/'report.json';report.write_text(json.dumps({'model_version':identity.model_version}),encoding='utf-8')
    assert verify_manifest(path)==identity
    report.write_text('different report',encoding='utf-8')
    assert verify_manifest(path)==identity


@pytest.mark.parametrize('kind',['weight_bytes','missing_file','escape','label_order','wrong_version','unknown_decoder','bool_size','report_cycle','unknown_base'])
def test_bad_model_identity_or_core_files_are_rejected_before_heavy_load(tmp_path,kind):
    path,value=model_files(tmp_path)
    if kind=='weight_bytes':(tmp_path/'model.safetensors').write_bytes(b'tampered')
    elif kind=='missing_file':(tmp_path/'tokenizer.json').unlink()
    elif kind=='escape':value['core']['files']['../escape']=value['core']['files'].pop('tokenizer.json')
    elif kind=='label_order':value['core']['labels'][0:2]=list(reversed(value['core']['labels'][0:2]))
    elif kind=='wrong_version':value['model_version']='0'*64
    elif kind=='unknown_decoder':value['core']['decoder_version']='unrecognized'
    elif kind=='bool_size':value['core']['files']['tokenizer.json']['bytes']=True
    elif kind=='report_cycle':value['core']['files']['report.json']=dict(sha256='a'*64,bytes=1)
    else:value['core']['base_model']='a-different-model'
    if kind!='wrong_version':value['model_version']=digest(value['core'])
    path.write_text(json.dumps(value,ensure_ascii=False),encoding='utf-8')
    with pytest.raises(ValueError):verify_manifest(path)
