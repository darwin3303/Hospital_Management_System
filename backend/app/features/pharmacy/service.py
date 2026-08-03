import uuid

from sqlalchemy.orm import Session

from app.core.audit import write_audit_log
from app.core.errors import NotFoundError, ConflictError, ValidationAppError
from app.features.auth.models import User
from app.features.emr.repository import EmrRepository
from app.features.pharmacy import domain
from app.features.pharmacy.exceptions import MedicineExpiredError, InsufficientStockError
from app.features.pharmacy.models import Medicine, PharmacyDispense
from app.features.pharmacy.repository import PharmacyRepositoryInterface, SqlAlchemyPharmacyRepository
from app.features.pharmacy.schemas import MedicineCreate, DispenseRequest


class PharmacyService:
    def __init__(self, db: Session, repo: PharmacyRepositoryInterface | None = None):
        self.db = db
        # Defaults to the real SQLAlchemy implementation; tests can inject a fake.
        self.repo = repo or SqlAlchemyPharmacyRepository(db)
        self.emr_repo = EmrRepository(db)

    def add_medicine(self, payload: MedicineCreate, actor: User) -> Medicine:
        medicine = Medicine(id=uuid.uuid4(), **payload.model_dump())
        self.repo.create_medicine(medicine)
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="ADD_MEDICINE", entity_type="Medicine", entity_id=str(medicine.id))
        self.db.commit()
        self.db.refresh(medicine)
        return medicine

    def list_medicines(self) -> list[Medicine]:
        return self.repo.list_medicines()

    def list_pending_prescriptions(self):
        return self.emr_repo.list_pending_prescription_items()

    def dispense(self, payload: DispenseRequest, actor: User) -> PharmacyDispense:
        """
        Transaction boundary (R10):
          BEGIN
            lock prescription item + medicine row
            validate: item PENDING, medicine not expired, stock >= quantity
            decrement stock
            insert dispense record
            update prescription item status
            audit log
          COMMIT
        """
        item = self.emr_repo.get_prescription_item(payload.prescription_item_id)
        if item is None:
            raise NotFoundError("Prescription item not found.", code="PRESCRIPTION_ITEM_NOT_FOUND")
        if not domain.can_dispense(item.status):
            raise ConflictError("This prescription item has already been dispensed.",
                                 code="ALREADY_DISPENSED")

        medicine = self.repo.get_medicine_for_update(str(item.medicine_id))
        if medicine is None:
            raise NotFoundError("Medicine not found.", code="MEDICINE_NOT_FOUND")

        if domain.is_expired(medicine.expiry_date):
            raise MedicineExpiredError()

        if not domain.has_sufficient_stock(medicine.quantity_in_stock, payload.quantity):
            raise InsufficientStockError(available=medicine.quantity_in_stock)

        medicine.quantity_in_stock -= payload.quantity
        dispense = PharmacyDispense(
            id=uuid.uuid4(), prescription_item_id=item.id, dispensed_by=actor.id, quantity=payload.quantity,
        )
        self.repo.create_dispense(dispense)
        item.status = "DISPENSED"

        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="DISPENSE_MEDICINE", entity_type="PharmacyDispense", entity_id=str(dispense.id))
        self.db.commit()
        self.db.refresh(dispense)
        return dispense
