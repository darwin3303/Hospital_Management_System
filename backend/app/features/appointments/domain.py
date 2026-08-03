"""Pure business rules for appointments. No SQLAlchemy/FastAPI imports."""
from datetime import datetime, timedelta

ACTIVE_STATUSES = {"SCHEDULED"}


def ranges_overlap(start_a: datetime, end_a: datetime, start_b: datetime, end_b: datetime) -> bool:
    return start_a < end_b and start_b < end_a


def has_overlap(new_start: datetime, new_duration_minutes: int, existing_appointments: list[dict]) -> bool:
    """R1: an appointment may not overlap another SCHEDULED appointment for the same doctor.
    existing_appointments: list of {"scheduled_at": dt, "duration_minutes": int, "status": str}."""
    new_end = new_start + timedelta(minutes=new_duration_minutes)
    for appt in existing_appointments:
        if appt["status"] not in ACTIVE_STATUSES:
            continue
        existing_end = appt["scheduled_at"] + timedelta(minutes=appt["duration_minutes"])
        if ranges_overlap(new_start, new_end, appt["scheduled_at"], existing_end):
            return True
    return False


def can_cancel_or_reschedule(status: str) -> bool:
    """R2: only SCHEDULED appointments may be cancelled or rescheduled."""
    return status == "SCHEDULED"


def can_complete(status: str, has_medical_record: bool) -> bool:
    """R3: completion requires an existing medical record."""
    return status == "SCHEDULED" and has_medical_record


def can_mark_no_show(status: str) -> bool:
    return status == "SCHEDULED"
