# 统一读取环境变量和 UTF-8 的 .env，校验模型、工具、MySQL 与 Milvus 配置。
from pathlib import Path
from typing import Literal

from pydantic import Field, HttpUrl, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    # 严格配置字段并隐藏校验异常中的输入值，防止错误输出带出真实密钥。
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
        populate_by_name=True,
        hide_input_in_errors=True,
        allow_inf_nan=False,
    )

    # 在线客服使用同一套模型地址、名称和密钥，通过环境变量切换上游。
    llm_base_url: HttpUrl = Field(validation_alias="LLM_BASE_URL")
    llm_model: str = Field(validation_alias="LLM_MODEL")
    llm_api_key: SecretStr = Field(validation_alias="LLM_API_KEY")
    # 知识库使用独立嵌入密钥，Dense 模型固定 BGE-M3，并分别设置 HTTP 与向量服务超时。
    siliconflow_api_key: SecretStr | None = Field(default=None, validation_alias="SILICONFLOW_API_KEY")
    embedding_model: Literal['BAAI/bge-m3'] = Field(default='BAAI/bge-m3', validation_alias='EMBEDDING_MODEL')
    embedding_timeout_seconds: float = Field(default=20, gt=0, validation_alias='EMBEDDING_TIMEOUT_SECONDS')
    milvus_uri: HttpUrl = Field(default='http://127.0.0.1:19530', validation_alias='MILVUS_URI')
    milvus_timeout_seconds: float = Field(default=5, gt=0, validation_alias='MILVUS_TIMEOUT_SECONDS')
    # 不同上游接受的输出上限字段可能不同，但应用只开放这两个协议字段。
    llm_token_limit_field: Literal["max_tokens", "max_completion_tokens"] = Field(
        default="max_tokens", validation_alias="LLM_TOKEN_LIMIT_FIELD"
    )
    # 在线输入预算、在线回答上限和离线 QA 抽取上限各自独立，避免互相挤占。
    input_token_budget: int = Field(default=2000, gt=0, validation_alias="INPUT_TOKEN_BUDGET")
    max_output_tokens: int = Field(default=512, gt=0, validation_alias="MAX_OUTPUT_TOKENS")
    qa_max_output_tokens: int = Field(default=2048, gt=0, validation_alias="QA_MAX_OUTPUT_TOKENS")
    llm_timeout_seconds: float = Field(default=60.0, gt=0, validation_alias="LLM_TIMEOUT_SECONDS")
    # MySQL 地址默认对应业务 Compose 实例，根用户密码仅供显式管理/测试操作使用。
    mysql_host: str = Field(default="127.0.0.1", validation_alias="MYSQL_HOST")
    mysql_port: int = Field(default=3307, gt=0, le=65535, validation_alias="MYSQL_PORT")
    mysql_database: str = Field(default="customer_service", validation_alias="MYSQL_DATABASE")
    mysql_user: str = Field(default="customer_service", validation_alias="MYSQL_USER")
    mysql_password: SecretStr | None = Field(default=None, validation_alias="MYSQL_PASSWORD")
    mysql_root_password: SecretStr | None = Field(default=None, validation_alias="MYSQL_ROOT_PASSWORD")
    # 工具输入含 Schema 和结果，超时与重试有硬上限，重试可关闭但不能无限增加。
    tool_input_token_budget: int = Field(default=8000, gt=0, validation_alias="TOOL_INPUT_TOKEN_BUDGET")
    tool_timeout_seconds: float = Field(default=5.0, gt=0, validation_alias="TOOL_TIMEOUT_SECONDS")
    tool_max_retries: int = Field(default=1, ge=0, le=1, validation_alias="TOOL_MAX_RETRIES")

    # 校验数据库密码并构造保留特殊字符的异步 MySQL 连接地址。
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

    # 拒绝全空白的模型名称，同时保留合法配置的原始值。
    @field_validator("llm_model")
    @classmethod
    def model_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("model must not be blank")
        return value

    # 在整数转换前排除布尔值，避免把开关误当作 QA 输出预算。
    @field_validator('qa_max_output_tokens', mode='before')
    @classmethod
    def qa_output_budget_must_not_be_bool(cls, value):
        if isinstance(value, bool):
            raise ValueError('QA output budget must be a positive integer')
        return value

    # 拒绝全空白的模型密钥，保持密钥包装类型不变。
    @field_validator("llm_api_key")
    @classmethod
    def api_key_must_not_be_blank(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("API key must not be blank")
        return value


# 从指定环境文件和环境变量加载经过校验的应用配置。
def load_settings(env_file: Path | str = ".env") -> Settings:
    return Settings(_env_file=env_file)
