import subprocess
from pathlib import Path

BASE = Path("/sandbox")


def create_workspace(job_id: str):
    ws = BASE / "workspaces" / job_id
    ws.mkdir(parents=True, exist_ok=True)
    return ws


def snapshot(job_id: str):
    snap_dir = BASE / "snapshots"
    snap_dir.mkdir(parents=True, exist_ok=True)
    snap = snap_dir / f"{job_id}.tar"
    # tar the workspace
    # -C moves to workspaces dir, so we just tar the folder name 'job_id'
    subprocess.run(
        ["tar", "-cf", str(snap), "-C", str(BASE / "workspaces"), job_id], check=True
    )
    return str(snap)
