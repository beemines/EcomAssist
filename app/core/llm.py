import httpx
from langchain_openai import ChatOpenAI

from app.config import Settings


def create_model(
    settings: Settings, *, http_async_client: httpx.AsyncClient | None = None,
) -> ChatOpenAI:
    """创建直连上游的 Chat Completions 客户端，并按配置设置请求中的输出上限。"""
    return ChatOpenAI(
        model=settings.llm_model,
        base_url=str(settings.llm_base_url),
        api_key=settings.llm_api_key.get_secret_value(),
        timeout=settings.llm_timeout_seconds,
        max_retries=0,
        use_responses_api=False,
        stream_usage=False,
        extra_body={settings.llm_token_limit_field: settings.max_output_tokens},
        http_async_client=http_async_client,
    )
