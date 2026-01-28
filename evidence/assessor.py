# evidence/assessor.py
from __future__ import annotations
from typing import List, Literal, Dict, Any

from .models import EvidenceAssessment
from .heuristics import (
    evaluate_evidence_presence,
    evaluate_max_similarity,
    evaluate_coverage,
    detect_conflicts,
)

COVERAGE_THRESHOLD = 0.50
MIN_SIM_THRESHOLD = 0.50

class EvidenceAssessor:
    def assess_evidence(
        self,
        query: str,
        executor_decision: Literal["noop", "retrieve"],
        retrieved_chunks: List[Dict[str, Any]],
    ) -> EvidenceAssessment:

        # If the system didn't retrieve, we don't evaluate retrieval evidence.
        if executor_decision != "retrieve":
            return EvidenceAssessment(
                evidence_present=False,
                sufficiency="insufficient",
                max_similarity=0.0,
                coverage_score=0.0,
                conflicting_sources=False,
                rationale="No retrieval executed; no external evidence available."
            )

        max_similarity = evaluate_max_similarity(retrieved_chunks)
        evidence_present = evaluate_evidence_presence(retrieved_chunks, min_sim_threshold=MIN_SIM_THRESHOLD)
        coverage_score = evaluate_coverage(retrieved_chunks, query)
        conflicting_sources = detect_conflicts(retrieved_chunks)

        if not evidence_present:
            return EvidenceAssessment(
                evidence_present=False,
                sufficiency="insufficient",
                max_similarity=max_similarity,
                coverage_score=coverage_score,
                conflicting_sources=conflicting_sources,
                rationale=f"No chunk met similarity threshold ({MIN_SIM_THRESHOLD})."
            )

        if conflicting_sources:
            return EvidenceAssessment(
                evidence_present=True,
                sufficiency="conflicting",
                max_similarity=max_similarity,
                coverage_score=coverage_score,
                conflicting_sources=True,
                rationale="Multiple high-scoring sources retrieved; treat as potentially conflicting."
            )
        
        if coverage_score < COVERAGE_THRESHOLD:
            return EvidenceAssessment(
                evidence_present=True,
                sufficiency="insufficient",
                max_similarity=max_similarity,
                coverage_score=coverage_score,
                conflicting_sources=False,
                rationale=f"Low key-term coverage ({coverage_score:.2f} < {COVERAGE_THRESHOLD})."
            )

        return EvidenceAssessment(
            evidence_present=True,
            sufficiency="sufficient",
            max_similarity=max_similarity,
            coverage_score=coverage_score,
            conflicting_sources=False,
            rationale="Evidence present; coverage threshold met; no conflicts detected."
        )
