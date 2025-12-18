import os
import uuid
import logging
import asyncio
import json
import requests
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime, timezone
from .db import init_db_pool, execute, fetchrow, fetch
from .leader import LeaderElector
from .scheduler import Scheduler

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("aura.manager")

app = FastAPI(title="Aura_Orchestra Manager")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# models
class PRD(BaseModel):
    project_id: int
    title: str
    tasks: list


class JobResult(BaseModel):
    success: bool
    details: dict = {}


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgres://aura_admin:change_me_securely@postgres:5432/aura_orchestra",
)

leader = LeaderElector()
scheduler = Scheduler(leader)


@app.on_event("startup")
async def startup():
    # init DB pool and start leader election + scheduler
    await init_db_pool()
    await leader.start()
    await scheduler.start()
    LOGGER.info("Manager started")


@app.on_event("shutdown")
async def shutdown():
    await scheduler.stop()
    await leader.stop()
    LOGGER.info("Manager stopped")


# Health endpoints
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/ready")
async def ready():
    # ready when DB pool acquired
    try:
        pool = await init_db_pool()
        return {"ready": True}
    except Exception as e:
        raise HTTPException(status_code=503, detail="DB not ready")


# PRD intake endpoint: create root job + child jobs for each task
@app.post("/prds", status_code=201)
async def create_prd(prd: PRD):
    # create job(s) in jobs table
    # root job ID for traceability
    root_job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    # insert root as QUEUED for manager to break down, but for now create child jobs per task
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            # ensure project exists (simple)
            await conn.execute(
                "INSERT INTO projects (id, name, created_at) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
                str(uuid.uuid4()),
                f"project-{prd.project_id}",
                now,
            )
            # create jobs for each task
            for t in prd.tasks:
                job_id = str(uuid.uuid4())
                await conn.execute(
                    """
                    INSERT INTO jobs (id, project_id, role, assigned_model, status, created_at)
                    VALUES ($1, NULL, $2, NULL, 'QUEUED', $3)
                """,
                    job_id,
                    t.get("role", "Employee"),
                    now,
                )
                await conn.execute(
                    """
                    INSERT INTO job_events (job_id, event_type, details)
                    VALUES ($1, 'created', $2::jsonb)
                """,
                    job_id,
                    json.dumps({"title": prd.title, "task_payload": t}),
                )
    return {"root_job_id": root_job_id, "message": "PRD accepted and tasks queued"}


# List jobs
@app.get("/jobs")
async def list_jobs(status: str = None):
    if status:
        rows = await fetch(
            "SELECT id, project_id, role, assigned_model, status, created_at FROM jobs WHERE status = $1 ORDER BY created_at DESC",
            status,
        )
    else:
        rows = await fetch(
            "SELECT id, project_id, role, assigned_model, status, created_at FROM jobs ORDER BY created_at DESC LIMIT 200"
        )
    return [dict(r) for r in rows]


# Manager assignment endpoint (manual override)
@app.post("/jobs/{job_id}/assign")
async def assign_job(job_id: str, assigned_model: str):
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        res = await conn.execute(
            "UPDATE jobs SET assigned_model=$1, status='ASSIGNED' WHERE id=$2",
            assigned_model,
            job_id,
        )
        # record event
        await conn.execute(
            "INSERT INTO job_events (job_id, event_type, details) VALUES ($1, 'assigned_manual', $2::jsonb)",
            job_id,
            json.dumps({"assigned_model": assigned_model}),
        )
    return {"job_id": job_id, "assigned_model": assigned_model}


# Simple claim endpoint for workers (workers should use DB claim in later batches; this is an HTTP helper)
@app.post("/jobs/{job_id}/claim")
async def claim_job(job_id: str, worker_id: str):
    # set job to IN_PROGRESS and record heartbeat
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        r = await conn.fetchrow("SELECT status FROM jobs WHERE id=$1", job_id)
        if not r:
            raise HTTPException(status_code=404, detail="job not found")
        if r["status"] not in ("ASSIGNED", "QUEUED"):
            raise HTTPException(
                status_code=400, detail=f"cannot claim job in status {r['status']}"
            )
        await conn.execute(
            "UPDATE jobs SET status='IN_PROGRESS', assigned_model=$1 WHERE id=$2",
            worker_id,
            job_id,
        )
        await conn.execute(
            "INSERT INTO job_events (job_id, event_type, details) VALUES ($1, 'claimed', $2::jsonb)",
            job_id,
            json.dumps(
                {"worker": worker_id, "ts": datetime.now(timezone.utc).isoformat()}
            ),
        )
    return {"job_id": job_id, "worker": worker_id}


@app.post("/jobs/{job_id}/complete")
async def complete_job(job_id: str, result: JobResult):
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        # Call Accountant
        try:
            # Fetch assigned model first
            row = await conn.fetchrow(
                "SELECT assigned_model FROM jobs WHERE id = $1", job_id
            )
            if row and row["assigned_model"]:
                assigned_model = row["assigned_model"]

                # Assume task payload is in job_events (simplified for MVP, ideally passed or fetched)
                # For now, pass a dummy task if not easily accessible, or rely on job details
                # In a real system, we'd fetch the task from jobs or job_events

                acc_payload = {
                    "model_name": assigned_model,
                    "job_id": job_id,
                    "task": {"min_length": 20},  # Default constraints
                    "model_output": result.details,
                }

                acc_res = requests.post(
                    "http://accountant:8000/evaluate", json=acc_payload, timeout=2
                )
                if acc_res.status_code == 200:
                    eval_data = acc_res.json()
                    action = eval_data.get("action", "none")

                    if action == "warn_or_suspend":
                        # Fetch current warnings
                        model_row = await conn.fetchrow(
                            "SELECT warnings_count FROM models WHERE name = $1",
                            assigned_model,
                        )
                        warnings = model_row["warnings_count"] if model_row else 0
                        warnings += 1

                        if warnings >= 2:
                            # Suspend
                            await conn.execute(
                                "UPDATE models SET suspended = TRUE, suspension_reason = $1, warnings_count = $2 WHERE name = $3",
                                f"Suspended after {warnings} warnings. Last job: {job_id}",
                                warnings,
                                assigned_model,
                            )
                            LOGGER.warning(
                                f"MODEL SUSPENDED: {assigned_model} (Warnings: {warnings})"
                            )
                        else:
                            # Warn
                            await conn.execute(
                                "UPDATE models SET warnings_count = $1, last_warning_at = $2 WHERE name = $3",
                                warnings,
                                datetime.now(timezone.utc),
                                assigned_model,
                            )
                            LOGGER.warning(
                                f"MODEL WARNED: {assigned_model} (Warning {warnings}/2)"
                            )

        except Exception as e:
            LOGGER.error(f"Accountant evaluation failed: {e}")

        await conn.execute(
            "UPDATE jobs SET status = $1, completed_at = $2 WHERE id = $3",
            ("COMPLETED" if result.success else "SUBMITTED"),
            datetime.now(timezone.utc),
            job_id,
        )
        await conn.execute(
            "INSERT INTO job_events (job_id, event_type, details) VALUES ($1, 'completed', $2::jsonb)",
            job_id,
            json.dumps({"success": result.success, "details": result.details}),
        )
    return {"job_id": job_id, "status": "COMPLETED" if result.success else "SUBMITTED"}


# --- Batch 4 Endpoints ---


@app.post("/alerts")
async def take_alert(payload: dict):
    # persist alert and escalate to manager dashboard
    job_id = payload.get("job_id")
    severity = payload.get("severity")
    reason = payload.get("reason")
    pool = await init_db_pool()
    # verify pool usage
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO audit_log (actor, action, details) VALUES ($1,$2,$3)",
            "auditor",
            "alert",
            json.dumps({"job_id": job_id, "severity": severity, "reason": reason}),
        )
    LOGGER.warning(f"ALERT received: {severity} - {reason}")
    # optionally reassign or escalate: for MVP just log and manager UI shows it
    return {"ok": True}


@app.get("/models")
async def list_models():
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, name, kind, endpoint, is_active FROM models ORDER BY id"
        )
    return [dict(r) for r in rows]


@app.post("/models/{model_name}/register")
async def register_model(model_name: str, payload: dict):
    kind = payload.get("kind", "local")
    endpoint = payload.get("endpoint")
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO models (name, kind, endpoint, is_active)
            VALUES ($1, $2, $3, TRUE)
            ON CONFLICT (name) DO UPDATE SET endpoint = EXCLUDED.endpoint, is_active = TRUE
        """,
            model_name,
            kind,
            endpoint,
        )
    return {"status": "registered", "model": model_name}


@app.post("/models/{model_name}/artifact")
async def upload_artifact(model_name: str, payload: dict):
    # payload: {job_id, artifact_type, artifact}
    job_id = payload.get("job_id")
    atype = payload.get("artifact_type")
    artifact = payload.get("artifact")

    pool = await init_db_pool()
    async with pool.acquire() as conn:
        # lookup model id
        mid = await conn.fetchval("SELECT id FROM models WHERE name = $1", model_name)
        if not mid:
            # auto register? or fail. Spec says generic worker might need logic.
            # lets fail or auto-register logic could be here. For MVP fail.
            raise HTTPException(status_code=404, detail="Model unknown")

        await conn.execute(
            """
            INSERT INTO model_artifacts (job_id, model_id, artifact_type, artifact)
            VALUES ($1, $2, $3, $4::jsonb)
        """,
            job_id,
            mid,
            atype,
            json.dumps(artifact),
        )

    return {"status": "stored"}


# --- Batch 7: Real-time Alerts (SSE) ---

from fastapi.responses import StreamingResponse
from fastapi import Request
import asyncio


@app.post("/alerts")
async def take_alert(payload: dict):
    # persist alert and escalate to manager dashboard
    job_id = payload.get("job_id")
    severity = payload.get("severity")
    reason = payload.get("reason")
    message = payload.get("message")

    pool = await init_db_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO audit_log (actor, action, details) VALUES ($1,$2,$3)",
            "auditor",
            "alert",
            json.dumps(payload),
        )

    LOGGER.warning(f"ALERT RECV: [{severity}] {reason}: {message}")

    return {"ok": True}


@app.get("/events")
async def event_stream(request: Request):
    """
    Server-Sent Events (SSE) endpoint for real-time monitoring.
    For MVP, uses polling. In prod, use Listen/Notify or Redis PubSub.
    """

    async def event_generator():
        pool = await init_db_pool()
        last_id = 0

        # Get last ID to start fresh so we don't replay history immediately
        async with pool.acquire() as conn:
            last_id = await conn.fetchval("SELECT MAX(id) FROM audit_log") or 0

        # Keepalive for initial connection
        yield ": keepalive\n\n"

        while True:
            if await request.is_disconnected():
                break

            try:
                async with pool.acquire() as conn:
                    rows = await conn.fetch(
                        "SELECT id, actor, action, details, created_at FROM audit_log WHERE id > $1 ORDER BY id ASC",
                        last_id,
                    )
                    for r in rows:
                        last_id = r["id"]
                        data = {
                            "id": r["id"],
                            "actor": r["actor"],
                            "action": r["action"],
                            "details": (
                                json.loads(r["details"])
                                if isinstance(r["details"], str)
                                else r["details"]
                            ),
                            "ts": r["created_at"].isoformat(),
                        }
                        yield f"data: {json.dumps(data)}\n\n"

                await asyncio.sleep(2)  # Poll interval
            except Exception as e:
                LOGGER.error(f"SSE error: {e}")
                await asyncio.sleep(5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
