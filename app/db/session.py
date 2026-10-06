from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class Database:
    """拥有连接池；调用方用 async with 和短事务管理独立 Session。"""

    def __init__(self, url: URL):
        self.engine = create_async_engine(url, pool_pre_ping=True, connect_args={"connect_timeout": 5})
        self._sessions = async_sessionmaker(self.engine, expire_on_commit=False)

    def session(self) -> AsyncSession:
        return self._sessions()

    async def dispose(self) -> None:
        await self.engine.dispose()
