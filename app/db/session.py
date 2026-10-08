# 管理异步 MySQL 引擎与数据库会话，集中负责连接资源的释放。
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class Database:
    """拥有连接池；调用方用 async with 和短事务管理独立 Session。"""

    # 创建异步数据库引擎和独立 Session 工厂，提交后保留已加载字段。
    def __init__(self, url: URL):
        self.engine = create_async_engine(url, pool_pre_ping=True, connect_args={"connect_timeout": 5})
        # 每次仓储操作创建自己的 Session，避免请求间共享事务状态。
        self._sessions = async_sessionmaker(self.engine, expire_on_commit=False)

    # 创建独立数据库会话，由调用方负责上下文退出和事务边界。
    def session(self) -> AsyncSession:
        return self._sessions()

    # 关闭引擎连接池，释放应用持有的数据库资源。
    async def dispose(self) -> None:
        await self.engine.dispose()
