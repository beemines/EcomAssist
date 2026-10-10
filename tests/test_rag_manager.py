"""使用真实存储和文件锁验证运行门槛、取消与恢复，外部资源全部替换。"""

import asyncio
from dataclasses import replace
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys

import httpx
import pytest

from app.rag_evaluation.contracts import CleanupResult
from app.rag_evaluation.dataset import load_dataset, DatasetError
from app.rag_evaluation.locking import RunBusy, RunLock
from app.rag_evaluation.report import STRATEGIES
from app.rag_evaluation.runner import _seed
from app.rag_evaluation.store import RunStore, StoreError
from tests.test_rag_resources import settings

ROOT = Path(__file__).resolve().parents[1]
DATASET_ID = 'merchant-rag-300-v1'


def api():
    """缺失模块以功能断言呈现 RED，避免导入收集错误。"""
    assert importlib.util.find_spec('app.rag_evaluation.manager'), '尚未实现运行管理器'
    return importlib.import_module('app.rag_evaluation.manager')


class Harness:
    """只替换收费与服务边界，记录和锁仍使用生产实现。"""
    def __init__(self, monkeypatch, tmp_path):
        """加载真正300题冻结数据，替身可阻塞、取消或制造清理故障。"""
        self.module = api()
        self.dataset = load_dataset(DATASET_ID, root=ROOT / 'evals/datasets')
        self.store = RunStore(tmp_path)
        self.entered, self.release = asyncio.Event(), asyncio.Event()
        self.block, self.swallow, self.bad_cleanup = False, False, False
        self.omit_last, self.prepare_error, self.cleanup_raises = False, False, False
        self.calls, self.cleanup_calls, self.recover_calls = 0, 0, 0
        owner = self
        class Resources:
            """资源替身不会创建外部连接，清理顺序通过运行状态验证。"""
            def __init__(self, configuration, store, run_id):
                """保留真实运行身份，便于清理期间验证锁和状态。"""
                self.store, self.run_id = store, run_id

            async def prepare(self, dataset):
                """准备阶段也可失败，且没有任何收费网络调用。"""
                if owner.prepare_error:
                    raise RuntimeError('private')
                return {chunk.chunk_key: i + 1 for i, chunk in enumerate(dataset.chunks)}

            async def cleanup(self):
                """清理必须持锁，不能在执行尚未结束时进入。"""
                owner.cleanup_calls += 1
                with pytest.raises(RunBusy):
                    RunLock(owner.store.root).acquire()
                if owner.cleanup_raises:
                    raise RuntimeError('private-cleanup-failure')
                return CleanupResult(not owner.bad_cleanup, ('failed',) if owner.bad_cleanup else (), ())

            async def recover(self, manifest):
                """恢复仅清理，不能进入 prepare 或评估。"""
                owner.recover_calls += 1
                return await self.cleanup()

        class Runner:
            """以合法逐题记录替代模型，质量故意低以验证门槛不看分数。"""
            def __init__(self, resources, store, run_id, configuration):
                """保存存储入口，所有阶段仍经过真实结构验证。"""
                self.store, self.run_id = store, run_id

            async def run_cases(self, dataset, id_map, case_ids, cancel_event):
                """生成合法零召回记录或模拟不响应一次取消的依赖。"""
                owner.calls += 1
                owner.entered.set()
                if owner.block:
                    try:
                        await owner.release.wait()
                    except asyncio.CancelledError:
                        if owner.swallow:
                            await owner.release.wait()
                        else:
                            return 'cancelled'
                if cancel_event.is_set():
                    return 'cancelled'
                selected = [case for case in dataset.cases if case.eval_id in case_ids]
                for case in selected:
                    for strategy in STRATEGIES:
                        if owner.omit_last and case == selected[-1] and strategy == STRATEGIES[-1]:
                            continue
                        row = _seed(case, strategy, id_map)
                        row.update(status='completed', stage='complete', refused=True,
                            query_plan={'standard': case.query, 'expansions': []}, candidate_ids=[],
                            final_ids=[], prompt_citations=[], decision={'useful': False,
                            'reason': '无证据', 'response_kind': 'knowledge', 'source': 'self_check'},
                            answer='资料不足', point_verdicts=[{'point_id': p.point_id,
                            'covered': False, 'reason': '未覆盖'} for p in case.points], claim_verdicts=[],
                            elapsed_ms=1, judge_snapshot={'prompt_version': 'v2', 'finish_reason': 'stop'})
                        await self.store.put_case(self.run_id, row)
                return 'completed'

        monkeypatch.setattr(self.module, 'OwnedResources', Resources)
        monkeypatch.setattr(self.module, 'EvaluationRunner', Runner)
        self.manager = self.module.RunManager(self.store, settings(), ROOT / 'evals/datasets')


async def test_single_start_and_cancel_idempotent(tmp_path, monkeypatch):
    """第二次启动拒绝，重复取消只触发一次清理且终态可读取。"""
    h = Harness(monkeypatch, tmp_path)
    h.block = True
    run_id = await h.manager.start(DATASET_ID, 'pilot')
    await h.entered.wait()
    with pytest.raises(RunBusy):
        await h.manager.start(DATASET_ID, 'pilot')
    await h.manager.cancel(run_id)
    await h.manager.cancel(run_id)
    result = await h.manager.wait(run_id)
    assert result['state'] == 'cancelled' and h.cleanup_calls == 1
    assert (await h.manager.cancel(run_id))['state'] == 'cancelled'
    RunLock(tmp_path).acquire().close()


async def test_full_requires_successful_matching_pilot(tmp_path, monkeypatch):
    """必须先有40条结构合法且清理成功的试运行；低质量仍可放行。"""
    h = Harness(monkeypatch, tmp_path)
    with pytest.raises(h.module.PilotRequired):
        await h.manager.start(DATASET_ID, 'full')
    assert h.calls == h.cleanup_calls == 0
    pilot = await h.manager.start(DATASET_ID, 'pilot')
    result = await h.manager.wait(pilot)
    assert result['counts']['completed'] == 40 and result['cleanup']['ok']
    full = await h.manager.start(DATASET_ID, 'full')
    await h.manager.cancel(full)
    assert (await h.manager.wait(full))['planned_records'] == 1200


@pytest.mark.parametrize('change', ['prompt', 'budget', 'corpus', 'cases', 'annotation', 'endpoint', 'transport', 'token'])
async def test_changed_prompt_budget_or_corpus_invalidates_pilot(tmp_path, monkeypatch, change):
    """每一种真实有效配置变动都使旧试运行失效，不依赖人工版本更新。"""
    h = Harness(monkeypatch, tmp_path)
    await h.manager.wait(await h.manager.start(DATASET_ID, 'pilot'))
    if change == 'prompt':
        monkeypatch.setattr(h.module.prompts, 'build_grounded_answer_system_prompt', lambda: 'changed')
    elif change in ('corpus', 'cases', 'annotation'):
        frozen = replace(h.dataset, **{change + '_hash': 'f' * 64})
        monkeypatch.setattr(h.module, 'load_dataset', lambda *args, **kwargs: frozen)
    else:
        fields = {'budget': ('tool_input_token_budget', 7000), 'endpoint': ('llm_base_url', 'https://example.test/v2'),
                  'transport': ('llm_timeout_seconds', 55), 'token': ('llm_token_limit_field', 'max_completion_tokens')}
        key, value = fields[change]
        h.manager.settings = h.manager.settings.model_copy(update={key: value})
    with pytest.raises(h.module.PilotRequired):
        await h.manager.start(DATASET_ID, 'full')


async def test_restart_interrupted_never_resumes_model(tmp_path, monkeypatch):
    """已启动记录保留成功产物后中断，缺席和未启动记录不冒充已执行。"""
    h = Harness(monkeypatch, tmp_path)
    config = h.module.build_run_config(h.dataset, settings(), 'pilot')
    case = h.dataset.cases[0]
    run_id = await h.store.create(config, [(case.eval_id, s) for s in STRATEGIES])
    row = _seed(case, 'dense', {c.chunk_key: i + 1 for i, c in enumerate(h.dataset.chunks)})
    row.update(status='running', stage='retrieval', query_plan={'standard': case.query, 'expansions': []})
    await h.store.put_case(run_id, row)
    await h.store.update(run_id, {'state': 'running'})
    await h.manager.startup()
    result = await h.store.get(run_id)
    saved = (await h.store.records(run_id))[0]
    assert result['state'] == 'interrupted' and h.calls == 0 and h.recover_calls == 1
    assert saved['status'] == 'cancelled' and saved['query_plan'] == row['query_plan']
    assert saved['error']['code'] == 'interrupted' and result['counts']['not_attempted'] == 3


@pytest.mark.parametrize('cancelled', [False, True])
async def test_cleanup_failure_overrides_completed_or_cancelled(tmp_path, monkeypatch, cancelled):
    """清理失败覆盖状态但保留原结果，不能成为全量运行凭据。"""
    h = Harness(monkeypatch, tmp_path)
    h.bad_cleanup, h.block = True, cancelled
    run_id = await h.manager.start(DATASET_ID, 'pilot')
    if cancelled:
        await h.entered.wait()
        await h.manager.cancel(run_id)
    result = await h.manager.wait(run_id)
    assert result['state'] == 'failed'
    assert result['outcome'] == ('cancelled' if cancelled else 'completed')
    with pytest.raises(h.module.PilotRequired):
        await h.manager.start(DATASET_ID, 'full')


async def test_hung_cancel_does_not_release_lease_early(tmp_path, monkeypatch):
    """依赖吞取消时 shutdown 有界返回，但真实执行结束之前禁止清理和第二任务。"""
    h = Harness(monkeypatch, tmp_path)
    h.block = h.swallow = True
    monkeypatch.setattr(h.module, 'SHUTDOWN_TIMEOUT_SECONDS', .02)
    run_id = await h.manager.start(DATASET_ID, 'pilot')
    await h.entered.wait()
    await h.manager.cancel(run_id)
    await h.manager.shutdown()
    assert h.cleanup_calls == 0
    with pytest.raises(RunBusy):
        RunLock(tmp_path).acquire()
    h.release.set()
    assert (await h.manager.wait(run_id))['state'] == 'cancelled'
    RunLock(tmp_path).acquire().close()


async def test_busy_startup_does_not_recover_live_owner(tmp_path, monkeypatch):
    """另一管理器启动只读退让，不能把活跃进程的归属当成崩溃残留删除。"""
    h = Harness(monkeypatch, tmp_path)
    h.block = True
    run_id = await h.manager.start(DATASET_ID, 'pilot')
    await h.entered.wait()
    other = h.module.RunManager(RunStore(tmp_path), settings(), ROOT / 'evals/datasets')
    await other.startup()
    assert h.recover_calls == 0 and (await h.store.get(run_id))['state'] == 'running'
    await h.manager.cancel(run_id)
    await h.manager.wait(run_id)


@pytest.mark.parametrize('invalid', ['partial', 'legacy', 'error'])
async def test_partial_pilot_and_legacy_config_cannot_authorize_full(tmp_path, monkeypatch, invalid):
    """完成标签不能代替40条合法记录，历史缺少出处也不能放行。"""
    h = Harness(monkeypatch, tmp_path)
    h.omit_last = invalid == 'partial'
    run_id = await h.manager.start(DATASET_ID, 'pilot')
    await h.manager.wait(run_id)
    if invalid == 'legacy':
        path = tmp_path / run_id / 'manifest.json'
        manifest = json.loads(path.read_text('utf-8'))
        manifest['config'].pop('provenance')
        path.write_text(json.dumps(manifest), encoding='utf-8')
    elif invalid == 'error':
        row = (await h.store.records(run_id))[-1]
        row.update(status='judge_error', stage='judgment', point_verdicts=None, claim_verdicts=None,
                   metrics=None, error={'code': 'judge_error', 'type': 'TimeoutError', 'message': '失败'})
        await h.store.put_case(run_id, row)
    with pytest.raises(h.module.PilotRequired):
        await h.manager.start(DATASET_ID, 'full')


async def test_terminal_publication_failure_retains_lease(tmp_path, monkeypatch):
    """终态落盘失败必须可见且持锁失败关闭，不允许新收费任务。"""
    h = Harness(monkeypatch, tmp_path)
    original = h.store.update
    async def fail_terminal(run_id, patch):
        """只拒绝终态发布，使执行及资源清理可以真实完成。"""
        if patch.get('finished_at'):
            raise StoreError('disk')
        await original(run_id, patch)
    monkeypatch.setattr(h.store, 'update', fail_terminal)
    run_id = await h.manager.start(DATASET_ID, 'pilot')
    with pytest.raises(StoreError):
        await h.manager.wait(run_id)
    assert h.cleanup_calls == 1
    with pytest.raises(RunBusy):
        RunLock(tmp_path).acquire()
    # 故障测试模拟进程退出释放句柄，生产不得在发布失败时执行此步骤。
    h.manager._lease.close()


async def test_all_dataset_preflight_before_resources(tmp_path, monkeypatch):
    """pilot也必须先全量验证，题库损坏不能创建资源或收费。"""
    h = Harness(monkeypatch, tmp_path)
    def invalid(*args, **kwargs):
        """模拟300题审标中后部失败，而不是仅试运行样本有效。"""
        raise DatasetError('invalid corpus')
    monkeypatch.setattr(h.module, 'load_dataset', invalid)
    with pytest.raises(DatasetError):
        await h.manager.start(DATASET_ID, 'pilot')
    assert h.calls == h.cleanup_calls == 0 and await h.store.list_runs() == []


async def test_aggregate_export_exceeds_snapshot_cap_without_private_data(tmp_path):
    """合法1200条报告可超过单快照2MiB限制，导出仍完整且没有私有裁判原文。"""
    assert importlib.util.find_spec('app.rag_evaluation.export'), '尚未实现聚合报告原子发布'
    exports = importlib.import_module('app.rag_evaluation.export')
    from tests.test_rag_metrics import record
    from tests.test_rag_store import config
    store = RunStore(tmp_path)
    rows = [record(f'E{i}', strategy, answer='证据正文' * 240,
                   prompt_citations=[{'n': 1, 'chunk_id': '1', 'section_path': None,
                                      'question': '退货', 'answer': '完整证据' * 400}])
            for i in range(300) for strategy in STRATEGIES]
    run_id = await store.create(config(), [(row['eval_id'], row['strategy']) for row in rows])
    manifest = await store.get(run_id)
    exports.publish_reports(tmp_path, manifest, rows)
    path = tmp_path / run_id / 'report.json'
    assert path.stat().st_size > 2 * 1024 * 1024
    report = json.loads(path.read_text('utf-8'))
    assert len(report['records']) == 1200 and 'ownership' not in report['run']
    assert 'PRIVATE-JUDGE' not in path.read_text('utf-8')
    assert '完整证据' in (tmp_path / run_id / 'report.md').read_text('utf-8')


def test_cli_validate_and_fixed_paths(tmp_path, capsys, monkeypatch):
    """离线validate不加载模型设置；CLI不接受任意输出和服务连接参数。"""
    assert importlib.util.find_spec('evals.rag_workbench'), '尚未实现工作台CLI'
    cli = importlib.import_module('evals.rag_workbench')
    def forbidden():
        """验证题库不能读取收费客户端配置或模型凭据。"""
        raise AssertionError('validate read settings')
    monkeypatch.setattr(cli, 'load_settings', forbidden)
    assert cli.main(['validate', '--dataset', DATASET_ID]) == 0
    assert json.loads(capsys.readouterr().out)['cases'] == 300
    with pytest.raises(SystemExit):
        cli.main(['run', '--dataset', DATASET_ID, '--scope', 'pilot', '--output', str(tmp_path)])


def test_legacy_cli_conflicts_with_manager_os_lock(tmp_path, monkeypatch):
    """旧CLI入口也必须在执行前取得相同锁，不能越过HTTP管理器。"""
    from evals import evaluate_retrieval as legacy
    import app.rag_evaluation.manager as manager
    monkeypatch.setattr(manager, 'RUNTIME_ROOT', tmp_path)
    source = tmp_path / 'cases.jsonl'
    source.write_text('{"eval_id":"E1"}\n', encoding='utf-8')
    calls = []
    async def execute(*args, **kwargs):
        """原算法入口用无外部请求替身，绕锁将被calls捕获。"""
        calls.append(True)
        return {'passed': True}
    monkeypatch.setattr(legacy, 'evaluate', execute)
    lease = RunLock(tmp_path).acquire()
    try:
        assert legacy.main(['--mode', 'compare', '--cases', str(source),
                            '--output', str(tmp_path / 'legacy.json')]) != 0
        assert calls == []
    finally:
        lease.close()


async def test_export_failure_holds_lease_after_cleanup(tmp_path, monkeypatch):
    """报告发布失败不能宣称终态或释放租约，即使清理已经成功。"""
    h = Harness(monkeypatch, tmp_path)
    def fail(*args):
        """定点模拟聚合报告落盘失败，不影响逐题检查点。"""
        raise StoreError('export failed')
    monkeypatch.setattr(h.module, 'publish_reports', fail)
    run_id = await h.manager.start(DATASET_ID, 'pilot')
    with pytest.raises(StoreError):
        await h.manager.wait(run_id)
    assert h.cleanup_calls == 1 and (await h.store.get(run_id))['state'] == 'running'
    with pytest.raises(RunBusy):
        RunLock(tmp_path).acquire()
    h.manager._lease.close()


async def test_cleanup_exception_is_failed_with_original_outcome(tmp_path, monkeypatch):
    """清理自身抛错也必须留失败终态，不能只让后台任务消失。"""
    h = Harness(monkeypatch, tmp_path)
    h.cleanup_raises = True
    run_id = await h.manager.start(DATASET_ID, 'pilot')
    try:
        result = await h.manager.wait(run_id)
        assert result['state'] == 'failed' and result['outcome'] == 'completed'
        assert result['cleanup']['ok'] is False
    finally:
        if h.manager._lease is not None:
            h.manager._lease.close()


async def test_shutdown_bound_includes_blocked_store(tmp_path, monkeypatch):
    """关闭阶段不能先无限等待存储读取，再开始计算有界等待。"""
    h = Harness(monkeypatch, tmp_path)
    h.block = h.swallow = True
    monkeypatch.setattr(h.module, 'SHUTDOWN_TIMEOUT_SECONDS', .02)
    run_id = await h.manager.start(DATASET_ID, 'pilot')
    await h.entered.wait()
    original = h.store.get
    blocked = asyncio.Event()
    async def get(run_id):
        """阻断存储读取以确认shutdown不依赖先完成该读取。"""
        await blocked.wait()
        return await original(run_id)
    monkeypatch.setattr(h.store, 'get', get)
    try:
        async with asyncio.timeout(.3):
            await h.manager.shutdown()
        assert h.cleanup_calls == 0
        with pytest.raises(RunBusy):
            RunLock(tmp_path).acquire()
    finally:
        blocked.set()
        h.release.set()
        await h.manager.wait(run_id)


async def test_prepare_failure_preserves_plan_and_zero_requests(tmp_path, monkeypatch):
    """准备失败不制造物理题目，完整计划与零请求必须保留。"""
    h = Harness(monkeypatch, tmp_path)
    h.prepare_error = True
    result = await h.manager.wait(await h.manager.start(DATASET_ID, 'pilot'))
    assert result['state'] == result['outcome'] == 'failed'
    assert result['counts']['not_attempted'] == 40 and h.calls == 0 and h.cleanup_calls == 1
    assert sum(result['request_counts'].values()) == 0


async def test_legacy_cli_real_process_conflict(tmp_path, monkeypatch):
    """另一个真正CLI进程必须被HTTP将使用的同一manager系统锁立即拒绝。"""
    h = Harness(monkeypatch, tmp_path)
    h.block = True
    run_id = await h.manager.start(DATASET_ID, 'pilot')
    await h.entered.wait()
    cases = tmp_path / 'cases.jsonl'
    cases.write_text('{"eval_id":"E1"}\n', encoding='utf-8')
    script = ('import sys; from pathlib import Path; from app.rag_evaluation import manager; '
              'manager.RUNTIME_ROOT=Path(sys.argv[1]); from evals.evaluate_retrieval import main; '
              'raise SystemExit(main(["--mode","compare","--cases",sys.argv[2],"--output",sys.argv[3]]))')
    child = await asyncio.to_thread(subprocess.run, [sys.executable, '-c', script, str(tmp_path),
        str(cases), str(tmp_path / 'unused.json')], capture_output=True, text=True, encoding='utf-8',
        timeout=30, cwd=ROOT, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    try:
        assert child.returncode == 2 and json.loads(child.stdout)['error_code'] == 'run_busy'
        assert not (tmp_path / 'unused.json').exists() and h.cleanup_calls == 0
    finally:
        await h.manager.cancel(run_id)
        await h.manager.wait(run_id)


async def test_actual_embedding_rerank_paths_change_fingerprint(monkeypatch):
    """真实HTTP适配器与报告共用有效端点，路径调整必须同步使试运行失效。"""
    from app.knowledge import embeddings
    from app.retrieval import rerank
    from pydantic import SecretStr
    module = api()
    data = load_dataset(DATASET_ID, root=ROOT / 'evals/datasets')
    configuration = settings().model_copy(update={'siliconflow_api_key': SecretStr('secret')})
    original = module.build_run_config(data, configuration, 'pilot')
    monkeypatch.setattr(embeddings, 'EMBEDDING_ENDPOINT', 'https://local.test/v2/embeddings', raising=False)
    monkeypatch.setattr(rerank, 'RERANK_ENDPOINT', 'https://local.test/v2/rerank', raising=False)
    urls = []
    async def respond(request):
        """真实HTTP客户端只进入本机MockTransport，返回适配器所需完整协议。"""
        urls.append(str(request.url))
        payload = {'data': [{'index': 0, 'embedding': [0.] * 1024}]} if request.url.path.endswith('embeddings') else {
            'results': [{'index': 0, 'relevance_score': .5}]}
        return httpx.Response(200, json=payload)
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as http:
        await embeddings.SiliconFlowEmbedder(configuration, http_client=http).embed(['正文'])
        await rerank.SiliconFlowReranker(configuration, http_client=http).rank('问题', ['正文'])
    assert urls == ['https://local.test/v2/embeddings', 'https://local.test/v2/rerank']
    changed = module.build_run_config(data, configuration, 'pilot')
    assert changed['fingerprint'] != original['fingerprint']
    assert changed['provenance']['endpoint_hashes']['embedding'] != original['provenance']['endpoint_hashes']['embedding']
    assert changed['provenance']['endpoint_hashes']['rerank'] != original['provenance']['endpoint_hashes']['rerank']


async def test_waiter_cancel_does_not_cancel_owner(tmp_path, monkeypatch):
    """HTTP请求断连或CLI等待者取消，不能悄悄取消运行所有者并释放租约。"""
    h = Harness(monkeypatch, tmp_path)
    h.block = True
    run_id = await h.manager.start(DATASET_ID, 'pilot')
    await h.entered.wait()
    waiter = asyncio.create_task(h.manager.wait(run_id))
    await asyncio.sleep(0)
    waiter.cancel()
    with pytest.raises(asyncio.CancelledError):
        await waiter
    assert h.cleanup_calls == 0
    with pytest.raises(RunBusy):
        RunLock(tmp_path).acquire()
    h.release.set()
    assert (await h.manager.wait(run_id))['state'] == 'completed'


async def test_unknown_ownership_recovery_stays_failed(tmp_path, monkeypatch):
    """无法核验的归属只能记录清理失败，不能以恢复成功授权新全量。"""
    h = Harness(monkeypatch, tmp_path)
    config = h.module.build_run_config(h.dataset, settings(), 'pilot')
    run_id = await h.store.create(config, [(h.dataset.pilot_ids[0], 'dense')])
    async def unknown(self, manifest):
        """资源层明确报告未核验，不调用任何删除接口。"""
        return CleanupResult(False, (), ('ownership:unverified',))
    monkeypatch.setattr(h.module.OwnedResources, 'recover', unknown)
    await h.manager.startup()
    result = await h.store.get(run_id)
    assert result['state'] == 'failed' and result['outcome'] == 'interrupted'
    assert result['cleanup']['unverified'] == ['ownership:unverified'] and h.calls == 0
    RunLock(tmp_path).acquire().close()


async def test_export_atomic_failure_and_cap_preserve_previous(tmp_path, monkeypatch):
    """独立聚合上限与原子替换失败都保留上一份完整文件，无截断降级。"""
    from app.rag_evaluation import export
    h = Harness(monkeypatch, tmp_path)
    run_id = await h.manager.start(DATASET_ID, 'pilot')
    await h.manager.wait(run_id)
    paths = [tmp_path / run_id / name for name in ('report.json', 'report.md')]
    before = [path.read_bytes() for path in paths]
    manifest, rows = await h.store.get(run_id), await h.store.records(run_id)
    with monkeypatch.context() as patcher:
        patcher.setattr(export, 'MAX_EXPORT_BYTES', 1024)
        with pytest.raises(StoreError):
            export.publish_reports(tmp_path, manifest, rows)
    assert [path.read_bytes() for path in paths] == before
    def broken(src, dst):
        """只破坏最终文件替换，让真实临时文件写入及清理执行。"""
        raise OSError('replace denied')
    with monkeypatch.context() as patcher:
        patcher.setattr(export.os, 'replace', broken)
        with pytest.raises(StoreError):
            export.publish_reports(tmp_path, manifest, rows)
    assert [path.read_bytes() for path in paths] == before
    assert not list((tmp_path / run_id).glob('.report-*.tmp'))


def test_cli_run_show_and_safe_provenance(tmp_path, monkeypatch, capsys):
    """真正CLI完成试运行并输出相同公开封套，show不加载模型设置。"""
    from evals import rag_workbench as cli
    h = Harness(monkeypatch, tmp_path)
    monkeypatch.setattr(cli.lifecycle, 'RUNTIME_ROOT', tmp_path)
    monkeypatch.setattr(cli, 'load_settings', settings)
    assert cli.main(['run', '--dataset', DATASET_ID, '--scope', 'pilot']) == 0
    report = json.loads(capsys.readouterr().out)
    assert report['run']['state'] == 'completed' and len(report['records']) == 40
    assert report['run']['config']['provenance']['corpus_hash'] == h.dataset.corpus_hash
    assert report['run']['config']['provenance']['dataset_fingerprint'] == h.dataset.fingerprint
    assert 'ownership' not in report['run']
    def forbidden():
        """历史展示不能读取模型配置或请求上游。"""
        raise AssertionError('show read settings')
    monkeypatch.setattr(cli, 'load_settings', forbidden)
    assert cli.main(['show', '--run-id', report['run_id']]) == 0
    assert json.loads(capsys.readouterr().out)['records'] == report['records']


@pytest.mark.parametrize('counter_failure', [False, True])
async def test_real_runner_manager_and_wrapped_counter_failure(tmp_path, monkeypatch, counter_failure):
    """实际runner和请求计数器借用生命周期；计数磁盘故障被SDK包装后仍停止全部出站。"""
    from app.rag_evaluation import runner
    from app.rag_evaluation.resources import RequestCounter
    from app.retrieval.query import QueryPlanner
    from tests.test_rag_runner import Model, Quality, Retrieval
    h = Harness(monkeypatch, tmp_path)
    dispatched = []
    async def respond(request):
        """计数钩子之后才算进入本机传输，用于确认故障不会继续出站。"""
        dispatched.append(True)
        return httpx.Response(200, json={})
    http = None
    original_cleanup = h.module.OwnedResources.cleanup
    async def prepare(owner, dataset):
        """只替换外部资源准备，runner、planner、裁判和计数器均为真实实现。"""
        nonlocal http
        counter = RequestCounter(h.store, owner.run_id, (await h.store.get(owner.run_id))['request_counts'])
        http = httpx.AsyncClient(transport=httpx.MockTransport(respond), event_hooks={'request': [counter.model_hook]})
        owner.requests, owner.model = counter, Model(http)
        owner.judge_model, owner.planner = owner.model, QueryPlanner(owner.model, 8000)
        owner.repository = owner.index = owner.embedder = owner.reranker = None
        owner.quality = Quality()
        return {chunk.chunk_key: i + 1 for i, chunk in enumerate(dataset.chunks)}
    async def cleanup(owner):
        """真实HTTP客户端仅由唯一资源所有者关闭，runner不能提前关闭。"""
        if http is not None:
            await http.aclose()
        return await original_cleanup(owner)
    monkeypatch.setattr(h.module.OwnedResources, 'prepare', prepare)
    monkeypatch.setattr(h.module.OwnedResources, 'cleanup', cleanup)
    monkeypatch.setattr(h.module, 'EvaluationRunner', runner.EvaluationRunner)
    monkeypatch.setattr(runner, 'RetrievalService', lambda *args: Retrieval())
    original_update = h.store.update
    async def update(run_id, patch):
        """只让真实HTTP计数快照发布失败，其余终态和清理记录仍可持久化。"""
        if counter_failure and 'request_counts' in patch:
            raise StoreError('counter disk failed')
        await original_update(run_id, patch)
    monkeypatch.setattr(h.store, 'update', update)
    run_id = await h.manager.start(DATASET_ID, 'pilot')
    result = await h.manager.wait(run_id)
    assert h.cleanup_calls == 1 and http.is_closed
    if counter_failure:
        assert result['state'] == 'failed' and dispatched == []
        assert result['counts']['running'] == 0 and result['counts']['attempted'] > 0
        assert result['counts']['not_attempted'] > 0
    else:
        assert result['state'] == 'completed' and result['counts']['completed'] == 40
        assert result['request_counts']['rewrite'] == 10 and result['request_counts']['judge'] == 40
        assert len(dispatched) == sum(result['request_counts'].values())
    RunLock(tmp_path).acquire().close()
