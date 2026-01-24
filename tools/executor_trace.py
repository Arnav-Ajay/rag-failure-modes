# tools/executor_trace.py
from datetime import datetime
import json
from executor import Executor

def traced_executor_execute(*, plan, wm=None, trace_path=None, metadata=None):
    executor = Executor()
    results = executor.execute(plan, wm=wm)

    trace = {
        "timestamp": datetime.utcnow().isoformat(),
        "phase": "executor",
        "plan": {
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
        "execution": results,
        "metadata": metadata or {},
    }

    if trace_path:
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        with open(trace_path, "w") as f:
            json.dump(trace, f, indent=2)

    return results