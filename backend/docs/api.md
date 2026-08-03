# API reference

Base URL: `http://localhost:8000/api/v1`

Full interactive docs (auto-generated from the code, always current):
`http://localhost:8000/docs`

Every response uses the standard envelope:

```json
{ "success": true, "data": ..., "meta": {...optional pagination...} }
```

```json
{ "success": false, "code": "SOME_CODE", "message": "...", "details": {} }
```

This list is generated directly from the live route table (see the code
comment at the bottom) rather than hand-maintained, so it won't drift from
the actual implementation.

## appointments
- `POST /api/v1/appointments` -- book_appointment
- `GET /api/v1/appointments` -- list_appointments
- `PUT /api/v1/appointments/{appointment_id}/cancel` -- cancel_appointment
- `PUT /api/v1/appointments/{appointment_id}/reschedule` -- reschedule_appointment
- `PUT /api/v1/appointments/{appointment_id}/complete` -- complete_appointment
- `PUT /api/v1/appointments/{appointment_id}/no-show` -- no_show_appointment

## auth
- `POST /api/v1/auth/login` -- login
- `GET /api/v1/auth/refresh` -- refresh
- `POST /api/v1/auth/logout` -- logout
- `POST /api/v1/auth/change-password` -- change_password

## billing
- `POST /api/v1/invoices` -- generate_invoice
- `GET /api/v1/invoices/appointment/{appointment_id}` -- get_invoice
- `POST /api/v1/invoices/{invoice_id}/payments` -- record_payment

## doctors
- `POST /api/v1/doctors` -- create_doctor
- `GET /api/v1/doctors` -- list_doctors
- `GET /api/v1/doctors/{doctor_id}` -- get_doctor
- `POST /api/v1/doctors/{doctor_id}/availability` -- add_availability
- `GET /api/v1/doctors/{doctor_id}/availability` -- list_availability

## emr
- `POST /api/v1/medical-records` -- create_medical_record
- `GET /api/v1/medical-records/appointment/{appointment_id}` -- get_by_appointment
- `GET /api/v1/medical-records/patient/{patient_id}/history` -- get_history
- `POST /api/v1/medical-records/{record_id}/amendments` -- add_amendment
- `POST /api/v1/medical-records/{record_id}/prescriptions` -- create_prescription

## inpatient
- `POST /api/v1/admissions` -- admit_patient
- `GET /api/v1/admissions/{admission_id}` -- get_admission
- `PUT /api/v1/admissions/{admission_id}/discharge` -- discharge_patient

## laboratory
- `POST /api/v1/lab-requests` -- create_lab_request
- `GET /api/v1/lab-requests` -- lab_queue
- `GET /api/v1/lab-requests/medical-record/{medical_record_id}` -- list_for_record
- `PUT /api/v1/lab-requests/{request_id}/collect-sample` -- collect_sample
- `PUT /api/v1/lab-requests/{request_id}/enter-result` -- enter_result
- `PUT /api/v1/lab-requests/{request_id}/generate-report` -- generate_report

## patients
- `POST /api/v1/patients` -- register_patient
- `GET /api/v1/patients/search` -- search_patients
- `GET /api/v1/patients/{patient_id}` -- get_patient
- `PUT /api/v1/patients/{patient_id}` -- update_patient
- `POST /api/v1/patients/{patient_id}/documents` -- upload_document
- `GET /api/v1/patients/{patient_id}/documents` -- list_documents
- `GET /api/v1/patients/documents/{document_id}/download` -- download_document

## pharmacy
- `POST /api/v1/pharmacy/medicines` -- add_medicine
- `GET /api/v1/pharmacy/medicines` -- list_medicines
- `GET /api/v1/pharmacy/prescriptions/pending` -- pending_prescriptions
- `POST /api/v1/pharmacy/dispense` -- dispense

## reports
- `GET /api/v1/reports/patients` -- patients_report
- `GET /api/v1/reports/appointments` -- appointments_report
- `GET /api/v1/reports/revenue` -- revenue_report
- `GET /api/v1/reports/pharmacy` -- pharmacy_report
- `GET /api/v1/reports/laboratory` -- laboratory_report
- `GET /api/v1/reports/staff` -- staff_report
- `GET /api/v1/reports/overview` -- overview

## staff
- `POST /api/v1/staff/departments` -- create_department
- `GET /api/v1/staff/departments` -- list_departments
- `POST /api/v1/staff/employees` -- create_employee
- `GET /api/v1/staff/employees` -- list_employees
- `GET /api/v1/staff/employees/{employee_id}` -- get_employee
- `POST /api/v1/staff/attendance` -- mark_attendance
- `POST /api/v1/staff/leave` -- request_leave
- `PUT /api/v1/staff/leave/{leave_id}/decision` -- decide_leave
- `GET /api/v1/staff/leave/{employee_id}` -- list_leave

## users
- `POST /api/v1/users` -- create_user
- `GET /api/v1/users` -- list_users
- `PUT /api/v1/users/{user_id}/status` -- set_user_status

---

To regenerate this list after adding/changing endpoints:

```python
from app.main import app
from collections import defaultdict

by_tag = defaultdict(list)
for route in app.routes:
    if not hasattr(route, 'path') or not route.path.startswith('/api'):
        continue
    tags = getattr(route, 'tags', ['other'])
    for m in sorted(route.methods - {'HEAD'}):
        by_tag[tags[0]].append((m, route.path, route.name))

for tag in sorted(by_tag):
    print(f'## {tag}')
    for m, path, name in by_tag[tag]:
        print(f'- `{m} {path}` -- {name}')
```
