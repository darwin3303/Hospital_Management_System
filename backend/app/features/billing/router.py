from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.core.roles import Role
from app.features.auth.models import User
from app.features.billing.schemas import InvoiceGenerateRequest, InvoiceOut, LineItemOut, PaymentRequest, PaymentOut
from app.features.billing.service import BillingService

router = APIRouter(prefix="/invoices", tags=["billing"])


def _to_invoice_out(service: BillingService, invoice) -> InvoiceOut:
    items = service.get_line_items(str(invoice.id))
    data = InvoiceOut.model_validate(invoice)
    data.line_items = [LineItemOut.model_validate(i) for i in items]
    return data


@router.post("", dependencies=[Depends(require_role(Role.ACCOUNTANT, Role.ADMIN))])
def generate_invoice(payload: InvoiceGenerateRequest, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    service = BillingService(db)
    invoice = service.generate_invoice(payload.appointment_id, current_user)
    return {"success": True, "data": _to_invoice_out(service, invoice)}


@router.get("/appointment/{appointment_id}")
def get_invoice(appointment_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    service = BillingService(db)
    invoice = service.get_by_appointment(appointment_id)
    return {"success": True, "data": _to_invoice_out(service, invoice)}


@router.post("/{invoice_id}/payments", dependencies=[Depends(require_role(Role.ACCOUNTANT, Role.ADMIN))])
def record_payment(invoice_id: str, payload: PaymentRequest, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    payment = BillingService(db).record_payment(invoice_id, payload, current_user)
    return {"success": True, "data": PaymentOut.model_validate(payment)}
