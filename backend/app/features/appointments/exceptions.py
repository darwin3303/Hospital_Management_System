from app.core.errors import ConflictError


class AppointmentOverlapError(ConflictError):
    code = "APPOINTMENT_OVERLAP"

    def __init__(self):
        super().__init__("This doctor already has an appointment in the selected time slot.")
