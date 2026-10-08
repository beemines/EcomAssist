# 模型客户端工厂，按配置直连上游并统一使用 Chat Completions 请求格式。
import httpx
from langchain_openai import ChatOpenAI

from app.config import Settings


# 依据配置创建 Chat Completions 客户端，设置超时和输出上限。
def create_model(
    settings: Settings, *, http_async_client: httpx.AsyncClient | None = None,
) -> ChatOpenAI:
    """创建直连上游的 Chat Completions 客户端，并按配置设置请求中的输出上限。"""
    return ChatOpenAI(
        model=settings.llm_model,
        base_url=str(settings.llm_base_url),
        api_key=settings.llm_api_key.get_secret_value(),
        timeout=settings.llm_timeout_seconds,
        # 模型请求不自动重试，避免一轮聊天悄悄重复生成或选工具。
        max_retries=0,
        # 应用固定使用 Chat Completions，流式正文不依赖额外的 usage 帧。
        use_responses_api=False,
        stream_usage=False,
        # 按配置发送上游接受的输出上限字段，允许切换模型而不改业务接口。
        extra_body={settings.llm_token_limit_field: settings.max_output_tokens},
        http_async_client=http_async_client,
    )
