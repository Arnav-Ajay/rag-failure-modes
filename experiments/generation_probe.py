# experiments/generation_probe.py
from pathlib import Path
import json
import pandas as pd

from tools.trace.generation_trace import traced_generation

QUESTIONS_PATH = "artifacts/failure_cases/questions/generation_questions.csv"
EVIDENCE_TRACE_DIR = Path("artifacts/failure_cases/traces/evidence")
GEN_TRACE_DIR = Path("artifacts/failure_cases/traces/generation")

GEN_TRACE_DIR.mkdir(parents=True, exist_ok=True)


def run_generation_probe(row):
    qid = int(row["question_id"])
    question = row["question_text"]

    evidence_trace_path = EVIDENCE_TRACE_DIR / f"q{qid:02d}.json"
    evidence_trace = json.loads(evidence_trace_path.read_text())

    evidence_summary = evidence_trace["assessment"]

    traced_generation(
        question=question,
        evidence_summary=evidence_summary,
        trace_path=GEN_TRACE_DIR / f"q{qid:02d}.json",
        metadata={
            "question_id": qid,
            "generation_case": row["generation_case"],
            "expected_behavior": row["expected_behavior"],
        },
    )


def main():
    df = pd.read_csv(QUESTIONS_PATH)

    for _, row in df.iterrows():
        run_generation_probe(row)


if __name__ == "__main__":
    main()
