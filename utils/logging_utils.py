# utils/logging_utils.py
import json
import os
from typing import Any, Dict

LOG_PATH = os.path.join("logs", "traces.jsonl")


def _ensure_logs_dir() -> None:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)


def write_trace(event: Dict[str, Any]) -> None:
    """
    Append a single structured trace event to disk.

    This function is intentionally dumb:
    - no validation
    - no interpretation
    - no formatting logic
    """
    _ensure_logs_dir()
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
