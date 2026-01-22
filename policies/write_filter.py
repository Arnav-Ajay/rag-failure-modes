# policies/write_filter.py
ALLOWED_SEMANTIC_KEYS = {
    "last_user_question",
    "last_answer_preview",
}

def allow_semantic_write(key, value, *, wm, episodic_tail):
    """
    Returns True if the semantic write is allowed.
    """

    # Block unknown keys
    if key not in ALLOWED_SEMANTIC_KEYS:
        return False

    # Block large payloads
    if isinstance(value, str) and len(value) > 500:
        return False

    return True