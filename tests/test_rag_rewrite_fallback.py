"""共享改写无效输出的有限降级、按题审计和版本门槛回归。"""

import asyncio
import copy
from dataclasses import replace
import hashlib
import json

import httpx
from langchain_core.exceptions import OutputParserException
import pytest

from app.core.errors import InputTooLong, ServiceError
from app.core.llm import create_model, model_with_output_budget
from app.rag_evaluation.manager import build_run_config, PilotRequired
from app.rag_evaluation.report import public_report, summarize_records, validate_case_record
from app.rag_evaluation.store import RunStore, StoreError, validate_config
from app.retrieval.query import QueryPlanner
from tests.test_rag_api import application, client_for, ManagerDouble, PREFIX
from tests.test_rag_manager import DATASET_ID, Harness
from tests.test_rag_metrics import record as completed_record
from tests.test_rag_resources import settings
from tests.test_rag_runner import setup, STRATEGIES

POLICY = 'original-query-on-invalid-v1'
QUESTION = 'MH-W40只买一台，金额199元，未拆封且不接受换货可以退吗？'


def declaration(status='success', code=None):
    """独立给出公开声明期望，避免调用生产声明构造器形成镜像断言。"""
    return dict(policy_version=POLICY, status=status, error=None if code is None else
        dict(code=code, type='ServiceError', message='该阶段执行失败'))


async def run_invalid_response(tmp_path, body, *, finish='stop', response_bytes=None, question=QUESTION,
                               downstream_failure=None):
    """只替换 HTTP 传输，真实 SDK、严格 planner、runner 与磁盘检查点仍执行。"""
    runner, resources, store, data, run_id, downstream_http = await setup(tmp_path)
    if downstream_failure == 'answer':
        resources.model.finish = 'length'
    elif downstream_failure == 'judge':
        resources.model.invalid_judge = True
    data = replace(data, cases=(replace(data.cases[0], query=question),))
    requests = []

    async def respond(request):
        """离线上游返回完整协议响应，支持私存响应直接回放而不打印正文。"""
        requests.append(json.loads(request.content))
        if response_bytes is not None:
            return httpx.Response(200, content=response_bytes, headers={'Content-Type': 'application/json'})
        return httpx.Response(200, json=dict(id='offline-rewrite', object='chat.completion', created=0,
            model='local-test', choices=[dict(index=0, message=dict(role='assistant',
                content=json.dumps(body, ensure_ascii=False)), finish_reason=finish)]))

    http = httpx.AsyncClient(transport=httpx.MockTransport(respond),
        event_hooks={'request': [resources.requests.model_hook]})
    model = create_model(settings(), http_async_client=http)
    resources.planner = QueryPlanner(model_with_output_budget(model, settings(), 2048), 8000)
    try:
        outcome = await runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, asyncio.Event())
        rows = await store.records(run_id)
        counts = (await store.get(run_id))['request_counts']
        return outcome, rows, counts, runner.retrieval.calls, requests
    finally:
        model.root_client.close()
        await http.aclose()
        await downstream_http.aclose()


@pytest.mark.parametrize('body', [
    [dict(answer=dict(standard='被包裹内容', expansions=[])), dict(standard='第二项', expansions=[])],
    dict(answer=dict(standard='被包裹内容', expansions=[])),
])
@pytest.mark.parametrize('finish', ['stop', 'length', 'content_filter'])
async def test_invalid_real_sdk_rewrite_uses_one_shared_original_plan(tmp_path, body, finish):
    """若解包猜字段、丢失型号金额否定条件或四路再规划，将破坏实际结果和请求计数。"""
    outcome, rows, counts, calls, requests = await run_invalid_response(tmp_path, body, finish=finish)
    assert outcome == 'completed'
    assert len(rows) == 4 and all(row['status'] == 'completed' for row in rows)
    assert all(row.get('rewrite') == declaration('degraded', 'invalid_structured_output') for row in rows)
    assert all(row['query_plan'] == dict(standard=QUESTION, expansions=[]) for row in rows)
    assert [strategy for strategy, _ in calls] == list(STRATEGIES)
    assert all(plan is calls[0][1] for _, plan in calls)
    assert [counts[name] for name in ('rewrite', 'self_check', 'answer', 'judge')] == [1, 4, 4, 4]
    assert len(requests) == 1 and requests[0]['messages'][-1]['content'] == QUESTION
    assert requests[0]['response_format'] == {'type': 'json_object'}
    assert requests[0]['max_tokens'] == 2048


@pytest.mark.parametrize('stage', ['answer', 'judge'])
async def test_downstream_validation_remains_strict_after_degraded_rewrite(tmp_path, stage):
    """原话降级不授权截断答案或非法裁判，错误仍阻止路线完成且保留改写失败。"""
    outcome, rows, counts, _, _ = await run_invalid_response(tmp_path, {'answer': {}}, downstream_failure=stage)
    assert outcome == 'completed_with_errors'
    assert all(row['status'] == ('answer_error' if stage == 'answer' else 'judge_error') for row in rows)
    assert all(row['rewrite'] == declaration('degraded', 'invalid_structured_output') for row in rows)
    assert counts['rewrite'] == 1 and counts['judge'] == (0 if stage == 'answer' else 4)


async def test_success_and_upstream_failure_have_distinct_rewrite_declarations(tmp_path):
    """改写失败不能按完成路线数被统计为成功，成功/错误均保留按题声明。"""
    all_rows = []
    for failed in (False, True):
        runner, resources, store, data, run_id, http = await setup(tmp_path / str(failed))
        resources.model.rewrite_error = failed
        data = replace(data, cases=(replace(data.cases[0], eval_id='E1' if failed else 'E0'),),
            pilot_ids=('E1' if failed else 'E0',))
        # 测试换题号后重新创建精确计划，不复用不匹配运行。
        run_id = await store.create(build_run_config(data, settings(), 'pilot'),
            [(data.cases[0].eval_id, strategy) for strategy in STRATEGIES])
        runner.run_id = resources.requests.run_id = run_id
        try:
            await runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, asyncio.Event())
            rows = await store.records(run_id)
            assert all(row.get('rewrite') == declaration('error', 'upstream_error') if failed else
                row.get('rewrite') == declaration() for row in rows)
            all_rows.extend(rows)
        finally:
            await http.aclose()
    degraded = [completed_record('E2', strategy, query=QUESTION,
        query_plan=dict(standard=QUESTION, expansions=[]),
        rewrite=declaration('degraded', 'invalid_structured_output')) for strategy in STRATEGIES]
    summary = summarize_records(all_rows + degraded)
    assert summary.get('rewrite') == dict(attempted_n=3, success_n=1, degraded_n=1, error_n=1,
        success_rate=1/3, unreported_n=0)


@pytest.mark.parametrize('change', ['query', 'expansion', 'code', 'missing_error', 'success_error', 'extra'])
def test_degraded_declaration_cannot_forge_original_query_or_safe_failure(change):
    """无原话/空扩展或安全无效输出原因的降级记录不得通过生产校验。"""
    row = completed_record(query=QUESTION, query_plan=dict(standard=QUESTION, expansions=[]),
        rewrite=declaration('degraded', 'invalid_structured_output'))
    if change == 'query':
        row['query_plan']['standard'] = 'MH-W40可以换货吗？'
    elif change == 'expansion':
        row['query_plan']['expansions'] = ['换货']
    elif change == 'code':
        row['rewrite']['error']['code'] = 'upstream_error'
    elif change == 'missing_error':
        row['rewrite']['error'] = None
    elif change == 'success_error':
        row['rewrite']['status'] = 'success'
    else:
        row['rewrite']['request_body'] = 'PRIVATE'
    with pytest.raises(ValueError):
        validate_case_record(row)


def test_rewrite_summary_excludes_unattempted_and_preserves_historical_missing():
    """历史缺声明不得补成成功；未尝试和无结果检查点不进入成功率分母。"""
    from tests.test_rag_store import record
    old = completed_record('OLD')
    assert 'rewrite' not in public_report(dict(schema_version=2, records=[old]))['records'][0]
    assert 'rewrite' not in summarize_records([old])
    rows = [completed_record('E0', strategy, rewrite=declaration()) for strategy in STRATEGIES]
    rows += [record('E1', strategy) | {'rewrite': None} for strategy in STRATEGIES]
    rows += [old]
    assert summarize_records(rows).get('rewrite') == dict(attempted_n=1, success_n=1,
        degraded_n=0, error_n=0, success_rate=1., unreported_n=1)


def test_failure_policy_is_fingerprinted_and_historical_config_stays_missing():
    """新失败策略若未进入指纹，旧严格试运行将错误授权新全量。"""
    from tests.test_rag_runner import frozen
    config = build_run_config(frozen(), settings(), 'pilot')
    assert config['provenance'].get('rewrite_failure_policy') == POLICY
    previous = copy.deepcopy(config)
    previous['provenance'].pop('rewrite_failure_policy')
    previous['fingerprint'] = hashlib.sha256(json.dumps({key: value for key, value in previous.items()
        if key not in ('scope', 'fingerprint')}, sort_keys=True, ensure_ascii=False,
        separators=(',', ':')).encode('utf-8')).hexdigest()
    assert validate_config(previous) == previous
    assert config['fingerprint'] != previous['fingerprint']
    assert build_run_config(frozen(), settings(), 'full')['fingerprint'] == config['fingerprint']


@pytest.mark.parametrize('change', ['missing', 'different_plan', 'different_declaration'])
async def test_full_gate_rejects_missing_or_inconsistent_rewrite_evidence(tmp_path, monkeypatch, change):
    """即使40条路线全部完成且审计合法，缺声明或四路计划不同也不能放行。"""
    h = Harness(monkeypatch, tmp_path)
    run_id = await h.manager.start(DATASET_ID, 'pilot')
    await h.manager.wait(run_id)
    path = next((tmp_path / run_id / 'records').glob('*.json'))
    row = json.loads(path.read_text(encoding='utf-8'))
    if change == 'missing':
        row.pop('rewrite', None)
    elif change == 'different_plan':
        row['query_plan']['standard'] = '别的题面'
    else:
        row['rewrite'] = declaration('degraded', 'invalid_structured_output')
    path.write_text(json.dumps(row, ensure_ascii=False), encoding='utf-8')
    fresh = type(h.manager)(RunStore(tmp_path), h.manager.settings, h.manager.dataset_root)
    assert await fresh.pilot_ready(DATASET_ID) is False
    with pytest.raises(PilotRequired):
        await fresh.start(DATASET_ID, 'full')


async def test_old_audited_v2_download_remains_readonly_with_missing_rewrite(tmp_path):
    """新读取器不得补写旧v2改写声明，原JSON/Markdown仍能按原字节下载。"""
    from app.rag_evaluation.export import publish_reports
    runner, _, store, data, run_id, http = await setup(tmp_path)
    try:
        await runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, asyncio.Event())
    finally:
        await http.aclose()
    for path in (tmp_path/run_id/'records').glob('*.json'):
        row = json.loads(path.read_text(encoding='utf-8'))
        row.pop('rewrite')
        path.write_text(json.dumps(row, ensure_ascii=False), encoding='utf-8')
    manifest_path = tmp_path/run_id/'manifest.json'
    historical = json.loads(manifest_path.read_text(encoding='utf-8'))
    historical['config']['provenance'].pop('rewrite_failure_policy')
    manifest_path.write_text(json.dumps(historical, ensure_ascii=False), encoding='utf-8')
    store = RunStore(tmp_path)
    final = dict(await store.get(run_id), state='completed', outcome='completed', stage='complete',
        cleanup=dict(ok=True, errors=[], unverified=[]))
    publish_reports(tmp_path, final, await store.records(run_id), await store.source_map(run_id))
    await store.update(run_id, {key: final[key] for key in ('state', 'outcome', 'stage', 'cleanup')})
    before = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in (tmp_path/run_id).rglob('*') if path.is_file()}
    app, _ = application(tmp_path, manager=ManagerDouble(store))
    async with client_for(app) as client:
        responses = [await client.get(f'{PREFIX}/runs/{run_id}/export?format={kind}') for kind in ('json', 'markdown')]
        detail = await client.get(f'{PREFIX}/runs/{run_id}/cases/E0/dense')
    assert [response.status_code for response in responses] == [200, 200]
    assert 'rewrite' not in detail.json()
    assert detail.json()['audit'] is not None
    assert before == {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in (tmp_path/run_id).rglob('*') if path.is_file()}


@pytest.mark.parametrize('kind', ['timeout', 'upstream', 'input', 'unknown', 'invalid_timeout',
    'invalid_input', 'invalid_store', 'wrapped_store', 'cancel', 'invalid_cancel', 'invalid_unknown'])
async def test_other_rewrite_exceptions_never_enter_retrieval(tmp_path, kind):
    """放宽错误匹配、忽略cause存储错误或吞取消，均会触发检索/错误状态断言。"""
    runner, resources, store, data, run_id, http = await setup(tmp_path)

    class FailingPlanner:
        """在已有服务边界注入精确异常链，保留真实runner/store请求钩子。"""
        async def plan(self, query):
            """只请求一次，并通过明确类型复现允许/禁止错误交叉边界。"""
            await resources.model.request('rewrite', [])
            if kind == 'cancel':
                raise asyncio.CancelledError()
            if kind in ('invalid_store', 'wrapped_store'):
                outer = ServiceError('invalid_structured_output' if kind == 'invalid_store' else
                    'upstream_error', 'private', 502)
                outer.__cause__ = StoreError('private-storage')
                raise outer
            if kind in ('invalid_timeout', 'invalid_input'):
                outer = ServiceError('invalid_structured_output', 'private', 502)
                outer.__cause__ = TimeoutError() if kind == 'invalid_timeout' else InputTooLong()
                raise outer
            if kind in ('invalid_cancel', 'invalid_unknown'):
                outer = ServiceError('invalid_structured_output', 'private', 502)
                outer.__cause__ = asyncio.CancelledError() if kind == 'invalid_cancel' else RuntimeError('private')
                raise outer
            raise {'timeout': TimeoutError(), 'upstream': ServiceError('upstream_error', 'private', 502),
                'input': InputTooLong(), 'unknown': RuntimeError('private')}[kind]

    resources.planner = FailingPlanner()
    try:
        if kind in ('invalid_store', 'wrapped_store'):
            with pytest.raises(StoreError):
                await runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, asyncio.Event())
        else:
            outcome = await runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, asyncio.Event())
            assert outcome == ('cancelled' if kind in ('cancel', 'invalid_cancel') else 'completed_with_errors')
            rows = await store.records(run_id)
            if kind in ('cancel', 'invalid_cancel'):
                assert [row['status'] for row in rows] == ['cancelled', 'not_attempted', 'not_attempted', 'not_attempted']
            else:
                assert all(row['status'] == 'rewrite_error' and row.get('rewrite', {}).get('status') == 'error' for row in rows)
        assert runner.retrieval.calls == []
        assert (await store.get(run_id))['request_counts']['rewrite'] == 1
    finally:
        await http.aclose()


async def test_invalid_output_arriving_after_absolute_deadline_stays_error(tmp_path):
    """无效输出到达后仍须复查原期限，不能因降级跳过超时或多付费。"""
    runner, resources, store, data, run_id, http = await setup(tmp_path)
    runner.settings = settings().model_copy(update={'query_timeout_seconds': .01})

    class LatePlanner:
        """延迟来自外部依赖，runner必须依靠自己的绝对期限再次拒绝。"""
        async def plan(self, query):
            """不重试，模拟一个迟到的已验证无效结构异常。"""
            await resources.model.request('rewrite', [])
            await asyncio.sleep(.03)
            raise ServiceError('invalid_structured_output', 'private', 502)

    resources.planner = LatePlanner()
    try:
        assert await runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, asyncio.Event()) == 'completed_with_errors'
        rows = await store.records(run_id)
        assert all(row.get('rewrite', {}).get('error', {}).get('type') == 'TimeoutError' for row in rows)
        assert runner.retrieval.calls == []
    finally:
        await http.aclose()


async def test_known_json_decoder_failure_is_still_structured_output_degradation(tmp_path):
    """已知JSON解析链不能误判未知上游故障，改写仍仅一次且保留无效结构原因。"""
    runner, resources, store, data, run_id, http = await setup(tmp_path)

    class InvalidJsonPlanner:
        """只在服务边界复现常见OutputParserException和JSONDecodeError原因链。"""
        async def plan(self, query):
            """上游无效JSON分类不丢失类型；原始正文从不进入公开错误。"""
            await resources.model.request('rewrite', [])
            parser = OutputParserException('private')
            parser.__cause__ = json.JSONDecodeError('private', '', 0)
            error = ServiceError('invalid_structured_output', 'private', 502)
            error.__cause__ = parser
            raise error

    resources.planner = InvalidJsonPlanner()
    try:
        assert await runner.run_cases(data, {'one': 1, 'two': 2}, data.pilot_ids, asyncio.Event()) == 'completed'
        assert all(row['rewrite'] == declaration('degraded', 'invalid_structured_output')
            for row in await store.records(run_id))
        assert len(runner.retrieval.calls) == 4
        assert (await store.get(run_id))['request_counts']['rewrite'] == 1
    finally:
        await http.aclose()
