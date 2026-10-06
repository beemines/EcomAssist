from pathlib import Path
from typing import Literal

from pydantic import Field, HttpUrl, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
        populate_by_name=True,
        hide_input_in_errors=True,
        allow_inf_nan=False,
    )

    llm_base_url: HttpUrl = Field(validation_alias="LLM_BASE_URL")
    llm_model: str = Field(validation_alias="LLM_MODEL")
    llm_api_key: SecretStr = Field(validation_alias="LLM_API_KEY")
    llm_token_limit_field: Literal["max_tokens", "max_completion_tokens"] = Field(
        default="max_tokens", validation_alias="LLM_TOKEN_LIMIT_FIELD"
    )
    input_token_budget: int = Field(default=2000, gt=0, validation_alias="INPUT_TOKEN_BUDGET")
    max_output_tokens: int = Field(default=512, gt=0, validation_alias="MAX_OUTPUT_TOKENS")
    llm_timeout_seconds: float = Field(default=60.0, gt=0, validation_alias="LLM_TIMEOUT_SECONDS")
    mysql_host: str = Field(default="127.0.0.1", validation_alias="MYSQL_HOST")
    mysql_port: int = Field(default=3307, gt=0, le=65535, validation_alias="MYSQL_PORT")
    mysql_database: str = Field(default="customer_service", validation_alias="MYSQL_DATABASE")
    mysql_user: str = Field(default="customer_service", validation_alias="MYSQL_USER")
    mysql_password: SecretStr | None = Field(default=None, validation_alias="MYSQL_PASSWORD")
    mysql_root_password: SecretStr | None = Field(default=None, validation_alias="MYSQL_ROOT_PASSWORD")
    tool_input_token_budget: int = Field(default=8000, gt=0, validation_alias="TOOL_INPUT_TOKEN_BUDGET")
    tool_timeout_seconds: float = Field(default=5.0, gt=0, validation_alias="TOOL_TIMEOUT_SECONDS")
    tool_max_retries: int = Field(default=1, ge=0, le=1, validation_alias="TOOL_MAX_RETRIES")

    @property
    def database_url(self) -> URL:
        # 使用 URL.create 保留原始密码，避免特殊字符被当作 URL 分隔符。
        if self.mysql_password is None or not self.mysql_password.get_secret_value().strip():
            raise ValueError("MYSQL_PASSWORD is required for database access")
        return URL.create(
            "mysql+aiomysql",
            username=self.mysql_user,
            password=self.mysql_password.get_secret_value(),
            host=self.mysql_host,
            port=self.mysql_port,
            database=self.mysql_database,
            query={"charset": "utf8mb4"},
        )

    @field_validator("llm_model")
    @classmethod
    def model_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("model must not be blank")
        return value

    @field_validator("llm_api_key")
    @classmethod
    def api_key_must_not_be_blank(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("API key must not be blank")
        return value


def load_settings(env_file: Path | str = ".env") -> Settings:
    return Settings(_env_file=env_file)
