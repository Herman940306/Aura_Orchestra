import asyncio
import logging
from .db import init_db_pool

LOGGER = logging.getLogger("aura.manager.leader")

# Choose a fixed bigint lock id for the application
ADVISORY_LOCK_ID = 987654321012345678


class LeaderElector:
    def __init__(self, poll_interval: float = 5.0):
        self._pool = None
        self.is_leader = False
        self._poll_interval = poll_interval
        self._task = None

    async def start(self):
        self._pool = await init_db_pool()
        self._task = asyncio.create_task(self._loop())

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _try_acquire(self, conn):
        # returns True if lock acquired
        return await conn.fetchval("SELECT pg_try_advisory_lock($1)", ADVISORY_LOCK_ID)

    async def _loop(self):
        while True:
            try:
                async with self._pool.acquire() as conn:
                    got = await self._try_acquire(conn)
                    if got and not self.is_leader:
                        LOGGER.info("Acquired leader lock")
                        self.is_leader = True
                    elif not got and self.is_leader:
                        LOGGER.warning("Lost leader lock")
                        self.is_leader = False
                await asyncio.sleep(self._poll_interval)
            except Exception as e:
                LOGGER.exception("Leader election loop error: %s", e)
                # on DB failure, we are not leader
                self.is_leader = False
                await asyncio.sleep(5)
