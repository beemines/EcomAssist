from datetime import datetime, timezone
from contextlib import asynccontextmanager

import pytest

from app.knowledge import cli


def test_mining_arguments_parse_iso_windows_and_default_batch():
    args = cli.parser().parse_args(['mine-conversations', '--start', '2026-10-06', '--end', '2026-10-07'])
    assert args.start == datetime(2026, 10, 6) and args.end == datetime(2026, 10, 7)
    assert args.batch_size == 20


def test_daily_uses_previous_beijing_day_including_utc_boundary():
    assert hasattr(cli, 'previous_day'), 'Beijing daily window is missing'
    assert cli.previous_day(datetime(2026, 10, 6, 17, tzinfo=timezone.utc)) == (datetime(2026, 10, 6), datetime(2026, 10, 7))


@pytest.mark.parametrize('command', ['deduplicate-staging', 'run-daily'])
def test_new_entry_commands_are_available(command):
    assert cli.parser().parse_args([command]).command == command


def test_job_failure_is_nonzero_and_hides_upstream_details(monkeypatch, capsys):
    async def fail(args):
        raise RuntimeError('SECRET synthetic data')
    monkeypatch.setattr(cli, 'run', fail)
    assert cli.main(['run-daily']) == 1
    assert 'SECRET' not in capsys.readouterr().err


@pytest.mark.parametrize('failure', [None, 'extract', 'vector', 'model_close'])
async def test_daily_holds_one_lock_and_closes_owned_resources(monkeypatch, failure, capsys):
    from tests.fakes import fake_settings
    from tests.test_knowledge_extraction import Model, conversation
    from tests.test_knowledge_mining import Repository
    events = []
    class Database:
        def __init__(self, url): pass
        async def dispose(self): events.append('database_closed')
    @asynccontextmanager
    async def lock(database):
        assert 'lock_acquired' not in events
        events.append('lock_acquired')
        try:
            yield
        finally:
            events.append('lock_released')
    class History:
        def __init__(self, db): pass
        async def completed(self, start, end, after_id=0, limit=20):
            assert start < end
            assert 'lock_released' not in events
            return [conversation()] if after_id == 0 else []
    class Client:
        def close(self): events.append('sync_model_closed')
    class AsyncClient:
        async def close(self):
            events.append('async_model_closed')
            if failure == 'model_close': raise RuntimeError('controlled close')
    class Index:
        def __init__(self, *a, **kw): pass
        async def ensure_collection(self): events.append('index_ready')
        async def aclose(self): events.append('index_closed')
    class Embedder:
        def __init__(self, settings): pass
        async def aclose(self): events.append('embedder_closed')
    class Vectorizer:
        def __init__(self, *a): pass
        async def run(self, batch):
            assert 'lock_released' not in events
            if failure == 'vector': raise RuntimeError('controlled vector')
            events.append('vectorized')
            return 0
    model = Model(fault=RuntimeError('controlled extraction') if failure == 'extract' else None)
    model.root_client, model.root_async_client = Client(), AsyncClient()
    online_settings = fake_settings(mysql_password='fake-only', input_token_budget=10000, max_output_tokens=512)
    monkeypatch.setattr(cli, 'load_settings', lambda: online_settings)
    monkeypatch.setattr(cli, 'previous_day', lambda: (datetime(2026, 10, 6), datetime(2026, 10, 7)))
    def model_factory(settings):
        assert settings.max_output_tokens == 2048
        assert settings.llm_model == online_settings.llm_model
        assert settings.llm_base_url == online_settings.llm_base_url
        assert settings.llm_api_key == online_settings.llm_api_key
        return model
    for name, value in [('Database', Database), ('job_lock', lock), ('KnowledgeHistory', History), ('KnowledgeRepository', lambda db: Repository()), ('create_model', model_factory), ('MilvusIndex', Index), ('SiliconFlowEmbedder', Embedder), ('PendingVectorizer', Vectorizer)]:
        monkeypatch.setattr(cli, name, value)
    if failure:
        with pytest.raises(Exception):
            await cli.run(cli.parser().parse_args(['run-daily']))
    else:
        await cli.run(cli.parser().parse_args(['run-daily']))
        assert 'vectorized' in events
        output = capsys.readouterr().out
        assert '2026-10-06' in output and '2026-10-07' in output
    assert events[-2:] == ['lock_released', 'database_closed']
    assert online_settings.max_output_tokens == 512
    assert events.count('lock_acquired') == 1
    assert events.count('async_model_closed') == events.count('sync_model_closed') == 1
    if failure != 'extract':
        assert events.count('embedder_closed') == events.count('index_closed') == 1


def test_powershell_launcher_fixes_directory_and_preserves_child_exit_code():
    import json
    from pathlib import Path
    import shutil
    import subprocess
    shell = shutil.which('pwsh') or shutil.which('powershell')
    if shell is None:
        pytest.skip('PowerShell launcher requires a Windows shell')
    script = Path(__file__).resolve().parents[1] / 'scripts/run-knowledge-daily.ps1'
    # Shadow only the external uv boundary; execute the actual launcher.
    code = "function uv { @{cwd=(Get-Location).Path; argv=$args} | ConvertTo-Json -Compress; $global:LASTEXITCODE=23 }; & '" + str(script).replace("'", "''") + "'; exit $LASTEXITCODE"
    result = subprocess.run([shell, '-NoProfile', '-Command', code], capture_output=True, text=True)
    assert result.returncode == 23
    invocation = json.loads(result.stdout)
    assert invocation['cwd'] == 'D:\\shixi\\ecommerce-customer-service'
    assert invocation['argv'] == ['--directory', 'D:\\shixi\\ecommerce-customer-service', 'run', 'python', '-m', 'app.knowledge.cli', 'run-daily']
