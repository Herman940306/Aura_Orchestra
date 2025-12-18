from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseAdapter(ABC):
    """
    Adapter interface every model worker implements.
    """

    @abstractmethod
    def generate(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Given a prompt and context (files, partial artifacts),
        returns a structured dict:
        {
           "output": "full generated content or instructions",
           "patch": unified_diff or None,
           "explanation": "...",
           "self_confidence": 0.0-1.0,
           "artifacts": {...}
        }
        """
        raise NotImplementedError
