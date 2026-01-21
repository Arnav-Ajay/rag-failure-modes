# planner/plan_schema.py

from dataclasses import dataclass
from typing import Any, Dict, List, Literal

Action = Literal["retrieve", "noop"]

@dataclass(frozen=True)
class PlanStep:
    step_id: int
    action: Action
    args: Dict[str, Any]
    rationale: str

@dataclass(frozen=True)
class Plan:
    objective: str
    steps: List[PlanStep]