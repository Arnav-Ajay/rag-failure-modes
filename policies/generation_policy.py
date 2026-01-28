# policy/generation_policy.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional

from evidence.models import EvidenceAssessment
from policies.refusal_codes import RefusalCode
from policies.hedge_codes import HedgeCode

Decision = Literal["answer", "hedge", "refuse"]

@dataclass(frozen=True)
class GenerationDecision:
    decision: Decision
    refusal_code: Optional[RefusalCode] = None
    hedge_code: Optional[HedgeCode] = None
    rationale: Optional[str] = None


class GenerationPolicy:
    """
    Pure policy layer.
    - No LLM calls
    - No retrieval access
    - No memory access
    """

    @staticmethod
    def decide(evidence: EvidenceAssessment) -> GenerationDecision:

        # --- Insufficient evidence → REFUSE ---
        if evidence.sufficiency == "insufficient":
            if not evidence.evidence_present:
                decision = GenerationDecision(
                    decision="refuse",
                    refusal_code=RefusalCode.NO_EVIDENCE,
                    rationale=evidence.rationale,
                )
            else:
                decision = GenerationDecision(
                    decision="refuse",
                    refusal_code=RefusalCode.INSUFFICIENT_COVERAGE,
                    rationale=evidence.rationale,
                )

        # --- Conflicting evidence → HEDGE ---
        elif evidence.sufficiency == "conflicting":
            decision = GenerationDecision(
                decision="hedge",
                hedge_code=HedgeCode.CONFLICTING_SOURCES,
                rationale=evidence.rationale,
            )

        # --- Sufficient evidence → ANSWER ---
        else:
            decision = GenerationDecision(
                decision="answer",
                rationale=evidence.rationale,
            )

        return decision