# memory/working.py
"""
Ephemeral, in-memory session context.

Rules:
- Never persist to disk
- Never import EpisodicStore or SemanticStore
- Never bypass MemoryRouter
- Safe to discard between runs
"""

from typing import Any, Dict, List, Optional


class WorkingMemory:
    """
    Short-lived, per-session scratch state.
    Cleared between runs. Not authoritative.
    """

    def __init__(self) -> None:
        # Current objective / intent
        self.goal: Optional[str] = None

        # Step-by-step reasoning artifacts (planner/executor)
        self.thoughts: List[str] = []

        # Temporary tool outputs or cached results
        self.tool_cache: Dict[str, Any] = {}

        # Flags or signals for the current run
        self.flags: Dict[str, bool] = {}

    # ---- Convenience helpers (optional but useful) ----

    def reset(self) -> None:
        """Clear all working state."""
        self.goal = None
        self.thoughts.clear()
        self.tool_cache.clear()
        self.flags.clear()

    def remember(self, key: str, value: Any) -> None:
        """Store temporary data for this run."""
        self.tool_cache[key] = value

    def recall(self, key: str) -> Optional[Any]:
        """Retrieve temporary data if present."""
        return self.tool_cache.get(key)
