# policies/retrieval_policy.py
def allow_retrieval(*, wm, episodic_tail):
    """
    Returns:
        - None → do not interfere
        - True → force retrieval
        - False → block retrieval
    """

    # If retrieval happened recently, force retrieval again
    if episodic_tail:
        last = episodic_tail[-1]
        if last.get("used_retrieval") is True:
            return True  # deliberate over-constraint

    return None
