# 统一读取环境变量和 UTF-8 的 .env，校验模型、工具、MySQL 与 Milvus 配置。
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, HttpUrl, SecretStr, field_validator, model_validator
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
    # 在线低思考由在线资源拥有者显式启用；缺省省略，与评估专属参数相互独立。
    online_reasoning_effort: Literal['low'] | None = Field(
        default=None, validation_alias='ONLINE_REASONING_EFFORT')
    # 知识库使用独立嵌入密钥，Dense 模型固定 BGE-M3，并分别设置 HTTP 与向量服务超时。
    siliconflow_api_key: SecretStr | None = Field(default=None, validation_alias="SILICONFLOW_API_KEY")
    embedding_model: Literal['BAAI/bge-m3'] = Field(default='BAAI/bge-m3', validation_alias='EMBEDDING_MODEL')
    embedding_timeout_seconds: float = Field(default=20, gt=0, validation_alias='EMBEDDING_TIMEOUT_SECONDS')
    milvus_uri: HttpUrl = Field(default='http://127.0.0.1:19530', validation_alias='MILVUS_URI')
    # 新检索链路使用独立混合集合，旧稠密评估仍保留原集合。
    milvus_collection: str = Field(default='knowledge_hybrid', min_length=1, validation_alias='MILVUS_COLLECTION')
    milvus_timeout_seconds: float = Field(default=5, gt=0, validation_alias='MILVUS_TIMEOUT_SECONDS')
    # 重排型号固定；离线校准可缺阈值，线上充分性/启动检查必须拒绝缺失阈值。
    rerank_model: Literal['BAAI/bge-reranker-v2-m3'] = Field(default='BAAI/bge-reranker-v2-m3', validation_alias='RERANK_MODEL')
    rerank_timeout_seconds: float = Field(default=20, gt=0, validation_alias='RERANK_TIMEOUT_SECONDS')
    query_timeout_seconds: float = Field(default=60, gt=0, le=60, validation_alias='QUERY_TIMEOUT_SECONDS')
    sufficiency_timeout_seconds: float = Field(default=20, gt=0, validation_alias='SUFFICIENCY_TIMEOUT_SECONDS')
    rerank_min_score: float | None = Field(default=None, validation_alias='RERANK_MIN_SCORE')
    # 不同上游接受的输出上限字段可能不同，但应用只开放这两个协议字段。
    llm_token_limit_field: Literal["max_tokens", "max_completion_tokens"] = Field(
        default="max_tokens", validation_alias="LLM_TOKEN_LIMIT_FIELD"
    )
    # 在线输入预算、在线回答上限和离线 QA 抽取上限各自独立，避免互相挤占。
    input_token_budget: int = Field(default=2000, gt=0, validation_alias="INPUT_TOKEN_BUDGET")
    max_output_tokens: int = Field(default=512, gt=0, validation_alias="MAX_OUTPUT_TOKENS")
    # 应用声明窗口，并非已经验证的供应商上限；Workflow实际接线统一使用派生预算。
    model_context_window: int = Field(default=128000, gt=0, validation_alias='MODEL_CONTEXT_WINDOW')
    max_user_input_tokens: int = Field(default=2000, gt=0, validation_alias='MAX_USER_INPUT_TOKENS')
    max_agent_steps: int = Field(default=4, gt=0, le=4, validation_alias='MAX_AGENT_STEPS')
    tool_result_max_tokens: int = Field(default=1200, gt=0, validation_alias='TOOL_RESULT_MAX_TOKENS')
    rerank_top_k: int = Field(default=10, gt=0, le=10, validation_alias='RERANK_TOP_K')
    context_target_rounds: int = Field(default=40, gt=0, validation_alias='CONTEXT_TARGET_ROUNDS')
    query_max_output_tokens: int = Field(default=2048, gt=0, validation_alias='QUERY_MAX_OUTPUT_TOKENS')
    sufficiency_max_output_tokens: int = Field(default=2048, gt=0, validation_alias='SUFFICIENCY_MAX_OUTPUT_TOKENS')
    qa_max_output_tokens: int = Field(default=2048, gt=0, validation_alias="QA_MAX_OUTPUT_TOKENS")
    faith_judge_input_token_budget: int = Field(default=16000, gt=0, validation_alias='FAITH_JUDGE_INPUT_TOKEN_BUDGET')
    faith_judge_max_output_tokens: int = Field(default=2048, gt=0, validation_alias='FAITH_JUDGE_MAX_OUTPUT_TOKENS')
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
    faq_timeout_seconds: float = Field(default=90, gt=0, le=90, validation_alias='FAQ_TIMEOUT_SECONDS')
    chat_timeout_seconds: float = Field(default=240, gt=0, le=240, validation_alias='CHAT_TIMEOUT_SECONDS')
    # Agent 控制预算与原最终回答上限独立，工具次数不能超过已确认的四次。
    agent_max_tool_calls: int = Field(default=4, gt=0, le=4, validation_alias='AGENT_MAX_TOOL_CALLS')
    agent_total_token_budget: int = Field(default=32000, gt=0, validation_alias='AGENT_TOTAL_TOKEN_BUDGET')
    agent_decision_max_output_tokens: int = Field(default=2048, gt=0, validation_alias='AGENT_DECISION_MAX_OUTPUT_TOKENS')
    intent_max_output_tokens: int = Field(default=2048, gt=0, validation_alias='INTENT_MAX_OUTPUT_TOKENS')
    # Workflow 检查点独立于业务 MySQL；相对路径由持久化入口锚定项目根目录。
    workflow_checkpoint_path: Path = Field(default=Path('runtime/workflow/checkpoints.sqlite'),
                                           validation_alias='WORKFLOW_CHECKPOINT_PATH')
    # 工作台默认只读；换本机端口时由启动环境显式配置 JSON 来源数组。
    rag_evaluation_enabled: bool = Field(default=False, validation_alias='RAG_EVALUATION_ENABLED')
    # 仅评估资源显式使用；缺省不发送新参数，空白及非提供商枚举由 Literal 拒绝。
    rag_evaluation_reasoning_effort: Literal['low', 'high', 'max'] | None = Field(
        default=None, validation_alias='RAG_EVALUATION_REASONING_EFFORT')
    rag_evaluation_allowed_origins: tuple[str, ...] = Field(
        default=('http://127.0.0.1:8001', 'http://localhost:8001'),
        validation_alias='RAG_EVALUATION_ALLOWED_ORIGINS')

    @model_validator(mode='after')
    def synchronize_agent_step_aliases(self):
        """区分显式旧4与缺省4；同步值不伪造显式字段来源。"""
        new_explicit = 'max_agent_steps' in self.model_fields_set
        old_explicit = 'agent_max_tool_calls' in self.model_fields_set
        if new_explicit and old_explicit and self.max_agent_steps != self.agent_max_tool_calls:
            raise ValueError('MAX_AGENT_STEPS conflicts with AGENT_MAX_TOOL_CALLS.')
        if new_explicit:
            object.__setattr__(self, 'agent_max_tool_calls', self.max_agent_steps)
        elif old_explicit:
            object.__setattr__(self, 'max_agent_steps', self.agent_max_tool_calls)
        return self

    @property
    def agent_total_token_budget_explicit(self) -> bool:
        """旧消费者保留有效32000；新消费者据此区别缺省推导和显式保护。"""
        return 'agent_total_token_budget' in self.model_fields_set

    @field_validator('rag_evaluation_allowed_origins')
    @classmethod
    def evaluation_origins_are_loopback(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        """来源仅为显式本机 origin，拒绝通配符、凭据、路径和非本机绑定。"""
        if not values:
            raise ValueError('evaluation origins require an explicit loopback whitelist')
        for value in values:
            parsed = urlsplit(value)
            if (parsed.scheme not in ('http', 'https') or parsed.hostname not in ('127.0.0.1', 'localhost')
                    or parsed.username is not None or parsed.password is not None
                    or parsed.path or parsed.query or parsed.fragment
                    or parsed.port is None or not 1 <= parsed.port <= 65535
                    or value != f'{parsed.scheme}://{parsed.hostname}:{parsed.port}'):
                raise ValueError('evaluation origins must be canonical explicit loopback origins')
        return tuple(dict.fromkeys(values))

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

    # 在整数转换前排除布尔值，避免把开关误当作各自独立的输出预算。
    @field_validator('qa_max_output_tokens', 'query_max_output_tokens', 'sufficiency_max_output_tokens',
                     'faith_judge_input_token_budget', 'faith_judge_max_output_tokens', mode='before')
    @classmethod
    def qa_output_budget_must_not_be_bool(cls, value):
        if isinstance(value, bool):
            raise ValueError('QA output budget must be a positive integer')
        return value

    @field_validator('agent_max_tool_calls', 'agent_total_token_budget',
                     'agent_decision_max_output_tokens', 'intent_max_output_tokens', mode='before')
    @classmethod
    def agent_limits_must_not_be_bool(cls, value):
        """转换前拒绝布尔值；正数、有限整数与工具硬上限由字段校验。"""
        if isinstance(value, bool):
            raise ValueError('Agent limits must be positive integers.')
        return value

    @field_validator('model_context_window', 'max_user_input_tokens', 'max_agent_steps',
                     'tool_result_max_tokens', 'rerank_top_k', 'context_target_rounds',
                     'max_output_tokens', mode='before')
    @classmethod
    def context_numbers_must_not_be_bool(cls, value):
        if isinstance(value, bool):
            raise ValueError('Context budgets must be positive integers.')
        return value

    # 新增数值配置在强制转换前排除布尔值，有限数校验沿用全局配置。
    @field_validator('rerank_timeout_seconds', 'query_timeout_seconds', 'sufficiency_timeout_seconds', 'rerank_min_score', 'faq_timeout_seconds', 'chat_timeout_seconds', mode='before')
    @classmethod
    def retrieval_numbers_must_not_be_bool(cls, value):
        if isinstance(value, bool):
            raise ValueError('retrieval numeric settings must not be boolean')
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
