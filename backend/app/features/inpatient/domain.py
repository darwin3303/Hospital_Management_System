def can_discharge(status: str, has_discharge_record: bool) -> bool:
    """R19: discharge requires a valid medical record as summary."""
    return status == "ACTIVE" and has_discharge_record
