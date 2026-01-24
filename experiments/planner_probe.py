# experiments/planner_probe.py
from pathlib import Path
import pandas as pd

from tools.planner_trace import traced_planner_plan

QUESTIONS_PATH = "artifacts/failure_cases/questions/planner_questions.xlsx"
TRACE_DIR = Path("artifacts/failure_cases/traces/planner")
TRACE_DIR.mkdir(parents=True, exist_ok=True)

TOP_K = 4

def run_planner_probe(row):
    question = row["question_text"]
    qid = int(row["question_id"])

    expected_retrieval = row.get("expected_retrieval", None)

    # For "planner-independent" pass, currently memory neutral
    # (Later, memory probe will set retrieval_advice=True/False intentionally.)
    memory_signal = {
        "retrieval_advice": False,
        "policy_enforced": False,
    }

    traced_planner_plan(
        question=question,
        k=TOP_K,
        memory_signal=memory_signal,
        trace_path=TRACE_DIR / f"q{qid:02d}.json",
        metadata={
            "question_id": qid,
            "phase": "planner",
            "expected_retrieval": expected_retrieval,
        },
    )

def main():
    df = pd.read_excel(QUESTIONS_PATH)

    for _, row in df.iterrows():
        run_planner_probe(row)


if __name__ == "__main__":
    main()