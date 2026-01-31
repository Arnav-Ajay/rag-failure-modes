# tools/trace/evidence_trace.py
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from evidence import EvidenceAssessor


def traced_evidence_assessment(
    *,
    question: str,
    retrieved_chunks: List[Dict[str, Any]],
    executor_decision: str = "retrieve",
    trace_path,
    metadata: Optional[Dict[str, Any]] = None,
):
    assessor = EvidenceAssessor()

    assessment = assessor.assess_evidence(
        query=question,
        retrieved_chunks=retrieved_chunks,
        executor_decision=executor_decision,
    )

    trace = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "metadata": metadata or {},
        "inputs": {
            "num_chunks": len(retrieved_chunks),
            "chunk_ids": [c.get("chunk_id") for c in retrieved_chunks],
        },
        "assessment": {
            "evidence_present": assessment.evidence_present,
            "sufficiency": assessment.sufficiency,
            "max_similarity": assessment.max_similarity,
            "coverage_score": assessment.coverage_score,
            "conflicting_sources": assessment.conflicting_sources,
            "rationale": assessment.rationale,
        },
    }

    trace_path.parent.mkdir(parents=True, exist_ok=True)
    with open(trace_path, "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2)

    return assessment
