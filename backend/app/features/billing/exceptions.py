from app.core.errors import ValidationAppError


class PaymentExceedsBalanceError(ValidationAppError):
    code = "PAYMENT_EXCEEDS_BALANCE"

    def __init__(self, outstanding_balance: float):
        super().__init__("Payment amount exceeds the outstanding balance.",
                          details={"outstanding_balance": outstanding_balance})
