"""验证评估资源归属、提交窗口与只清理自有数据的边界。"""

import asyncio
from contextlib import asynccontextmanager, closing
from dataclasses import replace
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import sysconfig
import time
from types import SimpleNamespace
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import create_engine, delete, select, text
from sqlalchemy.orm import Session

from app.config import Settings, load_settings
from app.db.models import FaithCase, KnowledgeChunk
from app.db.session import Database
from app.knowledge.types import ChunkDraft, ChunkRecord
from app.rag_evaluation.contracts import CorpusChunk, FrozenDataset
from app.rag_evaluation.store import RunStore
from app.rag_evaluation.locking import RunLock
from app.repositories.knowledge import KnowledgeRepository
from tests.test_rag_store import config


def api():
    """以缺失功能断言呈现 RED，避免收集错误遮蔽测试意图。"""
    assert importlib.util.find_spec('app.rag_evaluation.resources'), '尚未实现资源归属与恢复'
    return importlib.import_module('app.rag_evaluation.resources')


def settings():
    """提供无真实密钥的固定预算配置，测试不能意外收费。"""
    return Settings(_env_file=None, llm_base_url='https://example.test/v1',
                    llm_model='local-test', llm_api_key='test', mysql_password='test')


def dataset():
    """两个已冻结块分别覆盖内容与可空元数据。"""
    return FrozenDataset('merchant-rag-300-v1', 'a' * 64, 'b' * 64, 'c' * 64, 'd' * 64,
        (CorpusChunk('one', 'one.md', 0, ChunkDraft('测试', '退货', '七天退货', '一', 'policy', True)),
         CorpusChunk('two', 'two.md', 0, ChunkDraft('测试', '运费', '满99元包邮'))), (), ())


class LocalDatabase:
    """测试专用同步 SQLite 适配，仅事务行为使用真实 SQLAlchemy。"""
    def __init__(self):
        """创建内存表，不访问真实数据库或业务 DDL。"""
        self.engine = create_engine('sqlite://')
        self.closed = 0
        with self.engine.begin() as connection:
            connection.execute(text('CREATE TABLE knowledge_chunks (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'category TEXT NOT NULL, questions TEXT NOT NULL, answer TEXT NOT NULL, section_path TEXT, '
                'content_type TEXT, is_key_clause INTEGER DEFAULT 0, prev_chunk_id INTEGER, next_chunk_id INTEGER, '
                "vector_id TEXT, vectorize_status TEXT DEFAULT 'pending', created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
                'updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)'))

    @asynccontextmanager
    async def session(self):
        """每次调用均生成真实独立事务，异步外观用于仓储单测。"""
        with Session(self.engine, expire_on_commit=False) as session:
            yield LocalSession(session)

    async def dispose(self):
        """记录关闭次数但保留内存库供清理后的断言读取。"""
        self.closed += 1


class LocalSession:
    """只适配已用 SQLAlchemy 操作，提交与回滚仍由真实 Session 执行。"""
    def __init__(self, session):
        """保存当前专属会话。"""
        self.inner = session

    @asynccontextmanager
    async def begin(self):
        """异常退出会触发真实回滚，正常退出提交。"""
        with self.inner.begin():
            yield

    def add_all(self, rows):
        """加入真实 ORM 行等待 flush。"""
        self.inner.add_all(rows)

    async def flush(self):
        """发出真实 INSERT 并取得主键。"""
        self.inner.flush()

    async def scalars(self, statement):
        """执行真实参数化查询并返回标量结果。"""
        return self.inner.scalars(statement)

    async def execute(self, statement):
        """执行真实删除等语句。"""
        return self.inner.execute(statement)


async def all_rows(database):
    """读取数据库真实持久行，避免对 mock 调用作替代断言。"""
    async with database.session() as session:
        return list(await session.scalars(select(KnowledgeChunk).order_by(KnowledgeChunk.id)))


async def test_manifest_failure_rolls_back_flushed_rows():
    """登记失败必须回滚实际已 flush 的行，而非遗留孤儿。"""
    database = LocalDatabase()
    seen = []
    async def fail(ids):
        """确认有主键后模拟归属快照写盘失败。"""
        seen.extend(ids)
        raise OSError('磁盘失败')
    with pytest.raises(OSError):
        await KnowledgeRepository(database).add_chunks([dataset().chunks[0].draft], before_commit=fail)
    assert len(seen) == 1
    assert await all_rows(database) == []


async def test_recorded_ids_recover_after_commit_interruption(tmp_path, monkeypatch):
    """提交后登记清空失败，旧 pending 快照仍可找回并清理真正落库的行。"""
    module = api()
    owner, store, database = await local_owner(module, tmp_path, monkeypatch)
    original = store.update
    async def fail_after_commit(run_id, patch):
        """仅在提交后的 pending 清空窗口中断。"""
        if patch.get('ownership', {}).get('owned_ids') and not patch['ownership']['pending_ids']:
            raise OSError('提交后中断')
        await original(run_id, patch)
    monkeypatch.setattr(store, 'update', fail_after_commit)
    with pytest.raises(OSError):
        await owner.prepare(dataset())
    manifest = await store.get(owner.run_id)
    assert manifest['ownership']['pending_ids']
    assert len(await all_rows(database)) == 2
    monkeypatch.setattr(store, 'update', original)
    recovered = module.OwnedResources(settings(), store, owner.run_id)
    assert (await recovered.recover(manifest)).ok
    assert await all_rows(database) == []


class MemoryIndex:
    """外部 Milvus 的确定性替身，保留集合与行的真实状态转换。"""
    collections = {}
    def __init__(self, uri, *, collection, timeout, client=None):
        """每个实例只允许修改显式传入的集合。"""
        self.collection, self.timeout = collection, timeout
        self.closed = 0

    async def ensure_collection(self, **kwargs):
        """建立指定集合的独立存储。"""
        self.collections.setdefault(self.collection, {})

    async def upsert(self, rows):
        """保存完整源字段并返回确认主键。"""
        self.collections[self.collection].update({row.id: row for row in rows})
        return [row.id for row in rows]

    async def verify_rows(self, rows):
        """核对写回内容，不能伪造 ACK 成功。"""
        assert all(self.collections[self.collection][row.id] == row for row in rows)

    async def get_rows(self, ids):
        """只读现存行。"""
        return [self.collections[self.collection][i] for i in ids if i in self.collections[self.collection]]

    async def all_ids(self):
        """返回真实替身集合主键。"""
        return set(self.collections[self.collection])

    async def _call(self, method, collection, **kwargs):
        """模拟只针对精确集合的存在查询与删除。"""
        assert collection == self.collection
        if method == 'has_collection':
            return collection in self.collections
        if method == 'drop_collection':
            self.collections.pop(collection, None)
            return
        raise AssertionError(method)

    async def aclose(self):
        """关闭本实例一次由资源拥有者保障。"""
        self.closed += 1


class DeterministicEmbedder:
    """替换外部收费嵌入请求，保持固定 1024 维向量契约。"""
    def __init__(self, *args, **kwargs):
        """替身不创建外部客户端。"""

    async def embed(self, texts):
        """为每个非空文本生成同一确定性非零向量。"""
        return [[1.0] + [0.0] * 1023 for _ in texts]


async def local_owner(module, tmp_path, monkeypatch):
    """保留真实存储、仓储与模型构造，仅隔离外部服务。"""
    database = LocalDatabase()
    store = RunStore(tmp_path)
    run_id = await store.create(config(), [('E1', 'dense')])
    monkeypatch.setattr(module, 'Database', lambda url: database)
    monkeypatch.setattr(module, 'HybridMilvusIndex', MemoryIndex)
    monkeypatch.setattr(module, 'SiliconFlowEmbedder', DeterministicEmbedder)
    async def checked(self):
        """SQLite 无 information_schema，真实 MySQL 核验留给集成用例。"""
        return None
    monkeypatch.setattr(module.OwnedResources, '_verify_database', checked)
    return module.OwnedResources(settings(), store, run_id), store, database


async def test_cleanup_only_owned_ids_and_exact_collection(tmp_path, monkeypatch):
    """清理必须保留旁置知识、集合及原始归属证据。"""
    module = api()
    owner, store, database = await local_owner(module, tmp_path, monkeypatch)
    sentinel = await KnowledgeRepository(database).add_chunks([ChunkDraft('旁置', '保留', '不可删除')])
    other = 'knowledge_test_' + 'f' * 32
    MemoryIndex.collections[other] = {}
    mapping = await owner.prepare(dataset())
    assert set(mapping) == {'one', 'two'}
    assert [r.id for r in await owner.repository.get_done(sentinel + list(mapping.values()))] == list(mapping.values())
    result = await owner.cleanup()
    assert result.ok
    assert [r.id for r in await all_rows(database)] == sentinel
    assert other in MemoryIndex.collections and owner.collection not in MemoryIndex.collections
    assert (await store.get(owner.run_id))['ownership']['owned_ids'] == list(mapping.values())
    assert (await owner.cleanup()) == result and database.closed == 1


async def test_unverified_ownership_is_not_deleted(tmp_path, monkeypatch):
    """同主键内容变化必须保留行并标未核验，不凭 ID 强删。"""
    module = api()
    owner, store, database = await local_owner(module, tmp_path, monkeypatch)
    mapping = await owner.prepare(dataset())
    with database.engine.begin() as connection:
        connection.execute(text('UPDATE knowledge_chunks SET answer=:answer WHERE id=:id'),
                           {'answer': '已被其他任务改写', 'id': mapping['one']})
    result = await owner.cleanup()
    assert not result.ok and result.unverified
    assert [r.id for r in await all_rows(database)] == [mapping['one']]


async def test_partial_constructor_failure_closes_owned_clients(tmp_path, monkeypatch):
    """第二模型构造失败仍释放已经创建的 HTTP、第一模型及数据库。"""
    module = api()
    owner, store, database = await local_owner(module, tmp_path, monkeypatch)
    factory = module.create_model
    models = []
    def fail_second(*args, **kwargs):
        """只注入第二个独立模型的构造失败。"""
        if models:
            raise RuntimeError('模型构造失败')
        model = factory(*args, **kwargs)
        models.append(model)
        return model
    monkeypatch.setattr(module, 'create_model', fail_second)
    with pytest.raises(RuntimeError):
        await owner.prepare(dataset())
    result = await owner.cleanup()
    assert result.ok and database.closed == 1 and models[0].root_client.is_closed()
    assert all(client.is_closed for client in owner._http_clients)
    assert (await owner.cleanup()) == result and database.closed == 1


def test_content_hash_ignores_mutable_status_and_ids():
    """稳定六字段摘要不随主键和向量状态变化，但必须识别元数据差异。"""
    module = api()
    draft = dataset().chunks[0].draft
    record = ChunkRecord(**draft.__dict__, id=17, vector_id='17', vectorize_status='done')
    assert module.content_hash(draft) == module.content_hash(record)
    assert module.content_hash(draft) != module.content_hash(replace(draft, is_key_clause=False))


async def test_request_counter_serializes_actual_http_attempts(tmp_path):
    """两个并发阶段与失败请求均累积，缺阶段在外部请求之前拒绝。"""
    module = api()
    store = RunStore(tmp_path)
    run_id = await store.create(config(), [('E1', 'dense')])
    counter = module.RequestCounter(store, run_id, (await store.get(run_id))['request_counts'])
    seen = []
    async def transport(request):
        """只在真实 HTTPX dispatch 边界观察到达的请求。"""
        seen.append(request)
        return httpx.Response(500)
    async with httpx.AsyncClient(transport=httpx.MockTransport(transport),
                                event_hooks={'request': [counter.model_hook]}) as client:
        with pytest.raises(ValueError):
            await client.post('https://example.test/v1/chat/completions')
        async def send(stage):
            """上下文隔离使并发阶段不会互相串标。"""
            with counter.stage(stage):
                await client.post('https://example.test/v1/chat/completions')
        await asyncio.gather(send('answer'), send('self_check'), send('judge'))
    assert len(seen) == 3
    counts = (await store.get(run_id))['request_counts']
    assert counts['answer'] == counts['self_check'] == counts['judge'] == 1
    assert counts['embedding'] == counts['rewrite'] == counts['milvus'] == 0


async def test_real_mysql_callback_rollback(mysql_database):
    """真实 3308 事务中登记失败后，已 flush 行不可见且无残留。"""
    seen = []
    async def fail(ids):
        """在真实提交前模拟快照失败。"""
        seen.extend(ids)
        raise OSError('登记失败')
    with pytest.raises(OSError):
        await KnowledgeRepository(mysql_database).add_chunks([dataset().chunks[0].draft], before_commit=fail)
    async with mysql_database.session() as session:
        assert not list(await session.scalars(select(KnowledgeChunk).where(KnowledgeChunk.id.in_(seen))))


async def test_counter_publication_failure_prevents_dispatch(tmp_path, monkeypatch):
    """写盘失败不发未计数请求，恢复后从最后成功快照递增一次。"""
    module = api()
    store = RunStore(tmp_path)
    run_id = await store.create(config(), [('E1', 'dense')])
    counter = module.RequestCounter(store, run_id, (await store.get(run_id))['request_counts'])
    real_update = store.update
    seen = []
    async def fail(*args):
        """仅注入计数快照失败。"""
        raise OSError('计数写盘失败')
    async def dispatch(request):
        """到达传输层才记录出站请求。"""
        seen.append(request)
        return httpx.Response(200)
    async with httpx.AsyncClient(transport=httpx.MockTransport(dispatch),
            event_hooks={'request': [counter.fixed_hook('embedding')]}) as client:
        monkeypatch.setattr(store, 'update', fail)
        with pytest.raises(OSError):
            await client.post('https://example.test/embeddings')
        assert seen == []
        monkeypatch.setattr(store, 'update', real_update)
        await client.post('https://example.test/embeddings')
    assert len(seen) == 1
    assert (await store.get(run_id))['request_counts']['embedding'] == 1


async def test_cleanup_collects_failures_and_closes_once(tmp_path, monkeypatch):
    """行删除与集合删除都失败时仍关闭全部资源，并保存两项独立错误。"""
    module = api()
    owner, store, database = await local_owner(module, tmp_path, monkeypatch)
    await owner.prepare(dataset())
    async def fail_rows(*args):
        """只注入行删除失败。"""
        raise ValueError('无法删除行')
    async def fail_collection():
        """只注入集合删除失败。"""
        raise TimeoutError('无法删除集合')
    monkeypatch.setattr(owner, '_delete_rows', fail_rows)
    monkeypatch.setattr(owner, '_delete_collection', fail_collection)
    result = await owner.cleanup()
    assert not result.ok and len(result.errors) == 2
    assert database.closed == 1 and owner.index.closed == 1
    assert all(client.is_closed for client in owner._http_clients)
    assert (await store.get(owner.run_id))['cleanup']['errors'] == list(result.errors)
    assert await owner.cleanup() == result and database.closed == 1


async def test_recovery_rejects_forged_ownership(tmp_path, monkeypatch):
    """来自另一份输入的归属列表不能替代已持久快照。"""
    module = api()
    owner, store, database = await local_owner(module, tmp_path, monkeypatch)
    await owner.prepare(dataset())
    manifest = await store.get(owner.run_id)
    manifest['ownership']['collection'] = 'knowledge_test_' + 'e' * 32
    assert (await owner.recover(manifest)).unverified
    assert len(await all_rows(database)) == 2
    assert (await owner.cleanup()).ok


async def test_real_rpc_interceptor_counts_every_wire_call_and_reset(tmp_path):
    """本机 gRPC 服务实收请求数对应计数；新建通道仍计数而非只包装逻辑方法。"""
    import grpc
    module = api()
    store = RunStore(tmp_path)
    run_id = await store.create(config(), [('E1', 'dense')])
    counter = module.RequestCounter(store, run_id, (await store.get(run_id))['request_counts'])
    received = []
    async def echo(request, context):
        """真实本机传输收到任意二进制请求，回显且记录。"""
        received.append(request)
        return request
    server = grpc.aio.server()
    server.add_generic_rpc_handlers((grpc.method_handlers_generic_handler('test.Count', {
        'Echo': grpc.unary_unary_rpc_method_handler(echo)}),))
    port = server.add_insecure_port('127.0.0.1:0')
    await server.start()
    handler = module._CountedHandler(counter=counter, uri=f'http://127.0.0.1:{port}')
    try:
        for channel in (handler._async_channel, handler._create_channel(f'127.0.0.1:{port}')):
            try:
                call = channel.unary_unary('/test.Count/Echo')
                assert await call(b'schema') == b'schema'
                assert await call(b'upsert') == b'upsert'
                assert await call(b'replay') == b'replay'
            finally:
                if channel is not handler._async_channel:
                    await channel.close()
        assert len(received) == 6
        assert (await store.get(run_id))['request_counts']['milvus'] == 6
    finally:
        await handler.close()
        await server.stop(None)


async def database_snapshot(database):
    """只读完整知识与裁判台账，保留稳定序列以证明未误删旁置数据。"""
    async with database.session() as session:
        knowledge = [tuple(row) for row in (await session.execute(
            select(KnowledgeChunk.__table__).order_by(KnowledgeChunk.id))).all()]
        faith = [tuple(row) for row in (await session.execute(
            select(FaithCase.__table__).order_by(FaithCase.id))).all()]
    return knowledge, faith


async def test_real_prepare_cleanup_preserves_sentinels(mysql_database, milvus_collection, tmp_path, monkeypatch):
    """真实八表与 native BM25 完整准备后只回收本轮 50 块，保留业务 84 块及旁置证据。"""
    module = api()
    from app.rag_evaluation.dataset import load_dataset
    from app.retrieval.milvus import HybridMilvusIndex
    current_settings = load_settings()
    frozen = load_dataset('merchant-rag-300-v1', root=Path('evals/datasets'))
    store = RunStore(tmp_path)
    frozen_config = config() | {'fingerprint': frozen.fingerprint}
    run_id = await store.create(frozen_config, [('E1', 'dense')])
    owner = module.OwnedResources(current_settings, store, run_id)
    monkeypatch.setattr(module, 'SiliconFlowEmbedder', DeterministicEmbedder)
    rpc_methods = []
    original_intercept = module._RPCInterceptor.intercept_unary_unary
    async def observe(self, continuation, details, request):
        """记录真实 interceptor 边界的方法名，继续原有计数及真实网络请求。"""
        rpc_methods.append(details.method.decode().rsplit('/', 1)[-1])
        return await original_intercept(self, continuation, details, request)
    monkeypatch.setattr(module._RPCInterceptor, 'intercept_unary_unary', observe)
    sentinel = await KnowledgeRepository(mysql_database).add_chunks([ChunkDraft('旁置_' + run_id, '保留', '不得清除')])
    faith_id = 'R' + uuid4().hex[:15]
    async with mysql_database.session() as session, session.begin():
        session.add(FaithCase(eval_id=faith_id, bucket='A_policy', query='哨兵题', answer='哨兵答', reason='旁置证据'))
    sentinel_index = HybridMilvusIndex(milvus_collection.uri, collection=milvus_collection.name)
    business = Database(current_settings.database_url.set(host='127.0.0.1', port=3307,
                        database='customer_service', username='customer_service'))
    try:
        await sentinel_index.ensure_collection()
        before = await database_snapshot(mysql_database)
        business_before = await database_snapshot(business)
        assert len(business_before[0]) == 84
        collections_before = set(await milvus_collection.client.list_collections(timeout=5))
        with closing(RunLock(tmp_path).acquire()):
            mapping = await owner.prepare(frozen)
            assert len(mapping) == 50
            assert len(await owner.repository.get_done(list(mapping.values()) + sentinel)) == 50
            counts_before = (await store.get(run_id))['request_counts']
            assert counts_before['milvus'] == len(rpc_methods) > 10
            assert {'Connect', 'DescribeCollection', 'Upsert', 'Query'} <= set(rpc_methods)
            assert all(counts_before[key] == 0 for key in ('answer', 'rewrite', 'self_check', 'judge', 'embedding', 'rerank'))
            hits = await owner.index.recall(None, '退货', strategy='bm25')
            assert hits and all(hit.id in mapping.values() for hit in hits)
            result = await owner.cleanup()
            assert result.ok, result
            assert (await store.get(run_id))['request_counts']['milvus'] > counts_before['milvus']
            assert (await store.get(run_id))['request_counts']['milvus'] == len(rpc_methods)
        assert await database_snapshot(mysql_database) == before
        assert await database_snapshot(business) == business_before
        assert set(await milvus_collection.client.list_collections(timeout=5)) == collections_before
        (tmp_path / 'service-proof.json').write_text(json.dumps(dict(
            owned_chunks=len(mapping), business_chunks=len(business_before[0]),
            pending_sentinel_preserved=True, faith_sentinel_preserved=True,
            other_collections_preserved=True, cleanup_ok=result.ok,
            request_counts=(await store.get(run_id))['request_counts'],
            rpc_methods=rpc_methods), ensure_ascii=False, indent=2), encoding='utf-8')
    finally:
        await owner.cleanup()
        await business.dispose()
        await sentinel_index.aclose()
        async with mysql_database.session() as session, session.begin():
            await session.execute(delete(KnowledgeChunk).where(KnowledgeChunk.id.in_(sentinel)))
            await session.execute(delete(FaithCase).where(FaithCase.eval_id == faith_id))


CHILD_SCRIPT = r'''
import asyncio, json, os, sys
from contextlib import closing
from pathlib import Path
from app.config import load_settings
from app.rag_evaluation import resources
from app.rag_evaluation.store import RunStore
from app.rag_evaluation.locking import RunLock
from tests.test_rag_resources import dataset, DeterministicEmbedder

async def main():
    """只在父进程指定提交窗口暂停，不在生产代码添加故障入口。"""
    root, run_id, phase, ready = Path(sys.argv[1]), sys.argv[2], sys.argv[3], Path(sys.argv[4])
    store = RunStore(root)
    resources.SiliconFlowEmbedder = DeterministicEmbedder
    owner = resources.OwnedResources(load_settings(), store, run_id)
    original = store.update
    async def pause():
        """登记真实 PID 后等待父进程只终止这个专属进程。"""
        ready.write_text(json.dumps({'pid':os.getpid()}), encoding='utf-8')
        await asyncio.Event().wait()
    async def update(run_id, patch):
        """在归属发布前后或提交后清空前精确暂停。"""
        own = patch.get('ownership', {})
        if own.get('pending_ids') and phase == 'before_register':
            await pause()
        if own.get('owned_ids') and not own.get('pending_ids') and phase == 'committed':
            await pause()
        await original(run_id, patch)
        if own.get('pending_ids') and phase == 'registered':
            await pause()
    store.update = update
    with closing(RunLock(root).acquire()):
        await owner.prepare(dataset())
        if phase == 'vectorized':
            await pause()
        raise AssertionError('未命中预定中断窗口')

asyncio.run(main())
'''


@pytest.mark.parametrize('phase', ['before_register', 'registered', 'committed', 'vectorized'])
async def test_real_mysql_child_death_recovers_each_commit_window(mysql_database, milvus_collection, tmp_path, phase):
    """真实子进程死亡后仅靠持久归属恢复，回滚主键缺行可安全视为无残留。"""
    module = api()
    store = RunStore(tmp_path)
    run_id = await store.create(config(), [('E1', 'dense')])
    before = await database_snapshot(mysql_database)
    collections_before = set(await milvus_collection.client.list_collections(timeout=5))
    ready = tmp_path / 'ready.json'
    environment = os.environ.copy()
    environment['PYTHONPATH'] = os.pathsep.join([str(Path.cwd()), sysconfig.get_path('purelib')])
    process = subprocess.Popen([getattr(sys, '_base_executable', sys.executable), '-c', CHILD_SCRIPT,
        str(tmp_path), run_id, phase, str(ready)], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env=environment, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    recovered = module.OwnedResources(load_settings(), store, run_id)
    try:
        deadline = time.monotonic() + 40
        while not ready.exists() and process.poll() is None and time.monotonic() < deadline:
            await asyncio.sleep(.05)
        assert ready.exists(), '子进程未到达提交检查点'
        assert json.loads(ready.read_text('utf-8'))['pid'] == process.pid
        process.kill()
        await asyncio.to_thread(process.communicate, timeout=10)
        manifest = await RunStore(tmp_path).get(run_id)
        if phase == 'before_register':
            assert manifest['ownership']['owned_ids'] == []
        else:
            assert len(manifest['ownership']['owned_ids']) == 2
        if phase in ('registered', 'committed'):
            assert len(manifest['ownership']['pending_ids']) == 2
        with closing(RunLock(tmp_path).acquire()):
            result = await recovered.recover(manifest)
        assert result.ok, result
        assert await database_snapshot(mysql_database) == before
        assert set(await milvus_collection.client.list_collections(timeout=5)) == collections_before
    finally:
        if process.poll() is None:
            process.kill()
        await asyncio.to_thread(process.communicate, timeout=10)
        await recovered.cleanup()


async def test_actual_sdk_schema_replay_and_reconnect_are_counted(tmp_path):
    """真实本机 gRPC 返回一次 schema 漂移，安装 SDK 的自动重放与重连握手全部计数。"""
    import grpc
    from pymilvus import DataType
    from pymilvus.grpc_gen import common_pb2, milvus_pb2, milvus_pb2_grpc, schema_pb2
    module = api()
    store = RunStore(tmp_path)
    run_id = await store.create(config(), [('E1', 'dense')])
    counter = module.RequestCounter(store, run_id, (await store.get(run_id))['request_counts'])
    received = []
    class Service(milvus_pb2_grpc.MilvusServiceServicer):
        """只替换外部服务响应，客户端请求生成、schema 缓存与重放仍用真实 SDK。"""
        async def Connect(self, request, context):
            """返回合法握手标识。"""
            received.append('Connect')
            return milvus_pb2.ConnectResponse(identifier=123)

        async def DescribeCollection(self, request, context):
            """提供真实 protobuf 最小两字段 schema，允许 SDK 构造 upsert 请求。"""
            received.append('DescribeCollection')
            return milvus_pb2.DescribeCollectionResponse(collectionID=1,
                schema=schema_pb2.CollectionSchema(name=request.collection_name, fields=[
                    schema_pb2.FieldSchema(fieldID=100, name='id', is_primary_key=True, data_type=DataType.INT64),
                    schema_pb2.FieldSchema(fieldID=101, name='embedding', data_type=DataType.FLOAT_VECTOR,
                        type_params=[common_pb2.KeyValuePair(key='dim', value='2')])]))

        async def Upsert(self, request, context):
            """首次返回服务端 SchemaMismatch，第二次确认原主键而非伪造客户端调用。"""
            received.append('Upsert')
            if received.count('Upsert') == 1:
                return milvus_pb2.MutationResult(status=common_pb2.Status(error_code=common_pb2.SchemaMismatch,
                                                reason='test schema refresh'))
            return milvus_pb2.MutationResult(upsert_cnt=1,
                IDs=schema_pb2.IDs(int_id=schema_pb2.LongArray(data=[17])))
    server = grpc.aio.server()
    milvus_pb2_grpc.add_MilvusServiceServicer_to_server(Service(), server)
    port = server.add_insecure_port('127.0.0.1:0')
    await server.start()
    client = module._CountedMilvusClient(f'http://127.0.0.1:{port}', counter)
    try:
        async with asyncio.timeout(5):
            response = await client.upsert('knowledge_test_' + run_id,
                [{'id': 17, 'embedding': [1.0, 0.0]}], retry_times=0, retry_on_rate_limit=False)
        assert response['ids'] == [17]
        assert received == ['Connect', 'DescribeCollection', 'Upsert', 'DescribeCollection', 'Upsert']
        assert (await store.get(run_id))['request_counts']['milvus'] == 5
        await client._handler.reconnect(timeout=5)
        await client.has_collection('knowledge_test_' + run_id, retry_times=0, retry_on_rate_limit=False)
        assert received[-2:] == ['Connect', 'DescribeCollection']
        assert (await store.get(run_id))['request_counts']['milvus'] == len(received) == 7
    finally:
        await client.close()
        await server.stop(None)


async def test_factory_models_send_fixed_stage_budgets(tmp_path, monkeypatch):
    """真实模型序列化发送回答512与其余2048预算，工厂零重试且阶段分别持久计数。"""
    module = api()
    owner, store, database = await local_owner(module, tmp_path, monkeypatch)
    requests = []
    async def respond(request):
        """模拟收费边界的 HTTP 响应，保留工厂、SDK 和钩子真实行为。"""
        requests.append(json.loads(request.content))
        return httpx.Response(200, json=dict(id='chatcmpl-test', model='local-test', object='chat.completion',
            created=0, choices=[dict(index=0, message=dict(role='assistant', content='完成'), finish_reason='stop')]))
    def local_http(hook):
        """为拥有者注册确定性传输，测试不允许模型请求离开进程。"""
        client = httpx.AsyncClient(transport=httpx.MockTransport(respond), event_hooks={'request': [hook]})
        owner._http_clients.append(client)
        owner._closers.append(('http', client.aclose))
        return client
    monkeypatch.setattr(owner, '_http', local_http)
    try:
        await owner.prepare(dataset())
        for stage, model in [('answer', owner.model), ('judge', owner.judge_model),
            ('rewrite', module.model_with_output_budget(owner.model, settings(), 2048)),
            ('self_check', module.model_with_output_budget(owner.model, settings(), 2048))]:
            with owner.requests.stage(stage):
                await model.ainvoke('测试')
        assert [request['max_tokens'] for request in requests] == [512, 2048, 2048, 2048]
        assert owner.model is not owner.judge_model
        assert owner.model.max_retries == owner.judge_model.max_retries == 0
        counts = (await store.get(owner.run_id))['request_counts']
        assert [counts[stage] for stage in ('answer', 'judge', 'rewrite', 'self_check')] == [1, 1, 1, 1]
    finally:
        assert (await owner.cleanup()).ok


@pytest.mark.parametrize('operation', ['get', 'update'])
async def test_cleanup_snapshot_cancellation_still_closes_resources(tmp_path, monkeypatch, operation):
    """归属读取或结果落盘被取消，已经创建的客户端也必须各关闭一次。"""
    module = api()
    owner, store, database = await local_owner(module, tmp_path, monkeypatch)
    await owner.prepare(dataset())
    async def cancelled(*args):
        """模拟持久化等待期间的取消，避免依赖时序睡眠。"""
        raise asyncio.CancelledError()
    monkeypatch.setattr(store, operation, cancelled)
    result = await owner.cleanup()
    assert not result.ok
    assert database.closed == 1 and owner.index.closed == 1
    assert all(client.is_closed for client in owner._http_clients)
    assert (await owner.cleanup()) == result and database.closed == 1
