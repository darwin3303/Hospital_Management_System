from decimal import Decimal


def outstanding_balance(total_amount: Decimal, payments_sum: Decimal) -> Decimal:
    return total_amount - payments_sum


def can_generate_invoice(appointment_status: str) -> bool:
    """R13: invoice requires a COMPLETED appointment."""
    return appointment_status == "COMPLETED"


def can_accept_payment(amount: Decimal, balance: Decimal) -> bool:
    """R15: payment cannot exceed outstanding balance."""
    return Decimal("0") < amount <= balance


def compute_invoice_status(total_amount: Decimal, payments_sum: Decimal) -> str:
    if payments_sum <= 0:
        return "UNPAID"
    if payments_sum < total_amount:
        return "PARTIALLY_PAID"
    return "PAID"
