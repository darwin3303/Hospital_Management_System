from datetime import date, timedelta

from app.features.pharmacy import domain


def test_sufficient_stock():
    assert domain.has_sufficient_stock(10, 5) is True
    assert domain.has_sufficient_stock(3, 5) is False


def test_expiry_check():
    yesterday = date.today() - timedelta(days=1)
    tomorrow = date.today() + timedelta(days=1)
    assert domain.is_expired(yesterday) is True
    assert domain.is_expired(tomorrow) is False


def test_can_dispense_only_pending():
    assert domain.can_dispense("PENDING") is True
    assert domain.can_dispense("DISPENSED") is False
