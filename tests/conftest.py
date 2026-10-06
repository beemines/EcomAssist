import pytest
import pytest_asyncio


def pytest_addoption(parser):
    parser.addoption("--run-mysql", action="store_true", default=False, help="运行独立 MySQL 测试库集成测试")


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
