from datetime import date as date_type

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.staff.models import Department, Employee, Attendance, LeaveRequest


class StaffRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_department(self, dept: Department) -> Department:
        self.db.add(dept)
        self.db.flush()
        return dept

    def list_departments(self) -> list[Department]:
        return list(self.db.scalars(select(Department).order_by(Department.name)).all())

    def get_department(self, dept_id: str) -> Department | None:
        return self.db.get(Department, dept_id)

    def create_employee(self, emp: Employee) -> Employee:
        self.db.add(emp)
        self.db.flush()
        return emp

    def get_employee(self, employee_id: str) -> Employee | None:
        return self.db.get(Employee, employee_id)

    def list_employees(self, page: int, page_size: int) -> tuple[list[Employee], int]:
        from sqlalchemy import func
        items = self.db.scalars(
            select(Employee).order_by(Employee.last_name).offset((page - 1) * page_size).limit(page_size)
        ).all()
        total = self.db.scalar(select(func.count()).select_from(Employee))
        return list(items), total

    def get_attendance_for_day(self, employee_id: str, day: date_type) -> Attendance | None:
        return self.db.scalar(
            select(Attendance).where(Attendance.employee_id == employee_id, Attendance.date == day)
        )

    def create_attendance(self, record: Attendance) -> Attendance:
        self.db.add(record)
        self.db.flush()
        return record

    def create_leave_request(self, leave: LeaveRequest) -> LeaveRequest:
        self.db.add(leave)
        self.db.flush()
        return leave

    def get_leave_request(self, leave_id: str) -> LeaveRequest | None:
        return self.db.get(LeaveRequest, leave_id)

    def list_leave_requests_for_employee(self, employee_id: str) -> list[LeaveRequest]:
        return list(self.db.scalars(
            select(LeaveRequest).where(LeaveRequest.employee_id == employee_id)
            .order_by(LeaveRequest.created_at.desc())
        ).all())
