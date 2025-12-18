from fastapi import FastAPI
import requests
import os

MANAGER_URL = os.getenv("MANAGER_URL", "http://manager:8000")

app = FastAPI(title="Aura MCP Bridge")


@app.post("/mcp/command")
def mcp_command(payload: dict):
    """
    IDE -> MCP -> Manager
    Forwards instructions to Manager to create jobs.
    """
    # In a real scenario, this might validate keys or transform payload
    try:
        r = requests.post(f"{MANAGER_URL}/prds", json=payload, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


@app.get("/health")
def health():
    return {"status": "ok"}
