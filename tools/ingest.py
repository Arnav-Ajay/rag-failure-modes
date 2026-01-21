# tools/ingest.py
import pdfplumber
import unicodedata
import re

_TOKEN_RE = re.compile(r"[a-z0-9]+")

_STOPWORDS = {
    "the","a","an","and","or","but","if","then","else","for","to","of","in","on","at","by",
    "with","as","is","are","was","were","be","been","being","it","this","that","these","those",
    "from","into","over","under","after","before","during","about","between","within","without",
    "not","no","can","could","should","would","may","might","must","will","do","does","did"
}

def _tokens(text: str):
    return {t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOPWORDS}

def fix_pdf_mojibake(text: str) -> str:
    # Unicode canonical normalization
    text = unicodedata.normalize("NFKC", text)

    # Explicit PDF mojibake fixes
    replacements = {
        "â€“": "–",
        "â€”": "—",
        "â€™": "’",
        "â€œ": "“",
        "â€ ": "”",
        "â†’": "→",
        "â‰¥": "≥",
        "â‰¤": "≤",
        "Âµ": "µ",
        "Â°": "°",
        "Ã—": "×",
        "Ã·": "÷",
        "Â±": "±",
        "Â²": "²",
        "Â³": "³",
        "â€¢": "•",
        "âˆ‘": "∑",
        "âˆš": "√",
    }


    for bad, good in replacements.items():
        text = text.replace(bad, good)

    return text

# Function to load PDF and extract text
def load_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        previous_page_text = ""

        for page in pdf.pages:
            page_text = page.extract_text() or ""

            page_text = unicodedata.normalize("NFKC", page_text)
            page_text = fix_pdf_mojibake(page_text)

            normalized_text = " ".join(page_text.split())

            if len(normalized_text) < 50:
                continue

            if normalized_text == previous_page_text:
                continue

            text += normalized_text + "\n"
            previous_page_text = normalized_text

    return text

def chunk_fixed(text, chunk_size=500, overlap=50, max_chunks=1000):
    chunks = {}
    start = 0
    text_length = len(text)
    chunk_id = 0

    while start < text_length and chunk_id < max_chunks:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]
        chunks[chunk_id] = chunk
        chunk_id += 1

        if end == text_length:
            break

        start = end - overlap if overlap > 0 else end

    return chunks

def chunk_structural(
    text: str,
    max_chars: int = 900,
    min_chars: int = 250,
    merge_window_chars: int = 1200,
    max_chunks: int = 1000,
):
    """
    Structural chunking based on paragraph / header / list boundaries.
    Deterministic, PDF-robust.
    """

    # --- Step 1: split into lines ---
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    def is_header(line: str) -> bool:
        if len(line) > 80:
            return False
        upper_ratio = sum(1 for c in line if c.isupper()) / max(len(line), 1)
        return (
            upper_ratio > 0.5
            or line.endswith(":")
            or re.match(r"^\d+(\.\d+)*\s+", line) is not None
        )

    def is_bullet(line: str) -> bool:
        return bool(re.match(r"^[-•*]\s+|\d+[\.\)]\s+", line))

    # --- Step 2: build structural blocks ---
    blocks = []
    current = []

    for line in lines:
        if is_header(line) or is_bullet(line):
            if current:
                blocks.append(" ".join(current))
                current = []
            current.append(line)
        else:
            current.append(line)

    if current:
        blocks.append(" ".join(current))

    # --- Step 3: merge blocks into chunks ---
    chunks = []
    buf = ""

    for block in blocks:
        if not buf:
            buf = block
            continue

        if len(buf) + len(block) <= max_chars:
            buf += " " + block
        else:
            chunks.append(buf)
            buf = block

    if buf:
        chunks.append(buf)

    # --- Step 4: enforce min size by back-merging ---
    merged = []
    for c in chunks:
        if len(c) < min_chars and merged:
            if len(merged[-1]) + len(c) <= merge_window_chars:
                merged[-1] += " " + c
            else:
                merged.append(c)
        else:
            merged.append(c)

    # --- Step 5: split oversized chunks safely ---
    final_chunks = []
    sentence_split = re.compile(r"(?<=[\.\!\?;])\s+")

    for c in merged:
        if len(c) <= merge_window_chars:
            final_chunks.append(c)
        else:
            sentences = sentence_split.split(c)
            buf = ""
            for s in sentences:
                if len(buf) + len(s) <= max_chars:
                    buf += " " + s if buf else s
                else:
                    final_chunks.append(buf)
                    buf = s
            if buf:
                final_chunks.append(buf)

    # --- Step 6: cap and index ---
    out = {}
    for i, c in enumerate(final_chunks[:max_chunks]):
        out[i] = c.strip()

    return out

def chunk_semantic(
    text: str,
    target_chars: int = 700,
    min_chars: int = 300,
    max_chars: int = 1100,
    similarity_threshold: float = 0.18,
    lookback_sentences: int = 2,
    max_chunks: int = 1000,
):
    """
    Semantic chunking via lexical cohesion (Jaccard similarity).
    Deterministic and retriever-agnostic.
    """

    # --- Step 1: sentence segmentation ---
    sentences = re.split(r"(?<=[\.\!\?])\s+|\n+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    chunks = []
    cur_sents = []
    cur_tokens = set()
    cur_len = 0

    def flush():
        nonlocal cur_sents, cur_tokens, cur_len
        if cur_sents:
            chunks.append(" ".join(cur_sents))
        cur_sents = []
        cur_tokens = set()
        cur_len = 0

    for s in sentences:
        s_tokens = _tokens(s)

        # rolling topic tokens
        topic_tokens = cur_tokens if cur_tokens else s_tokens
        overlap = (
            len(s_tokens & topic_tokens) / max(len(s_tokens | topic_tokens), 1)
        )

        should_split = (
            cur_len >= min_chars
            and overlap < similarity_threshold
            and cur_len >= target_chars
        )

        if should_split or cur_len + len(s) > max_chars:
            flush()

        cur_sents.append(s)
        cur_len += len(s)
        cur_tokens |= s_tokens

        # restrict topic drift
        if len(cur_sents) > lookback_sentences:
            recent = cur_sents[-lookback_sentences:]
            cur_tokens = set().union(*(_tokens(x) for x in recent))

    flush()

    # --- Step 2: merge undersized chunks ---
    merged = []
    for c in chunks:
        if len(c) < min_chars and merged:
            merged[-1] += " " + c
        else:
            merged.append(c)

    # --- Step 3: cap and index ---
    out = {}
    for i, c in enumerate(merged[:max_chunks]):
        out[i] = c.strip()

    return out

def chunk_texts(text, strategy="fixed", **kwargs):
    if strategy == "fixed":
        return chunk_fixed(text, **kwargs)
    elif strategy == "structural":
        return chunk_structural(text, **kwargs)
    elif strategy == "semantic":
        return chunk_semantic(text, **kwargs)
    else:
        raise ValueError(f"Unknown chunking strategy: {strategy}")