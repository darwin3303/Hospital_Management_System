import uuid
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.audit import write_audit_log
from app.core.errors import NotFoundError, ConflictError, ValidationAppError
from app.features.appointments.repository import AppointmentRepository
from app.features.auth.models import User
from app.features.billing import domain
from app.features.billing.exceptions import PaymentExceedsBalanceError
from app.features.billing.models import Invoice, InvoiceLineItem, Payment
from app.features.billing.repository import BillingRepositoryInterface, SqlAlchemyBillingRepository
from app.features.billing.schemas import PaymentRequest
from app.features.doctors.repository import DoctorRepository
from app.features.emr.repository import EmrRepository
from app.features.laboratory.repository import LaboratoryRepository
from app.features.pharmacy.repository import SqlAlchemyPharmacyRepository

# Flat fee applied per completed lab test; the specification does not define
# a per-test price field, so a single configurable rate is used here.
LAB_TEST_FEE = Decimal("1500.00")


class BillingService:
    def __init__(self, db: Session, repo: BillingRepositoryInterface | None = None):
        self.db = db
        self.repo = repo or SqlAlchemyBillingRepository(db)
        self.appt_repo = AppointmentRepository(db)
        self.doctor_repo = DoctorRepository(db)
        self.emr_repo = EmrRepository(db)
        self.lab_repo = LaboratoryRepository(db)
        self.pharmacy_repo = SqlAlchemyPharmacyRepository(db)

    def generate_invoice(self, appointment_id: str, actor: User) -> Invoice:
        """
        Transaction boundary (billing generation):
          BEGIN
            validate appointment COMPLETED
            gather billable items: consultation fee, completed lab tests, dispensed pharmacy items
            insert invoice (unique appointment_id -- guards concurrent double-invoice)
            insert line items
            audit log
          COMMIT
        """
        appt = self.appt_repo.get(appointment_id)
        if appt is None:
            raise NotFoundError("Appointment not found.", code="APPOINTMENT_NOT_FOUND")
        if not domain.can_generate_invoice(appt.status):
            raise ValidationAppError("Invoice can only be generated for a completed appointment.",
                                      code="APPOINTMENT_NOT_COMPLETED")
        if self.repo.get_by_appointment(appointment_id) is not None:
            raise ConflictError("An invoice already exists for this appointment.",
                                 code="INVOICE_ALREADY_EXISTS")

        doctor = self.doctor_repo.get(str(appt.doctor_id))
        record = self.emr_repo.get_by_appointment(appointment_id)

        line_items_data = []
        total = Decimal("0")

        if doctor:
            fee = Decimal(str(doctor.consultation_fee))
            line_items_data.append(("CONSULTATION", appt.id, "Consultation fee", fee))
            total += fee

        if record:
            for lab in self.lab_repo.list_for_medical_record(str(record.id)):
                if lab.status == "REPORT_GENERATED":
                    line_items_data.append(("LABORATORY", lab.id, f"Lab test: {lab.test_name}", LAB_TEST_FEE))
                    total += LAB_TEST_FEE

            # Pharmacy line items: walk this record's prescriptions -> items -> dispensed only
            from app.features.emr.models import Prescription, PrescriptionItem
            from app.features.pharmacy.models import Medicine
            from sqlalchemy import select
            prescriptions = self.db.scalars(
                select(Prescription).where(Prescription.medical_record_id == record.id)
            ).all()
            for presc in prescriptions:
                items = self.db.scalars(
                    select(PrescriptionItem).where(
                        PrescriptionItem.prescription_id == presc.id,
                        PrescriptionItem.status == "DISPENSED",
                    )
                ).all()
                for item in items:
                    medicine = self.db.get(Medicine, item.medicine_id)
                    if medicine:
                        amount = Decimal(str(medicine.unit_price)) * item.quantity
                        line_items_data.append(("PHARMACY", item.id, f"Medicine: {medicine.name}", amount))
                        total += amount

        invoice = Invoice(id=uuid.uuid4(), appointment_id=appointment_id, total_amount=total,
                           status="UNPAID", generated_by=actor.id)
        try:
            self.repo.create_invoice(invoice)
        except IntegrityError:
            raise ConflictError("An invoice already exists for this appointment.", code="INVOICE_ALREADY_EXISTS")

        for source_type, source_id, description, amount in line_items_data:
            self.repo.add_line_item(InvoiceLineItem(
                id=uuid.uuid4(), invoice_id=invoice.id, source_type=source_type,
                source_id=source_id, description=description, amount=amount,
            ))

        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="GENERATE_INVOICE", entity_type="Invoice", entity_id=str(invoice.id))
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def get_by_appointment(self, appointment_id: str) -> Invoice:
        invoice = self.repo.get_by_appointment(appointment_id)
        if invoice is None:
            raise NotFoundError("Invoice not found.", code="INVOICE_NOT_FOUND")
        return invoice

    def get_line_items(self, invoice_id: str) -> list[InvoiceLineItem]:
        return self.repo.list_line_items(invoice_id)

    def record_payment(self, invoice_id: str, payload: PaymentRequest, actor: User) -> Payment:
        """
        Transaction boundary (payment recording):
          BEGIN
            lock invoice row
            compute outstanding balance
            validate amount within balance (R15)
            insert payment
            update invoice status
            audit log
          COMMIT
        """
        invoice = self.repo.get_invoice_for_update(invoice_id)
        if invoice is None:
            raise NotFoundError("Invoice not found.", code="INVOICE_NOT_FOUND")

        payments_sum = self.repo.sum_payments(invoice_id)
        balance = domain.outstanding_balance(Decimal(str(invoice.total_amount)), payments_sum)
        amount = Decimal(str(payload.amount))

        if not domain.can_accept_payment(amount, balance):
            raise PaymentExceedsBalanceError(outstanding_balance=float(balance))

        payment = Payment(id=uuid.uuid4(), invoice_id=invoice_id, amount=amount,
                           method=payload.method, recorded_by=actor.id)
        self.repo.create_payment(payment)

        new_sum = payments_sum + amount
        invoice.status = domain.compute_invoice_status(Decimal(str(invoice.total_amount)), new_sum)

        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="RECORD_PAYMENT", entity_type="Payment", entity_id=str(payment.id))
        self.db.commit()
        self.db.refresh(payment)
        return payment
