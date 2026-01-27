# tools/trace/reranker_trace.py
import json
from datetime import datetime
from tools.reranker_core import rerank_candidates


def traced_reranker(
    *,
    candidates_df,
    trace_path,
    metadata=None,
):
    """
    Observational trace for reranker behavior.
    Does NOT change reranking logic.
    """

    reranked = rerank_candidates(candidates_df)

    trace = {
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": metadata or {},
        "results": [],
    }

    for row in reranked.itertuples():
        trace["results"].append({
            "chunk_id": int(row.chunk_id),
            "doc_id": row.doc_id,
            "rerank_rank": int(row.rerank_rank),
            "rerank_score": float(row.S),
        })

    with open(trace_path, "w") as f:
        json.dump(trace, f, indent=2)

    return reranked
