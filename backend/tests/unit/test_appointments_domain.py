from datetime import datetime

from app.features.appointments import domain


def test_no_overlap_when_no_existing_appointments():
    start = datetime(2026, 8, 10, 9, 0)
    assert domain.has_overlap(start, 30, []) is False


def test_detects_direct_overlap():
    start = datetime(2026, 8, 10, 9, 0)
    existing = [{"scheduled_at": datetime(2026, 8, 10, 9, 15), "duration_minutes": 30, "status": "SCHEDULED"}]
    assert domain.has_overlap(start, 30, existing) is True


def test_back_to_back_appointments_do_not_overlap():
    start = datetime(2026, 8, 10, 9, 30)
    existing = [{"scheduled_at": datetime(2026, 8, 10, 9, 0), "duration_minutes": 30, "status": "SCHEDULED"}]
    assert domain.has_overlap(start, 30, existing) is False


def test_cancelled_appointments_are_ignored():
    start = datetime(2026, 8, 10, 9, 0)
    existing = [{"scheduled_at": datetime(2026, 8, 10, 9, 0), "duration_minutes": 30, "status": "CANCELLED"}]
    assert domain.has_overlap(start, 30, existing) is False


def test_can_complete_requires_scheduled_and_record():
    assert domain.can_complete("SCHEDULED", True) is True
    assert domain.can_complete("SCHEDULED", False) is False
    assert domain.can_complete("COMPLETED", True) is False
