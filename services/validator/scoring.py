from datetime import datetime, timedelta
import math

# weights (tunable)
WEIGHTS = {
    "tests": 0.40,
    "cross_agreement": 0.30,
    "docs_quality": 0.10,
    "performance": 0.10,
    "penalties": -0.25,
}


def score_from_signals(signals: dict, penalties: float = 0.0) -> float:
    """
    signals example:
    {
      "tests_passed": True,
      "test_score": 0.9,         # normalized 0..1
      "coverage": 0.72,         # 0..1
      "docs_quality": 0.8,      # 0..1
      "performance_ok": True,
      "cross_model_agreement": 0.6  # 0..1, how many other models had same design
    }
    """
    test_component = signals.get("test_score", 0.0) * WEIGHTS["tests"]
    agreement_component = (
        signals.get("cross_model_agreement", 0.0) * WEIGHTS["cross_agreement"]
    )
    docs_component = signals.get("docs_quality", 0.0) * WEIGHTS["docs_quality"]
    perf_component = (1.0 if signals.get("performance_ok", False) else 0.0) * WEIGHTS[
        "performance"
    ]
    penalty_component = penalties * WEIGHTS["penalties"]
    raw = (
        test_component
        + agreement_component
        + docs_component
        + perf_component
        + penalty_component
    )
    # clamp to 0..1
    final = max(0.0, min(1.0, raw))
    return final
