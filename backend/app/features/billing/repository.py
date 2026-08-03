from abc import ABC, abstractmethod
from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.features.billing.models import Invoice, InvoiceLineItem, Payment


class BillingRepositoryInterface(ABC):
    """Interface introduced for the same reason as pharmacy's: billing's
    aggregation and balance logic benefits from fake-backed unit tests."""

    @abstractmethod
    def get_by_appointment(self, appointment_id: str) -> Invoice | None: ...

    @abstractmethod
    def create_invoice(self, invoice: Invoice) -> Invoice: ...

    @abstractmethod
    def add_line_item(self, item: InvoiceLineItem) -> InvoiceLineItem: ...

    @abstractmethod
    def get_invoice_for_update(self, invoice_id: str) -> Invoice | None: ...

    @abstractmethod
    def sum_payments(self, invoice_id: str) -> Decimal: ...

    @abstractmethod
    def create_payment(self, payment: Payment) -> Payment: ...

    @abstractmethod
    def list_line_items(self, invoice_id: str) -> list[InvoiceLineItem]: ...


class SqlAlchemyBillingRepository(BillingRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def get_by_appointment(self, appointment_id: str) -> Invoice | None:
        return self.db.scalar(select(Invoice).where(Invoice.appointment_id == appointment_id))

    def create_invoice(self, invoice: Invoice) -> Invoice:
        self.db.add(invoice)
        try:
            self.db.flush()
        except IntegrityError:
            # R14 backstop: unique constraint on appointment_id catches a
            # concurrent double-invoice attempt that slipped past the app check.
            self.db.rollback()
            raise
        return invoice

    def add_line_item(self, item: InvoiceLineItem) -> InvoiceLineItem:
        self.db.add(item)
        self.db.flush()
        return item

    def get_invoice_for_update(self, invoice_id: str) -> Invoice | None:
        return self.db.scalar(select(Invoice).where(Invoice.id == invoice_id).with_for_update())

    def sum_payments(self, invoice_id: str) -> Decimal:
        total = self.db.scalar(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.invoice_id == invoice_id)
        )
        return Decimal(total)

    def create_payment(self, payment: Payment) -> Payment:
        self.db.add(payment)
        self.db.flush()
        return payment

    def list_line_items(self, invoice_id: str) -> list[InvoiceLineItem]:
        return list(self.db.scalars(
            select(InvoiceLineItem).where(InvoiceLineItem.invoice_id == invoice_id)
        ).all())
