import os, json, subprocess, shutil, time

# Assuming PYTHONPATH includes the project root or services root
from services.employees.common.adapter import BaseAdapter

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")


class OllamaAdapter(BaseAdapter):
    def __init__(self, model_name="llama3"):
        self.model = model_name

    def generate(self, prompt: str, context: dict) -> dict:
        try:
            # Minimal example: call ollama via CLI or HTTP
            # For simplicity using curl/subprocess if CLI not installed,
            # or just requests if we had it. But spec uses subprocess example.

            # Using basic requests logic is usually safer than CLI inside container unless CLI installed.
            # But the spec code used subprocess. Let's try requests as it's cleaner if we add it to requirements.
            import requests

            payload = {"model": self.model, "prompt": prompt, "stream": False}

            # Adjust host for docker networking
            host = OLLAMA_HOST
            if "localhost" in host and os.path.exists("/.dockerenv"):
                # if passing localhost in env but running in docker, might need host.docker.internal or service name
                # But usually we set OLLAMA_HOST=http://host.docker.internal:11434 or http://ollama:11434
                pass

            resp = requests.post(f"{host}/api/generate", json=payload, timeout=120)
            if resp.status_code == 200:
                out = resp.json().get("response", "")
            else:
                out = f"Error: {resp.status_code} {resp.text}"

            response = {"output": out}
        except Exception as e:
            response = {"output": "", "error": str(e)}

        return {
            "output": response.get("output", ""),
            "patch": None,
            "explanation": "Ollama adapter output",
            "self_confidence": 0.8,
            "artifacts": {},
        }
