from datetime import date


def has_sufficient_stock(quantity_in_stock: int, requested_quantity: int) -> bool:
    """R11: no negative stock."""
    return quantity_in_stock >= requested_quantity


def is_expired(expiry_date: date, as_of: date | None = None) -> bool:
    """R12: cannot dispense expired medicine."""
    as_of = as_of or date.today()
    return expiry_date < as_of


def can_dispense(item_status: str) -> bool:
    return item_status == "PENDING"
