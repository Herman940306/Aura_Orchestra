class ErrorClassifier:
    def classify(self, penalties: list, warnings_triggered: bool):
        severity = "low"

        # Critical if warnings triggered (hallucination, drift, empty)
        if warnings_triggered:
            severity = "critical"
        elif "low_confidence" in penalties or "too_short" in penalties:
            if len(penalties) > 1:
                severity = "medium"
            else:
                severity = "low"
        elif len(penalties) > 0:
            severity = "medium"

        return {
            "severity": severity,  # low, medium, high, critical
            "categories": penalties,
            "action": self._get_action(severity),
        }

    def _get_action(self, severity):
        if severity == "critical":
            return "warn_or_suspend"  # Handled by Manager logic (2 strikes)
        elif severity == "high":
            return "penalty_-5"
        elif severity == "medium":
            return "penalty_-1"
        return "none"
