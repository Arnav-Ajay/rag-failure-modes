from pathlib import Path
import pandas as pd

from tools.trace.policy_trace import traced_policy_plan

QUESTIONS_PATH = "artifacts/failure_cases/questions/policy_questions.xlsx"
TRACE_DIR = Path("artifacts/failure_cases/traces/policy")
TRACE_DIR.mkdir(parents=True, exist_ok=True)

TOP_K = 4


def run_policy_probe(row):
    question = row["question_text"]
    qid = int(row["question_id"])

    traced_policy_plan(
        question=question,
        k=TOP_K,
        trace_path=TRACE_DIR / f"q{qid:02d}.json",
        metadata={
            "question_id": qid,
            "policy_case": row["policy_case"],
            "expected_retrieval": row["expected_retrieval"],
            "phase": "policy",
        },
    )


def main():
    df = pd.read_excel(QUESTIONS_PATH)
    for _, row in df.iterrows():
        run_policy_probe(row)


if __name__ == "__main__":
    main()