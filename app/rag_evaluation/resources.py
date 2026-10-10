"""隔离评估资源的唯一拥有者；提交前登记、哈希核验后删除、实际请求计数。"""

import asyncio
from collections.abc import Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import asdict, fields
from hashlib import sha256
from importlib.metadata import version
import json
from types import MappingProxyType

import grpc
import httpx
from pymilvus import AsyncMilvusClient
from pymilvus.client.async_grpc_handler import AsyncGrpcHandler
from sqlalchemy import delete, select, text

from app.config import Settings
from app.core.llm import create_model, model_with_output_budget
from app.db.models import Base, KnowledgeChunk
from app.db.session import Database
from app.knowledge.embeddings import SiliconFlowEmbedder
from app.knowledge.hybrid_jobs import HybridKnowledgeJobs
from app.knowledge.types import ChunkDraft, ChunkRecord
from app.quality.repository import QualityRepository
from app.rag_evaluation.contracts import CleanupResult, FrozenDataset
from app.rag_evaluation.store import RunStore, validate_manifest
from app.repositories.knowledge import KnowledgeRepository, _ids, _record
from app.retrieval.milvus import HybridMilvusIndex
from app.retrieval.query import QueryPlanner
from app.retrieval.rerank import SiliconFlowReranker

DATABASE_IDENTITY = {'host': '127.0.0.1', 'port': 3308, 'name': 'customer_service_test'}
REQUEST_STAGES = ('rewrite', 'self_check', 'answer', 'judge', 'embedding', 'rerank', 'milvus')


def content_hash(chunk: ChunkDraft | ChunkRecord) -> str:
    """六个 ChunkDraft 字段按键排序、紧凑 JSON、原样 Unicode UTF-8 作 SHA256；排除可变身份状态。"""
    stable = {field.name: getattr(chunk, field.name) for field in fields(ChunkDraft)}
    return sha256(json.dumps(stable, ensure_ascii=False, sort_keys=True,
                             separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()


class RequestCounter:
    """一个运行共用的串行计数器；发出前落盘，失败禁止未登记请求出站。"""
    def __init__(self, store: RunStore, run_id: str, initial: Mapping[str, int]):
        """从已验证 manifest 恢复绝对计数，阶段上下文按异步任务隔离。"""
        if set(initial) != set(REQUEST_STAGES) or any(type(v) is not int or v < 0 for v in initial.values()):
            raise ValueError('invalid request counter snapshot')
        self._store, self._run_id, self._counts = store, run_id, dict(initial)
        self._lock = asyncio.Lock()
        self._stage = ContextVar(f'rag-stage-{run_id}', default=None)

    @contextmanager
    def stage(self, stage: str):
        """runner 借用此同步上下文包围一次阶段调用，嵌套退出还原原阶段。"""
        if stage not in REQUEST_STAGES[:4]:
            raise ValueError('invalid model request stage')
        token = self._stage.set(stage)
        try:
            yield
        finally:
            self._stage.reset(token)

    async def increment(self, stage: str) -> None:
        """仅由真实请求边界调用；持锁更新完整快照，不用读取加一竞争。"""
        if stage not in REQUEST_STAGES:
            raise ValueError('missing or invalid request stage')
        async with self._lock:
            counts = dict(self._counts)
            counts[stage] += 1
            await self._store.update(self._run_id, {'request_counts': counts})
            self._counts = counts

    async def model_hook(self, request: httpx.Request) -> None:
        """HTTPX 已准备的模型请求出站前计数，缺明确阶段直接失败。"""
        await self.increment(self._stage.get())

    def fixed_hook(self, stage: str):
        """给嵌入和重排专用客户端绑定固定阶段，不从 URL 或正文猜测。"""
        if stage not in ('embedding', 'rerank'):
            raise ValueError('invalid fixed HTTP request stage')
        async def hook(request: httpx.Request) -> None:
            """每个实际 HTTP 请求（含失败响应）只增加一次对应计数。"""
            await self.increment(stage)
        return hook


class _RPCInterceptor(grpc.aio.UnaryUnaryClientInterceptor):
    """在真实 gRPC continuation 前计数，包含握手、轮询、schema 刷新与重放。"""
    def __init__(self, counter: RequestCounter):
        """保存与 HTTP 共用的单一计数器。"""
        self.counter = counter

    async def intercept_unary_unary(self, continuation, client_call_details, request):
        """发布成功后立即交给 gRPC，发布失败不发网络请求。"""
        await self.counter.increment('milvus')
        return await continuation(client_call_details, request)


class _CountedHandler(AsyncGrpcHandler):
    """固定 PyMilvus 3.0.2 局部适配：每次创建/重建通道均安装计数拦截器。"""
    def __init__(self, *, counter, **kwargs):
        """先绑定计数器，再允许父构造创建独占通道。"""
        self._counter = counter
        self._channel_closures = {}
        self._handler_closing = False
        super().__init__(**kwargs)

    def _create_channel(self, address):
        """仅隔离评估使用本机明文服务；禁底层重试，避免不可观察的额外 attempt。"""
        if self._handler_closing:
            raise ValueError('Milvus handler is closing')
        if self._secure:
            raise ValueError('evaluation requires the local Milvus endpoint')
        channel = grpc.aio.insecure_channel(address, options=[
            ('grpc.max_send_message_length', -1), ('grpc.max_receive_message_length', -1),
            ('grpc.enable_retries', 0)], interceptors=[_RPCInterceptor(self._counter)])
        # 注册早于握手或发布；未安装的替换通道同样属于本拥有者。
        self._channel_closures[channel] = None
        return channel

    async def _close_channel(self, channel, grace=None):
        """每条通道只启动一次真实 close，保留任务直到完成或失败供最终清理核验。"""
        closing = self._channel_closures[channel]
        if closing is None:
            closing = asyncio.create_task(channel.close(grace=grace))
            self._channel_closures[channel] = closing
        await asyncio.shield(closing)

    async def reconnect(self, address=None, timeout=10):
        """复用固定 SDK 握手与发布步骤，任何取消窗口都回收尚未发布的替换通道。"""
        target = address or self._address
        deadline = timeout if timeout is not None else 10
        channel = self._create_channel(target)
        try:
            final_channel, stub = self._build_stub(channel)
            identifier, final_channel, stub = await self._setup_identifier_interceptor_for_channel(
                final_channel, stub, self._user, timeout=deadline)
            async with self._reconnect_lock:
                if self._handler_closing:
                    raise ValueError('Milvus handler is closing')
                previous = self._async_channel
                self._address = target
                self._async_channel, self._final_channel, self._async_stub = channel, final_channel, stub
                self._async_identifier_interceptor = identifier
                self._is_channel_ready = True
        except BaseException:
            try:
                await self._close_channel(channel)
            except (Exception, asyncio.CancelledError):
                # 原取消/握手错误继续传播；关闭失败留在登记任务中由 owner 汇总。
                pass
            raise
        if previous is not None:
            retired = asyncio.create_task(self._close_retired_channel(previous, grace=deadline))
            self._retired_channel_close_tasks.add(retired)
            retired.add_done_callback(self._retired_channel_close_tasks.discard)

    async def _close_retired_channel(self, channel, grace):
        """SDK 退休路径与最终清理共用同一 close 任务，错误留给最终清理汇总。"""
        try:
            await self._close_channel(channel, grace=grace)
        except (Exception, asyncio.CancelledError):
            pass

    async def close(self):
        """关闭并等待所有已登记通道，包含握手未发布和退休中的通道，不首错中断。"""
        self._handler_closing = True
        async with self._reconnect_lock:
            self._async_channel = self._final_channel = self._async_stub = None
            self._is_channel_ready = False
        outcomes = await asyncio.gather(*(self._close_channel(channel)
            for channel in self._channel_closures), return_exceptions=True)
        if self._retired_channel_close_tasks:
            await asyncio.gather(*tuple(self._retired_channel_close_tasks), return_exceptions=True)
        errors = [outcome for outcome in outcomes if isinstance(outcome, BaseException)]
        if errors:
            # 已收集的关闭取消同样是清理失败，不能以 BaseExceptionGroup 跳过 owner 后续清理。
            raise RuntimeError('Milvus channel cleanup failed') from BaseExceptionGroup('channel errors', errors)


class _CountedMilvusClient(AsyncMilvusClient):
    """只替换固定 SDK 的私有连接接缝，数据与 BM25 操作仍由原客户端实现。"""
    def __init__(self, uri: str, counter: RequestCounter):
        """版本或本机端点不符就拒绝，绝不退回逻辑调用估数。"""
        if version('pymilvus') != '3.0.2':
            raise ValueError('counted Milvus adapter requires pymilvus 3.0.2')
        from urllib.parse import urlsplit
        parsed = urlsplit(uri)
        if parsed.scheme != 'http' or parsed.hostname not in ('127.0.0.1', 'localhost', '::1'):
            raise ValueError('evaluation requires the local Milvus endpoint')
        super().__init__(uri=uri, timeout=None)
        self._counter = counter
        self._connect_lock = asyncio.Lock()

    async def _connect(self):
        """延迟建立专属 handler，提前保留句柄以便握手失败仍能关闭。"""
        async with self._connect_lock:
            if self._handler is None:
                self._handler = _CountedHandler(counter=self._counter, uri=self._config.uri,
                    address=self._config.address, token=self._config.token,
                    db_name=self._config.db_name, **self._config.get_handler_kwargs())
                await self._handler.ensure_channel_ready(timeout=5)
                self._using = f'rag-evaluation-{id(self)}'
                self.is_self_hosted = self._handler.get_server_type() == 'milvus'

    async def close(self):
        """本实例只关闭其专属 handler，不触碰全局连接管理器。"""
        if not self._closed:
            self._closed = True
            if self._handler is not None:
                await self._handler.close()


class ScopedRepository:
    """只暴露本次拥有主键的读取与向量化状态更新，不继承全库写入入口。"""
    def __init__(self, database: Database, ids: list[int]):
        """冻结允许访问的主键集合。"""
        _ids(ids)
        self.database, self.ids = database, frozenset(ids)

    async def pending(self, limit: int = 20) -> list[ChunkRecord]:
        """只读本次 pending，确保嵌入 HTTP 前当前短事务已结束。"""
        return await self._page('pending', 0, limit)

    async def done_page(self, *, after_id: int = 0, limit: int = 20) -> list[ChunkRecord]:
        """本次 done 主键分页，不消费旁置测试数据。"""
        return await self._page('done', after_id, limit)

    async def _page(self, status: str, after_id: int, limit: int) -> list[ChunkRecord]:
        """查询包含白名单、状态与游标三个条件并验证分页参数。"""
        if type(limit) is not int or limit < 1 or type(after_id) is not int or not 0 <= after_id <= 9223372036854775807:
            raise ValueError('invalid scoped page')
        async with self.database.session() as session, session.begin():
            rows = await session.scalars(select(KnowledgeChunk).where(
                KnowledgeChunk.id.in_(self.ids), KnowledgeChunk.vectorize_status == status,
                KnowledgeChunk.id > after_id).order_by(KnowledgeChunk.id).limit(limit))
            return [_record(row) for row in rows]

    async def get_done(self, ids: list[int]) -> list[ChunkRecord]:
        """输入顺序回填白名单已完成行，外部命中无法进入生成证据。"""
        _ids(ids)
        return await KnowledgeRepository(self.database).get_done([i for i in ids if i in self.ids])

    async def mark_done(self, ids: list[int]) -> None:
        """禁止混入非自有 ID 的整批状态修改。"""
        _ids(ids)
        if not set(ids) <= self.ids:
            raise ValueError('cannot update unowned knowledge')
        await KnowledgeRepository(self.database).mark_done(ids)


class OwnedResources:
    """一个运行唯一资源所有者，runner 仅借用公开依赖并负责持有 RunLease。"""
    def __init__(self, settings: Settings, store: RunStore, run_id: str):
        """构造不发 I/O，资源成功创建后立即登记相应关闭函数。"""
        self.settings, self.store, self.run_id = settings, store, run_id
        self.collection = f'knowledge_test_{run_id}'
        self.database = self.index = self.requests = None
        self._closers = []
        self._http_clients = []
        self._cleanup_result = None
        self._cleanup_lock = asyncio.Lock()
        self._started = False

    def _open_database(self):
        """强制使用既有 3308 测试账号地址，业务 Settings 不被改写。"""
        if self.database is None:
            self.database = Database(self.settings.database_url.set(**{
                'host': '127.0.0.1', 'port': 3308, 'database': 'customer_service_test',
                'username': 'customer_service'}))
            self._closers.append(('database', self.database.dispose))

    async def _verify_database(self):
        """只读确认实际库名及现行八表，缺表不自动迁移或重建。"""
        async with self.database.session() as session:
            if await session.scalar(text('SELECT DATABASE()')) != 'customer_service_test':
                raise ValueError('evaluation database identity mismatch')
            tables = set(await session.scalars(text(
                'SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE()')))
            if tables != set(Base.metadata.tables):
                raise ValueError('evaluation requires the existing eight-table schema')

    def _open_index(self):
        """客户端和索引分开登记，后者借用前者且不重复关闭。"""
        client = _CountedMilvusClient(str(self.settings.milvus_uri), self.requests)
        self._closers.append(('milvus_client', client.close))
        self.index = HybridMilvusIndex(str(self.settings.milvus_uri), collection=self.collection,
                                      timeout=self.settings.milvus_timeout_seconds, client=client)
        self._closers.append(('index', self.index.aclose))

    def _http(self, hook):
        """创建独占且仅一次关闭的 HTTP 客户端，适配器只借用它。"""
        client = httpx.AsyncClient(event_hooks={'request': [hook]})
        self._http_clients.append(client)
        self._closers.append(('http', client.aclose))
        return client

    def _models(self):
        """回答与裁判各自经工厂创建；预算副本不拥有新客户端。"""
        http = self._http(self.requests.model_hook)
        self.model = create_model(self.settings, http_async_client=http)
        self._register_model(self.model)
        self.judge_model = create_model(self.settings.model_copy(update={
            'max_output_tokens': self.settings.faith_judge_max_output_tokens}), http_async_client=http)
        self._register_model(self.judge_model)
        self.planner = QueryPlanner(model_with_output_budget(self.model, self.settings,
            self.settings.query_max_output_tokens), self.settings.tool_input_token_budget,
            timeout=self.settings.query_timeout_seconds)
        self.quality = QualityRepository(self.database)
        self.embedder = SiliconFlowEmbedder(self.settings, http_client=self._http(self.requests.fixed_hook('embedding')))
        self.reranker = SiliconFlowReranker(self.settings, http_client=self._http(self.requests.fixed_hook('rerank')))

    def _register_model(self, model):
        """同步 SDK 独占客户端单次关闭；异步 SDK 借用 HTTP，由其唯一所有者关闭。"""
        async def close():
            """关闭同步 HTTP 池放到线程，资源清理可执行十秒上限。"""
            await asyncio.to_thread(model.root_client.close)
        self._closers.append(('model', close))

    async def prepare(self, dataset: FrozenDataset) -> Mapping[str, int]:
        """先冻结归属，再分批短事务导入，HTTP 嵌入在事务外执行并核对全集。"""
        if self._started or self._cleanup_result is not None:
            raise ValueError('resources already used')
        self._started = True
        manifest = await self.store.get(self.run_id)
        provenance = manifest['config'].get('provenance')
        if (manifest['ownership'] is not None or dataset.dataset_id != manifest['config']['dataset_id']
                or not isinstance(provenance, dict)
                or any(provenance.get(key) != value for key, value in {
                    'dataset_fingerprint': dataset.fingerprint, 'corpus_hash': dataset.corpus_hash,
                    'cases_hash': dataset.cases_hash, 'annotation_hash': dataset.annotation_hash}.items())
                or not dataset.chunks
                or len({chunk.chunk_key for chunk in dataset.chunks}) != len(dataset.chunks)):
            raise ValueError('dataset or resource ownership mismatch')
        self.requests = RequestCounter(self.store, self.run_id, manifest['request_counts'])
        self._open_database()
        await self._verify_database()
        try:
            self._open_index()
            self._models()
        except BaseException:
            await self.cleanup()
            raise
        async with asyncio.timeout(self.index.timeout):
            if await self.index._call('has_collection', self.collection):
                raise ValueError('evaluation collection already exists')
        ownership = dict(database=dict(DATABASE_IDENTITY), collection=self.collection,
                         owned_ids=[], content_hashes={}, pending_ids=[])
        await self.store.update(self.run_id, {'ownership': ownership})
        await self.index.ensure_collection()
        mapping = {}
        repository = KnowledgeRepository(self.database)
        for start in range(0, len(dataset.chunks), 20):
            batch = dataset.chunks[start:start + 20]
            async def register(ids):
                """当前批次 flush 主键、稳定内容哈希与累积 pending 同一快照发布。"""
                new = dict(ownership, owned_ids=ownership['owned_ids'] + ids,
                    content_hashes={**ownership['content_hashes'], **{
                        str(i): content_hash(chunk.draft) for i, chunk in zip(ids, batch)}},
                    pending_ids=ownership['pending_ids'] + ids)
                await self.store.update(self.run_id, {'ownership': new})
                ownership.update(new)
            ids = await repository.add_chunks([chunk.draft for chunk in batch], before_commit=register)
            ownership['pending_ids'] = [i for i in ownership['pending_ids'] if i not in ids]
            await self.store.update(self.run_id, {'ownership': ownership})
            mapping.update({chunk.chunk_key: i for chunk, i in zip(batch, ids)})
        self.repository = ScopedRepository(self.database, ownership['owned_ids'])
        jobs = HybridKnowledgeJobs(self.repository, self.embedder, self.index)
        if await jobs.vectorize_pending() != len(dataset.chunks):
            raise ValueError('evaluation vectorized count mismatch')
        proof = await jobs.verify_done()
        rows = await self.repository.get_done(ownership['owned_ids'])
        if (not proof['ready'] or len(rows) != len(dataset.chunks) or len(mapping) != len(rows)
                or any(content_hash(row) != ownership['content_hashes'][str(row.id)] for row in rows)):
            raise ValueError('evaluation physical identity verification failed')
        return MappingProxyType(mapping)

    async def _delete_rows(self, ownership, unverified):
        """同一短事务锁住候选行，摘要相等才删；已回滚的缺行自然无残留。"""
        async with self.database.session() as session, session.begin():
            rows = await session.scalars(select(KnowledgeChunk).where(
                KnowledgeChunk.id.in_(ownership['owned_ids'])).with_for_update())
            verified = []
            for row in rows:
                if content_hash(_record(row)) == ownership['content_hashes'][str(row.id)]:
                    verified.append(row.id)
                else:
                    unverified.append(f'knowledge:{row.id}')
            if verified:
                await session.execute(delete(KnowledgeChunk).where(KnowledgeChunk.id.in_(verified)))

    async def _delete_collection(self):
        """仅删除已登记的精确 UUID 集合，整个 Milvus 动作沿用五秒期限。"""
        async with asyncio.timeout(self.index.timeout):
            if await self.index._call('has_collection', self.collection):
                await self.index._call('drop_collection', self.collection)

    async def cleanup(self) -> CleanupResult:
        """逐项最多十秒，失败仍尝试剩余动作，重复调用不再关闭客户端。"""
        async with self._cleanup_lock:
            if self._cleanup_result is not None:
                return self._cleanup_result
            errors, unverified = [], []
            async def attempt(label, action):
                """有界执行一个清理动作，只留安全标识与异常类型。"""
                try:
                    async with asyncio.timeout(10):
                        await action()
                    return True
                except (Exception, asyncio.CancelledError) as exc:
                    errors.append(f'{label}:{type(exc).__name__}')
                    return False
            ownership = None
            try:
                async with asyncio.timeout(10):
                    manifest = await self.store.get(self.run_id)
                ownership = manifest['ownership']
                if ownership is not None:
                    if ownership['database'] != DATABASE_IDENTITY or ownership['collection'] != self.collection:
                        raise ValueError('resource ownership mismatch')
                    if self.requests is None:
                        self.requests = RequestCounter(self.store, self.run_id, manifest['request_counts'])
                    self._open_database()
                    if await attempt('database_identity', self._verify_database):
                        await attempt('knowledge', lambda: self._delete_rows(ownership, unverified))
                    if self.index is None:
                        self._open_index()
                    await attempt('collection', self._delete_collection)
            except (Exception, asyncio.CancelledError) as exc:
                unverified.append(f'ownership:{type(exc).__name__}')
            while self._closers:
                label, close = self._closers.pop()
                await attempt(label, close)
            result = CleanupResult(not errors and not unverified, tuple(errors), tuple(unverified))
            try:
                async with asyncio.timeout(10):
                    await self.store.update(self.run_id, {'cleanup': asdict(result) | {
                        'errors': list(result.errors), 'unverified': list(result.unverified)}})
            except (Exception, asyncio.CancelledError) as exc:
                result = CleanupResult(False, result.errors + (f'cleanup_snapshot:{type(exc).__name__}',), result.unverified)
            self._cleanup_result = result
            return result

    async def recover(self, manifest: Mapping[str, object]) -> CleanupResult:
        """只恢复当前持久快照的归属，不执行模型或根据外来 ID 推断所有权。"""
        try:
            checked = validate_manifest(manifest)
            current = await self.store.get(self.run_id)
            if checked['run_id'] != self.run_id or checked['ownership'] != current['ownership']:
                raise ValueError('recovery ownership differs from stored manifest')
        except Exception as exc:
            return CleanupResult(False, (), (f'manifest:{type(exc).__name__}',))
        return await self.cleanup()
