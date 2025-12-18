import requests
import os

MANAGER_URL = os.getenv("MANAGER_URL", "http://manager:8000")


def report(job_id, success, details):
    try:
        requests.post(
            f"{MANAGER_URL}/jobs/{job_id}/complete",
            json={"success": success, "details": details},
            timeout=15,
        )
    except Exception as e:
        print(f"Failed to report job {job_id}: {e}")
