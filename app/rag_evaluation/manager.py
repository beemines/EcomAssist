"""拥有完整评估生命周期：全量预检、版本门槛、执行收回、清理及持锁终态发布。"""

import asyncio
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from app.config import Settings
from app.core import prompts
from app.knowledge import embeddings
from app.rag_evaluation import judgment
from app.rag_evaluation.contracts import CleanupResult, FrozenDataset, Scope
from app.rag_evaluation.dataset import DatasetError, load_dataset
from app.rag_evaluation.export import publish_reports
from app.rag_evaluation.locking import RunBusy, RunLock
from app.rag_evaluation.report import STRATEGIES
from app.rag_evaluation.resources import OwnedResources
from app.rag_evaluation.runner import EvaluationRunner
from app.rag_evaluation.store import OUTCOMES, RunStore, StoreError, public_run_metadata, validate_config
from app.retrieval import rerank

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = PROJECT_ROOT / 'runtime/rag-evaluation'
DATASET_ROOT = PROJECT_ROOT / 'evals/datasets'
SHUTDOWN_TIMEOUT_SECONDS = 30.


class PilotRequired(ValueError):
    """全量评估需要配置完全匹配、结构合法且清理成功的固定试运行。"""


def _digest(value: object) -> str:
    """仅对显式安全数据进行规范 JSON 哈希，不接受模型对象或请求正文。"""
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()


def _endpoint(address: str, suffix: str = '') -> tuple[str, str]:
    """公开只保存 origin；路径参与摘要，凭据、查询串和片段均不序列化。"""
    parsed = urlsplit(str(address))
    host = parsed.hostname
    if parsed.scheme not in ('http', 'https') or not host:
        raise StoreError('上游端点非法')
    host = '[' + host + ']' if ':' in host else host
    netloc = host + (':' + str(parsed.port) if parsed.port else '')
    origin = urlunsplit((parsed.scheme, netloc, '', '', ''))
    path = parsed.path.rstrip('/') + suffix if suffix else parsed.path or '/'
    return origin, _digest(urlunsplit((parsed.scheme, netloc, path, '', '')))


def build_run_config(dataset: FrozenDataset, settings: Settings, scope: Scope) -> dict[str, object]:
    """冻结实际预算、模型、Prompt内容及独立资料摘要；scope不影响匹配指纹。"""
    addresses = {'llm': _endpoint(str(settings.llm_base_url), '/chat/completions'),
        'embedding': _endpoint(embeddings.EMBEDDING_ENDPOINT),
        'rerank': _endpoint(rerank.RERANK_ENDPOINT),
        'milvus': _endpoint(str(settings.milvus_uri))}
    config = dict(dataset_id=dataset.dataset_id, scope=scope, mode='content_ablation',
        models=dict(answer=settings.llm_model, rewrite=settings.llm_model, self_check=settings.llm_model,
                    judge=settings.llm_model, embedding=settings.embedding_model, rerank=settings.rerank_model),
        budgets=dict(candidate_k=50, final_k=10, chunk_target_chars=1200, chunk_overlap_chars=120,
            case_concurrency=2, answer_output_tokens=settings.max_output_tokens,
            rewrite_output_tokens=settings.query_max_output_tokens,
            self_check_output_tokens=settings.sufficiency_max_output_tokens,
            judge_input_tokens=settings.faith_judge_input_token_budget,
            judge_output_tokens=settings.faith_judge_max_output_tokens,
            tool_input_tokens=settings.tool_input_token_budget, model_retries=0,
            rewrite_timeout_s=settings.query_timeout_seconds, self_check_timeout_s=settings.sufficiency_timeout_seconds,
            faq_timeout_s=settings.faq_timeout_seconds, chat_timeout_s=settings.chat_timeout_seconds,
            judge_timeout_s=settings.llm_timeout_seconds, embedding_timeout_s=settings.embedding_timeout_seconds,
            rerank_timeout_s=settings.rerank_timeout_seconds, milvus_timeout_s=settings.milvus_timeout_seconds),
        prompt_versions=dict(rewrite='query-v1', self_check='sufficiency-v1', answer='grounded-answer-v1',
                             judge=judgment.PROMPT_VERSION),
        upstream_summary={key: addresses[key][0] for key in ('llm', 'embedding', 'rerank')},
        provenance=dict(dataset_fingerprint=dataset.fingerprint, corpus_hash=dataset.corpus_hash,
            cases_hash=dataset.cases_hash, annotation_hash=dataset.annotation_hash,
            prompt_hashes=dict(rewrite=_digest(prompts.build_query_messages('')[0].content),
                self_check=_digest(prompts.build_sufficiency_messages('', {})[0].content),
                answer=_digest(prompts.build_grounded_answer_system_prompt()), judge=_digest(judgment.JUDGE_PROMPT)),
            endpoint_hashes={key: address[1] for key, address in addresses.items()},
            llm_timeout_s=settings.llm_timeout_seconds, llm_token_limit_field=settings.llm_token_limit_field))
    config['fingerprint'] = _digest({key: value for key, value in config.items() if key != 'scope'})
    return validate_config(config)


def _now() -> str:
    """生命周期审计使用有时区 UTC，避免不同入口时间语义不同。"""
    return datetime.now(timezone.utc).isoformat()


class RunManager:
    """后台 owner 强引用执行任务与租约，取消调用方不能提前释放任何所有权。"""
    def __init__(self, store: RunStore, settings: Settings, dataset_root: Path):
        """构造无收费或恢复副作用；同根跨入口使用同一个系统文件锁。"""
        self.store, self.settings, self.dataset_root = store, settings, dataset_root
        self._guard = asyncio.Lock()
        self._lease = self._task = self._execution = None
        self._run_id = None
        self._cancel_event = asyncio.Event()
        self._cancel_sent = False
        self._closing = False

    async def startup(self) -> None:
        """持锁后才读取并恢复；其他进程忙时直接退让，不触碰活跃归属。"""
        async with self._guard:
            if self._lease is not None:
                return
            try:
                self._lease = RunLock(self.store.root).acquire()
            except RunBusy:
                return
            self._task = asyncio.create_task(self._recover_all())
            self._task.add_done_callback(self._observe)
            task = self._task
        await asyncio.shield(task)

    def _observe(self, task: asyncio.Task) -> None:
        """取回后台异常防止静默丢失；强引用和租约仍留给等待方检查。"""
        if not task.cancelled():
            task.exception()

    async def _history(self, *, persist_repair: bool = True) -> list[dict]:
        """分页遍历完整历史，不因第一页没有匹配试运行而错判。"""
        result, offset = [], 0
        while True:
            page = await self.store.list_runs(offset, 100, persist_repair=persist_repair)
            result.extend(page)
            if len(page) < 100:
                return result
            offset += len(page)

    async def _recover_all(self) -> None:
        """恢复不续跑模型；逐个清理、发布中断快照，全部成功发布后释放锁。"""
        for manifest in await self._history():
            if manifest['state'] not in OUTCOMES:
                owner = OwnedResources(self.settings, self.store, manifest['run_id'])
                try:
                    result = await owner.recover(manifest)
                except (Exception, asyncio.CancelledError) as exc:
                    result = CleanupResult(False, ('recovery:' + type(exc).__name__,), ('ownership',))
                await self._finish(manifest['run_id'], 'interrupted', result, 'interrupted')
        self._release()

    def _release(self) -> None:
        """只有已收回执行、清理并完成报告和终态发布才允许调用。"""
        self._lease.close()
        self._lease = None

    async def _pilot(self, dataset: FrozenDataset, config: dict, *, persist_repair: bool = True) -> bool:
        """固定十题四路必须全部合法完成，分数高低不参与放行。"""
        expected = {(key, strategy) for key in dataset.pilot_ids for strategy in STRATEGIES}
        identity = {key: value for key, value in config.items() if key != 'scope'}
        for manifest in await self._history(persist_repair=persist_repair):
            previous = manifest['config']
            if (previous.get('provenance') is None or previous['scope'] != 'pilot'
                    or {key: value for key, value in previous.items() if key != 'scope'} != identity
                    or manifest['state'] != 'completed' or manifest['outcome'] != 'completed'
                    or manifest['cleanup'] != {'ok': True, 'errors': [], 'unverified': []}
                    or set(map(tuple, manifest['case_keys'])) != expected or len(expected) != 40):
                continue
            rows = await self.store.records(manifest['run_id'], persist_repair=persist_repair)
            source_map = await self.store.source_map(manifest['run_id'])
            if len(rows) == 40 and source_map is not None and all(row['status'] == 'completed' and
                    row.get('audit') is not None and row['audit']['audit_version'] == 1 and
                    row['audit']['source_map_id'] == source_map['source_map_id'] for row in rows):
                from app.rag_evaluation.audit import build_source_map, validate_audit_sources
                mapping = {source['chunk_key']: source['chunk_id'] for source in source_map['sources']}
                if set(mapping) != {chunk.chunk_key for chunk in dataset.chunks} or source_map != build_source_map(dataset, mapping):
                    continue
                for row in rows:
                    validate_audit_sources(row, source_map)
                return True
        return False

    async def pilot_ready(self, dataset_id: str) -> bool:
        """只读公开匹配门槛，复用完整出处检查且不持锁、建资源或调用模型。"""
        dataset = load_dataset(dataset_id, root=self.dataset_root)
        configuration = self.settings.model_copy(deep=True)
        return await self._pilot(dataset, build_run_config(dataset, configuration, 'full'), persist_repair=False)

    async def start(self, dataset_id: str, scope: Scope) -> str:
        """任何收费前全量离线预检，随后非排队取得跨进程锁并冻结新计划。"""
        if scope not in ('pilot', 'full'):
            raise DatasetError('未知运行范围')
        dataset = load_dataset(dataset_id, root=self.dataset_root)
        configuration = self.settings.model_copy(deep=True)
        config = build_run_config(dataset, configuration, scope)
        async with self._guard:
            if self._closing or self._lease is not None:
                raise RunBusy('已有评估运行或管理器正在关闭')
            self._lease = RunLock(self.store.root).acquire()
            try:
                # 未经 startup 的 CLI 也不能越过此前崩溃留下的归属。
                stale = any(row['state'] not in OUTCOMES for row in await self._history())
                if stale:
                    self._task = asyncio.create_task(self._recover_all())
                    self._task.add_done_callback(self._observe)
                    raise RunBusy('正在恢复上次评估，请稍后重试')
                if scope == 'full' and not await self._pilot(dataset, config):
                    raise PilotRequired('需要配置匹配且清理成功的40条合法试运行')
                ids = dataset.pilot_ids if scope == 'pilot' else tuple(case.eval_id for case in dataset.cases)
                run_id = await self.store.create(config, [(key, strategy) for key in ids for strategy in STRATEGIES])
            except PilotRequired:
                self._release()
                raise
            except RunBusy:
                raise
            except BaseException:
                # 磁盘故障可能留下不确定快照，保留锁直到进程重启后恢复。
                raise
            self._run_id, self._cancel_event, self._cancel_sent = run_id, asyncio.Event(), False
            self._execution = None
            self._task = asyncio.create_task(self._drive(run_id, dataset, ids, configuration))
            self._task.add_done_callback(self._observe)
            return run_id

    async def _execute(self, owner, dataset, ids, configuration) -> str:
        """执行任务只负责准备与借用 runner；唯一 lifecycle owner 负责清理。"""
        if self._cancel_event.is_set():
            return 'cancelled'
        await self.store.update(self._run_id, {'state': 'preparing', 'started_at': _now()})
        id_map = await owner.prepare(dataset)
        if self._cancel_event.is_set():
            return 'cancelled'
        await self.store.update(self._run_id, {'state': 'running'})
        return await EvaluationRunner(owner, self.store, self._run_id, configuration).run_cases(
            dataset, id_map, ids, self._cancel_event)

    async def _drive(self, run_id, dataset, ids, configuration) -> None:
        """严格执行 drain→cleanup→报告→终态→release，任何发布失败保持租约。"""
        owner = OwnedResources(configuration, self.store, run_id)
        outcome, error = 'failed', None
        self._execution = asyncio.create_task(self._execute(owner, dataset, ids, configuration))
        try:
            outcome = await self._execution
            if self._cancel_event.is_set():
                outcome = 'cancelled'
        except asyncio.CancelledError:
            outcome = 'cancelled'
        except Exception:
            error = 'execution_failed'
        # runner 的异常返回已 drain 全部题任务；再核验执行任务确实完成。
        await asyncio.gather(self._execution, return_exceptions=True)
        try:
            await self.store.update(run_id, {'stage': 'cleanup'})
        except StoreError:
            outcome, error = 'failed', 'storage_failed'
        try:
            cleanup = await owner.cleanup()
        except (Exception, asyncio.CancelledError) as exc:
            cleanup = CleanupResult(False, ('cleanup:' + type(exc).__name__,), ('ownership',))
        await self._finish(run_id, outcome, cleanup, error)
        self._release()

    async def _finish(self, run_id, outcome, cleanup: CleanupResult, error: str | None) -> None:
        """只改变真实开始的检查点，先发布完整安全报告再发布权威终态。"""
        for row in await self.store.records(run_id):
            if row['status'] == 'running':
                row.update(status='cancelled', error={'code': error or 'cancelled',
                    'type': 'InterruptedError', 'message': '该阶段执行失败'})
                await self.store.put_case(run_id, row)
        patch = dict(state=outcome if cleanup.ok else 'failed', outcome=outcome,
            stage='complete' if cleanup.ok else 'cleanup', cleanup=asdict(cleanup) | {
                'errors': list(cleanup.errors), 'unverified': list(cleanup.unverified)}, finished_at=_now(),
            error=None if error is None and cleanup.ok else {'code': error or 'cleanup_failed',
                'type': 'RuntimeError', 'message': '该阶段执行失败'})
        manifest = dict(await self.store.get(run_id), **patch)
        publish_reports(self.store.root, manifest, await self.store.records(run_id), await self.store.source_map(run_id))
        await self.store.update(run_id, patch)

    async def cancel(self, run_id: str) -> dict[str, object]:
        """取消幂等且不等待不可控依赖；第二次请求不会再次打断资源清理。"""
        async with self._guard:
            if self._run_id == run_id and self._lease is not None:
                self._signal_cancel()
            manifest = await self.store.get(run_id, persist_repair=False)
            if manifest['state'] not in OUTCOMES and self._run_id == run_id and self._lease is not None:
                await self.store.update(run_id, {'state': 'cancelling'})
                manifest = await self.store.get(run_id, persist_repair=False)
            return public_run_metadata(manifest)

    def _signal_cancel(self) -> None:
        """停止执行不依赖磁盘，关闭期限也必须包含任何受阻存储等待。"""
        self._cancel_event.set()
        if not self._cancel_sent:
            self._cancel_sent = True
            if self._execution is not None and not self._execution.done():
                self._execution.cancel()

    async def wait(self, run_id: str) -> dict[str, object]:
        """CLI等待与HTTP取消请求分开，等待者取消不传递给生命周期任务。"""
        if run_id == self._run_id and self._task is not None:
            await asyncio.shield(self._task)
        return public_run_metadata(await self.store.get(run_id))

    async def shutdown(self) -> None:
        """有界等候真正结束；超时保留后台强引用、原租约和归属。"""
        self._closing = True
        if self._lease is None:
            return
        self._signal_cancel()
        if self._task is not None:
            done, _ = await asyncio.wait((self._task,), timeout=SHUTDOWN_TIMEOUT_SECONDS)
            if done:
                await asyncio.shield(self._task)
