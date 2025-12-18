from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from scorer import Scorer
from error_classifier import ErrorClassifier
from ledger import Ledger

app = FastAPI(title="Aura Accountant")

scorer = Scorer()
classifier = ErrorClassifier()
ledger = Ledger()


class EvaluateRequest(BaseModel):
    model_name: str
    job_id: str
    task: Dict[str, Any]
    model_output: Dict[str, Any]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/evaluate")
def evaluate(req: EvaluateRequest):
    # 1. Score
    result = scorer.score(req.model_output, req.task)

    # 2. Classify
    classification = classifier.classify(result.penalties, result.warnings_triggered)

    # 3. Record
    ledger.record(
        req.model_name,
        req.job_id,
        result.score,
        result.penalties,
        classification["severity"],
    )

    return {
        "score": result.score,
        "penalties": result.penalties,
        "severity": classification["severity"],
        "action": classification["action"],
        "message": "Evaluation recorded",
    }
