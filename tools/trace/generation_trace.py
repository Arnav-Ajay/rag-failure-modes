# tools/trace/generation_trace.py
from datetime import datetime
import json
from pathlib import Path

from generator import Generator
from evidence.models import EvidenceAssessment
from policies import GenerationPolicy

def traced_generation(
    *,
    question: str,
    evidence_summary: dict,
    trace_path: Path,
    metadata: dict | None = None,
):
    """
    Trace generation behavior given fixed evidence assessment.
    """

    timestamp = datetime.now().isoformat()
    evidence = EvidenceAssessment(
        evidence_present=evidence_summary["evidence_present"],
        sufficiency=evidence_summary["sufficiency"],
        max_similarity=evidence_summary["max_similarity"],
        coverage_score=evidence_summary["coverage_score"],
        conflicting_sources=evidence_summary["conflicting_sources"],
        rationale=evidence_summary["rationale"]
        )
    # Apply generation policy (no logic change)
    policy_decision = GenerationPolicy().decide(
        evidence=evidence
    )

    if policy_decision.refusal_code:
        output = {
            "type": "refusal",
            "refusal_code": policy_decision.refusal_code,
        }
    if policy_decision.hedge_code:
        output = {
            "type": "hedge",
            "hedge_code": policy_decision.hedge_code,
        }
    else:
        output = {
            "type": "answer",
            "answer": Generator().generate(
                question=question,
                context="",
                decision=policy_decision,
                llm_call=lambda prompt: f"Simulated answer for prompt with question: {question}",
            ),
        }

    trace = {
        "timestamp": timestamp,
        "phase": "generation",
        "query": question,
        "metadata": metadata or {},
        "evidence_summary": evidence_summary,
        "policy_decision": {
            "allowed": policy_decision.decision,
            "refusal_code": policy_decision.refusal_code,
        },
        "output": output,
    }

    trace_path.parent.mkdir(parents=True, exist_ok=True)
    trace_path.write_text(json.dumps(trace, indent=2))

    return trace
