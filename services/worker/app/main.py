import os, time, importlib, requests, json, sys

# from sandbox import create_workspace, snapshot # assuming logic moved or we copy it
# In Batch 3 we put sandbox.py in services/worker/app/sandbox.py
# If we are reusing the worker image or logic, we should be fine.
# But "employees" might check out their own code.
# For Batch 5, we are creating "employee_ollama" service which acts as a worker.
# Wait, the spec says "Update services/worker/app/main.py ... to load adapter".
# So meaningful change: The "worker" service becomes the generic runner for all employees?
# OR we have multiple containers (employee_ollama, employee_openai) all running this same code but with different env vars.
# YES. "Docker Compose additions... employee_ollama build: ./services/employee_ollama".
# Wait, if they build from employee_ollama, they don't have the generic worker code.
# The spec says: "Update services/worker/app/main.py (or create new employee_worker.py) to load adapter".
# And "Build adapters and workers: docker compose build employee_ollama ..."
# This implies employee_ollama container RUNS the generic worker logic + specific adapter.
# So I should create a shared base image or copy the worker logic into each employee.
# OR, simpler:
# Use one Dockerfile (the worker one) for all employees, but mount the specific adapter code?
# Or update `services/worker` to be the "base" and `employee_ollama` just inherits/installs adapter?

# Let's look at `services/employee_ollama` folder. It has `adapter.py`.
# Does it have a main.py? No.
# So how does it run?
# Spec says: "Update services/worker/app/main.py ... to load adapter by env var MODEL_BACKEND".
# And "services/employee_ollama/Dockerfile" isn't fully specified in Batch 4 text, but implied in point 7 "build: ./services/employee_ollama".

# Decision: I will modify `services/worker/app/main.py` to be the universal run loop.
# I will make `services/worker` the build context for a "base worker" or just Copy the worker app into the employee images.
# Actually, the cleanest way given the files I have:
# 1. Update `services/worker/app/main.py` to support pluggable adapters.
# 2. In `docker-compose.yml`, for `employee_ollama`:
#    Build from root or a specialized dockerfile that copies `services/worker/app` AND `services/employee_ollama`.
#    Command: `python app/main.py` (the worker main).

# Let's try to update `services/worker/app/main.py` first.
# AND I need `sandbox.py` and `reporter.py` accessible to it. They are already in `services/worker/app`.

from sandbox import create_workspace, snapshot
from reporter import report

MANAGER_URL = os.getenv("MANAGER_URL", "http://manager:8000")
MODEL_BACKEND = os.getenv("MODEL_BACKEND", "ollama")  # ollama | openai | gemini
WORKER_ID = os.getenv("WORKER_ID", "worker_default")

print(
    f"Worker {WORKER_ID} (Backend: {MODEL_BACKEND}) starting...",
    file=sys.stderr,
    flush=True,
)


def load_adapter(name):
    # This assumes the adapter code is in PYTHONPATH
    # verification: in docker-compose, we can mount ./services/employee_ollama:/app/services/employee_ollama
    # or install it.
    try:
        if name == "ollama":
            from services.employee_ollama.adapter import OllamaAdapter

            return OllamaAdapter()
        if name == "openai":
            from services.employee_openai.adapter import OpenAIAdapter

            return OpenAIAdapter()
        if name == "gemini":
            from services.employee_gemini.adapter import GeminiAdapter

            return GeminiAdapter()
    except ImportError as e:
        print(f"Failed to load adapter {name}: {e}", file=sys.stderr)
        # Fallback or strict fail?
        # For now, let's allow fail to debug
        raise e
    raise RuntimeError(f"Unknown model backend: {name}")


# We need to ensure the services package is importable.
# We'll rely on Docker setup to put 'services' in path.

adapter = None
try:
    adapter = load_adapter(MODEL_BACKEND)
except Exception as e:
    print(f"Adapter load error: {e}. Running in stub mode/limited.", file=sys.stderr)


def poll_job():
    try:
        # Filter logic: In batch 2/3 we assigned to specific IDs.
        # Now we might assign to roles or capabilities.
        # For MVP, Manager Manual Assign -> assigned_model = 'employee_ollama'
        # So we look for jobs assigned to US.
        url = f"{MANAGER_URL}/jobs?status=ASSIGNED"
        r = requests.get(url, timeout=5)
        jobs = r.json()

        # Filter for my ID
        my_jobs = [j for j in jobs if j.get("assigned_model") == WORKER_ID]

        if not my_jobs:
            return None
        return my_jobs[0]
    except Exception as e:
        print(f"Poll error: {e}", file=sys.stderr, flush=True)
        return None


while True:
    try:
        job = poll_job()
        if not job:
            time.sleep(2)
            continue

        job_id = job["id"]
        print(f"Claiming job {job_id}", file=sys.stderr, flush=True)

        # Claim
        claim_r = requests.post(
            f"{MANAGER_URL}/jobs/{job_id}/claim",
            params={"worker_id": WORKER_ID},
            timeout=5,
        )
        if claim_r.status_code != 200:
            print(f"Claim failed: {claim_r.text}", file=sys.stderr, flush=True)
            time.sleep(2)
            continue

        print(f"Claimed job {job_id}. Executing...", file=sys.stderr, flush=True)

        # Create Workspace
        ws = create_workspace(job_id)

        # GENERATE
        prompt = f"Implement task for job {job_id}. Context: {job}"
        # In real usage, we'd fetch PRD details using job['project_id'] etc.

        out = {"output": "Adapter not loaded"}
        if adapter:
            out = adapter.generate(prompt, context={"job": job})

        # Write Output
        (ws / "result.txt").write_text(out["output"])

        # Upload Artifact
        try:
            requests.post(
                f"{MANAGER_URL}/models/{MODEL_BACKEND}/artifact",
                json={
                    "job_id": job_id,
                    "artifact_type": "result",
                    "artifact": {
                        "output": out["output"],
                        "explanation": out.get("explanation"),
                    },
                },
                timeout=10,
            )
        except Exception as e:
            print(f"Artifact upload failed: {e}", file=sys.stderr)

        # Snapshot
        snap_path = snapshot(job_id)

        # Report
        report(
            job_id,
            True,
            {
                "snapshot": snap_path,
                "worker": WORKER_ID,
                "output_snippet": str(out.get("output"))[:100],
            },
        )
        print(f"Job {job_id} reporting complete", file=sys.stderr, flush=True)

    except Exception as outer_e:
        print(f"Worker loop error: {outer_e}", file=sys.stderr, flush=True)

    time.sleep(1)
