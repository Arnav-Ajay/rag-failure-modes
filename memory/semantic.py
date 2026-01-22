# memory/semantic.py
import os
import json
from typing import Any, Dict, Optional

class SemanticStore:
    """
    Small JSON dict store. Gating/dedup can be added later via policies/.
    """
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def load(self) -> Dict[str, Any]:
        if not os.path.exists(self.path):
            return {}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save(self, data: Dict[str, Any]) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get(self, key: str) -> Optional[Any]:
        data = self.load()
        return data.get(key)

    def set(self, key: str, value: Any) -> None:
        data = self.load()
        data[key] = value
        self.save(data)