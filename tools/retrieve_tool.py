from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Dict, Any

from tools.retriever_core import (
    create_vector_store,
    create_bm25_index,
    hybrid_retriever,
)
from tools.reranker_core import rerank_candidates
from tools.ingest import load_pdf, chunk_texts

# --------------
# Data contracts 
# --------------

@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: int
    text: str
    score: float | Dict[str, Any]
    source: str

# -------------------------
# Corpus bootstrap (cached)
# -------------------------

_CORPUS_CACHE: Dict[str, Any] = {}
PDF_DIR = "data/input_pdfs/"

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

# --------------
# Retrieval Tool
# --------------

def retrieve_tool(question: str, k: int = 4, pdf_dir: str = PDF_DIR,
    chunking_strategy: str = "fixed", enable_rerank: bool = False,) -> Dict[str, Any]:
    
    corpus = _load_corpus(
        pdf_dir=pdf_dir,
        chunking_strategy=chunking_strategy,
    )

    raw_results = hybrid_retriever(
        question,
        corpus["vector_store"],
        corpus["bm25_index"],
        top_k=max(k * 5, 20),
    )

    QUESTION_ID = 0  # single-query context

    if enable_rerank:
        import pandas as pd

        rows = []
        for cid, doc_id, text, score in raw_results:
            rows.append({
                "question_id": QUESTION_ID,
                "question_text": question,
                "chunk_id": cid,
                "doc_id": doc_id,
                "chunk_text": text,
                "dense_score": score.get("dense_score"),
                "sparse_score": score.get("sparse_score") or score.get("bm25_score"),
            })

        df = pd.DataFrame(rows)
        df = rerank_candidates(df)
        df = df.sort_values("rerank_rank").head(k)

        chunks = [
            RetrievedChunk(
                chunk_id=int(r.chunk_id),
                text=r.chunk_text,
                score=float(r.S),
                source=r.doc_id,
            )
            for r in df.itertuples()
        ]

    else:
        chunks = [
            RetrievedChunk(
                chunk_id=cid,
                text=text,
                score=score,
                source=doc_id,
            )
            for cid, doc_id, text, score in raw_results[:k]
        ]

    return {
        "k": k,
        "mode": "hybrid",
        "reranked": enable_rerank,
        "candidate_pool_size": len(raw_results),
        "chunks": [c.__dict__ for c in chunks],
    }
