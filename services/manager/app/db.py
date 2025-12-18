import os
import asyncio
import asyncpg
from typing import Optional

DATABASE_URL = os.getenv("DATABASE_URL", "postgres://aura_admin:change_me_securely@postgres:5432/aura_orchestra")

_pool: Optional[asyncpg.pool.Pool] = None

async def init_db_pool():
    global _pool
    if _pool:
        return _pool
    _pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=8)
    return _pool

async def close_db_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None

# simple helper to run single SQL
async def fetchrow(query: str, *args):
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, *args)

async def fetch(query: str, *args):
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(query, *args)

async def execute(query: str, *args):
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        return await conn.execute(query, *args)
