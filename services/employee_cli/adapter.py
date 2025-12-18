import subprocess

try:
    from services.employees.common.adapter import BaseAdapter
except ImportError:

    class BaseAdapter:
        pass


class CLIAdapter(BaseAdapter):
    """
    Wraps any CLI tool as a model adapter.
    Useful for: linters, formatters, static analyzers, custom scripts.
    """

    def __init__(self, command=None):
        self.command = command or ["echo"]  # Default to echo if no command

    def generate(self, prompt: str, context: dict) -> dict:
        try:
            # Get command from context or use default
            cmd = context.get("command", self.command)
            if isinstance(cmd, str):
                cmd = cmd.split()

            # Execute command with prompt as input
            result = subprocess.run(
                cmd + [prompt],
                capture_output=True,
                text=True,
                timeout=context.get("timeout", 30),
            )

            return {
                "output": (
                    result.stdout.strip()
                    if result.returncode == 0
                    else result.stderr.strip()
                ),
                "tokens_used": {},  # CLI tools don't have token concept
                "confidence": 1.0 if result.returncode == 0 else 0.0,
                "raw": {
                    "returncode": result.returncode,
                    "stderr": result.stderr[:200] if result.stderr else "",
                },
            }
        except subprocess.TimeoutExpired:
            return {
                "output": "CLI command timed out",
                "tokens_used": {},
                "confidence": 0.0,
                "raw": {},
                "error": "timeout",
            }
        except Exception as e:
            return {
                "output": f"CLI Error: {str(e)}",
                "tokens_used": {},
                "confidence": 0.0,
                "raw": {},
                "error": str(e),
            }
