import os
import yaml
import asyncpg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Aura Router")

DATABASE_URL = os.getenv("DATABASE_URL")
MANAGER_URL = os.getenv("MANAGER_URL", "http://manager:8000")

# Load capabilities
with open("/app/capabilities.yaml") as f:
    CAPABILITIES = yaml.safe_load(f)


class RouteRequest(BaseModel):
    requirements: List[str] = []
    priority: str = "normal"
    exclude_models: List[str] = []


class RouteResponse(BaseModel):
    model: str
    reason: str
    capabilities: List[str]
    cost_tier: str


@app.get("/health")
def health():
    return {"status": "ok"}

    return CAPABILITIES
