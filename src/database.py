from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.DB_config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME, REDIS_HOST, REDIS_PORT
from sqlalchemy.orm import DeclarativeBase
from aioredis import from_url


DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
redis = from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}/0")

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

class Base(DeclarativeBase):
    pass

