from tests.fakes import fake_settings


def test_test_cli_target_is_fixed_and_does_not_mutate_original_settings():
    from app.flywheel.cli import database_url
    settings = fake_settings(mysql_password='test-only', mysql_port=3307, mysql_database='customer_service')
    test_url = database_url(settings, 'test')
    assert (test_url.host, test_url.port, test_url.database) == ('127.0.0.1', 3308, 'customer_service_test')
    assert settings.mysql_port == 3307 and settings.mysql_database == 'customer_service'
    configured = database_url(settings, 'configured')
    assert configured.port == 3307 and configured.database == 'customer_service'
