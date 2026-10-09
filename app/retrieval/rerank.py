# 固定 SiliconFlow BGE 重排：仅映射合法的原文位置，故障和取消直接传播。
import asyncio
import math

import httpx

from app.config import Settings
from app.retrieval.types import RerankHit


class SiliconFlowReranker:
    # 记录重排配置及HTTP客户端归属，注入客户端由调用方负责关闭。
    def __init__(self, settings: Settings, *, http_client=None):
        self.settings = settings
        self._owns_client = http_client is None
        self._client = http_client if http_client is not None else httpx.AsyncClient()

    # 发送固定模型的零重试重排请求，校验全集位置和分数后稳定排序裁剪。
    async def rank(self, query: str, documents: list[str], *, top_n: int = 10) -> list[RerankHit]:
        if not isinstance(query, str) or not query.strip():
            raise ValueError('rerank query must be nonempty text')
        if not isinstance(documents, list) or any(not isinstance(text, str) or not text.strip() for text in documents):
            raise ValueError('rerank documents must be nonempty text')
        if type(top_n) is not int or top_n <= 0:
            raise ValueError('top_n must be a positive integer')
        if not documents:
            return []
        key = self.settings.siliconflow_api_key
        if key is None or not key.get_secret_value().strip():
            raise ValueError('SILICONFLOW_API_KEY is required for reranking')
        # 外层绝对期限也约束慢速分块响应，HTTP 各阶段超时不能延长本次调用。
        async with asyncio.timeout(self.settings.rerank_timeout_seconds):
            response = await self._client.post(
                'https://api.siliconflow.cn/v1/rerank',
                headers={'Authorization': f'Bearer {key.get_secret_value()}'},
                json={'model': self.settings.rerank_model, 'query': query, 'documents': documents,
                      'top_n': top_n, 'return_documents': False},
                timeout=self.settings.rerank_timeout_seconds,
            )
            response.raise_for_status()
            body = response.json()
        results = body.get('results') if isinstance(body, dict) else None
        if not isinstance(results, list):
            raise ValueError('invalid rerank results')
        hits, seen = [], set()
        for item in results:
            if not isinstance(item, dict):
                raise ValueError('invalid rerank entry')
            index, score = item.get('index'), item.get('relevance_score')
            if type(index) is not int or not 0 <= index < len(documents) or index in seen:
                raise ValueError('invalid or duplicate rerank index')
            if type(score) not in (int, float):
                raise ValueError('rerank score must be finite')
            try:
                finite = math.isfinite(score)
            except OverflowError:
                finite = False
            if not finite:
                raise ValueError('rerank score must be finite')
            seen.add(index)
            hits.append(RerankHit(index=index, score=score))
        # Python 稳定排序在同分时维持服务返回顺序；校验全集后再裁剪。
        return sorted(hits, key=lambda hit: -hit.score)[:min(top_n, len(documents))]

    # 仅关闭本适配器创建的HTTP客户端，保持外部注入资源可复用。
    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()
