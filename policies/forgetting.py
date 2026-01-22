# policies/forgetting.py
def apply_forgetting(episodic_records, *, max_records=50):
    """
    Returns a pruned list of episodic records.
    """

    if len(episodic_records) <= max_records:
        return episodic_records

    # Drop oldest records
    return episodic_records[-max_records:]
