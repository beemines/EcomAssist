"""Download a fixed public base and measure one full-parameter optimizer step."""

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
from uuid import uuid4


BASE_MODEL = 'hfl/chinese-roberta-wwm-ext'
BASE_REVISION = '5c58d0b8ec1d9014354d691c538661bf00bfdb44'
BASE_FILES = frozenset(('config.json', 'vocab.txt', 'pytorch_model.bin', 'tokenizer.json',
                        'tokenizer_config.json', 'special_tokens_map.json'))
REQUIRED_FILES = frozenset(('config.json', 'vocab.txt', 'pytorch_model.bin'))


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def verify_base(base_dir: Path) -> dict:
    """Verify provenance and every byte before passing any weight to Torch."""
    try:
        path = base_dir / 'base-receipt.json'
        if path.is_symlink() or path.stat().st_size > 64 * 1024:
            raise ValueError('Invalid base receipt file')
        receipt = json.loads(path.read_text(encoding='utf-8'))
        if (type(receipt) is not dict or set(receipt) != {'schema_version', 'model', 'revision', 'files'}
                or type(receipt['schema_version']) is not int or receipt['schema_version'] != 1
                or receipt['model'] != BASE_MODEL or receipt['revision'] != BASE_REVISION
                or type(receipt['files']) is not dict
                or not REQUIRED_FILES <= receipt['files'].keys()
                or not receipt['files'].keys() <= BASE_FILES):
            raise ValueError('Base identity does not match the approved fixed revision')
        for name, record in receipt['files'].items():
            local = base_dir / name
            if (type(record) is not dict or set(record) != {'sha256', 'bytes'}
                    or type(record['bytes']) is not int or record['bytes'] <= 0
                    or local.is_symlink() or not local.is_file()
                    or local.stat().st_size != record['bytes'] or file_hash(local) != record['sha256']):
                raise ValueError('Base file verification failed')
        return receipt
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ValueError('Base receipt is missing or invalid') from exc


def ensure_base(base_dir: Path) -> dict:
    if base_dir.exists():
        return verify_base(base_dir)
    from huggingface_hub import snapshot_download
    base_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = base_dir.parent / ('.base-download-' + uuid4().hex)
    snapshot_download(BASE_MODEL, revision=BASE_REVISION, local_dir=staging, token=False,
                      allow_patterns=sorted(BASE_FILES), max_workers=2)
    records = {path.name: {'sha256': file_hash(path), 'bytes': path.stat().st_size}
               for path in staging.iterdir() if path.name in BASE_FILES and path.is_file()}
    receipt = dict(schema_version=1, model=BASE_MODEL, revision=BASE_REVISION, files=records)
    (staging / 'base-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    verify_base(staging)
    os.rename(staging, base_dir)
    return receipt


def _probe(base_dir: Path, micro_batch: int) -> dict:
    import torch
    from transformers import AutoConfig, AutoModelForSequenceClassification, AutoTokenizer, set_seed
    from app.topics.taxonomy import default_taxonomy
    set_seed(20261021)
    taxonomy = default_taxonomy()
    config = AutoConfig.from_pretrained(base_dir, local_files_only=True, trust_remote_code=False)
    if (config.model_type != 'bert' or config.hidden_size != 768 or config.num_hidden_layers != 12
            or config.num_attention_heads != 12):
        raise ValueError('Base configuration is not the approved HFL BERT architecture')
    config.num_labels = 17
    config.problem_type = 'multi_label_classification'
    config.id2label = dict(enumerate(taxonomy.ordered_names))
    config.label2id = {name: index for index, name in config.id2label.items()}
    tokenizer = AutoTokenizer.from_pretrained(base_dir, local_files_only=True, trust_remote_code=False)
    model = AutoModelForSequenceClassification.from_pretrained(base_dir, config=config,
        local_files_only=True, trust_remote_code=False, use_safetensors=False, weights_only=True)
    model.gradient_checkpointing_enable()
    model.train().to('cuda')
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)
    scaler = torch.amp.GradScaler('cuda')
    encoded = tokenizer(['尺码不合适，需要换货。'] * micro_batch, padding='max_length',
        max_length=128, truncation=False, return_tensors='pt')
    encoded = {key: value.to('cuda') for key, value in encoded.items()}
    labels = torch.tensor([taxonomy.encode(('退换货', '尺码'))] * micro_batch,
                          device='cuda', dtype=torch.float32)
    torch.cuda.reset_peak_memory_stats()
    optimizer.zero_grad(set_to_none=True)
    with torch.autocast(device_type='cuda', dtype=torch.float16):
        output = model(**encoded, labels=labels)
    if not math.isfinite(output.loss.item()):
        raise ValueError('Nonfinite GPU probe loss')
    scaler.scale(output.loss).backward()
    if any(not parameter.requires_grad or parameter.grad is None for parameter in model.parameters()):
        raise ValueError('Not every model parameter participates in the training step')
    scaler.unscale_(optimizer)
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    scaler.step(optimizer)
    scaler.update()
    torch.cuda.synchronize()
    if len(optimizer.state) != len(list(model.parameters())):
        raise ValueError('The probe did not allocate full Adam state')
    result = dict(micro_batch=micro_batch, gradient_accumulation=16 // micro_batch,
        effective_batch=16, max_tokens=128, loss=output.loss.item(),
        parameters=sum(parameter.numel() for parameter in model.parameters()),
        trainable_parameters=sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad),
        optimizer_parameter_states=len(optimizer.state), peak_allocated_bytes=torch.cuda.max_memory_allocated(),
        peak_reserved_bytes=torch.cuda.max_memory_reserved(), weights_discarded=True)
    del optimizer, model, encoded, labels, output
    torch.cuda.empty_cache()
    return result


def doctor(base_dir: Path, *, probe: bool) -> dict:
    import torch
    receipt = ensure_base(base_dir)
    report = dict(python=platform.python_version(), model=BASE_MODEL, revision=BASE_REVISION,
        base_files=receipt['files'], cuda_available=torch.cuda.is_available(),
        dependency_lock_sha256=file_hash(Path(__file__).with_name('uv.lock')),
        torch_cuda=torch.version.cuda, versions={name: importlib.metadata.version(name) for name in
            ('torch', 'transformers', 'accelerate', 'numpy', 'scikit-learn', 'safetensors', 'huggingface-hub')})
    if probe:
        if not torch.cuda.is_available():
            raise RuntimeError('CUDA unavailable; the approved full GPU training cannot proceed')
        report['gpu'] = torch.cuda.get_device_name(0)
        report['gpu_total_bytes'] = torch.cuda.get_device_properties(0).total_memory
        attempts = []
        for micro_batch in (4, 2, 1):
            try:
                report['probe'] = _probe(base_dir, micro_batch)
                break
            except torch.OutOfMemoryError:
                attempts.append(dict(micro_batch=micro_batch, outcome='cuda_oom'))
                import gc
                gc.collect()
                torch.cuda.empty_cache()
        else:
            raise RuntimeError('Full-parameter probe cannot fit even at micro-batch 1')
        report['oom_attempts'] = attempts
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-dir', type=Path, required=True)
    parser.add_argument('--probe', action='store_true')
    args = parser.parse_args()
    report = doctor(args.base_dir, probe=args.probe)
    destination = args.base_dir.parent / 'doctor.json'
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
