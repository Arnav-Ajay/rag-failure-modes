# memory/router.py
from __future__ import annotations

import json
import os
import time
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from memory.episodic import EpisodicStore
from memory.semantic import SemanticStore
from memory.schemas import MemoryEvent

class MemoryRouter:
    """
    The only place allowed to touch persisted memory.
    Runtime calls this. Planner/Executor do not.
    """

    def __init__(
        self,
        episodic_path: str = "artifacts/memory/episodic.jsonl",
        semantic_path: str = "artifacts/memory/semantic.json",
        events_path: str = "artifacts/memory/events.jsonl",
    ):
        self.episodic = EpisodicStore(episodic_path)
        self.semantic = SemanticStore(semantic_path)
        self.events_path = events_path
        os.makedirs(os.path.dirname(events_path), exist_ok=True)

    def _log_event(self, ev: MemoryEvent) -> None:
        with open(self.events_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(ev), ensure_ascii=False) + "\n")

    # ---- Reads ----
    def read_semantic(self, key: str) -> Optional[Any]:
        val = self.semantic.get(key)
        self._log_event(MemoryEvent(
            ts_utc=time.time(),
            event_type="read",
            store="semantic",
            key=key,
            payload={"found": val is not None},
        ))
        return val

    def read_recent_episodic(self, n: int = 25) -> List[Dict[str, Any]]:
        rows = self.episodic.tail(n=n)
        self._log_event(MemoryEvent(
            ts_utc=time.time(),
            event_type="read",
            store="episodic",
            key=f"tail:{n}",
            payload={"returned": len(rows)},
        ))
        return rows

    # ---- Writes ----
    def write_episodic(self, record: Dict[str, Any]) -> None:
        self.episodic.append(record)
        self._log_event(MemoryEvent(
            ts_utc=time.time(),
            event_type="write",
            store="episodic",
            key="append",
            payload={"keys": sorted(list(record.keys()))[:25]},
        ))

    def write_semantic(self, key: str, value: Any) -> None:
        self.semantic.set(key, value)
        self._log_event(MemoryEvent(
            ts_utc=time.time(),
            event_type="write",
            store="semantic",
            key=key,
            payload={"type": type(value).__name__},
        ))
