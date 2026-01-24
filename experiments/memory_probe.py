# experiments/memory_probe.py
from pathlib import Path
import pandas as pd

from tools.trace.memory_trace import traced_memory_run

QUESTIONS_PATH = "artifacts/failure_cases/questions/memory_questions.xlsx"
TRACE_DIR = Path("artifacts/failure_cases/traces/memory")
TRACE_DIR.mkdir(parents=True, exist_ok=True)

TOP_K = 4

# Minimal semantic keys 
SEMANTIC_KEYS = [
    "last_user_question",
    # "transformer_layers",
]


def run_memory_probe(row):
    qid = int(row["question_id"])
    question = row["question_text"]
    memory_case = row.get("memory_case", "")
    expected_memory_use = row.get("expected_memory_use", "")
    notes = row.get("notes", "")

    traced_memory_run(
        question=question,
        k=TOP_K,
        trace_path=TRACE_DIR / f"q{qid:02d}.json",
        metadata={
            "question_id": qid,
            "memory_case": memory_case,
            "expected_memory_use": expected_memory_use,
            "notes": notes,
        },
        semantic_keys=SEMANTIC_KEYS,
        seed_semantic=None,  # keep None for v1
    )


def main():
    df = pd.read_excel(QUESTIONS_PATH)
    for _, row in df.iterrows():
        run_memory_probe(row)


if __name__ == "__main__":
    main()