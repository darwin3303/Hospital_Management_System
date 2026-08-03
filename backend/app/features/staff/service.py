import uuid
from datetime import date, datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.audit import write_audit_log
from app.core.errors import NotFoundError, ConflictError, ValidationAppError
from app.features.auth.models import User
from app.features.staff import domain
from app.features.staff.models import Department, Employee, Attendance, LeaveRequest
from app.features.staff.repository import StaffRepository
from app.features.staff.schemas import DepartmentCreate, EmployeeCreate, LeaveRequestCreate


class StaffService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = StaffRepository(db)

    def create_department(self, payload: DepartmentCreate, actor: User) -> Department:
        dept = Department(id=uuid.uuid4(), name=payload.name)
        try:
            self.repo.create_department(dept)
        except IntegrityError:
            self.db.rollback()
            raise ConflictError("A department with this name already exists.", code="DEPARTMENT_NAME_TAKEN")
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="CREATE_DEPARTMENT", entity_type="Department", entity_id=str(dept.id))
        self.db.commit()
        self.db.refresh(dept)
        return dept

    def list_departments(self) -> list[Department]:
        return self.repo.list_departments()

    def create_employee(self, payload: EmployeeCreate, actor: User) -> Employee:
        if self.repo.get_department(payload.department_id) is None:
            raise NotFoundError("Department not found.", code="DEPARTMENT_NOT_FOUND")

        emp = Employee(
            id=uuid.uuid4(),
            user_id=payload.user_id,
            department_id=payload.department_id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            phone=payload.phone,
            hired_at=payload.hired_at or date.today(),
        )
        self.repo.create_employee(emp)
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="CREATE_EMPLOYEE", entity_type="Employee", entity_id=str(emp.id))
        self.db.commit()
        self.db.refresh(emp)
        return emp

    def get_employee(self, employee_id: str) -> Employee:
        emp = self.repo.get_employee(employee_id)
        if emp is None:
            raise NotFoundError("Employee not found.", code="EMPLOYEE_NOT_FOUND")
        return emp

    def list_employees(self, page: int, page_size: int) -> tuple[list[Employee], int]:
        return self.repo.list_employees(page, page_size)

    # ---- Attendance -----------------------------------------------------

    def mark_attendance(self, employee_id: str, status: str, actor: User) -> Attendance:
        if self.repo.get_employee(employee_id) is None:
            raise NotFoundError("Employee not found.", code="EMPLOYEE_NOT_FOUND")

        today = date.today()
        existing = self.repo.get_attendance_for_day(employee_id, today)
        if not domain.can_mark_attendance(existing):
            raise ConflictError("Attendance for this employee has already been marked today.",
                                 code="ATTENDANCE_ALREADY_MARKED")

        record = Attendance(id=uuid.uuid4(), employee_id=employee_id, date=today, status=status)
        self.repo.create_attendance(record)
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="MARK_ATTENDANCE", entity_type="Attendance", entity_id=str(record.id))
        self.db.commit()
        self.db.refresh(record)
        return record

    # ---- Leave ------------------------------------------------------------

    def request_leave(self, payload: LeaveRequestCreate, actor: User) -> LeaveRequest:
        if payload.end_date < payload.start_date:
            raise ValidationAppError("End date cannot be before start date.", code="INVALID_LEAVE_RANGE")
        if self.repo.get_employee(payload.employee_id) is None:
            raise NotFoundError("Employee not found.", code="EMPLOYEE_NOT_FOUND")

        leave = LeaveRequest(
            id=uuid.uuid4(),
            employee_id=payload.employee_id,
            start_date=payload.start_date,
            end_date=payload.end_date,
            reason=payload.reason,
            status="PENDING",
        )
        self.repo.create_leave_request(leave)
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="REQUEST_LEAVE", entity_type="LeaveRequest", entity_id=str(leave.id))
        self.db.commit()
        self.db.refresh(leave)
        return leave

    def decide_leave(self, leave_id: str, approve: bool, actor: User) -> LeaveRequest:
        leave = self.repo.get_leave_request(leave_id)
        if leave is None:
            raise NotFoundError("Leave request not found.", code="LEAVE_REQUEST_NOT_FOUND")
        if not domain.can_decide_leave(leave.status):
            raise ConflictError("This leave request has already been decided.", code="LEAVE_ALREADY_DECIDED")

        leave.status = "APPROVED" if approve else "REJECTED"
        leave.decided_by = actor.id
        leave.decided_at = datetime.now(timezone.utc)
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="DECIDE_LEAVE", entity_type="LeaveRequest", entity_id=str(leave.id))
        self.db.commit()
        self.db.refresh(leave)
        return leave

    def list_leave_for_employee(self, employee_id: str) -> list[LeaveRequest]:
        return self.repo.list_leave_requests_for_employee(employee_id)