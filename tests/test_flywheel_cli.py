from tests.fakes import fake_settings


def test_test_cli_target_is_fixed_and_does_not_mutate_original_settings():
    from app.flywheel.cli import database_url
    settings = fake_settings(mysql_password='test-only', mysql_port=3307, mysql_database='customer_service')
    test_url = database_url(settings, 'test')
    assert (test_url.host, test_url.port, test_url.database) == ('127.0.0.1', 3308, 'customer_service_test')
    assert settings.mysql_port == 3307 and settings.mysql_database == 'customer_service'
    configured = database_url(settings, 'configured')
    assert configured.port == 3307 and configured.database == 'customer_service'


def test_process_is_dry_by_default_and_does_not_load_credentials(monkeypatch, capsys):
    from app.flywheel import cli
    def forbidden(): raise AssertionError('Dry command read credentials')
    monkeypatch.setattr(cli, 'load_settings', forbidden)
    cli.main(['process', '--database', 'test', '--pool-id', '1'])
    assert 'dry-run' in capsys.readouterr().out


def test_management_always_requires_one_canonical_selected_id():
    import pytest
    from app.flywheel import cli
    for args in (['process', '--database', 'test'],
                 ['initialize', '--database', 'test', '--pool-id', '01']):
        with pytest.raises(SystemExit):
            cli.main(args)


def test_ch09_budget_helper_reuses_the_same_persistent_run_after_recreation(tmp_path):
    import pytest
    from app.flywheel.acceptance import acceptance_cap, RUN_ID
    from app.context.acceptance import AcceptanceLimitExceeded
    first = acceptance_cap(RUN_ID, root=tmp_path)
    for _ in range(280):
        first.reserve('glm')
    second = acceptance_cap(RUN_ID, root=tmp_path)
    with pytest.raises(AcceptanceLimitExceeded):
        second.reserve('glm')
    assert second.status()['counts'] == {'glm': 280, 'embedding': 0, 'rerank': 0}
    with pytest.raises(ValueError):
        acceptance_cap('different-run', root=tmp_path)


def test_publication_commands_are_single_id_and_dry_by_default(monkeypatch, capsys):
    import pytest
    from app.flywheel import cli
    monkeypatch.setattr(cli, 'load_settings', lambda: pytest.fail('Dry-run read credentials'))
    cli.main(['publish', '--database', 'test', '--review-id', '1'])
    cli.main(['retry-publication', '--database', 'test', '--review-id', '1'])
    assert capsys.readouterr().out.count('dry-run') == 2
    with pytest.raises(SystemExit): cli.main(['publish', '--database', 'test'])


def test_history_batch_defaults_to_no_credentials_and_requires_a_bounded_range(monkeypatch,capsys):
    import pytest
    from app.flywheel import cli
    monkeypatch.setattr(cli,'load_settings',lambda:pytest.fail('Dry-run read credentials'))
    cli.main(['batch','--database','test','--from-id','1','--to-id','20','--limit','5'])
    assert 'dry-run' in capsys.readouterr().out
    for arguments in (['batch','--database','test'],
        ['batch','--database','test','--from-id','20','--to-id','1'],
        ['batch','--database','test','--from-id','1','--to-id','20','--limit','101']):
        with pytest.raises(SystemExit): cli.main(arguments)
