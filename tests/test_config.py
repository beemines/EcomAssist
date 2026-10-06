import pytest
from pydantic import SecretStr, ValidationError

from app.config import Settings, load_settings


ENV_NAMES = (
    "LLM_BASE_URL", "LLM_MODEL", "LLM_API_KEY", "LLM_TOKEN_LIMIT_FIELD",
    "INPUT_TOKEN_BUDGET", "MAX_OUTPUT_TOKENS", "LLM_TIMEOUT_SECONDS",
)


@pytest.fixture(autouse=True)
def isolate_settings_environment(monkeypatch):
    for name in ENV_NAMES:
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def dotenv(tmp_path):
    path = tmp_path / ".env"
    path.write_text(
        "LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/\n"
        "LLM_MODEL=glm-5.3-flash\nLLM_API_KEY=test-secret\n",
        encoding="utf-8",
    )
    return path


def test_load_settings_uses_dotenv_with_independent_default_budgets(dotenv):
    settings = load_settings(dotenv)
    assert settings.llm_model == "glm-5.3-flash"
    assert str(settings.llm_base_url) == "https://open.bigmodel.cn/api/paas/v4/"
    assert settings.input_token_budget == 2000
    assert settings.max_output_tokens == 512
    assert settings.llm_timeout_seconds == 60.0
    assert settings.llm_token_limit_field == "max_tokens"
    assert isinstance(settings.llm_api_key, SecretStr)
    assert "test-secret" not in repr(settings)
    assert "test-secret" not in settings.model_dump_json()


def test_default_dotenv_is_relative_to_current_directory(dotenv, monkeypatch):
    monkeypatch.chdir(dotenv.parent)
    assert load_settings().llm_model == "glm-5.3-flash"


def test_load_settings_accepts_string_path(dotenv):
    assert load_settings(str(dotenv)).llm_model == "glm-5.3-flash"


def test_environment_overrides_dotenv_and_init_overrides_environment(dotenv, monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "environment-model")
    assert Settings(_env_file=dotenv).llm_model == "environment-model"
    assert Settings(_env_file=dotenv, llm_model="direct-model").llm_model == "direct-model"


@pytest.mark.parametrize("name,value,field,expected", [
    ("INPUT_TOKEN_BUDGET", "3000", "input_token_budget", 3000),
    ("MAX_OUTPUT_TOKENS", "1024", "max_output_tokens", 1024),
    ("LLM_TIMEOUT_SECONDS", "12.5", "llm_timeout_seconds", 12.5),
    ("LLM_TOKEN_LIMIT_FIELD", "max_completion_tokens", "llm_token_limit_field", "max_completion_tokens"),
    ("LLM_BASE_URL", "http://localhost:11434/v1/", "llm_base_url", "http://localhost:11434/v1/"),
])
def test_environment_names_set_corresponding_fields(dotenv, monkeypatch, name, value, field, expected):
    monkeypatch.setenv(name, value)
    actual = getattr(Settings(_env_file=dotenv), field)
    assert (str(actual) if field == "llm_base_url" else actual) == expected


@pytest.mark.parametrize("name,value", [
    ("LLM_API_KEY", ""), ("LLM_API_KEY", " \t "),
    ("LLM_MODEL", ""), ("LLM_MODEL", " \t "),
    ("LLM_BASE_URL", "not-a-url"), ("LLM_BASE_URL", "ftp://example.com/v1/"),
    ("INPUT_TOKEN_BUDGET", "0"), ("INPUT_TOKEN_BUDGET", "-1"),
    ("MAX_OUTPUT_TOKENS", "0"), ("MAX_OUTPUT_TOKENS", "-1"),
    ("LLM_TIMEOUT_SECONDS", "0"), ("LLM_TIMEOUT_SECONDS", "-1"),
    ("LLM_TIMEOUT_SECONDS", "inf"), ("LLM_TIMEOUT_SECONDS", "nan"),
    ("LLM_TOKEN_LIMIT_FIELD", "unsupported"),
])
def test_invalid_settings_are_rejected(dotenv, monkeypatch, name, value):
    monkeypatch.setenv(name, value)
    with pytest.raises(ValidationError):
        Settings(_env_file=dotenv)


def test_valid_api_key_is_not_stripped(dotenv, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", " test-secret ")
    assert Settings(_env_file=dotenv).llm_api_key.get_secret_value() == " test-secret "


def test_unknown_dotenv_keys_rejected_without_sensitive_error_text(dotenv):
    with dotenv.open("a", encoding="utf-8") as file:
        file.write("UNKNOWN_KEY=test-secret\n")
    with pytest.raises(ValidationError) as exc:
        load_settings(dotenv)
    assert "test-secret" not in str(exc.value)
    assert "test-secret" not in repr(exc.value)


def test_secret_validation_input_is_hidden(dotenv):
    with pytest.raises(ValidationError) as exc:
        Settings(_env_file=dotenv, llm_api_key={"secret": "test-secret"})
    assert "test-secret" not in str(exc.value)


@pytest.mark.parametrize("missing", ["LLM_BASE_URL", "LLM_MODEL", "LLM_API_KEY"])
def test_upstream_fields_are_required(dotenv, missing):
    lines = dotenv.read_text(encoding="utf-8").splitlines()
    dotenv.write_text("\n".join(line for line in lines if not line.startswith(missing + "=")), encoding="utf-8")
    with pytest.raises(ValidationError):
        load_settings(dotenv)
