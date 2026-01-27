from pathlib import Path
import json
import pandas as pd

from tools.trace.reranker_trace import traced_reranker

# -------------------------
# Paths
# -------------------------

QUESTIONS_PATH = "artifacts/failure_cases/questions/retrieval_questions.xlsx"

RETRIEVAL_TRACE_DIR = Path("artifacts/failure_cases/traces/retrieval")
RERANKER_TRACE_DIR = Path("artifacts/failure_cases/traces/reranker")
RERANKER_TRACE_DIR.mkdir(parents=True, exist_ok=True)

CHUNKS_PATH = "data/chunks_output.csv"

# -------------------------
# Load canonical chunk store
# -------------------------

CHUNKS_DF = pd.read_csv(CHUNKS_PATH)

# enforce consistent typing
CHUNKS_DF["chunk_id"] = CHUNKS_DF["chunk_id"].astype(int)
CHUNKS_DF["doc_id"] = CHUNKS_DF["doc_id"].astype(str)

# -------------------------
# Core probe logic
# -------------------------

def run_reranker_probe(row):
    qid = int(row["question_id"])

    retrieval_trace_path = RETRIEVAL_TRACE_DIR / f"q{qid:02d}.json"
    if not retrieval_trace_path.exists():
        print(f"[SKIP] No retrieval trace for q{qid:02d}")
        return

    # ---- Load retrieval trace ----
    with open(retrieval_trace_path, "r") as f:
        trace = json.load(f)

    retrieval_results = trace["results"]
    if not retrieval_results:
        print(f"[SKIP] Empty retrieval results for q{qid:02d}")
        return

    retrieval_df = pd.DataFrame(retrieval_results)

    # enforce types
    retrieval_df["chunk_id"] = retrieval_df["chunk_id"].astype(int)
    retrieval_df["doc_id"] = retrieval_df["doc_id"].astype(str)

    # ---- Materialize chunk text ----
    candidates_df = retrieval_df.merge(
        CHUNKS_DF,
        on=["chunk_id", "doc_id"],
        how="left",
    )

    # sanity check — this should NEVER fail
    if candidates_df["chunk_text"].isna().any():
        missing = candidates_df[candidates_df["chunk_text"].isna()]
        raise RuntimeError(
            f"Missing chunk_text for chunk_ids: {missing['chunk_id'].tolist()}"
        )
    candidates_df["question_id"] = row["question_id"]
    candidates_df["question_text"] = row["question_text"]

    # ---- Run reranker with tracing ----
    traced_reranker(
        candidates_df=candidates_df,
        trace_path=RERANKER_TRACE_DIR / f"q{qid:02d}.json",
        metadata={
            "question_id": qid,
            "question_text": row["question_text"],
            "gold_chunk_id": int(row["gold_chunk_id"]),
            "phase": "reranker",
            "source": "retrieval_candidates + chunks_output",
        },
    )


    print(f"[OK] Reranker trace written for q{qid:02d}")

# -------------------------
# Entrypoint
# -------------------------

def main():
    df = pd.read_excel(QUESTIONS_PATH)

    for _, row in df.iterrows():
        run_reranker_probe(row)

if __name__ == "__main__":
    main()
