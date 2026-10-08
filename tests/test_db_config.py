import pytest
from pydantic import ValidationError

from tests.fakes import fake_settings


# 验证数据库与工具默认设置、特殊字符密码 URL 及设置表示中的密码脱敏。
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


# 验证普通设置可无数据库密码，访问数据库 URL 时才要求提供密码。
def test_db_password_required_only_when_url_is_requested():
    settings = fake_settings()
    with pytest.raises(ValueError, match="MYSQL_PASSWORD"):
        _ = settings.database_url


# 验证非法端口、非正预算与超时以及不支持的重试次数被拒绝。
@pytest.mark.parametrize("overrides", [
    {"tool_input_token_budget": 0}, {"tool_timeout_seconds": 0},
    {"tool_max_retries": -1}, {"tool_max_retries": 2},
    {"mysql_port": 0}, {"mysql_port": 65536},
])
def test_db_and_tool_config_reject_invalid_limits(overrides):
    with pytest.raises(ValidationError):
        fake_settings(**overrides)


# 验证工具重试次数接受零次和一次两个支持值。
@pytest.mark.parametrize("retries", [0, 1])
def test_tool_retry_limit_accepts_supported_values(retries):
    assert fake_settings(tool_max_retries=retries).tool_max_retries == retries
