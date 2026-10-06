import pytest
from pydantic import ValidationError

from tests.fakes import fake_settings


def test_db_defaults_and_secret_url():
    settings = fake_settings(mysql_password="a@:/b", mysql_root_password="root-test")
    assert settings.mysql_host == "127.0.0.1"
    assert settings.mysql_port == 3307
    assert settings.mysql_database == settings.mysql_user == "customer_service"
    assert settings.database_url.drivername == "mysql+aiomysql"
    assert settings.database_url.password == "a@:/b"
    assert settings.database_url.query == {"charset": "utf8mb4"}
    assert settings.tool_input_token_budget == 8000
    assert settings.tool_timeout_seconds == 5
    assert settings.tool_max_retries == 1
    assert "a@:/b" not in repr(settings)
    assert "root-test" not in repr(settings)


def test_db_password_required_only_when_url_is_requested():
    settings = fake_settings()
    with pytest.raises(ValueError, match="MYSQL_PASSWORD"):
        _ = settings.database_url


@pytest.mark.parametrize("overrides", [
    {"tool_input_token_budget": 0}, {"tool_timeout_seconds": 0},
    {"tool_max_retries": -1}, {"tool_max_retries": 2},
    {"mysql_port": 0}, {"mysql_port": 65536},
])
def test_db_and_tool_config_reject_invalid_limits(overrides):
    with pytest.raises(ValidationError):
        fake_settings(**overrides)


@pytest.mark.parametrize("retries", [0, 1])
def test_tool_retry_limit_accepts_supported_values(retries):
    assert fake_settings(tool_max_retries=retries).tool_max_retries == retries
