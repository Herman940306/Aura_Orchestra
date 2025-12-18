import os
import time
import requests
import asyncpg
import asyncio
import logging
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("auditor")

DATABASE_URL = os.getenv("DATABASE_URL")
MANAGER_URL = os.getenv("MANAGER_URL", "http://manager:8000")


async def scan_stalled_jobs(pool, conn):
    # Rule: In progress > 5 mins
    rows = await conn.fetch(
        """
        SELECT id, created_at FROM jobs 
        WHERE status = 'IN_PROGRESS' 
        AND created_at < NOW() - INTERVAL '5 minutes'
    """
    )
    for r in rows:
        job_id = str(r["id"])
        msg = f"Job {job_id} stalled since {r['created_at']}"
        await trigger_alert(conn, job_id, "high", "stalled_job", msg)


async def scan_cost_spikes(pool, conn):
    # Rule: Single job cost > $1.00
    rows = await conn.fetch(
        """
        SELECT job_id, estimated_cost FROM model_runs
        WHERE estimated_cost > 1.00
        AND created_at > NOW() - INTERVAL '1 hour'
        AND job_id NOT IN (
            SELECT (details->>'job_id')::uuid FROM audit_log 
            WHERE action='alert' AND details->>'reason'='cost_spike'
        )
    """
    )
    for r in rows:
        job_id = str(r["job_id"]) if r["job_id"] else None
        msg = f"High cost detected: ${r['estimated_cost']}"
        await trigger_alert(conn, job_id, "medium", "cost_spike", msg)


async def scan_high_failure_rate(pool, conn):
    # Rule: > 3 failures for a model in last hour
    rows = await conn.fetch(
        """
        SELECT assigned_model, COUNT(*) as failures
        FROM jobs
        WHERE status = 'FAILED'
        AND completed_at > NOW() - INTERVAL '1 hour'
        GROUP BY assigned_model
        HAVING COUNT(*) > 3
    """
    )
    for r in rows:
        model = r["assigned_model"]
        msg = f"Model {model} failed {r['failures']} jobs in last hour"
        # Alert without job_id (system level)
        await trigger_alert(conn, None, "high", "high_failure_rate", msg)


async def trigger_alert(conn, job_id, severity, reason, message):
    # Check if recently alerted to avoid spam
    # (Simple check: looked at audit_log in scan query or do dedup here)
    # For MVP, just send.

    payload = {
        "job_id": job_id,
        "severity": severity,
        "reason": reason,
        "message": message,
    }

    # 1. Log to DB
    await conn.execute(
        "INSERT INTO audit_log (actor, action, details) VALUES ($1,$2,$3)",
        "auditor",
        "alert",
        str(payload),
    )

    # 2. Notify Manager
    try:
        requests.post(f"{MANAGER_URL}/alerts", json=payload, timeout=2)
        logger.info(f"Alert sent: {reason} - {message}")
    except Exception as e:
        logger.error(f"Failed to send alert: {e}")


async def main():
    if not DATABASE_URL:
        logger.error("DATABASE_URL missing")
        return

    logger.info("Auditor Watchdog Service Started")

    while True:
        try:
            pool = await asyncpg.create_pool(DATABASE_URL)
            async with pool.acquire() as conn:
                await scan_stalled_jobs(pool, conn)
                await scan_cost_spikes(pool, conn)
                await scan_high_failure_rate(pool, conn)
            await pool.close()
        except Exception as e:
            logger.error(f"Watchdog scan error: {e}")

        await asyncio.sleep(30)  # Scan every 30s


if __name__ == "__main__":
    asyncio.run(main())
