"""Lightweight immutable model identity verification; never imports Torch/NumPy."""
import hashlib
import json
from pathlib import Path
from typing import Literal
from pydantic import Field,model_validator
from app.topics.cleaning import CLEANING_VERSION
from app.topics.reviews import digest
from app.topics.taxonomy import default_taxonomy
from app.topics.types import StrictRecord,ModelIdentity

DECODER_VERSION='ch10-multilabel-v1'
REQUIRED_FILES=frozenset(('config.json','model.safetensors','tokenizer.json','tokenizer_config.json','thresholds.json'))
ALLOWED_FILES=REQUIRED_FILES|{'vocab.txt','special_tokens_map.json'}


class FileDigest(StrictRecord):
    sha256:str=Field(pattern=r'^[0-9a-f]{64}$')
    bytes:int=Field(ge=1,le=2_000_000_000)


class CoreManifest(StrictRecord):
    schema_version:Literal[1]
    base_model:Literal['hfl/chinese-roberta-wwm-ext']
    base_revision:Literal['5c58d0b8ec1d9014354d691c538661bf00bfdb44']
    taxonomy_version:str
    taxonomy_hash:str=Field(pattern=r'^[0-9a-f]{64}$')
    labels:tuple[str,...]
    cleaning_version:str
    decoder_version:str
    max_tokens:Literal[128]
    seed:Literal[20261021]
    dataset_hash:str=Field(pattern=r'^[0-9a-f]{64}$')
    augmentation_hash:str=Field(pattern=r'^[0-9a-f]{64}$')
    pilot_receipt_hash:str=Field(pattern=r'^[0-9a-f]{64}$')
    training_receipt_hash:str=Field(pattern=r'^[0-9a-f]{64}$')
    training_config_hash:str=Field(pattern=r'^[0-9a-f]{64}$')
    dependency_lock_hash:str=Field(pattern=r'^[0-9a-f]{64}$')
    files:dict[str,FileDigest]

    @model_validator(mode='after')
    def compatibility(self):
        taxonomy=default_taxonomy()
        if (self.taxonomy_version!=taxonomy.version or self.taxonomy_hash!=taxonomy.digest
                or self.labels!=taxonomy.ordered_names or self.cleaning_version!=CLEANING_VERSION
                or self.decoder_version!=DECODER_VERSION or not REQUIRED_FILES<=self.files.keys()
                or not self.files.keys()<=ALLOWED_FILES):
            raise ValueError('Unsupported model metadata or core file set')
        return self


class ModelManifest(StrictRecord):
    core:CoreManifest
    model_version:str=Field(pattern=r'^[0-9a-f]{64}$')

    @model_validator(mode='after')
    def identity(self):
        if self.model_version!=digest(self.core.model_dump(mode='json')):
            raise ValueError('Model core identity changed')
        return self


def _sha(path):
    result=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):result.update(block)
    return result.hexdigest()


def read_manifest(path:Path) -> ModelManifest:
    path=Path(path)
    if path.is_dir():path=path/'manifest.json'
    try:
        if path.is_symlink() or path.parent.is_symlink() or not path.is_file() or path.stat().st_size>65536:
            raise ValueError('Model manifest unavailable or oversized')
        value=ModelManifest.model_validate_json(path.read_text(encoding='utf-8'))
        root=path.parent.resolve()
        for name,record in value.core.files.items():
            local=root/name
            if (local.is_symlink() or not local.is_file() or local.stat().st_size!=record.bytes
                    or name.endswith('.json') and record.bytes>8*1024*1024 or _sha(local)!=record.sha256):
                raise ValueError('Model core file missing or changed')
        config=json.loads((root/'config.json').read_text(encoding='utf-8'))
        if (config.get('model_type')!='bert' or config.get('hidden_size')!=768
                or config.get('num_hidden_layers')!=12 or config.get('num_attention_heads')!=12
                or config.get('problem_type')!='multi_label_classification'
                or config.get('id2label')!={str(i):label for i,label in enumerate(value.core.labels)}
                or config.get('label2id')!={label:i for i,label in enumerate(value.core.labels)}):
            raise ValueError('Model architecture or label-column mapping changed')
        return value
    except (OSError,TypeError,AttributeError,json.JSONDecodeError) as exc:
        raise ValueError('Model manifest or files are unavailable/invalid') from exc


def verify_manifest(path:Path) -> ModelIdentity:
    value=read_manifest(path)
    return ModelIdentity(model_version=value.model_version,taxonomy_version=value.core.taxonomy_version,
        taxonomy_hash=value.core.taxonomy_hash,cleaning_version=value.core.cleaning_version,max_tokens=128)


REQUIRED_EVIDENCE=frozenset(('evaluation-complete.json','silver.json','predictions.jsonl','review-selection.json',
    'probe.json','cpu-roundtrip.json','gold-pack.json','gold-receipt.json','gold-report.json'))
OPTIONAL_EVIDENCE=frozenset(('error-pack.json','error-receipt.json','error-report.json'))

class ReleaseManifest(StrictRecord):
    schema_version:Literal[1]
    model_version:str=Field(pattern=r'^[0-9a-f]{64}$')
    human_status:Literal['reviewed']
    files:dict[str,FileDigest]
    release_hash:str=Field(pattern=r'^[0-9a-f]{64}$')

    @model_validator(mode='after')
    def bound(self):
        names=set(self.files)
        if (not REQUIRED_EVIDENCE<=names or names-REQUIRED_EVIDENCE not in (set(),set(OPTIONAL_EVIDENCE))
                or any(record.bytes>16*1024*1024 for record in self.files.values())):
            raise ValueError('Release requires the exact review/evaluation evidence file set')
        fields=self.model_dump(mode='json');fields.pop('release_hash')
        if digest(fields)!=self.release_hash:raise ValueError('Outer release identity changed')
        return self


def verify_release(path:Path)->ModelIdentity:
    """Verify evidence without importing ML libraries or changing core identity."""
    from app.topics.reviews import ReviewPack,ReviewReceipt,apply_review,verify_pack
    root=Path(path)
    identity=verify_manifest(root)
    try:
        release_path=root/'release.json';evidence=root/'evidence'
        if release_path.is_symlink() or evidence.is_symlink() or release_path.stat().st_size>65536:
            raise ValueError('Invalid release paths')
        release=ReleaseManifest.model_validate_json(release_path.read_text(encoding='utf-8'))
        if release.model_version!=identity.model_version:raise ValueError('Release belongs to another model')
        for name,record in release.files.items():
            local=evidence/name
            if local.is_symlink() or not local.is_file() or local.stat().st_size!=record.bytes or _sha(local)!=record.sha256:
                raise ValueError('Release evidence missing or changed')
        read=lambda name:json.loads((evidence/name).read_text(encoding='utf-8'))
        completion=read('evaluation-complete.json');selection=read('review-selection.json')
        for value,key in ((completion,'completion_hash'),(selection,'selection_hash')):
            if value.get(key)!=digest({k:v for k,v in value.items() if k!=key}):raise ValueError('Evaluation evidence identity changed')
        if (completion.get('model_version')!=identity.model_version or not completion.get('model_published')
                or completion.get('probe_passed') is not True or selection.get('model_version')!=identity.model_version
                or read('probe.json').get('passed') is not True or read('cpu-roundtrip.json').get('passed') is not True):
            raise ValueError('Model did not pass actual export checks')
        if bool(selection['errors_count'])!=bool(OPTIONAL_EVIDENCE<=set(release.files)):
            raise ValueError('Error review evidence is incomplete')
        for prefix,key in (('gold','gold_pack_hash'),('error','error_pack_hash')):
            if prefix=='error' and not selection['errors_count']:continue
            pack=ReviewPack.model_validate_json((evidence/f'{prefix}-pack.json').read_text(encoding='utf-8'))
            receipt=ReviewReceipt.model_validate_json((evidence/f'{prefix}-receipt.json').read_text(encoding='utf-8'))
            verify_pack(pack)
            if pack.pack_hash!=selection[key]:raise ValueError('Reviewed a different frozen selection')
            fields=receipt.model_dump(mode='json');fields.pop('receipt_hash')
            if receipt.receipt_hash!=digest(fields):raise ValueError('Review receipt changed')
            expected=apply_review(pack,receipt.decisions).model_dump(mode='json');actual=receipt.model_dump(mode='json')
            for value in (expected,actual):value.pop('created_at');value.pop('receipt_hash')
            report=read(f'{prefix}-report.json')
            if (actual!=expected or not receipt.samples or report.get('receipt_hash')!=receipt.receipt_hash
                    or report.get('model_version')!=identity.model_version):raise ValueError('Human review is incomplete or inconsistent')
        return identity
    except (OSError,KeyError,TypeError,json.JSONDecodeError) as exc:
        raise ValueError('Release evidence is unavailable or invalid') from exc
