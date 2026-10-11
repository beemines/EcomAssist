# 模型客户端工厂，按配置直连上游并统一使用 Chat Completions 请求格式。
from typing import Literal

import httpx
from langchain_openai import ChatOpenAI

from app.config import Settings


# 浅副本合并真实请求extra_body，不创建/拥有新客户端；只关闭来源实例一次。
# 外部注入的其他模型由调用方配置预算，保持其接口与资源所有权。
def model_with_output_budget(model, settings: Settings, budget: int):
    if type(budget) is not int or budget <= 0:
        raise ValueError('output budget must be a positive integer')
    if not isinstance(model, ChatOpenAI):
        return model
    body = dict(model.extra_body or {})
    body[settings.llm_token_limit_field] = budget
    return model.model_copy(update={'extra_body': body}, deep=False)


# 依据配置创建 Chat Completions 客户端，设置超时和输出上限。
def create_model(
    settings: Settings, *, http_async_client: httpx.AsyncClient | None = None,
    reasoning_effort: Literal['low', 'high', 'max'] | None = None,
) -> ChatOpenAI:
    """创建直连客户端；努力等级仅由评估调用方显式传入，普通调用保留省略行为。"""
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
        # None 时连构造参数也省略，不从在线 Settings 自动读取评估专属值。
        **({'reasoning_effort': reasoning_effort} if reasoning_effort is not None else {}),
    )
