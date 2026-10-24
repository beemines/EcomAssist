"""A downloaded base must match its fixed provenance before any deserialization."""

import hashlib
import json

import pytest

from ml.topic_classifier.doctor import BASE_MODEL, BASE_REVISION, verify_base


def base_files(tmp_path):
    files = {}
    for name, content in {'config.json': b'{"model_type":"bert"}',
                          'vocab.txt': b'[PAD]\n[UNK]\n',
                          'pytorch_model.bin': b'not-unpickled-by-verifier'}.items():
        (tmp_path / name).write_bytes(content)
        files[name] = {'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}
    receipt = dict(schema_version=1, model=BASE_MODEL, revision=BASE_REVISION, files=files)
    (tmp_path / 'base-receipt.json').write_text(json.dumps(receipt), encoding='utf-8')
    return receipt


def test_valid_base_verifies_bytes_without_deserializing_weights(tmp_path):
    receipt = base_files(tmp_path)
    assert verify_base(tmp_path) == receipt


@pytest.mark.parametrize('change', ['revision', 'hash', 'size', 'missing', 'escape', 'extra', 'bool_size'])
def test_invalid_base_is_rejected_before_loading(tmp_path, change):
    receipt = base_files(tmp_path)
    if change == 'revision':
        receipt['revision'] = 'main'
    elif change == 'hash':
        receipt['files']['pytorch_model.bin']['sha256'] = '0' * 64
    elif change == 'size':
        receipt['files']['pytorch_model.bin']['bytes'] += 1
    elif change == 'missing':
        (tmp_path / 'vocab.txt').unlink()
    elif change == 'escape':
        receipt['files']['../escape'] = receipt['files']['vocab.txt']
    elif change == 'extra':
        receipt['trust_remote_code'] = True
    else:
        receipt['files']['vocab.txt']['bytes'] = True
    (tmp_path / 'base-receipt.json').write_text(json.dumps(receipt), encoding='utf-8')
    with pytest.raises(ValueError):
        verify_base(tmp_path)


def test_unreceipted_existing_base_is_not_silently_trusted(tmp_path):
    (tmp_path / 'pytorch_model.bin').write_bytes(b'unverified')
    with pytest.raises(ValueError):
        verify_base(tmp_path)
