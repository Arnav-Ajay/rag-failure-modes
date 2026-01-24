# tools/memory_trace.py
from __future__ import annotations

from pathlib import Path
from datetime import datetime
import json
from typing import Any, Dict, List, Optional

from memory.router import MemoryRouter
from memory.working import WorkingMemory

from planner.planner import Planner
from executor.executor import Executor

def _read_jsonl_tail(path: str, n: int = 200) -> List[Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return []
    lines = p.read_text(encoding="utf-8").splitlines()
    out: List[Dict[str, Any]] = []
    for ln in lines[-n:]:
        ln = ln.strip()
        if not ln:
            continue
        try:
            out.append(json.loads(ln))
        except Exception:
            continue
    return out

def traced_memory_run(
    *,
    question: str,
    k: int,
    trace_path: Path,
    metadata: Dict[str, Any],
    # which semantic keys to sample for this run (keep explicit & minimal)
    semantic_keys: Optional[List[str]] = None,
    # if you want to seed memory for a particular run
    seed_semantic: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    trace_path.parent.mkdir(parents=True, exist_ok=True)

    # --- init ---
    wm = WorkingMemory()
    wm.goal = question

    mem = MemoryRouter()  # uses your default artifact paths
    planner = Planner()
    executor = Executor()

    # capture current event cursor (line count) so we can slice "this run"
    events_file = mem.events_path
    before_events = _read_jsonl_tail(events_file, n=10_000)  # safe for small local files
    before_len = len(before_events)

    # --- optional seeding (explicit, traceable) ---
    if seed_semantic:
        for key, value in seed_semantic.items():
            mem.write_semantic(key, value)

    # --- memory reads (explicit) ---
    episodic_tail = mem.read_recent_episodic(n=10)

    semantic_reads: Dict[str, Any] = {}
    for key in (semantic_keys or []):
        semantic_reads[key] = mem.read_semantic(key)

    # --- plan + execute (policy neutral) ---
    plan = planner.generate_plan(
        question,
        k=k,
        wm=wm,
        memory_signal={
            "retrieval_advice": False,
            "policy_enforced": False,
        },
    )

    result = executor.execute(plan, wm=wm)

    # --- events written during this run ---
    after_events = _read_jsonl_tail(events_file, n=10_000)
    run_events = after_events[before_len:] if len(after_events) >= before_len else after_events

    # --- trace object ---
    trace = {
        "timestamp": datetime.utcnow().isoformat(),
        "phase": "memory",
        "query": question,
        "top_k": k,
        "metadata": metadata,
        "memory_reads": {
            "episodic_tail_n": 10,
            "episodic_tail": episodic_tail,
            "semantic_reads": semantic_reads,
        },
        "planner": {
            "objective": plan.objective,
            "steps": [
                {
                    "step_id": s.step_id,
                    "action": s.action,
                    "args": s.args,
                    "rationale": s.rationale,
                }
                for s in plan.steps
            ],
        },
        "executor": {
            "result": result,
        },
        "working_memory": {
            "goal": wm.goal,
            "thoughts": wm.thoughts,
            "flags": wm.flags,
        },
        "memory_events": run_events,
    }

    trace_path.write_text(json.dumps(trace, indent=2, ensure_ascii=False), encoding="utf-8")
    return trace
