import os, time, requests, asyncpg, asyncio, json
from services.validator.scoring import score_from_signals

MANAGER_URL = os.getenv("MANAGER_URL", "http://manager:8000")
DATABASE_URL = os.getenv("DATABASE_URL")


async def validate_loop():
    pool = await asyncpg.create_pool(DATABASE_URL)
    print("Validator started")
    while True:
        try:
            # Poll for jobs that are COMPLETED (worker done) but not VALIDATED?
            # Or Manager moves them to 'SUBMITTED' (per main.py: "status": "COMPLETED" if result.success else "SUBMITTED")
            # Wait, main.py says: "UPDATE jobs SET status = ... 'COMPLETED' ... 'SUBMITTED'"
            # If success, it goes COMPLETED. Does Validator run on COMPLETED?
            # "Validator picks job up... and runs scoring... call Manager endpoint POST /jobs/{job_id}/validate"
            # We probably want a new status 'VALIDATED' or just add a score to model_runs.
            # Let's say we look for 'COMPLETED' jobs that don't have a model_runs entry yet?
            # Or use a separate status 'NEEDS_REVIEW'?
            # For MVP, let's poll 'COMPLETED' jobs and check if we already scored them.

            async with pool.acquire() as conn:
                # Find recent completed jobs
                rows = await conn.fetch(
                    """
                    SELECT j.id, j.assigned_model, j.project_id 
                    FROM jobs j
                    WHERE j.status = 'COMPLETED'
                    AND NOT EXISTS (SELECT 1 FROM model_runs mr WHERE mr.job_id = j.id)
                    LIMIT 10
                """
                )

                for r in rows:
                    job_id = r["id"]
                    model_name = r["assigned_model"]
                    project_id = r["project_id"]  # might be null per schema

                    print(f"Validating job {job_id}")

                    # Fetch artifacts/events to compute signals
                    # This implies reading from DB or Manager.
                    # For MVP, we'll mock signals or check if artifact exists.

                    # Check for result artifact
                    has_artifact = await conn.fetchval(
                        """
                        SELECT EXISTS(SELECT 1 FROM model_artifacts WHERE job_id = $1 AND artifact_type='result')
                    """,
                        job_id,
                    )

                    signals = {
                        "tests_passed": True,  # Mock
                        "test_score": 0.9 if has_artifact else 0.0,
                        "coverage": 0.8,
                        "docs_quality": 0.8,
                        "performance_ok": True,
                        "cross_model_agreement": 0.5,
                    }

                    score = score_from_signals(signals)

                    # Lookup model_id
                    mid = await conn.fetchval(
                        "SELECT id FROM models WHERE name = $1", model_name
                    )
                    if not mid:
                        # try to find it or log error
                        print(f"Model {model_name} not found in models table")
                        continue

                    # Insert execution run
                    await conn.execute(
                        """
                        INSERT INTO model_runs (model_id, job_id, project_id, success, confidence, score, details)
                        VALUES ($1, $2, $3, TRUE, 0.9, $4, $5::jsonb)
                    """,
                        mid,
                        job_id,
                        project_id,
                        score,
                        json.dumps(signals),
                    )

                    print(f"Scored job {job_id}: {score}")

        except Exception as e:
            print(f"Validator error: {e}")

        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(validate_loop())
