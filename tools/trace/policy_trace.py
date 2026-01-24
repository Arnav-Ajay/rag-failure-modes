# tools/policy_trace.py
from pathlib import Path
import json
import time

from planner.planner import Planner
from memory.working import WorkingMemory
from memory.router import MemoryRouter
from policies import apply_forgetting, allow_retrieval

def traced_policy_plan(
    *,
    question: str,
    k: int,
    trace_path: Path,
    metadata: dict,
):
    wm = WorkingMemory()
    wm.goal = question

    mem = MemoryRouter()

    # --- Read episodic memory ---
    episodic_tail = mem.read_recent_episodic(n=10)
    pruned_tail = apply_forgetting(episodic_tail)

    # --- Apply retrieval policy ---
    policy_signal = allow_retrieval(
        wm=wm,
        episodic_tail=pruned_tail,
    )

    memory_signal = {
        "retrieval_advice": policy_signal,
        "policy_enforced": True,
    }

    planner = Planner()
    plan = planner.generate_plan(
        question,
        k=k,
        wm=wm,
        memory_signal=memory_signal,
    )

    trace = {
        "timestamp": time.time(),
        "question": question,
        "policy": {
            "episodic_tail_len": len(episodic_tail),
            "policy_signal": policy_signal,
        },
        "planner": {
            "steps": [s.__dict__ for s in plan.steps],
            "thoughts": wm.thoughts,
        },
        "metadata": metadata,
    }

    trace_path.parent.mkdir(parents=True, exist_ok=True)
    with open(trace_path, "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2, ensure_ascii=False)

    return trace