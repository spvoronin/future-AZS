import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

db_pool: asyncpg.Pool | None = None


async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(
        host=os.getenv("HOST"),
        user=os.getenv("NAME_USER"),
        password=os.getenv("PASSWORD"),
        database=os.getenv("DATABASE"),
        min_size=2,
        max_size=10,
    )


async def close_db():
    global db_pool
    if db_pool:
        await db_pool.close()


async def get_db_pool():
    if db_pool is None:
        raise RuntimeError("База данных не инициализирована!")
    return db_pool