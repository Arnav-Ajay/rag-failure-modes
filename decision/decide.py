from __future__ import annotations
import re
from decision.schema import RetrievalDecision


# Evidence-dependent triggers (tight + conservative)
EVIDENCE_PATTERNS = [
    r"\btable\b", r"\bfigure\b", r"\bsection\b", r"\bappendix\b",
    r"\bpage\b", r"\bline\b", r"\bquote\b", r"\bcite\b", r"\bcitation\b",
    r"\bBLEU\b", r"\baccuracy\b", r"\bF1\b", r"\bAUC\b", r"\bperplexity\b",
    r"\bwhat did .* report\b", r"\baccording to\b",
    r"\bexact\b", r"\bspecific\b", r"\bnumber\b", r"\bvalue\b", r"\bscore\b",
    r"\bsummarize\b", r"\bsummary\b", r"\bverbatim\b", r"\bword-for-word\b",
]

# Cases that are typically parametric (conceptual / mechanistic)
PARAMETRIC_HINTS = [
    r"\bwhat is\b", r"\bexplain\b", r"\bwhy\b", r"\bhow does\b",
    r"\bintuition\b", r"\bconcept\b", r"\btrade-?off\b",
]

def decide_retrieval(question: str) -> RetrievalDecision:
    """
    Docstring for decide_retrieval
    
    :param question: Description
    :type question: str
    :return: Description
    :rtype: RetrievalDecision

    Binary decision: does the answer require external evidence?
    Constraint: Decision sees ONLY the question.
    """
    q = question.strip()
    q_lower = q.lower()

    # Strong evidence dependence
    for pat in EVIDENCE_PATTERNS:
        if re.search(pat, q_lower, flags=re.IGNORECASE):
            return RetrievalDecision(
                requires_external_evidence=True,
                decision_rationale="evidence-dependent request (source-specific)",
                confidence="high",
            )

    # Numeric / empirical-looking request (common in papers)
    if re.search(r"\b(\d+(\.\d+)?)\b", q_lower) and re.search(r"\b(report|reported|results|score|metric)\b", q_lower):
        return RetrievalDecision(
            requires_external_evidence=True,
            decision_rationale="empirical value requested",
            confidence="high",
        )

    # If it looks purely conceptual, default NO
    for pat in PARAMETRIC_HINTS:
        if re.search(pat, q_lower, flags=re.IGNORECASE):
            return RetrievalDecision(
                requires_external_evidence=False,
                decision_rationale="conceptual/mechanistic answer likely parametric",
                confidence="medium",
            )

    # Default: NO retrieval (conservative)
    return RetrievalDecision(
        requires_external_evidence=False,
        decision_rationale="no strong evidence dependency detected",
        confidence="low",
    )
