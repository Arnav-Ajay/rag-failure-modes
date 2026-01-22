# memory/schema.py
from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class MemoryEvent:
    ts_utc: float
    event_type: str  # "read" | "write"
    store: str       # "episodic" | "semantic"
    key: str
    payload: Dict[str, Any]