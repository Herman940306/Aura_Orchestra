import os, time
import asyncpg
import asyncio
from datetime import datetime, timedelta

DATABASE_URL = os.getenv("DATABASE_URL")
WINDOW_DAYS = int(os.getenv("HR_WINDOW_DAYS", "30"))
PROMOTE_THRESHOLD = float(os.getenv("PROMOTE_THRESHOLD", "0.85"))
DEMOTE_THRESHOLD = float(os.getenv("DEMOTE_THRESHOLD", "0.50"))


async def evaluate(pool):
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT m.id as model_id, AVG(mr.score) as avg_score, COUNT(*) as count
            FROM model_runs mr
            JOIN models m ON m.id = mr.model_id
            WHERE mr.created_at >= now() - interval '$1 days'
            GROUP BY m.id
        """,
            float(WINDOW_DAYS),
        )
        for r in rows:
            mid = r["model_id"]
            avg = float(r["avg_score"] or 0.0)
            cnt = r["count"]
            if cnt < 3:
                continue
            if avg >= PROMOTE_THRESHOLD:
                # create promotion record
                await conn.execute(
                    "INSERT INTO promotions (model_id, action, reason) VALUES ($1,$2,$3)",
                    mid,
                    "promote",
                    f"avg_score {avg}",
                )
                # optional: update models table or weighting in manager mapping
                await conn.execute(
                    "UPDATE models SET is_active = TRUE WHERE id = $1", mid
                )
            elif avg < DEMOTE_THRESHOLD:
                await conn.execute(
                    "INSERT INTO promotions (model_id, action, reason) VALUES ($1,$2,$3)",
                    mid,
                    "demote",
                    f"avg_score {avg}",
                )
                await conn.execute(
                    "UPDATE models SET is_active = FALSE WHERE id = $1", mid
                )


async def main():
    if not DATABASE_URL:
        print("DATABASE_URL not set, HR worker exiting.")
        return

    pool = await asyncpg.create_pool(DATABASE_URL)
    print("HR Worker started")
    while True:
        try:
            await evaluate(pool)
        except Exception as e:
            print("HR eval error:", e)
        await asyncio.sleep(60 * 60)  # run hourly


if __name__ == "__main__":
    asyncio.run(main())
