# tools/retriever_trace.py
import json
from datetime import datetime
from tools.retriever_core import hybrid_retriever

def traced_hybrid_retriever(
    *,
    query,
    vector_store,
    bm25_index,
    top_k,
    trace_path,
    metadata=None
):
    results = hybrid_retriever(
        query=query,
        vector_store=vector_store,
        bm25_index=bm25_index,
        top_k=top_k
    )

    trace = {
        "timestamp": datetime.utcnow().isoformat(),
        "query": query,
        "top_k": top_k,
        "metadata": metadata or {},
        "results": []
    }

    for rank, (chunk_id, doc_id, text, score) in enumerate(results, start=1):
        trace["results"].append({
            "rank": rank,
            "chunk_id": chunk_id,
            "doc_id": doc_id,
            "dense_rank": score["dense_rank"],
            "dense_score": score["dense_score"],
            "sparse_rank": score["sparse_rank"],
            "sparse_score": score["sparse_score"],
            "priority": score["priority"],
        })

    with open(trace_path, "w") as f:
        json.dump(trace, f, indent=2)

    return results
