import os
import json
import asyncio
import logging
import requests
from .leader import LeaderElector

LOGGER = logging.getLogger("aura.manager.scheduler")
ROUTER_URL = os.getenv("ROUTER_URL", "http://router:8000")


class Scheduler:
    def __init__(self, leader: LeaderElector):
        self.leader = leader
        self.running = False
        self.task = None

    async def start(self):
        self.running = True
        self.task = asyncio.create_task(self._run())

    async def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()

    async def _run(self):
        from .db import init_db_pool

        while self.running:
            try:
                if not self.leader.is_leader:
                    await asyncio.sleep(2)
                    continue

                pool = await init_db_pool()
                async with pool.acquire() as conn:
                    # Find QUEUED jobs
                    jobs = await conn.fetch(
                        "SELECT id, role FROM jobs WHERE status = 'QUEUED' ORDER BY created_at LIMIT 10"
                    )

                    for job in jobs:
                        job_id = job["id"]
                        role = job["role"]

                        # Try Router first
                        model_name = await self._route_via_router(job_id, role)

                        # Fallback to role-based
                        if not model_name:
                            model_name = self._select_model_for_role(role)

                        # Assign
                        await conn.execute(
                            "UPDATE jobs SET assigned_model = $1, status = 'ASSIGNED' WHERE id = $2",
                            model_name,
                            job_id,
                        )

                        # Log event
                        await conn.execute(
                            "INSERT INTO job_events (job_id, event_type, details) VALUES ($1, 'assigned', $2::jsonb)",
                            job_id,
                            json.dumps(
                                {
                                    "assigned_model": model_name,
                                    "method": "router" if model_name else "fallback",
                                }
                            ),
                        )

                        LOGGER.info(f"Assigned job {job_id} to {model_name}")

            except Exception as e:
                LOGGER.error(f"Scheduler error: {e}")

            await asyncio.sleep(2)

    async def _route_via_router(self, job_id, role):
        """Call Router service for intelligent model selection"""
        try:
            # Map role to requirements
            requirements_map = {
                "Employee": ["code", "fast"],
                "Architect": ["deep_reason", "code"],
                "Reviewer": ["analysis", "code"],
            }

            requirements = requirements_map.get(role, ["code"])

            response = requests.post(
                f"{ROUTER_URL}/route",
                json={"requirements": requirements, "priority": "normal"},
                timeout=2,
            )

            if response.status_code == 200:
                data = response.json()
                LOGGER.info(
                    f"Router selected {data['model']} for job {job_id}: {data['reason']}"
                )
                return data["model"]
        except Exception as e:
            LOGGER.warning(f"Router unavailable, using fallback: {e}")

        return None

    def _select_model_for_role(self, role: str) -> str:
        """Fallback role-based selection"""
        mapping = {
            "Employee": "employee_ollama",
            "Architect": "employee_openai",
            "Reviewer": "employee_gemini",
        }
        return mapping.get(role, "employee_ollama")
