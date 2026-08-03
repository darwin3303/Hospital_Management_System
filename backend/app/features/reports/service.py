"""Reports owns no tables. It reads across other features exclusively
through their repositories/services -- never touching another feature's
table directly with raw SQL, consistent with the strict ownership rule."""
from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.features.patients.models import Patient
from app.features.appointments.models import Appointment
from app.features.billing.models import Invoice, Payment
from app.features.pharmacy.models import Medicine
from app.features.laboratory.models import LabRequest
from app.features.staff.models import Employee


class ReportsService:
    def __init__(self, db: Session):
        self.db = db

    def patients_report(self) -> list[Patient]:
        return list(self.db.scalars(select(Patient)).all())

    def appointments_report(self, status: str | None = None) -> list[Appointment]:
        stmt = select(Appointment)
        if status:
            stmt = stmt.where(Appointment.status == status)
        return list(self.db.scalars(stmt).all())

    def revenue_report(self) -> dict:
        total_invoiced = self.db.scalar(select(func.coalesce(func.sum(Invoice.total_amount), 0))) or Decimal(0)
        total_collected = self.db.scalar(select(func.coalesce(func.sum(Payment.amount), 0))) or Decimal(0)
        return {
            "total_invoiced": float(total_invoiced),
            "total_collected": float(total_collected),
            "outstanding": float(total_invoiced) - float(total_collected),
        }

    def pharmacy_report(self) -> list[Medicine]:
        return list(self.db.scalars(select(Medicine)).all())

    def laboratory_report(self, status: str | None = None) -> list[LabRequest]:
        stmt = select(LabRequest)
        if status:
            stmt = stmt.where(LabRequest.status == status)
        return list(self.db.scalars(stmt).all())

    def staff_report(self) -> list[Employee]:
        return list(self.db.scalars(select(Employee)).all())

    def overview(self) -> dict:
        """A single aggregate endpoint (ADR-005), composed server-side rather
        than requiring the Admin frontend to fire three separate report calls."""
        total_patients = self.db.scalar(select(func.count()).select_from(Patient))
        total_appointments_today = self.db.scalar(
            select(func.count()).select_from(Appointment).where(
                func.date(Appointment.scheduled_at) == func.current_date()
            )
        )
        revenue = self.revenue_report()
        return {
            "total_patients": total_patients,
            "appointments_today": total_appointments_today,
            "revenue": revenue,
        }
