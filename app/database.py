"""
数据库连接模块
统一管理 SQLite / PostgreSQL 异步连接配置和会话
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings, is_sqlite_url, normalize_database_url

database_url = normalize_database_url(settings.database_url)

engine_kwargs = {
    "echo": settings.database_echo,
    "future": True,
    "pool_pre_ping": True,
}

if is_sqlite_url(database_url):
    engine_kwargs["connect_args"] = {"timeout": 60}
else:
    engine_kwargs.update({
        "pool_size": 20,
        "max_overflow": 40,
        "pool_recycle": 1800,
    })

# 创建异步引擎
engine = create_async_engine(
    database_url,
    **engine_kwargs
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# 创建 Base 类
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    获取数据库会话
    用于 FastAPI 依赖注入
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    初始化数据库
    创建所有表
    """
    async with engine.begin() as conn:
        if is_sqlite_url(database_url):
            await conn.execute(text("PRAGMA journal_mode=WAL"))
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    关闭数据库连接
    """
    await engine.dispose()
