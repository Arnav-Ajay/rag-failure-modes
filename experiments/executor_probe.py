# experiments/executor_probe.py
from pathlib import Path
import json
import pandas as pd

from tools.trace.executor_trace import traced_executor_execute
from memory.working import WorkingMemory
from planner.plan_schema import Plan, PlanStep

QUESTIONS_PATH = "artifacts/failure_cases/questions/planner_executor_questions.xlsx"
PLANNER_TRACE_DIR = Path("artifacts/failure_cases/traces/planner")
EXECUTOR_TRACE_DIR = Path("artifacts/failure_cases/traces/executor")

EXECUTOR_TRACE_DIR.mkdir(parents=True, exist_ok=True)

def load_plan_from_planner_trace(qid: int) -> Plan:
    trace_file = PLANNER_TRACE_DIR / f"q{qid:02d}.json"
    with open(trace_file) as f:
        trace = json.load(f)

    steps = [
        PlanStep(
            step_id=s["step_id"],
            action=s["action"],
            args=s["args"],
            rationale=s["rationale"],
        )
        for s in trace["plan"]["steps"]
    ]

    return Plan(
        objective=trace["plan"]["objective"],
        steps=steps,
    )

def run_executor_probe(row):
    qid = int(row["question_id"])
    question = row["question_text"]

    plan = load_plan_from_planner_trace(qid)
    wm = WorkingMemory()

    traced_executor_execute(
        plan=plan,
        wm=wm,
        trace_path=EXECUTOR_TRACE_DIR / f"q{qid:02d}.json",
        metadata={
            "question_id": qid,
            "question_text": question,
            "phase": "executor",
        },
    )

def main():
    df = pd.read_excel(QUESTIONS_PATH)

    for _, row in df.iterrows():
        run_executor_probe(row)

if __name__ == "__main__":
    main()