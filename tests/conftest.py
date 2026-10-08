import pytest
import pytest_asyncio
import os
from uuid import uuid4
from types import SimpleNamespace

# PyMilvus 3.0.2 imports load_dotenv() and otherwise injects real credentials into
# every offline test during collection. Pydantic still reads explicit env files.
os.environ['PYTHON_DOTENV_DISABLED'] = '1'


# 注册显式启用 MySQL 与 Milvus 集成测试的命令行开关。
def pytest_addoption(parser):
    parser.addoption("--run-mysql", action="store_true", default=False, help="运行独立 MySQL 测试库集成测试")
    parser.addoption('--run-milvus', action='store_true', default=False, help='运行本机 Milvus knowledge_test_* 集成测试')


# 为显式启用的测试分配随机 Milvus 集合名，检查服务并在结束后清理集合和客户端。
@pytest_asyncio.fixture
async def milvus_collection(request):
    if not request.config.getoption('--run-milvus'):
        pytest.skip('需要显式传入 --run-milvus')
    from pymilvus import AsyncMilvusClient
    client = AsyncMilvusClient(uri='http://127.0.0.1:19530', timeout=5)
    name = 'knowledge_test_' + uuid4().hex
    connected = False
    try:
        unavailable = None
        try:
            await client.list_collections(timeout=5)
            connected = True
        except Exception as exc:
            unavailable = type(exc).__name__
        if unavailable:
            pytest.fail(f'Milvus 测试服务未就绪（{unavailable}），请启动 ecs-knowledge Compose', pytrace=False)
        yield SimpleNamespace(client=client, name=name, uri='http://127.0.0.1:19530')
    finally:
        try:
            if connected and await client.has_collection(name, timeout=5):
                await client.drop_collection(name, timeout=5)
        finally:
            await client.close()


# 仅连接固定的独立测试库，验证数据库身份后提供连接并负责释放。
@pytest_asyncio.fixture
async def mysql_database(request):
    if not request.config.getoption("--run-mysql"):
        pytest.skip("需要显式传入 --run-mysql")

    from sqlalchemy import text
    from app.config import load_settings
    from app.db.session import Database

    # 固定独立测试库与端口，禁止消费生产库配置或执行建表/清表。
    settings = load_settings()
    url = settings.database_url.set(host="127.0.0.1", port=3308, database="customer_service_test", username="customer_service")
    database = Database(url)
    try:
        unavailable = None
        try:
            async with database.session() as session:
                assert await session.scalar(text("SELECT DATABASE()")) == "customer_service_test"
        except Exception as exc:
            unavailable = type(exc).__name__
        if unavailable:
            pytest.fail(f"MySQL 测试库未就绪（{unavailable}），请启动 Compose test profile", pytrace=False)
        yield database
    finally:
        await database.dispose()


# 用随机标记隔离知识测试数据，检查表结构并在测试结束后仅清理本次插入的行。
@pytest_asyncio.fixture
async def knowledge_rows(mysql_database):
    """Only clean rows identified by this fixture's unguessable marker."""
    from sqlalchemy import text
    token = "test_knowledge_" + uuid4().hex
    async with mysql_database.session() as session:
        tables = set((await session.scalars(text("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE()"))).all())
        if not {"knowledge_chunks", "qa_extraction_staging"} <= tables:
            pytest.fail("Knowledge schema prerequisite missing: explicitly migrate customer_service_test before repository tests", pytrace=False)
    yield SimpleNamespace(database=mysql_database, token=token)
    async with mysql_database.session() as session, session.begin():
        await session.execute(text("DELETE FROM knowledge_chunks WHERE category=:token OR LEFT(questions,:length)=:token"), {"token": token, "length": len(token)})
        await session.execute(text("DELETE FROM qa_extraction_staging WHERE batch_no=:token"), {"token": token})


# 创建迁移测试专用的随机数据库，并在测试结束后删除该库和释放连接。
@pytest_asyncio.fixture
async def migration_database(mysql_database):
    """Own a fresh schema; never drop the configured or shared database."""
    from sqlalchemy import text
    from app.config import load_settings
    from app.db.session import Database
    settings = load_settings()
    name = "ch03_migration_" + uuid4().hex
    root = Database(settings.database_url.set(host="127.0.0.1", port=3308, database="mysql", username="root", password=settings.mysql_root_password.get_secret_value()))
    database = Database(root.engine.url.set(database=name))
    try:
        async with root.engine.begin() as connection:
            await connection.execute(text(f"CREATE DATABASE `{name}` CHARACTER SET utf8mb4"))
        yield database
    finally:
        await database.dispose()
        async with root.engine.begin() as connection:
            await connection.execute(text(f"DROP DATABASE `{name}`"))
        await root.dispose()
