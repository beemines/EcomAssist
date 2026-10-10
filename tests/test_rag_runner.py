"""四策略执行器的公平计划、实际请求、取消与检查点回归。"""

import asyncio
from dataclasses import replace
from contextlib import closing
import importlib
import json
from pathlib import Path
from types import SimpleNamespace

import httpx
from langchain_core.messages import AIMessage, AIMessageChunk
import pytest

from app.knowledge.types import ChunkRecord, VectorHit
from app.rag_evaluation.contracts import AnswerPoint, EvalCase, GoldGroup
from app.rag_evaluation.resources import RequestCounter
from app.rag_evaluation.store import RunStore, validate_manifest
from app.retrieval.types import QueryPlan, RetrievalBundle, ScoredChunk
from tests.test_rag_resources import dataset, settings
from tests.test_rag_store import config, record

STRATEGIES = ('dense', 'bm25', 'hybrid', 'hybrid_rerank')


def api():
    """缺失执行器应呈现功能断言，避免导入错误掩盖 RED。"""
    assert importlib.util.find_spec('app.rag_evaluation.runner'), '尚未实现四策略执行器'
    return importlib.import_module('app.rag_evaluation.runner')


def frozen(count=1):
    """金标带专属秘密词，便于检测它是否泄露到生成输入。"""
    cases = tuple(EvalCase(f'E{i}', 'B_model', 'single', 'HX-600可以退货吗？', None, False,
        (GoldGroup('secret-group', (('one',),)),),
        (AnswerPoint('p1', 'SECRET-GOLD', None, ()),), f'TE{i}') for i in range(count))
    return replace(dataset(), cases=cases, pilot_ids=tuple(c.eval_id for c in cases))


class Model:
    """本机 HTTPX transport 驱动实际 stage hook，模型语义保持确定性。"""
    def __init__(self, http):
        """保存可审计输入和可控错误，绝不访问真实上游。"""
        self.http, self.inputs = http, []
        self.finish, self.rewrite_error = 'stop', False
        self.delay, self.cancel_stage = 0., None
        self.unsupported, self.invalid_judge = False, False
        self.raise_after_cancel = False
        self.useful = True
        self.entered, self.release = asyncio.Event(), asyncio.Event()

    def with_structured_output(self, schema, **kwargs):
        """使用真实 Pydantic schema，只有严格合法原文可进入生产服务。"""
        return Structured(self, schema)

    async def request(self, stage, messages):
        """出站钩子与依赖等待分开，可模拟吞取消及共享改写耗时。"""
        self.inputs.append((stage, messages))
        await self.http.post('https://example.test/model', json={'stage': stage})
        if stage == self.cancel_stage:
            self.entered.set()
            try:
                await self.release.wait()
            except asyncio.CancelledError:
                if self.raise_after_cancel:
                    raise RuntimeError('依赖包装了取消')
        if stage == 'rewrite':
            await asyncio.sleep(self.delay)
            if self.rewrite_error:
                raise RuntimeError('private-upstream-error')

    async def astream(self, messages):
        """真实异步迭代协议，结束状态可故意缺失或截断。"""
        await self.request('answer', messages)
        yield AIMessageChunk('七天退货。[1]')
        if self.finish is not None:
            yield AIMessageChunk('', response_metadata={'finish_reason': self.finish})


class Structured:
    """模型返回值包含真实 schema 验证结果及 stop 原始消息。"""
    def __init__(self, model, schema):
        """绑定调用方已配置的共享模型和本轮 schema。"""
        self.model, self.schema = model, schema

    async def ainvoke(self, messages):
        """按 schema 选择明确阶段，不从生产请求正文猜计数阶段。"""
        name = self.schema.__name__
        stage = 'rewrite' if name == 'QueryPlan' else 'self_check' if name == '_Assessment' else 'judge'
        await self.model.request(stage, messages)
        if stage == 'rewrite':
            body = {'standard': 'HX-600可以退货吗？', 'expansions': []}
        elif stage == 'self_check':
            body = {'useful': self.model.useful, 'reason': '正文充分性判断', 'response_kind': 'knowledge'}
        else:
            source = json.loads(messages[-1].content)
            body = {'points': [{'point_id': p['point_id'], 'covered': True, 'reason': '覆盖要点'}
                for p in source['coverage_rubric']], 'claims': [{'claim': '七天退货',
                'supported': not self.model.unsupported, 'reason': '本轮证据判断'}]}
            if not self.model.useful:
                body['claims'] = []
            if self.model.invalid_judge:
                body['claims'][0]['supported'] = 'false'
        raw = AIMessage(json.dumps(body, ensure_ascii=False), response_metadata={'finish_reason': 'stop'})
        try:
            parsed, error = self.schema.model_validate(body), None
        except ValueError as exc:
            parsed, error = None, exc
        return {'raw': raw, 'parsed': parsed, 'parsing_error': error}


class Retrieval:
    """检索替身冻结候选与正文，并记录实际计划对象供公平性核对。"""
    def __init__(self):
        """注入阶段延迟及取消边界，不模拟请求计数。"""
        self.calls, self.delay = [], 0.
        self.cancel, self.block = None, False
        self.entered = asyncio.Event()

    async def retrieve(self, question, *, category, strategy, query_plan):
        """仅接收题面和共用计划，金标由 runner 本地评分使用。"""
        self.calls.append((strategy, query_plan))
        self.entered.set()
        if self.cancel is not None:
            self.cancel.set()
        if self.block:
            await asyncio.Event().wait()
        await asyncio.sleep(self.delay)
        chunk = ChunkRecord('测试', 'HX-600退货规则', '七天退货', id=1, vectorize_status='done')
        return RetrievalBundle(query_plan, strategy, [VectorHit(1, .9), VectorHit(2, .8)],
            [ScoredChunk(chunk, .9, 'rerank' if strategy == 'hybrid_rerank' else 'cosine')])


class Quality:
    """只记录编造台账，不存在低置信问题写入入口。"""
    def __init__(self):
        """收集每条策略完整证据和裁判原因供断言。"""
        self.rows = []

    async def record_fabrication(self, row):
        """模拟已授权持久化入口，不影响真实数据库。"""
        self.rows.append(row)


async def setup(tmp_path, count=1):
    """建立真实磁盘 store 及本机 transport，复用实际 planner 和裁判。"""
    module = api()
    from app.retrieval.query import QueryPlanner
    store, data = RunStore(tmp_path), frozen(count)
    run_id = await store.create(config(), [(c.eval_id, s) for c in data.cases for s in STRATEGIES])
    counter = RequestCounter(store, run_id, (await store.get(run_id))['request_counts'])
    async def dispatch(request):
        """实际 HTTP dispatch 只返回本机响应，保留 request hook 行为。"""
        return httpx.Response(200, json={})
    http = httpx.AsyncClient(transport=httpx.MockTransport(dispatch), event_hooks={'request': [counter.model_hook]})
    model = Model(http)
    resources = SimpleNamespace(requests=counter, model=model, judge_model=model,
        planner=QueryPlanner(model, 8000), repository=None, embedder=None, index=None,
        reranker=None, quality=Quality())
    runner = module.EvaluationRunner(resources, store, run_id, settings())
    runner.retrieval = Retrieval()
    return runner, resources, store, data, run_id, http


async def test_one_query_plan_shared_by_four_strategies_and_no_gold_in_generation(tmp_path):
    """重复规划或把金标加入生成 prompt 都会使本测试失败。"""
    runner, resources, store, data, run_id, http = await setup(tmp_path)
    try:
        assert await runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, asyncio.Event()) == 'completed'
        calls = runner.retrieval.calls
        assert [s for s, _ in calls] == list(STRATEGIES)
        assert all(p is calls[0][1] for _, p in calls)
        for stage, messages in resources.model.inputs:
            if stage != 'judge':
                assert 'SECRET-GOLD' not in str(messages) and 'secret-group' not in str(messages)
        counts = (await store.get(run_id))['request_counts']
        assert counts['rewrite'] == 1 and counts['answer'] == counts['self_check'] == counts['judge'] == 4
        rows = await store.records(run_id)
        assert len(rows) == 4 and all(r['metrics']['candidate_group_coverage'] == 1 for r in rows)
        assert all(r['candidate_ids'] == [1, 2] and r['final_ids'] == [1] for r in rows)
    finally:
        await http.aclose()


async def test_shared_rewrite_failure_four_errors_one_request(tmp_path):
    """共享规划失败留下四条错误，HTTP实际边界仍只有一次。"""
    runner, resources, store, data, run_id, http = await setup(tmp_path)
    resources.model.rewrite_error = True
    try:
        assert await runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, asyncio.Event()) == 'completed_with_errors'
        assert {r['status'] for r in await store.records(run_id)} == {'rewrite_error'}
        manifest = await store.get(run_id)
        assert manifest['counts']['errors'] == 4 and manifest['request_counts']['rewrite'] == 1
        assert runner.retrieval.calls == []
    finally:
        await http.aclose()


async def test_shared_rewrite_elapsed_charged_independently(tmp_path, monkeypatch):
    """各路扣相同改写耗时，后路不会承担前路检索耗时。"""
    runner, resources, store, data, run_id, http = await setup(tmp_path)
    resources.model.delay, runner.retrieval.delay = .15, .2
    runner.settings = settings().model_copy(update={'faq_timeout_seconds': .7, 'chat_timeout_seconds': 2.})
    starts, deadlines = [], []
    original_route, original_timeout = runner._route, asyncio.timeout_at
    async def observe_route(*args):
        """保留真实路线，只记录每路入口及传入共享改写耗时。"""
        starts.append((asyncio.get_running_loop().time(), args[3]))
        return await original_route(*args)
    def observe_timeout(when):
        """继续真实绝对 timeout，同时观察截止时间的数值而非只比较最终结果。"""
        deadlines.append(when)
        return original_timeout(when)
    monkeypatch.setattr(runner, '_route', observe_route)
    monkeypatch.setattr(asyncio, 'timeout_at', observe_timeout)
    try:
        assert await runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, asyncio.Event()) == 'completed'
        assert len(runner.retrieval.calls) == 4
        assert all(r['elapsed_ms'] >= 350 for r in await store.records(run_id))
        assert len(deadlines) == 8 and len(starts) == 4
        assert len({elapsed for _, elapsed in starts}) == 1
        for index, (start, rewrite_elapsed) in enumerate(starts):
            assert deadlines[2 * index] - start == pytest.approx(2. - rewrite_elapsed, abs=.02)
            assert deadlines[2 * index + 1] - start == pytest.approx(.7 - rewrite_elapsed, abs=.02)
    finally:
        await http.aclose()


@pytest.mark.parametrize('finish', [None, 'length'])
async def test_truncated_stream_and_swallowed_cancel_do_not_finish(tmp_path, finish):
    """缺 stop 或 length 的最终流不能交给裁判或写完成记录。"""
    runner, resources, store, data, run_id, http = await setup(tmp_path)
    resources.model.finish = finish
    try:
        assert await runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, asyncio.Event()) == 'completed_with_errors'
        assert {r['status'] for r in await store.records(run_id)} == {'answer_error'}
        assert (await store.get(run_id))['request_counts']['judge'] == 0
    finally:
        await http.aclose()


@pytest.mark.parametrize('stage', ['rewrite', 'self_check', 'answer', 'judge'])
async def test_swallowed_cancellation_stays_cancelled(tmp_path, stage):
    """上游吞 CancelledError 后返回合法产物也不能使取消成为成功。"""
    runner, resources, store, data, run_id, http = await setup(tmp_path)
    resources.model.cancel_stage = stage
    cancel = asyncio.Event()
    task = asyncio.create_task(runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, cancel))
    try:
        await asyncio.wait_for(resources.model.entered.wait(), 2)
        cancel.set()
        assert await asyncio.wait_for(task, 2) == 'cancelled'
        rows = await store.records(run_id)
        assert [r['status'] for r in rows] == ['cancelled', 'not_attempted', 'not_attempted', 'not_attempted']
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        await http.aclose()


async def test_cancel_keeps_started_and_unstarted_distinct(tmp_path):
    """两个已开始题 dense 被取消，等待并发槽的第三题保持未执行。"""
    runner, resources, store, data, run_id, http = await setup(tmp_path, 3)
    runner.retrieval.block = True
    cancel = asyncio.Event()
    task = asyncio.create_task(runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, cancel))
    try:
        while len(runner.retrieval.calls) < 2:
            await asyncio.sleep(0)
        cancel.set()
        assert await asyncio.wait_for(task, 2) == 'cancelled'
        rows = await store.records(run_id)
        assert sum(r['status'] == 'cancelled' for r in rows) == 2
        assert sum(r['status'] == 'not_attempted' for r in rows) == 10
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        await http.aclose()


@pytest.mark.parametrize('invalid', [False, True])
async def test_only_valid_unsupported_claims_enter_faith_ledger(tmp_path, invalid):
    """非法裁判不能写台账；合法 unsupported 保留每路全部引用及版本。"""
    runner, resources, store, data, run_id, http = await setup(tmp_path)
    resources.model.unsupported, resources.model.invalid_judge = True, invalid
    try:
        outcome = await runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, asyncio.Event())
        assert outcome == ('completed_with_errors' if invalid else 'completed')
        assert len(resources.quality.rows) == (0 if invalid else 4)
        if not invalid:
            assert {r.strategy for r in resources.quality.rows} == set(STRATEGIES)
            assert all(r.eval_id == 'TE0' and len(r.citations) == 1 and 'joint-generation-v2.1' in r.reason
                for r in resources.quality.rows)
    finally:
        await http.aclose()


async def test_legal_refusal_skips_answer_http_and_online_low_confidence_write(tmp_path):
    """正式评估拒答仅留报告，零断言忠实度N/A且没有生成HTTP或线上问题写入。"""
    from app.core.answer_validation import REFUSAL_TEXT
    runner, resources, store, data, run_id, http = await setup(tmp_path)
    data = replace(data, cases=(replace(data.cases[0], should_refuse=True, groups=(), points=()),))
    resources.model.useful = False
    try:
        assert await runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, asyncio.Event()) == 'completed'
        rows = await store.records(run_id)
        assert all(row['answer'] == REFUSAL_TEXT and row['refused'] and row['claim_verdicts'] == [] for row in rows)
        assert all(row['metrics']['faithfulness'] is None and row['metrics']['absent_refusal_rate'] == 1 for row in rows)
        counts = (await store.get(run_id))['request_counts']
        assert counts['answer'] == 0 and counts['judge'] == 4
        assert resources.quality.rows == []
    finally:
        await http.aclose()


async def test_running_checkpoint_and_legacy_counts_compatibility(tmp_path):
    """in-flight必须可诚实持久化，旧无 running 计数按零规范化。"""
    store = RunStore(tmp_path)
    run_id = await store.create(config(), [('E1', 'dense')])
    row = record()
    row['status'] = 'running'
    await store.put_case(run_id, row)
    manifest = await store.get(run_id)
    assert manifest['counts']['running'] == manifest['counts']['attempted'] == 1
    assert manifest['counts']['errors'] == manifest['counts']['completed'] == 0
    with pytest.raises(ValueError):
        await store.put_case(run_id, row | {'stage': 'complete'})
    legacy = await RunStore(tmp_path / 'legacy').create(config(), [('E1', 'dense')])
    old = await RunStore(tmp_path / 'legacy').get(legacy)
    old['counts'].pop('running')
    assert validate_manifest(old)['counts']['running'] == 0


async def test_checkpoint_disk_failure_is_not_four_model_errors(tmp_path, monkeypatch):
    """存储发布失败应停止所有收费任务，不能伪装成共享模型改写失败。"""
    from app.rag_evaluation.store import StoreError
    runner, resources, store, data, run_id, http = await setup(tmp_path)
    original = store.put_case
    async def fail_running(run, row):
        """只有真正活动检查点写入失败，保留 seed 文件作为恢复证据。"""
        if row['status'] == 'running':
            raise StoreError('磁盘不可写')
        await original(run, row)
    monkeypatch.setattr(store, 'put_case', fail_running)
    try:
        with pytest.raises(StoreError):
            await runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, asyncio.Event())
        assert (await store.get(run_id))['request_counts']['rewrite'] == 0
        assert {r['status'] for r in await store.records(run_id)} == {'not_attempted'}
    finally:
        await http.aclose()


async def test_counter_disk_failure_inside_http_hook_aborts_run(tmp_path, monkeypatch):
    """真实HTTP hook持久化失败被planner包装后仍应中断运行，不虚构模型错误。"""
    from app.rag_evaluation.store import StoreError
    runner, resources, store, data, run_id, http = await setup(tmp_path)
    original = store.update
    async def fail_counter(run, patch):
        """只破坏请求快照发布，保留真实HTTPX钩子及planner错误包装链。"""
        if 'request_counts' in patch:
            raise StoreError('计数快照不可写')
        await original(run, patch)
    monkeypatch.setattr(store, 'update', fail_counter)
    try:
        with pytest.raises(StoreError):
            await runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, asyncio.Event())
        assert (await store.get(run_id))['request_counts']['rewrite'] == 0
        rows = await store.records(run_id)
        assert [r['status'] for r in rows] == ['running', 'not_attempted', 'not_attempted', 'not_attempted']
    finally:
        await http.aclose()


@pytest.mark.parametrize('stage', ['rewrite', 'self_check', 'answer', 'judge'])
async def test_external_task_cancel_keeps_honest_checkpoint(tmp_path, stage):
    """直接取消 runner task 与事件取消有相同诚实记录，吞取消仍无后续收费。"""
    runner, resources, store, data, run_id, http = await setup(tmp_path)
    resources.model.cancel_stage = stage
    task = asyncio.create_task(runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, asyncio.Event()))
    try:
        await asyncio.wait_for(resources.model.entered.wait(), 5)
        task.cancel()
        assert await asyncio.wait_for(task, 5) == 'cancelled'
        assert sum(r['status'] == 'cancelled' for r in await store.records(run_id)) == 1
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        await http.aclose()


@pytest.mark.parametrize('stage', ['rewrite', 'self_check', 'answer', 'judge'])
async def test_dependency_wraps_cancellation_without_marking_unstarted_errors(tmp_path, stage):
    """依赖把取消包装为普通异常时仍取消已开始路线，后路不得成为改写错误。"""
    runner, resources, store, data, run_id, http = await setup(tmp_path)
    resources.model.cancel_stage, resources.model.raise_after_cancel = stage, True
    cancel = asyncio.Event()
    task = asyncio.create_task(runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, cancel))
    try:
        await asyncio.wait_for(resources.model.entered.wait(), 5)
        cancel.set()
        assert await asyncio.wait_for(task, 5) == 'cancelled'
        assert [r['status'] for r in await store.records(run_id)] == [
            'cancelled', 'not_attempted', 'not_attempted', 'not_attempted']
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        await http.aclose()


async def test_route_enters_in_order_and_running_stage_products_are_complete(tmp_path, monkeypatch):
    """每个阶段进入前都发布合法 preceding 产物，后路在实际入口前仍未执行。"""
    runner, resources, store, data, run_id, http = await setup(tmp_path)
    original, checkpoints = store.put_case, []
    async def observe(run, row):
        """继续真实校验与写盘，仅取独立副本观察入口。"""
        await original(run, row)
        if row['status'] == 'running':
            checkpoints.append(json.loads(json.dumps(row)))
            if row['strategy'] == 'dense' and row['stage'] == 'rewrite':
                assert all(r['status'] == ('running' if r['strategy'] == 'dense' else 'not_attempted')
                    for r in await store.records(run))
    monkeypatch.setattr(store, 'put_case', observe)
    try:
        assert await runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, asyncio.Event()) == 'completed'
        assert [(r['strategy'], r['stage']) for r in checkpoints] == [('dense', 'rewrite')] + [
            (strategy, stage) for strategy in STRATEGIES for stage in ('retrieval', 'self_check', 'answer', 'judgment')]
    finally:
        await http.aclose()


async def test_expired_checkpoint_does_not_start_next_model_stage(tmp_path, monkeypatch):
    """检查点等待耗尽聊天期限后不得再开始自评模型HTTP请求。"""
    runner, resources, store, data, run_id, http = await setup(tmp_path)
    runner.settings = settings().model_copy(update={'chat_timeout_seconds': .3})
    original = runner._publish
    async def slow_self_check(row):
        """只在已保存检索产物后耗尽期限，保留完整真实写盘行为。"""
        await original(row)
        if row['status'] == 'running' and row['stage'] == 'self_check':
            # 同步延迟模拟真实fsync阻塞事件循环，timeout回调尚未得到运行机会。
            import time
            time.sleep(.35)
    monkeypatch.setattr(runner, '_publish', slow_self_check)
    try:
        assert await runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, asyncio.Event()) == 'completed_with_errors'
        assert (await store.get(run_id))['request_counts']['self_check'] == 0
        assert {r['status'] for r in await store.records(run_id)} == {'self_check_error'}
    finally:
        await http.aclose()


@pytest.mark.parametrize('stage,budget_field,expected_status', [
    ('rewrite', 'query_timeout_seconds', 'rewrite_error'),
    ('self_check', 'sufficiency_timeout_seconds', 'self_check_error'),
    ('judge', 'llm_timeout_seconds', 'judge_error'),
])
async def test_swallowed_internal_stage_timeout_cannot_advance(tmp_path, stage, budget_field, expected_status):
    """服务内部timeout取消被吞并uncancel后，独立绝对阶段期限仍拒绝后续成功链路。"""
    runner, resources, store, data, run_id, http = await setup(tmp_path)
    runner.settings = settings().model_copy(update={budget_field: .05})
    resources.planner.timeout = runner.settings.query_timeout_seconds
    resources.model.cancel_stage, resources.model.unsupported = stage, True
    assert runner.settings.faq_timeout_seconds == 90 and runner.settings.chat_timeout_seconds == 240
    try:
        outcome = await asyncio.wait_for(runner.run_cases(data, {'one': 1, 'two': 2},
            data.pilot_ids, asyncio.Event()), 8)
        assert outcome == 'completed_with_errors'
        rows = await store.records(run_id)
        assert {row['status'] for row in rows} == {expected_status}
        assert all(row['error']['type'] == 'TimeoutError' for row in rows)
        counts = (await store.get(run_id))['request_counts']
        assert counts['rewrite'] == 1
        assert counts['self_check'] == (0 if stage == 'rewrite' else 4)
        assert counts['answer'] == (4 if stage == 'judge' else 0)
        assert counts['judge'] == (4 if stage == 'judge' else 0)
        assert resources.quality.rows == []
        if stage == 'rewrite':
            assert all(row['query_plan'] is None and row['candidate_ids'] is None for row in rows)
        else:
            assert all(row['candidate_ids'] == [1, 2] and row['final_ids'] == [1]
                and len(row['prompt_citations']) == 1 for row in rows)
        if stage == 'self_check':
            assert all(row['decision'] is None and row['answer'] is None for row in rows)
        elif stage == 'judge':
            assert all(row['decision']['useful'] and row['answer'] and row['refused'] is False
                and row['point_verdicts'] is None and row['claim_verdicts'] is None for row in rows)
    finally:
        await http.aclose()


class OfflineModel(Model):
    """真实检索集成中的确定性模型，不拥有客户端且不发任何 HTTP 请求。"""
    def __init__(self, http):
        """提供 owner 所需同步 root close 协议，关闭只有确定性测试对象。"""
        super().__init__(http)
        self.root_client = self

    def close(self):
        """确定性模型没有网络池，保留真实 owner 的生命周期调用形状。"""
        return None

    async def request(self, stage, messages):
        """仅保留测试审计输入；生产 HTTP counter 不增加虚构请求。"""
        self.inputs.append((stage, messages))


class OfflineReranker:
    """依据题面词匹配排序真实数据库正文，保持 rerank 输入位置协议。"""
    def __init__(self, *args, **kwargs):
        """不创建云端客户端或额外资源。"""
        self.calls = []

    async def rank(self, question, documents, *, top_n):
        """仅用题面和实际候选正文作确定性排序，不读取任何金标。"""
        from app.retrieval.types import RerankHit
        self.calls.append((question, tuple(documents), top_n))
        words = question.split()
        ranked = sorted(range(len(documents)), key=lambda i: sum(w in documents[i] for w in words), reverse=True)
        return [RerankHit(index=i, score=.9 - rank * .01) for rank, i in enumerate(ranked[:top_n])]


async def test_real_four_strategies_mysql_milvus_preserve_other_resources(mysql_database,
        milvus_collection, tmp_path, monkeypatch):
    """真实四策略检索50块，核对型号及跨节候选，cleanup精确保留旁置资源。"""
    from sqlalchemy import delete
    from uuid import uuid4
    from app.config import load_settings
    from app.db.models import FaithCase, KnowledgeChunk
    from app.db.session import Database
    from app.knowledge.types import ChunkDraft
    from app.rag_evaluation import resources as resource_module
    from app.rag_evaluation.dataset import load_dataset
    from app.rag_evaluation.locking import RunLock
    from app.repositories.knowledge import KnowledgeRepository
    from app.retrieval.milvus import HybridMilvusIndex
    from tests.test_rag_resources import DeterministicEmbedder, database_snapshot
    current = load_settings()
    data = load_dataset('merchant-rag-300-v1', root=Path('evals/datasets'))
    case_ids = ('B1', 'E5')
    store = RunStore(tmp_path)
    run_id = await store.create(config() | {'fingerprint': data.fingerprint},
        [(case_id, strategy) for case_id in case_ids for strategy in STRATEGIES])
    models = []
    def offline_model(*args, **kwargs):
        """由原 owner 建立模型引用，测试只替换外部收费依赖。"""
        model = OfflineModel(None)
        models.append(model)
        return model
    monkeypatch.setattr(resource_module, 'create_model', offline_model)
    monkeypatch.setattr(resource_module, 'SiliconFlowEmbedder', DeterministicEmbedder)
    monkeypatch.setattr(resource_module, 'SiliconFlowReranker', OfflineReranker)
    owner = resource_module.OwnedResources(current, store, run_id)
    sentinel = await KnowledgeRepository(mysql_database).add_chunks([
        ChunkDraft('runner旁置_' + run_id, '保留问题', '不得删除正文')])
    faith_id = 'S' + uuid4().hex[:15]
    async with mysql_database.session() as session, session.begin():
        session.add(FaithCase(eval_id=faith_id, bucket='A_policy', query='保留题', answer='保留答', reason='保留'))
    other_index = HybridMilvusIndex(milvus_collection.uri, collection=milvus_collection.name)
    business = Database(current.database_url.set(host='127.0.0.1', port=3307,
        database='customer_service', username='customer_service'))
    try:
        await other_index.ensure_collection()
        before, business_before = await database_snapshot(mysql_database), await database_snapshot(business)
        collections_before = set(await milvus_collection.client.list_collections(timeout=5))
        with closing(RunLock(tmp_path).acquire()):
            mapping = await owner.prepare(data)
            assert len(mapping) == 50
            runner = api().EvaluationRunner(owner, store, run_id, current)
            outcome = await runner.run_cases(data, mapping, case_ids, asyncio.Event())
            assert outcome == 'completed'
            rows = await store.records(run_id)
            assert len(rows) == 8 and {r['strategy'] for r in rows} == set(STRATEGIES)
            assert all(r['query_plan']['standard'] == r['query'] for r in rows)
            assert all(len(r['candidate_ids']) <= 50 and len(r['final_ids']) <= 10 for r in rows)
            assert all(set(r['candidate_ids']) <= set(mapping.values()) for r in rows)
            e_rows = [r for r in rows if r['eval_id'] == 'E5']
            dense = next(r for r in e_rows if r['strategy'] == 'dense')
            assert len(dense['candidate_ids']) == 50
            assert dense['metrics']['candidate_group_coverage'] == 1
            bm25 = next(r for r in e_rows if r['strategy'] == 'bm25')
            assert any('MH-W40' in c['answer'] or 'MH-W40' in c['question'] for c in bm25['prompt_citations'])
            expected_ids = {mapping[k] for group in next(c for c in data.cases if c.eval_id == 'E5').groups
                for alternative in group.alternatives for k in alternative}
            assert len(expected_ids & set(bm25['candidate_ids'])) >= 3
            assert owner.reranker.calls and all(call[2] == 10 for call in owner.reranker.calls)
            counts = (await store.get(run_id))['request_counts']
            assert counts['milvus'] > 0 and all(counts[k] == 0 for k in counts if k != 'milvus')
            cleanup = await owner.cleanup()
            assert cleanup.ok, cleanup
        assert await database_snapshot(mysql_database) == before
        assert await database_snapshot(business) == business_before
        assert set(await milvus_collection.client.list_collections(timeout=5)) == collections_before
        proof = {'owned_chunks': len(mapping), 'records': len(rows), 'case_ids': list(case_ids),
            'outcome': outcome, 'business_chunks': len(business_before[0]), 'cleanup_ok': cleanup.ok,
            'pending_sentinel_preserved': True, 'faith_sentinel_preserved': True,
            'other_collections_preserved': True, 'request_counts': (await store.get(run_id))['request_counts'],
            'candidate_ids': {r['eval_id'] + '--' + r['strategy']: r['candidate_ids'] for r in rows},
            'mapped_cross_section_ids': sorted(expected_ids)}
        Path('.cache/task6-service-proof.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2), encoding='utf-8')
    finally:
        await owner.cleanup()
        await business.dispose()
        await other_index.aclose()
        async with mysql_database.session() as session, session.begin():
            await session.execute(delete(KnowledgeChunk).where(KnowledgeChunk.id.in_(sentinel)))
            await session.execute(delete(FaithCase).where(FaithCase.eval_id == faith_id))
