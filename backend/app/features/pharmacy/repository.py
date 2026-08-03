from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.pharmacy.models import Medicine, PharmacyDispense


class PharmacyRepositoryInterface(ABC):
    """Abstract interface -- pharmacy stock logic is exactly the kind of rule
    (R10/R11/R12) worth unit-testing against a fake, in-memory implementation."""

    @abstractmethod
    def get_medicine_for_update(self, medicine_id: str) -> Medicine | None: ...

    @abstractmethod
    def create_medicine(self, medicine: Medicine) -> Medicine: ...

    @abstractmethod
    def list_medicines(self) -> list[Medicine]: ...

    @abstractmethod
    def create_dispense(self, dispense: PharmacyDispense) -> PharmacyDispense: ...


class SqlAlchemyPharmacyRepository(PharmacyRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def get_medicine_for_update(self, medicine_id: str) -> Medicine | None:
        # Row lock closes the race window between the stock check and the
        # decrement (two pharmacists dispensing the same low-stock item).
        return self.db.scalar(select(Medicine).where(Medicine.id == medicine_id).with_for_update())

    def create_medicine(self, medicine: Medicine) -> Medicine:
        self.db.add(medicine)
        self.db.flush()
        return medicine

    def list_medicines(self) -> list[Medicine]:
        return list(self.db.scalars(select(Medicine).order_by(Medicine.name)).all())

    def create_dispense(self, dispense: PharmacyDispense) -> PharmacyDispense:
        self.db.add(dispense)
        self.db.flush()
        return dispense
