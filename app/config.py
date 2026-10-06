from pathlib import Path
from typing import Literal

from pydantic import Field, HttpUrl, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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
