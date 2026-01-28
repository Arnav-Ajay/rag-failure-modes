# evidence/heuristics.py
from __future__ import annotations
import re
from typing import List, Dict, Any

_TOKEN_RE = re.compile(r"[a-z0-9]+")

_STOPWORDS = {
    "the","a","an","and","or","but","if","then","else","for","to","of","in","on","at","by",
    "with","as","is","are","was","were","be","been","being","it","this","that","these","those",
    "you","your","we","our","they","their","i","me","my","from","into","over","under","after",
    "before","during","about","between","within","without","not","no","can","could","should",
    "would","may","might","must","will","do","does","did"
}

def _tokenize(text: str) -> List[str]:
    if not isinstance(text, str):
        return []
    return _TOKEN_RE.findall(text.lower())

def _non_stop_tokens(text: str) -> List[str]:
    return [t for t in _tokenize(text) if t not in _STOPWORDS]

def chunk_score(chunk: Dict[str, Any]) -> float:
    """
    Your pipeline returns either:
      - score: float (reranked=True)  :contentReference[oaicite:5]{index=5}
      - score: dict  (reranked=False) 
    Evidence needs ONE comparable scalar.
    """
    s = chunk.get("score", 0.0)
    if isinstance(s, (int, float)):
        return float(s)

    # If hybrid provenance dict: prefer dense_score if present, else sparse_score
    if isinstance(s, dict):
        ds = s.get("dense_score")
        ss = s.get("sparse_score")
        if isinstance(ds, (int, float)):
            return float(ds)
        if isinstance(ss, (int, float)):
            return float(ss)

    return 0.0

def evaluate_evidence_presence(chunks: List[Dict[str, Any]], min_sim_threshold: float = 0.75) -> bool:
    return any(chunk_score(c) >= min_sim_threshold for c in chunks)

def evaluate_max_similarity(chunks: List[Dict[str, Any]]) -> float:
    return max((chunk_score(c) for c in chunks), default=0.0)

def _key_terms(query: str, top_n: int = 6) -> List[str]:
    # Deterministic "key terms": unique non-stop tokens, longest first (stable tie-break)
    toks = list(dict.fromkeys(_non_stop_tokens(query)))
    toks.sort(key=lambda t: (-len(t), t))
    return toks[:top_n]

def evaluate_coverage(chunks: List[Dict[str, Any]], query: str, top_n: int = 6) -> float:
    """
    Coverage = fraction of top query key-terms that appear in at least one chunk.
    This is NOT "support", but it blocks "topic-only" retrieval from green-lighting generation.
    """
    keys = _key_terms(query, top_n=top_n)
    if not keys:
        return 0.0

    covered = set()
    for c in chunks:
        text = c.get("text", "") or ""
        cset = set(_tokenize(text))
        for k in keys:
            if k in cset:
                covered.add(k)

    return len(covered) / len(keys)

def detect_conflicts(chunks: List[Dict[str, Any]], hi_threshold: float = 0.80) -> bool:
    """
    v1 conflict heuristic (cheap + deterministic):
    - if multiple high-scoring chunks come from different sources, mark as "potentially conflicting"
    This is intentionally conservative: it forces HEDGE/REFUSE rather than false confidence.
    """
    sources = set()
    for c in chunks:
        if chunk_score(c) >= hi_threshold:
            src = c.get("source") or c.get("doc_id") or c.get("source_id")
            if src:
                sources.add(str(src))
    return len(sources) > 1