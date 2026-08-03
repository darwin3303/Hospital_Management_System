"""
Seeds a complete, realistic demo dataset covering the full clinical/financial
pipeline -- the same chain we walked through manually in Swagger, made
repeatable. Safe to re-run: skips anything that already exists by name.

Usage (from the backend/ folder, with venv active):
    python scripts/seed_demo_data.py
"""
import sys
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.features.auth.models import User
from app.features.staff.models import Department, Employee
from app.features.doctors.models import Doctor, DoctorAvailability
from app.features.patients.models import Patient
from app.features.appointments.models import Appointment
from app.features.pharmacy.models import Medicine

from scripts.seed_admin import seed_admin, DEFAULT_USERNAME, DEFAULT_PASSWORD


def get_or_create_user(db, username, password, role):
    user = db.query(User).filter(User.username == username).first()
    if user:
        return user
    user = User(id=uuid.uuid4(), username=username, password_hash=hash_password(password),
                role=role, is_active=True)
    db.add(user)
    db.flush()
    return user


def get_or_create_department(db, name):
    dept = db.query(Department).filter(Department.name == name).first()
    if dept:
        return dept
    dept = Department(id=uuid.uuid4(), name=name)
    db.add(dept)
    db.flush()
    return dept


def seed_demo_data() -> None:
    seed_admin()  # ensure admin exists first

    db = SessionLocal()
    try:
        dept = get_or_create_department(db, "Cardiology")

        doctor_user = get_or_create_user(db, "drnadeesha", "Doctor@1234", "DOCTOR")
        get_or_create_user(db, "receptionist1", "Reception@1234", "RECEPTIONIST")
        get_or_create_user(db, "labstaff1", "LabStaff@1234", "LAB_STAFF")
        get_or_create_user(db, "pharmacist1", "Pharma@1234", "PHARMACIST")
        get_or_create_user(db, "accountant1", "Account@1234", "ACCOUNTANT")

        employee = db.query(Employee).filter(Employee.user_id == doctor_user.id).first()
        if not employee:
            employee = Employee(id=uuid.uuid4(), user_id=doctor_user.id, department_id=dept.id,
                                 first_name="Nadeesha", last_name="Perera", phone="0771234567",
                                 hired_at=date(2024, 1, 15))
            db.add(employee)
            db.flush()

        doctor = db.query(Doctor).filter(Doctor.employee_id == employee.id).first()
        if not doctor:
            doctor = Doctor(id=uuid.uuid4(), employee_id=employee.id, specialty="Cardiology",
                             consultation_fee=2000)
            db.add(doctor)
            db.flush()
            db.add(DoctorAvailability(id=uuid.uuid4(), doctor_id=doctor.id, day_of_week=0,
                                       start_time="09:00:00", end_time="17:00:00"))

        patient = db.query(Patient).filter(Patient.phone == "0719876543").first()
        if not patient:
            patient = Patient(id=uuid.uuid4(), first_name="Kasun", last_name="Fernando",
                               phone="0719876543", date_of_birth=date(1990, 5, 20),
                               gender="MALE", address="Negombo")
            db.add(patient)
            db.flush()

        appointment = db.query(Appointment).filter(Appointment.patient_id == patient.id).first()
        if not appointment:
            appointment = Appointment(
                id=uuid.uuid4(), patient_id=patient.id, doctor_id=doctor.id,
                scheduled_at=datetime.now() + timedelta(days=3), duration_minutes=30,
                status="SCHEDULED", created_by=doctor_user.id,
            )
            db.add(appointment)

        medicine = db.query(Medicine).filter(Medicine.name == "Atorvastatin 20mg").first()
        if not medicine:
            medicine = Medicine(id=uuid.uuid4(), name="Atorvastatin 20mg", unit_price=45.00,
                                 quantity_in_stock=100, expiry_date=date(2027, 12, 31))
            db.add(medicine)

        db.commit()
        print("Demo data seeded:")
        print(f"  Department: {dept.name} ({dept.id})")
        print(f"  Doctor user: drnadeesha / Doctor@1234  -> doctor_id={doctor.id}")
        print(f"  Patient: Kasun Fernando -> patient_id={patient.id}")
        print(f"  Appointment: {appointment.id} (status={appointment.status})")
        print(f"  Medicine: Atorvastatin 20mg ({medicine.id})")
        print("  Other logins: receptionist1/Reception@1234, labstaff1/LabStaff@1234, "
              "pharmacist1/Pharma@1234, accountant1/Account@1234")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
