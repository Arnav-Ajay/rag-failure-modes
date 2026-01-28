# policy/hedge_codes.py
from enum import Enum

class HedgeCode(str, Enum):
    CONFLICTING_SOURCES = "conflicting_sources"
    PARTIAL_SUPPORT = "partial_support"
