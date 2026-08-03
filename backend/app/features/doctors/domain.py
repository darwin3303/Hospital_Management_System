"""R7: a Doctor profile may only be linked to an Employee whose User role is DOCTOR."""


def can_link_doctor(employee_user_role: str | None) -> bool:
    return employee_user_role == "DOCTOR"
