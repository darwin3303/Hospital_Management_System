def can_mark_attendance(existing_record_for_day) -> bool:
    """R16: one attendance record per employee per day."""
    return existing_record_for_day is None


def can_decide_leave(current_status: str) -> bool:
    """R17: a leave request may only be decided once."""
    return current_status == "PENDING"
