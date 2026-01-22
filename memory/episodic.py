# memory/episodic.py

import os
import json
from typing import Any, Dict, List

class EpisodicStore:
    """
    Append-only event memory. Decay policy can be added later via policies/.
    """
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def append(self, record: Dict[str, Any]) -> None:
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def tail(self, n: int = 50) -> List[Dict[str, Any]]:
        if not os.path.exists(self.path):
            return []
        # Simple tail: read all then slice
        with open(self.path, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f.readlines() if ln.strip()]
        out = []
        for ln in lines[-n:]:
            try:
                out.append(json.loads(ln))
            except Exception:
                continue
        return out