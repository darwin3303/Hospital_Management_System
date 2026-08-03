from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.core.pagination import page_params, paginate_meta, PageParams
from app.core.roles import Role
from app.features.auth.models import User
from app.features.staff.schemas import (
    DepartmentCreate, DepartmentOut, EmployeeCreate, EmployeeOut,
    AttendanceMarkRequest, AttendanceOut, LeaveRequestCreate, LeaveDecisionRequest, LeaveRequestOut,
)
from app.features.staff.service import StaffService

router = APIRouter(prefix="/staff", tags=["staff"])


@router.post("/departments", dependencies=[Depends(require_role(Role.ADMIN))])
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    dept = StaffService(db).create_department(payload, current_user)
    return {"success": True, "data": DepartmentOut.model_validate(dept)}


@router.get("/departments")
def list_departments(db: Session = Depends(get_db), _=Depends(get_current_user)):
    depts = StaffService(db).list_departments()
    return {"success": True, "data": [DepartmentOut.model_validate(d) for d in depts]}


@router.post("/employees", dependencies=[Depends(require_role(Role.ADMIN))])
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    emp = StaffService(db).create_employee(payload, current_user)
    return {"success": True, "data": EmployeeOut.model_validate(emp)}


@router.get("/employees", dependencies=[Depends(require_role(Role.ADMIN))])
def list_employees(db: Session = Depends(get_db), pagination: PageParams = Depends(page_params)):
    items, total = StaffService(db).list_employees(pagination.page, pagination.page_size)
    return {"success": True, "data": [EmployeeOut.model_validate(e) for e in items],
            "meta": paginate_meta(pagination.page, pagination.page_size, total)}


@router.get("/employees/{employee_id}", dependencies=[Depends(require_role(Role.ADMIN))])
def get_employee(employee_id: str, db: Session = Depends(get_db)):
    emp = StaffService(db).get_employee(employee_id)
    return {"success": True, "data": EmployeeOut.model_validate(emp)}


@router.post("/attendance")
def mark_attendance(payload: AttendanceMarkRequest, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    record = StaffService(db).mark_attendance(payload.employee_id, payload.status, current_user)
    return {"success": True, "data": AttendanceOut.model_validate(record)}


@router.post("/leave")
def request_leave(payload: LeaveRequestCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    leave = StaffService(db).request_leave(payload, current_user)
    return {"success": True, "data": LeaveRequestOut.model_validate(leave)}


@router.put("/leave/{leave_id}/decision", dependencies=[Depends(require_role(Role.ADMIN))])
def decide_leave(leave_id: str, payload: LeaveDecisionRequest, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    leave = StaffService(db).decide_leave(leave_id, payload.approve, current_user)
    return {"success": True, "data": LeaveRequestOut.model_validate(leave)}


@router.get("/leave/{employee_id}")
def list_leave(employee_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    items = StaffService(db).list_leave_for_employee(employee_id)
    return {"success": True, "data": [LeaveRequestOut.model_validate(l) for l in items]}
