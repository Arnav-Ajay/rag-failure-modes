# evidence/models.py
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class EvidenceAssessment:
    evidence_present: bool
    sufficiency: Literal["sufficient", "insufficient", "conflicting"]
    max_similarity: float
    coverage_score: float
    conflicting_sources: bool
    rationale: str
