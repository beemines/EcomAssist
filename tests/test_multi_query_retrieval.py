"""三路原生 hybrid 的第二层 RRF、权威正文与失败原子性。"""
import asyncio
import importlib.util

import pytest

from app.core.errors import ServiceError
from app.knowledge.types import ChunkRecord, VectorHit
from app.retrieval.types import RerankHit
from tests.test_retrieval_service import service_parts


class LaneIndex:
    """仅替代远程 Milvus，按查询返回不同有序主键或故障。"""
    def __init__(self, lanes):
        """记录每路收到的策略与过滤。"""
        self.lanes, self.calls = lanes, []
    async def recall(self, vector, text, *, strategy, category=None):
        """提供可含重复主键的远程响应以验证上层去重边界。"""
        self.calls.append((vector, text, strategy, category))
        result = self.lanes[len(self.calls) - 1]
        if isinstance(result, BaseException):
            raise result
        return result


def workflow(lanes, rows=(), ranked=()):
    """组合真实两层检索，替换嵌入、索引、仓储、重排四个外部边界。"""
    assert importlib.util.find_spec('app.retrieval.multi'), 'bounded workflow retriever is missing'
    from app.retrieval.multi import WorkflowRetriever
    service, _, repo, embedder, _, planner, reranker = service_parts(rows=rows, rerank_hits=ranked)
    service.index = LaneIndex(lanes)
    return WorkflowRetriever(service), service, repo, embedder, service.index, planner, reranker


async def test_rrf_union_deduplicates_before_single_rerank():
    """重复项不挤掉后续独立排名，最多50候选和10证据，重排仅一次。"""
    rows = [ChunkRecord('售后', f'问题{i}', f'权威{i}', id=i, vectorize_status='done') for i in range(1, 130)]
    lanes = [[VectorHit(2, 100), VectorHit(2, 99), VectorHit(1, 98),
              *[VectorHit(i, 0) for i in range(3, 65)]],
             [VectorHit(1, 100), VectorHit(2, 99), *[VectorHit(i, 0) for i in range(65, 100)]],
             [VectorHit(i, 0) for i in range(100, 130)]]
    retriever, _, repo, embedder, index, planner, reranker = workflow(
        lanes, rows, [RerankHit(index=i, score=.9 - .01 * i) for i in range(10)])
    result = await retriever.retrieve(question='能退吗', queries=('能退吗', '退货条件', '申请流程'), category='售后')
    assert len(index.calls) == 3 and len(reranker.calls) == 1 and planner.calls == []
    assert embedder.texts == ['能退吗', '退货条件', '申请流程']
    assert [call[1:] for call in index.calls] == [('能退吗', 'hybrid', '售后'),
        ('退货条件', 'hybrid', '售后'), ('申请流程', 'hybrid', '售后')]
    # 1和2互换前两名，总分相同，按主键升序；若重复项占排名则不再相同。
    assert repo.calls[0][:2] == [1, 2] and len(repo.calls) == 1 and len(repo.calls[0]) == 50
    assert result.payload['retrieval']['candidate_count'] == 50
    assert len(result.payload['matches']) == 10
    assert len({match['id'] for match in result.payload['matches']}) == 10
    assert result.payload['matches'][0]['answer'] == '权威1'
    assert set(result.payload) == {'found', 'matches', 'retrieval'}
    assert result.audit['query_count'] == 3 and result.audit['candidate_count'] == 50
    assert result.audit['provenance'][1] == [{'query_index': 0, 'rank': 2}, {'query_index': 1, 'rank': 1}]
    assert result.audit['provenance'][2] == [{'query_index': 0, 'rank': 1}, {'query_index': 1, 'rank': 2}]


async def test_filter_and_authority_apply_to_each_query():
    """每路带显式分类，SQL缺失/漂移/未完成正文都不能进入一次统一重排。"""
    rows = [ChunkRecord('售后', '正确', '权威答案', id=1, vectorize_status='done'),
            ChunkRecord('配送', '漂移', '错误', id=2, vectorize_status='done'),
            ChunkRecord('售后', '未完成', '错误', id=3, vectorize_status='pending')]
    retriever, _, _, _, index, planner, reranker = workflow(
        [[VectorHit(1, .9), VectorHit(2, .8)], [VectorHit(3, .9), VectorHit(4, .8)]],
        rows, [RerankHit(index=0, score=.8)])
    result = await retriever.retrieve(question='维修', queries=('维修', '保修'), category='售后')
    assert [call[3] for call in index.calls] == ['售后', '售后'] and planner.calls == []
    assert reranker.calls == [('维修', ['category: 售后\nquestions: 正确\nanswer: 权威答案'], 10)]
    assert [match['id'] for match in result.payload['matches']] == [1]


async def test_plain_faq_never_calls_planner():
    """纯FAQ显式空扩写计划，只有一次召回及一次重排。"""
    row = ChunkRecord('政策', '退货政策', '政策原文', id=1, vectorize_status='done')
    retriever, _, _, _, index, planner, reranker = workflow([[VectorHit(1, .1)]], [row], [RerankHit(index=0, score=.7)])
    result = await retriever.retrieve(question='退货政策', queries=('退货政策',), category=None)
    assert result.payload['found'] and len(index.calls) == len(reranker.calls) == 1 and planner.calls == []
    assert index.calls[0][3] is None and result.audit['query_count'] == 1


async def test_single_query_keeps_native_candidates_and_empty_plan():
    """单路不施加第二层RRF，显式空扩写计划复用旧四策略入口。"""
    retriever, service, _, _, _, planner, _ = workflow([[VectorHit(2, .9), VectorHit(1, .8)]])
    observed = []
    original = service.finalize_candidates
    async def capture(**kwargs):
        """记录真实最终阶段收到的计划和候选，再执行原权威回填。"""
        observed.append((kwargs['plan'], kwargs['candidates']))
        return await original(**kwargs)
    service.finalize_candidates = capture
    await retriever.retrieve(question='问题', queries=('问题',), category=None)
    assert observed[0][0].standard == '问题' and observed[0][0].expansions == []
    assert observed[0][1] == [VectorHit(2, .9), VectorHit(1, .8)] and planner.calls == []


async def test_equal_rrf_scores_are_stable_across_rank_permutations():
    """相同1/61+1/62+1/68不能因浮点累加次序导致ID逆序。"""
    lanes = [[VectorHit(i, 0) for i in ids] for ids in (
        [2, 1, 3, 4, 5, 6, 7, 8], [9, 2, 10, 11, 12, 13, 14, 1],
        [1, 15, 16, 17, 18, 19, 20, 2])]
    retriever, _, repo, _, _, _, _ = workflow(lanes)
    await retriever.retrieve(question='问题', queries=('问题', '条件', '流程'), category=None)
    assert repo.calls[0][:2] == [1, 2]


async def test_fused_candidates_keep_rrf_scores_and_global_policy_without_filter():
    """真实候选分使用跨路倒数排名，未显式过滤时允许全局政策正文。"""
    row = ChunkRecord('通用政策', '退货规则', '全局政策', id=7, vectorize_status='done')
    retriever, service, _, _, index, _, _ = workflow(
        [[VectorHit(7, 99), VectorHit(8, 1)], [VectorHit(8, 99), VectorHit(7, 1)]],
        [row], [RerankHit(index=0, score=.8)])
    observed = []
    original = service.finalize_candidates
    async def capture(**kwargs):
        """保存真实候选边界后继续权威回填。"""
        observed.extend(kwargs['candidates'])
        return await original(**kwargs)
    service.finalize_candidates = capture
    result = await retriever.retrieve(question='退货', queries=('退货', '退货条件'), category=None)
    assert [hit.id for hit in observed] == [7, 8]
    assert [hit.score for hit in observed] == pytest.approx([.03252247488101534, .03252247488101534])
    assert [call[3] for call in index.calls] == [None, None]
    assert result.payload['matches'][0]['answer'] == '全局政策'


async def test_swallowed_repository_cancellation_never_starts_rerank():
    """权威源即使吞取消返回迟到正文，也必须在重排前检查取消。"""
    row = ChunkRecord('售后', '问题', '答案', id=1, vectorize_status='done')
    retriever, service, _, _, _, _, reranker = workflow(
        [[VectorHit(1, .9)], [VectorHit(1, .8)]], [row], [RerankHit(index=0, score=.9)])
    started = asyncio.Event()
    async def swallowed(ids):
        """模拟故障仓储吞掉调用方取消。"""
        started.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            return [row]
    service.repository.get_done = swallowed
    task = asyncio.create_task(retriever.retrieve(question='问题', queries=('问题', '条件'), category=None))
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert reranker.calls == []


async def test_outer_aggregate_deadline_stops_second_lane_without_finalize():
    """上游统一期限取消第二路，第一路不能形成成功响应。"""
    retriever, service, repo, _, _, _, reranker = workflow([[VectorHit(1, .1)]])
    original = service.index.recall
    stopped = asyncio.Event()
    async def blocking(vector, text, **kwargs):
        """仅第二路等待取消，以前一路真实候选验证失败原子性。"""
        if text == '问题':
            return await original(vector, text, **kwargs)
        try:
            await asyncio.Event().wait()
        finally:
            stopped.set()
    service.index.recall = blocking
    with pytest.raises(TimeoutError):
        async with asyncio.timeout(.01):
            await retriever.retrieve(question='问题', queries=('问题', '条件'), category=None)
    assert stopped.is_set() and repo.calls == reranker.calls == []


async def test_one_failing_lane_fails_request():
    """第二路失败后不召回第三路、不回填、不以第一路假装成功。"""
    failure = ServiceError('upstream_error', '索引故障', 502)
    retriever, _, repo, _, index, _, reranker = workflow([[VectorHit(1, .1)], failure, []])
    with pytest.raises(ServiceError) as caught:
        await retriever.retrieve(question='问题', queries=('问题', '条件', '流程'), category=None)
    assert caught.value is failure and len(index.calls) == 2 and repo.calls == reranker.calls == []


@pytest.mark.parametrize('kind', ['cancel', 'timeout', 'timeout_cancel_context'])
async def test_wrapped_cancellation_never_becomes_partial_success(kind):
    """包装链中的调用方取消或期限必须传播，禁止将首路结果送去重排。"""
    failure = ServiceError('invalid_structured_output', '外层', 502)
    inner = RuntimeError('wrapper')
    failure.__cause__ = inner
    if kind == 'cancel':
        inner.__context__ = asyncio.CancelledError()
        expected = asyncio.CancelledError
    else:
        timeout = TimeoutError('deadline')
        inner.__cause__ = timeout
        if kind == 'timeout_cancel_context':
            timeout.__context__ = asyncio.CancelledError()
        expected = TimeoutError
    retriever, _, repo, _, _, _, reranker = workflow([[VectorHit(1, .9)], failure])
    with pytest.raises(expected):
        await retriever.retrieve(question='问题', queries=('问题', '条件'), category=None)
    assert reranker.calls == repo.calls == []


@pytest.mark.parametrize('queries', [(), ('问题', 'a', 'b', 'c'), ('别的问题',), ('问题', ' '),
                                    ('问题', '问题'), ('问题', '问 题'), ('问题', 'a' * 513)])
async def test_invalid_queries_fail_before_dependencies(queries):
    """边界拒绝空、过多、改写首条、空白、重复及超长查询。"""
    retriever, _, repo, embedder, index, planner, reranker = workflow([[], [], []])
    with pytest.raises(ValueError):
        await retriever.retrieve(question='问题', queries=queries, category=None)
    assert repo.calls == embedder.texts == index.calls == planner.calls == reranker.calls == []
