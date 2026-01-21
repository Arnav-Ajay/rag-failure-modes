from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

Confidence = Literal["high", "medium", "low"]

@dataclass
class RetrievalDecision:
    """
    Docstring for RetrievalDecision
    - Must be computed from question
    - Must be loggable
    - decision_rationale is a short label (not a chain of thoughts)
    """
    requires_external_evidence: bool
    decision_rationale: str
    confidence: Confidence