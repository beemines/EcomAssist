import json
from types import SimpleNamespace

import pytest
from dotenv import dotenv_values


def test_prepare_is_idempotent_and_separates_sdk_from_server_secrets(tmp_path):
    from app.observability.local_stack import prepare
    prepare(tmp_path, port=3010)
    env_path = tmp_path / 'local.env'
    first = env_path.read_bytes()
    prepare(tmp_path, port=3010)
    assert env_path.read_bytes() == first
    server = dotenv_values(env_path)
    sdk = dotenv_values(tmp_path / 'sdk.env')
    assert sdk['LANGFUSE_BASE_URL'] == 'http://127.0.0.1:3010'
    assert sdk['LANGFUSE_PUBLIC_KEY'] == server['LANGFUSE_INIT_PROJECT_PUBLIC_KEY']
    assert sdk['LANGFUSE_SECRET_KEY'] == server['LANGFUSE_INIT_PROJECT_SECRET_KEY']
    assert 'POSTGRES_PASSWORD' not in sdk
    assert set(sdk) == {'LANGFUSE_ENABLED', 'LANGFUSE_BASE_URL',
                        'LANGFUSE_PUBLIC_KEY', 'LANGFUSE_SECRET_KEY'}
    assert len(server['ENCRYPTION_KEY']) == 64
    assert len(server['LANGFUSE_INIT_USER_PASSWORD']) >= 24


def test_prepare_does_not_replace_credentials_for_different_port(tmp_path):
    from app.observability.local_stack import prepare
    prepare(tmp_path, port=3000)
    original = (tmp_path / 'local.env').read_bytes()
    with pytest.raises(ValueError):
        prepare(tmp_path, port=3001)
    assert (tmp_path / 'local.env').read_bytes() == original


def test_prepare_rejects_partial_state_instead_of_resetting_passwords(tmp_path):
    from app.observability.local_stack import prepare
    (tmp_path / 'local.env').write_text('SALT=old\n', encoding='utf-8')
    with pytest.raises(ValueError):
        prepare(tmp_path)
    assert (tmp_path / 'local.env').read_text() == 'SALT=old\n'


def test_refuses_to_manage_project_containers_owned_by_another_checkout(monkeypatch, tmp_path):
    from app.observability import local_stack

    def docker_response(*args, **kwargs):
        if args[0] == 'ps':
            return 'abc123\n'
        assert args[:2] == ('inspect', 'abc123')
        return json.dumps({'com.docker.compose.project.working_dir': str(tmp_path / 'other')})

    monkeypatch.setattr(local_stack, '_docker', docker_response)
    with pytest.raises(RuntimeError, match='another checkout'):
        local_stack._owned_containers()


def test_docker_failure_keeps_redacted_local_diagnostic(monkeypatch, tmp_path):
    from app.observability import local_stack
    local_stack.prepare(tmp_path / 'runtime/langfuse')
    values = dotenv_values(tmp_path / 'runtime/langfuse/local.env')
    secret = values['LANGFUSE_INIT_PROJECT_SECRET_KEY']
    monkeypatch.setattr(local_stack, 'ROOT', tmp_path)
    monkeypatch.setattr(local_stack.subprocess, 'run', lambda *args, **kwargs:
        SimpleNamespace(returncode=1, stdout='', stderr=f'registry connection failed; key={secret}'))
    with pytest.raises(RuntimeError) as error:
        local_stack._docker('compose', 'up')
    assert secret not in str(error.value)
    diagnostic = (tmp_path / 'runtime/langfuse/docker-error.log').read_text(encoding='utf-8')
    assert 'registry connection failed' in diagnostic
    assert secret not in diagnostic
