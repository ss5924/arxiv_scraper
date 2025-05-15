from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DB_ENGINE_URL
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


# SQL 사용시
async def get_db_pool():
    return await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT
    )


# SQLAlchemy ORM 사용
engine = create_async_engine(
    url=DB_ENGINE_URL,
    pool_size=10,
    max_overflow=5,
    pool_timeout=30,
    echo=False
)
async_session = async_sessionmaker(engine, expire_on_commit=False)
