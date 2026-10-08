# 嵌入服务只负责生成稠密向量；知识文本仍以 MySQL 存储为准。
"""Direct asynchronous SiliconFlow dense embeddings; MySQL text stays authoritative."""

import math

import httpx

from app.config import Settings


# 要求列表恰有 1024 个有限数值，排除布尔、NaN 和无穷后转换为 float。
def validate_vector(vector: list[float]) -> list[float]:
    if not isinstance(vector, list) or len(vector) != 1024:
        raise ValueError('embedding must contain exactly 1024 numbers')
    result = []
    for value in vector:
        if type(value) not in (int, float):
            raise ValueError('embedding values must be finite numbers')
        try:
            number = float(value)
        except OverflowError:
            raise ValueError('embedding values must be finite numbers') from None
        if not math.isfinite(number):
            raise ValueError('embedding values must be finite numbers')
        result.append(number)
    return result


class SiliconFlowEmbedder:
    # 保存配置与异步 HTTP 客户端，并记录是否由本适配器负责关闭客户端。
    def __init__(self, settings: Settings, *, http_client=None):
        self.settings = settings
        self._owns_client = http_client is None
        self._client = http_client if http_client is not None else httpx.AsyncClient()

    # 校验文本并请求批量嵌入；校验回包数量、索引及向量后按原输入顺序返回。
    async def embed(self, texts: list[str]) -> list[list[float]]:
        key = self.settings.siliconflow_api_key
        if key is None or not key.get_secret_value().strip():
            raise ValueError('SILICONFLOW_API_KEY is required for embeddings')
        if not isinstance(texts, list) or any(not isinstance(text, str) or not text.strip() for text in texts):
            raise ValueError('embedding inputs must be nonempty text')
        if not texts:
            return []
        response = await self._client.post(
            'https://api.siliconflow.cn/v1/embeddings',
            headers={'Authorization': f'Bearer {key.get_secret_value()}'},
            json={'model': self.settings.embedding_model, 'input': texts, 'encoding_format': 'float'},
            timeout=self.settings.embedding_timeout_seconds,
        )
        response.raise_for_status()
        body = response.json()
        data = body.get('data') if isinstance(body, dict) else None
        if not isinstance(data, list) or len(data) != len(texts):
            raise ValueError('embedding response count differs from input')
        # 回包可能乱序；每个输入索引须唯一且合法，再按索引还原文本与向量的对应关系。
        by_index = {}
        for item in data:
            if not isinstance(item, dict):
                raise ValueError('invalid embedding response entry')
            position = item.get('index')
            if type(position) is not int or not 0 <= position < len(texts) or position in by_index:
                raise ValueError('embedding response has invalid or duplicate index')
            by_index[position] = validate_vector(item.get('embedding'))
        return [by_index[position] for position in range(len(texts))]

    # 只关闭本适配器创建的客户端，外部注入的客户端由调用方管理。
    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()
