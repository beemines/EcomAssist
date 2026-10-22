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
