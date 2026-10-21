"""The side-channel profile cannot change budgets or select a remote endpoint."""
import json
from pathlib import Path
import pytest

from app.topics.profile import load_profile


def test_relative_paths_are_frozen_against_the_profile_directory(tmp_path):
    path = tmp_path/'profile.json'
    path.write_text(json.dumps(dict(service_url='http://localhost:8103/',
        manifest_path='bundle/manifest.json', runtime_root='runtime')), encoding='utf-8')
    result = load_profile(path)
    assert result.service_url == 'http://127.0.0.1:8103'
    assert result.manifest_path == tmp_path/'bundle/manifest.json'
    assert result.runtime_root == tmp_path/'runtime'
    assert not result.runtime_root.exists()  # Reading a profile is never initialization.


@pytest.mark.parametrize('change', [dict(service_url='https://external.invalid'),
    dict(budget_path='different.sqlite3'), dict(runtime_root=''), dict(manifest_path=None)])
def test_profile_rejects_remote_secret_extra_and_invalid_fields(tmp_path, change):
    path = tmp_path/'profile.json'
    path.write_text(json.dumps(dict(service_url='http://127.0.0.1:8103', manifest_path='manifest.json',
        runtime_root='runtime') | change), encoding='utf-8')
    with pytest.raises(ValueError):
        load_profile(path)


def test_profile_rejects_duplicate_keys_and_unbounded_files(tmp_path):
    path = tmp_path/'profile.json'
    path.write_text('{"service_url":"http://127.0.0.1:8103","service_url":"http://127.0.0.1:8104"}', encoding='utf-8')
    with pytest.raises(ValueError):
        load_profile(path)
    path.write_text(' '*20000, encoding='utf-8')
    with pytest.raises(ValueError):
        load_profile(path)
