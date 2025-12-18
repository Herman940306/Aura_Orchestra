import os

try:
    from services.employees.common.adapter import BaseAdapter
except ImportError:

    class BaseAdapter:
        pass


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


class GeminiAdapter(BaseAdapter):
    def __init__(self, model_name="gemini-1.5-pro"):
        self.model = model_name
        self.genai = None

        if GEMINI_API_KEY:
            try:
                import google.generativeai as genai

                genai.configure(api_key=GEMINI_API_KEY)
                self.genai = genai
            except ImportError:
                pass  # SDK not installed

    def generate(self, prompt: str, context: dict) -> dict:
        if not self.genai or not GEMINI_API_KEY:
            return {
                "output": f"[STUB] Gemini would respond to: {prompt[:100]}...",
                "tokens_used": {"input_tokens": 0, "output_tokens": 0},
                "confidence": 0.0,
                "raw": {},
                "error": "GEMINI_API_KEY not set or google-generativeai not installed",
            }

        try:
            model = self.genai.GenerativeModel(
                context.get("model", self.model),
                safety_settings={
                    "HARASSMENT": "BLOCK_NONE",
                    "HATE": "BLOCK_NONE",
                    "SEXUAL": "BLOCK_NONE",
                    "DANGEROUS": "BLOCK_NONE",
                },
            )

            response = model.generate_content(prompt)

            # Gemini doesn't always provide token counts
            tokens = {
                "input_tokens": (
                    getattr(response.usage_metadata, "prompt_token_count", 0)
                    if hasattr(response, "usage_metadata")
                    else 0
                ),
                "output_tokens": (
                    getattr(response.usage_metadata, "candidates_token_count", 0)
                    if hasattr(response, "usage_metadata")
                    else 0
                ),
            }

            return {
                "output": response.text,
                "tokens_used": tokens,
                "confidence": 0.92,  # Gemini doesn't provide confidence
                "raw": {
                    "candidates": (
                        len(response.candidates)
                        if hasattr(response, "candidates")
                        else 0
                    )
                },
            }
        except Exception as e:
            return {
                "output": f"Gemini Error: {str(e)}",
                "tokens_used": {"input_tokens": 0, "output_tokens": 0},
                "confidence": 0.0,
                "raw": {},
                "error": str(e),
            }
