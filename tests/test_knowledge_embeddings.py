# 嵌入客户端离线协议测试，检查三栏输入、向量顺序和维度，以及安全失败与资源关闭。
import json

import httpx
import pytest
from pydantic import ValidationError

from app.config import Settings
from app.knowledge.types import ChunkDraft, embedding_text


# 构造使用指定 HTTP 客户端的真实嵌入适配器。
def embedder(settings, client):
    try:
        from app.knowledge.embeddings import SiliconFlowEmbedder
    except ImportError:
        pytest.fail('cloud embedder is missing')
    return SiliconFlowEmbedder(settings, http_client=client)


# 创建含虚假密钥的离线嵌入设置，并允许覆盖模型、端点或超时。
def settings(**kwargs):
    values = dict(llm_base_url='https://example.test', llm_model='test', llm_api_key='placeholder', siliconflow_api_key='synthetic-key')
    values.update(kwargs)
    return Settings(_env_file=None, **values)


# 构造嵌入服务的模型、数据及用量响应包。
def payload(entries):
    return {'model': 'BAAI/bge-m3', 'data': entries, 'usage': {'prompt_tokens': 1, 'total_tokens': 1}}


# 验证嵌入文本仅含三个权威字段，请求参数正确并按索引恢复乱序响应。
async def test_posts_only_three_fields_and_restores_out_of_order_batch():
    draft = ChunkDraft('运费', '配送费用', '标准配送8元。', section_path='private/path', content_type='faq', is_key_clause=True)
    assert embedding_text(draft) == 'category: 运费\nquestions: 配送费用\nanswer: 标准配送8元。'
    # 检查嵌入请求正文、凭据与超时，再返回逆序向量以检验批次重排。
    def handle(request):
        assert str(request.url) == 'https://api.siliconflow.cn/v1/embeddings'
        assert json.loads(request.content) == {'model': 'BAAI/bge-m3', 'input': ['category: 运费\nquestions: 配送费用\nanswer: 标准配送8元。', 'second'], 'encoding_format': 'float'}
        assert request.headers['Authorization'] == 'Bearer synthetic-key'
        assert request.extensions['timeout']['read'] == 20
        return httpx.Response(200, json=payload([{'object': 'embedding', 'index': 1, 'embedding': [2.0] * 1024}, {'object': 'embedding', 'index': 0, 'embedding': [1.0] * 1024}]))
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        worker = embedder(settings(), client)
        assert await worker.embed([embedding_text(draft), 'second']) == [[1.0] * 1024, [2.0] * 1024]
        await worker.aclose()
        assert not client.is_closed


# 验证重复或缺失索引、数量维度不符、非法数值及非有限向量被拒绝。
@pytest.mark.parametrize('entries', [
    [{'index': 0, 'embedding': [1.0] * 1024}, {'index': 0, 'embedding': [1.0] * 1024}],
    [{'embedding': [1.0] * 1024}, {'index': 1, 'embedding': [1.0] * 1024}],
    [{'index': 0, 'embedding': [1.0] * 1024}],
    [{'index': True, 'embedding': [1.0] * 1024}, {'index': 0, 'embedding': [1.0] * 1024}],
    [{'index': 0, 'embedding': [1.0] * 1023}, {'index': 1, 'embedding': [1.0] * 1024}],
    *[[{'index': 0, 'embedding': [bad] + [0.0] * 1023}, {'index': 1, 'embedding': [1.0] * 1024}] for bad in (True, '1', float('nan'), float('inf'), -float('inf'))],
], ids=['duplicate', 'missing-index', 'wrong-count', 'bool-index', 'dimension', 'bool', 'text', 'nan', 'inf', 'neg-inf'])
async def test_rejects_malformed_cloud_vectors(entries):
    # 直接用字节响应构造非法 NaN/Infinity，确保解码后的校验分支会拒绝它们。
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, content=json.dumps(payload(entries))))) as client:
        with pytest.raises(ValueError):
            await embedder(settings(), client).embed(['first', 'second'])


# 验证缺失嵌入密钥时在 HTTP 请求前失败。
async def test_missing_key_fails_before_http_and_no_retry_on_service_error():
    # 任何 HTTP 请求都令测试失败，证明缺失密钥的提前校验。
    def forbidden(request):
        pytest.fail('missing key must not reach HTTP')
    async with httpx.AsyncClient(transport=httpx.MockTransport(forbidden)) as client:
        with pytest.raises(ValueError, match='SILICONFLOW_API_KEY'):
            await embedder(settings(siliconflow_api_key=None), client).embed(['text'])


# 验证服务 HTTP 错误直接传播且只请求一次。
async def test_service_error_is_propagated_without_retry():
    requests = []
    # 记录请求并返回限流状态，核对适配器不会自动重试。
    def handle(request):
        requests.append(request)
        return httpx.Response(429)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        with pytest.raises(httpx.HTTPStatusError):
            await embedder(settings(), client).embed(['text'])
    assert len(requests) == 1


# 验证非固定嵌入模型、非正或无限超时被拒绝。
@pytest.mark.parametrize('kwargs', [{'embedding_model': 'other'}, {'embedding_timeout_seconds': 0}, {'milvus_timeout_seconds': float('inf')}])
def test_fixed_model_and_finite_timeouts_rejected(kwargs):
    with pytest.raises(ValidationError):
        settings(**kwargs)


# 验证固定模型以及显式 Milvus 端点和有限超时可正常配置。
def test_embedding_settings_accept_explicit_endpoint_and_timeouts():
    config = settings(embedding_model='BAAI/bge-m3', embedding_timeout_seconds=12, milvus_uri='http://127.0.0.1:19530', milvus_timeout_seconds=3)
    assert config.embedding_model == 'BAAI/bge-m3'
    assert config.embedding_timeout_seconds == 12
    assert config.milvus_timeout_seconds == 3
    assert str(config.milvus_uri).rstrip('/') == 'http://127.0.0.1:19530'


# 验证嵌入适配器关闭自己创建的 HTTP 客户端。
async def test_closes_owned_http_client():
    from app.knowledge.embeddings import SiliconFlowEmbedder
    worker = SiliconFlowEmbedder(settings())
    await worker.aclose()
    assert worker._client.is_closed
