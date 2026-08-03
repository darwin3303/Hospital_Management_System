"""R9: lab requests follow a strict one-directional state machine."""

VALID_TRANSITIONS = {
    "REQUESTED": {"SAMPLE_COLLECTED"},
    "SAMPLE_COLLECTED": {"RESULT_ENTERED"},
    "RESULT_ENTERED": {"REPORT_GENERATED"},
    "REPORT_GENERATED": set(),
}


def can_transition(current_status: str, target_status: str) -> bool:
    return target_status in VALID_TRANSITIONS.get(current_status, set())
