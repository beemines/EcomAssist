"""Context CLI exposes explicit migration and read-only verification, without secrets."""
import importlib

import pytest


@pytest.mark.parametrize('command', ['migrate', 'verify'])
def test_context_cli_dispatches_and_disposes(monkeypatch, capsys, command):
    cli = importlib.import_module('app.context.cli')
    from tests.fakes import fake_settings
    events = []

    class Database:
        def __init__(self, url):
            pass

        async def dispose(self):
            events.append('disposed')

    async def migrate(database):
        events.append('migrate')

    async def verify(database):
        events.append('verify')

    monkeypatch.setattr(cli, 'load_settings', lambda: fake_settings(mysql_password='fake-only'))
    monkeypatch.setattr(cli, 'Database', Database)
    monkeypatch.setattr(cli, 'migrate_context', migrate)
    monkeypatch.setattr(cli, 'verify_context', verify)
    assert cli.main([command]) == 0
    assert events == [command, 'disposed']
    assert 'ready' in capsys.readouterr().out.lower()


def test_context_cli_failure_hides_database_url_and_password(monkeypatch, capsys):
    cli = importlib.import_module('app.context.cli')

    async def failure(args):
        raise RuntimeError('mysql://private:SECRET@private-host/private-db')

    monkeypatch.setattr(cli, 'run', failure)
    assert cli.main(['verify']) == 1
    output = capsys.readouterr()
    assert 'RuntimeError' in output.err
    assert not any(value in output.out + output.err for value in ('SECRET', 'private', 'mysql://'))
