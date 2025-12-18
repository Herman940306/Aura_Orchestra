from pydantic import BaseModel
from typing import List, Dict


class ScoreResult(BaseModel):
    score: float
    penalties: List[str]
    confidence: float
    warnings_triggered: bool


class Scorer:
    def __init__(self):
        # Keywords suggesting drift without Director approval
        self.drift_keywords = [
            "completely rewrite",
            "ignore previous",
            "change direction",
            "different approach",
            "alternative plan",
        ]
        # Keywords suggesting drift justification (which makes it okay-ish)
        self.justification_keywords = [
            "Director approved",
            "per instruction",
            "as requested",
            "enhancement suggestion",
            "reasoning:",
        ]

    def score(self, model_output: dict, task: dict) -> ScoreResult:
        penalties = []
        warnings_triggered = False

        text = model_output.get("output", "")
        confidence = model_output.get("confidence", 0.0)

        # 1. Confidence Penalty
        if confidence < 0.5:
            penalties.append("low_confidence")

        # 2. Empty Output (Critical)
        if len(text.strip()) == 0:
            penalties.append("empty_output")
            # Empty output is useless, but maybe not malicious drift.
            # We'll treat it as severe but maybe not warning-triggering unless repeated?
            # User said "hallucination/empty -> critical". So yes, warning.
            warnings_triggered = True

        # 3. Hallucination / Drift Heuristic
        # Simple keyword check for now. In real prod, this needs finding undefined vars.
        # Check for drift
        lower_text = text.lower()

        has_drift = any(k in lower_text for k in self.drift_keywords)
        has_justification = any(k in lower_text for k in self.justification_keywords)

        if has_drift and not has_justification:
            penalties.append("model_drift")
            warnings_triggered = True  # Critical

        # 4. Length Heuristic
        min_len = task.get("min_length", 20)
        if len(text) < min_len and len(text) > 0:
            penalties.append("too_short")

        # Calculate Score
        base_score = confidence * 100
        penalty_points = len(penalties) * 15  # Stricter

        # Heavy penalty for warnings
        if warnings_triggered:
            penalty_points += 50

        final_score = max(0.0, base_score - penalty_points)

        return ScoreResult(
            score=final_score,
            penalties=penalties,
            confidence=confidence,
            warnings_triggered=warnings_triggered,
        )
