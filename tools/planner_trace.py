# tools/planner_trace.py
import json
from datetime import datetime
from typing import Any, Dict, Optional

from decision.decide import decide_retrieval
from planner.planner import Planner

def traced_planner_plan(
    *,
    question: str,
    k: int,
    memory_signal: Optional[Dict[str, Any]],
    trace_path,
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Traces the planner's decision independently of retrieval execution.

    Logs:
      - decide_retrieval output (requires_external_evidence, confidence, rationale)
      - memory signal (retrieval_advice, policy_enforced, etc.)
      - planner output plan + chosen action + rationale
    """
    decision = decide_retrieval(question)

    planner = Planner()
    plan = planner.generate_plan(question, k=k, wm=None, memory_signal=memory_signal)

    # Plan is single-step right now
    step = plan.steps[0]
    trace = {
        "timestamp": datetime.utcnow().isoformat(),
        "question": question,
        "k": k,
        "metadata": metadata or {},
        "inputs": {
            "memory_signal": memory_signal or {},
        },
        "decision": {
            "requires_external_evidence": decision.requires_external_evidence,
            "confidence": decision.confidence,
            "decision_rationale": decision.decision_rationale,
        },
        "plan": {
            "objective": plan.objective,
            "steps": [
                {
                    "step_id": step.step_id,
                    "action": step.action,
                    "args": step.args,
                    "rationale": step.rationale,
                }
            ],
        },
        "summary": {
            "planner_action": step.action,
            "memory_advice_used": bool((memory_signal or {}).get("retrieval_advice")),
            "decision_requires_evidence": bool(decision.requires_external_evidence),
        }
    }

    with open(trace_path, "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2)

    return plan