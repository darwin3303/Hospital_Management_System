def can_document(appointment_status: str) -> bool:
    """R4: diagnosis may be documented while the appointment is SCHEDULED."""
    return appointment_status == "SCHEDULED"


def owns_record(record_doctor_id: str, requesting_doctor_id: str) -> bool:
    """R6: a doctor may only view/edit their own patients' records."""
    return record_doctor_id == requesting_doctor_id
