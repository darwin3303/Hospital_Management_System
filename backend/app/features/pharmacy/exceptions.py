from app.core.errors import ValidationAppError


class MedicineExpiredError(ValidationAppError):
    code = "MEDICINE_EXPIRED"

    def __init__(self):
        super().__init__("This medicine has expired and cannot be dispensed.")


class InsufficientStockError(ValidationAppError):
    code = "INSUFFICIENT_STOCK"

    def __init__(self, available: int):
        super().__init__("Insufficient stock to fulfill this quantity.", details={"available": available})
