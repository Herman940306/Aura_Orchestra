import os

try:
    from services.employees.common.adapter import BaseAdapter
except ImportError:

    class BaseAdapter:
        pass


# Modern OpenAI SDK (v1.0+)
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


class OpenAIAdapter(BaseAdapter):
    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        self.client = None
        if OPENAI_API_KEY:
            self.client = OpenAI(api_key=OPENAI_API_KEY)

    def generate(self, prompt: str, context: dict) -> dict:
        if not self.client:
            return {
                "output": f"[STUB] OpenAI would respond to: {prompt[:100]}...",
                "tokens_used": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
                "confidence": 0.0,
                "raw": {},
                "error": "OPENAI_API_KEY not set",
            }

        try:
            model = context.get("model", self.model)

            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=context.get("max_tokens", 1200),
                temperature=context.get("temperature", 0.7),
            )

            content = response.choices[0].message.content
            usage = response.usage

            return {
                "output": content,
                "tokens_used": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens,
                },
                "confidence": 0.90,  # OpenAI doesn't provide confidence, using high default
                "raw": response.model_dump() if hasattr(response, "model_dump") else {},
            }
        except Exception as e:
            return {
                "output": f"OpenAI Error: {str(e)}",
                "tokens_used": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
                "confidence": 0.0,
                "raw": {},
                "error": str(e),
            }
