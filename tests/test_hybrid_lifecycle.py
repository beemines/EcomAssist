# 混合依赖启动仅核验并按所有权回收；失败不得执行产品 DDL。
import pytest

import app.main as main
from tests.fakes import ConversationStore, FAQStub, StreamingModel, fake_settings
from tests.test_hybrid_chat import QualityStore
from tests.fakes import AssessmentModel


# 缺线上阈值时启动必须失败，不能服务一个未校准的混合 FAQ。
async def test_startup_requires_finite_calibrated_threshold():
    app = main.create_app(fake_settings(rerank_min_score=None), model=StreamingModel(),
                          repository=ConversationStore(), faq_repository=FAQStub())
    with pytest.raises(ValueError, match='threshold'):
        async with app.router.lifespan_context(app):
            pass


# 注入质量依赖必须保持外部所有权，应用不重复建立或关闭模型客户端。
async def test_injected_quality_dependencies_remain_caller_owned():
    import inspect
    assert 'sufficiency_service' in inspect.signature(main.create_app).parameters, 'quality injection is missing'
    repository = ConversationStore()
    quality = QualityStore(repository)
    assessment = AssessmentModel()
    app = main.create_app(fake_settings(rerank_min_score=.5), model=StreamingModel(),
        repository=repository, faq_repository=FAQStub(), sufficiency_service=assessment, quality_repository=quality)
    async with app.router.lifespan_context(app):
        assert app.state.chat_service.sufficiency_service is assessment
        assert app.state.chat_service.quality_repository is quality


# 已有 Milvus 描述允许读；缺集合必须失败而不是创建集合。
async def test_missing_online_collection_never_creates_schema():
    from app.retrieval.milvus import HybridMilvusIndex
    class Client:
        # 返回缺集合；任何创建 RPC 都会令本测试失败。
        async def has_collection(self, *args, **kwargs):
            return False
    import inspect
    assert 'create_if_missing' in inspect.signature(HybridMilvusIndex.ensure_collection).parameters, 'read-only collection check is missing'
    index = HybridMilvusIndex('unused', client=Client())
    with pytest.raises(ValueError, match='missing'):
        await index.ensure_collection(create_if_missing=False)


# 只读质量核验遇到缺表时必须拒绝，任何 DDL API 都不存在。
async def test_missing_quality_tables_fail_read_only_verification():
    from contextlib import asynccontextmanager
    from types import SimpleNamespace
    from app.quality.migration import verify_quality
    class Connection:
        # 仅支持当前库身份及缺表 SELECT；没有任何 DDL 执行入口。
        async def scalar(self, statement):
            return 'customer_service_test'
        # 断言核验只读，返回零质量表。
        async def scalars(self, statement):
            assert str(statement).startswith('SELECT ')
            return SimpleNamespace(all=lambda: [])
    class Engine:
        url = SimpleNamespace(database='customer_service_test')
        # 提供只读连接，若启动尝试自动迁移就会缺少 begin/exec_driver_sql 失败。
        @asynccontextmanager
        async def connect(self):
            yield Connection()
    import app.quality.migration as migration
    assert hasattr(migration, 'verify_quality'), 'read-only quality verifier is missing'
    with pytest.raises(RuntimeError, match='explicit migration'):
        await verify_quality(SimpleNamespace(engine=Engine()))


# 在线只读模式仍校验 Schema/两索引并加载既有集合，不走创建分支。
async def test_existing_collection_is_verified_and_loaded_without_ddl():
    from app.retrieval.milvus import HybridMilvusIndex
    from tests.test_hybrid_milvus import SchemaClient
    client = SchemaClient(exists=True)
    await HybridMilvusIndex('unused', client=client).ensure_collection(create_if_missing=False)
    methods = [method for method, _, _ in client.calls]
    assert methods == ['has_collection', 'describe_collection', 'list_indexes', 'describe_index', 'describe_index', 'load_collection']


# 启动质量核验失败仍回收全部自建资源，不能留下嵌入/重排 HTTP 或数据库连接。
async def test_quality_startup_failure_closes_all_owned_resources(monkeypatch):
    from tests.test_knowledge_lifecycle import owned_resources
    created, closed = owned_resources(monkeypatch)
    main.Database.engine = object()
    # 只替代只读数据库结构故障，其他资源用真实工厂生命周期注册。
    async def fail_quality(database):
        raise RuntimeError('controlled quality schema failure')
    monkeypatch.setattr(main, 'verify_quality', fail_quality)
    app = main.create_app(fake_settings(mysql_password='fake-only'))
    with pytest.raises(RuntimeError, match='controlled quality'):
        async with app.router.lifespan_context(app):
            pass
    assert created == ['database', 'model', 'embedder', 'index', 'ready', 'reranker']
    assert closed == ['reranker', 'index', 'embedder', 'async_model', 'sync_model', 'database']
