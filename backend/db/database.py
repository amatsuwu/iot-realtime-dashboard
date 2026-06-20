from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from backend.core.config import settings

engine = create_async_engine(
    settings.get_database_url,
    echo=True,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

# 改為 AsyncSessionLocal 以符合 dependencies.py 的呼叫
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

class Base(DeclarativeBase):
    pass