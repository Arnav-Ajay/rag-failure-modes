# experiments/evidence_probe.py
from pathlib import Path
import pandas as pd
import json

from tools.trace.evidence_trace import traced_evidence_assessment

QUESTIONS_PATH = "artifacts/failure_cases/questions/evidence_questions.xlsx"
RETRIEVAL_TRACES = Path("artifacts/failure_cases/traces/retrieval")
TRACE_DIR = Path("artifacts/failure_cases/traces/evidence")
TRACE_DIR.mkdir(parents=True, exist_ok=True)


def run_evidence_probe(row):
    qid = int(row["question_id"])
    question = row["question_text"]

    # Load retrieval trace as evidence input
    retrieval_trace_path = RETRIEVAL_TRACES / f"q{qid:02d}.json"
    with open(retrieval_trace_path, "r", encoding="utf-8") as f:
        retrieval_trace = json.load(f)

    retrieved_chunks = retrieval_trace["results"]

    # Normalize retrieval trace → evidence input contract
    for c in retrieved_chunks:
        if "score" not in c:
            if c.get("dense_score") is not None:
                c["score"] = c["dense_score"]
            elif c.get("sparse_score") is not None:
                c["score"] = c["sparse_score"]
            else:
                c["score"] = 0.0


    traced_evidence_assessment(
        question=question,
        retrieved_chunks=retrieved_chunks,
        trace_path=TRACE_DIR / f"q{qid:02d}.json",
        metadata={
            "question_id": qid,
            "phase": "evidence",
            "expected_evidence_sufficient": row["expected_evidence_sufficient"],
        },
    )


def main():
    df = pd.read_excel(QUESTIONS_PATH)
    for _, row in df.iterrows():
        run_evidence_probe(row)


if __name__ == "__main__":
    main()
