# tools/reranker_core.py
from __future__ import annotations
import re
from typing import Dict, List

import numpy as np
import pandas as pd

# -------------------------
# Tokenization helpers
# -------------------------

_TOKEN_RE = re.compile(r"[a-z0-9]+")

_STOPWORDS = {
    "the","a","an","and","or","but","if","then","else","for","to","of","in","on","at","by",
    "with","as","is","are","was","were","be","been","being","it","this","that","these","those",
    "you","your","we","our","they","their","i","me","my","from","into","over","under","after",
    "before","during","about","between","within","without","not","no","can","could","should",
    "would","may","might","must","will","do","does","did"
}

def tokenize(text: str) -> List[str]:
    if not isinstance(text, str):
        return []
    return _TOKEN_RE.findall(text.lower())


def non_stop_tokens(text: str) -> List[str]:
    return [t for t in tokenize(text) if t not in _STOPWORDS]


# -------------------------
# Feature functions
# -------------------------

def overlap_score(chunk_text: str, query_text: str) -> float:
    c = set(non_stop_tokens(chunk_text))
    q = set(non_stop_tokens(query_text))
    if not c or not q:
        return 0.0
    return len(c & q) / max(len(c | q), 1)


def keyphrase_score(chunk_text: str, query_text: str, top_n: int = 6) -> float:
    keys = sorted(
        dict.fromkeys(non_stop_tokens(query_text)),
        key=lambda t: (-len(t), t)
    )[:top_n]

    if not keys:
        return 0.0

    cset = set(tokenize(chunk_text))
    return sum(1 for k in keys if k in cset) / len(keys)


_PATTERNS = [
    r"\b(is|are)\s+defined\s+as\b",
    r"\bmeans\b",
    r"\brefers\s+to\b",
    r"\bbecause\b",
    r"\btherefore\b",
    r"\bstep\s+\d+\b",
    r"\bmust\b",
    r"\bshould\b",
]

def pattern_score(text: str) -> float:
    if not isinstance(text, str):
        return 0.0
    hits = sum(1 for p in _PATTERNS if re.search(p, text.lower()))
    return min(hits, 4) / 4.0


def length_penalty(text: str, min_chars: int = 200) -> float:
    if not isinstance(text, str):
        return 1.0
    n = len(text)
    if n >= min_chars:
        return 0.0
    return (min_chars - n) / min_chars

# -------------------------
# Normalization
# -------------------------

def minmax(series: pd.Series) -> pd.Series:
    s = series.astype(float)
    if s.notna().sum() == 0:
        return pd.Series([0.0] * len(s), index=s.index)
    mn, mx = s.min(), s.max()
    if mn == mx:
        return pd.Series([0.0] * len(s), index=s.index)
    return (s - mn) / (mx - mn + 1e-12)

def rerank_candidates(
    candidates: pd.DataFrame,
    *,
    weights: Dict[str, float] | None = None,
) -> pd.DataFrame:
    """
    Pure reranker.

    REQUIRED columns:
      - question_id
      - question_text
      - chunk_text
      - dense_score (float | NaN)
      - sparse_score (float | NaN)

    Returns:
      same rows with:
        - S
        - rerank_rank
    """

    w = weights or {
        "wd": 0.4,
        "wb": 0.3,
        "wo": 0.1,
        "wk": 0.1,
        "wp": 0.0,
        "wl": 0.1,
    }

    df = candidates.copy()

    # Safety
    df["chunk_text"] = df["chunk_text"].fillna("")
    df["question_text"] = df["question_text"].fillna("")

    # Normalize per question
    df["norm_dense"] = df.groupby("question_id")["dense_score"].transform(minmax)
    df["norm_sparse"] = df.groupby("question_id")["sparse_score"].transform(minmax)

    # Features
    df["overlap"] = df.apply(lambda r: overlap_score(r.chunk_text, r.question_text), axis=1)
    df["keyphrase"] = df.apply(lambda r: keyphrase_score(r.chunk_text, r.question_text), axis=1)
    df["pattern"] = df["chunk_text"].apply(pattern_score)
    df["len_penalty"] = df["chunk_text"].apply(length_penalty)

    # Final score
    df["S"] = (
        w["wd"] * df["norm_dense"] +
        w["wb"] * df["norm_sparse"] +
        w["wo"] * df["overlap"] +
        w["wk"] * df["keyphrase"] +
        w["wp"] * df["pattern"] -
        w["wl"] * df["len_penalty"]
    )

    # Rank per question
    df = df.sort_values(["question_id", "S"], ascending=[True, False])
    df["rerank_rank"] = df.groupby("question_id").cumcount() + 1

    return df
