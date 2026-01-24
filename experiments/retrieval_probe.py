# experiments/week9_retrieval_tracing.py
from pathlib import Path
from typing import Any, Dict
import os
from tools.trace.retriever_trace import traced_hybrid_retriever
from tools.ingest import load_pdf, chunk_texts
from tools.retriever_core import create_vector_store, create_bm25_index

PDF_DIR = "data/input_pdfs/"
QUESTIONS_PATH = "artifacts/failure_cases/questions/retrieval_questions.xlsx"
TRACE_DIR = Path("artifacts/failure_cases/traces/retrieval")
TRACE_DIR.mkdir(parents=True, exist_ok=True)

_CORPUS_CACHE: Dict[str, Any] = {}
CHUNKING_STRATEGY = "fixed"
TOP_K = 4

def _load_corpus(pdf_dir: str, chunking_strategy: str="fixed",
                 max_chunks: int=1000,):
    cache_key = f"{pdf_dir}:{chunking_strategy}:{max_chunks}"
    if cache_key in _CORPUS_CACHE:
        return _CORPUS_CACHE[cache_key]
    
    all_chunks = {}
    global_chunk_id = 0

    for filename in sorted(os.listdir(pdf_dir)):
        if not filename.endswith(".pdf"):
            continue

        text = load_pdf(os.path.join(pdf_dir, filename))
        chunks = chunk_texts(text, strategy=chunking_strategy)

        for _, chunk_text in chunks.items():
            all_chunks[global_chunk_id] = {
                "doc_id": filename,
                "text": chunk_text,
            }
            global_chunk_id += 1
            if global_chunk_id >= max_chunks:
                break

    vector_store = create_vector_store(all_chunks)
    bm25_index = create_bm25_index(all_chunks)

    payload = {
        "chunks": all_chunks,
        "vector_store": vector_store,
        "bm25_index": bm25_index,
    }

    _CORPUS_CACHE[cache_key] = payload
    return payload


def run_retrieval_probe(question_row):
    question = question_row["question_text"]
    qid = question_row["question_id"]
    gold_chunk = question_row["gold_chunk_id"]

    # Load corpus ONCE (or cache globally)
    corpus = _load_corpus(
        pdf_dir=PDF_DIR,
        chunking_strategy=CHUNKING_STRATEGY,
    )

    traced_hybrid_retriever(
        query=question,
        vector_store=corpus["vector_store"],
        bm25_index=corpus["bm25_index"],
        top_k=max(TOP_K * 5, 20),
        trace_path=TRACE_DIR / f"q{qid:02d}.json",
        metadata={
            "question_id": qid,
            "gold_chunk_id": gold_chunk,
            "phase": "retrieval"
        }
    )

def main():
    import pandas as pd

    questions_df = pd.read_excel(QUESTIONS_PATH)


    for _, row in questions_df.iterrows():
        run_retrieval_probe(row)

if __name__ == "__main__":
    main()