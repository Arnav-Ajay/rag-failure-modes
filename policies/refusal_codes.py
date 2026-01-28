# policy/refusal_codes.py
from enum import Enum

class RefusalCode(str, Enum):
    NO_EVIDENCE = "no_evidence"
    INSUFFICIENT_COVERAGE = "insufficient_coverage"
    CONFLICTING_EVIDENCE = "conflicting_evidence"
    PARAMETRIC_NOT_ALLOWED = "parametric_not_allowed"
