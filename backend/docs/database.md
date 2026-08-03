# Database

PostgreSQL, managed via Alembic migrations (`alembic/versions/`).

## Entity relationships

```
User --1:1(optional)-- Employee --1:1(optional)-- Doctor -- DoctorAvailability
                            |
                       Department

Patient -- Document
Patient -- Appointment -- Doctor
                |
          MedicalRecord -- MedicalRecordAmendment
                |
          Prescription -- PrescriptionItem -- Medicine
                |
          LabRequest

Prescription -- PharmacyDispense
Appointment -- Admission
Appointment -- Invoice -- InvoiceLineItem -- Payment

Employee -- Attendance
Employee -- LeaveRequest

(all mutating actions) -- AuditLog
```

## Key design decisions

- **User / Employee / Doctor specialization chain.** `Doctor.employee_id`
  references `Employee`, not `User` directly. A Doctor is a clinical
  specialization of employment; login capability is separate. `Employee.user_id`
  is nullable to support non-login staff.
- **Patient is never a User.** No patient portal in scope.
- **MedicalRecord is 1:1 with Appointment**, enforced via a unique constraint.
  Corrections go through append-only `MedicalRecordAmendment`, never in-place edits.
- **Invoice + InvoiceLineItem** model itemized billing: each line item
  references its source (`CONSULTATION`, `LABORATORY`, `PHARMACY`) via
  `source_type` + `source_id`.
- **AuditLog** captures actor, action, entity, and timestamp for all
  state-changing operations.

## Business rules enforced at the database level

| Rule | Constraint |
|---|---|
| One invoice per appointment | `UNIQUE(appointment_id)` on `invoices` |
| One attendance record per employee per day | `UNIQUE(employee_id, date)` on `attendance` |
| No negative pharmacy stock | `CHECK (quantity_in_stock >= 0)` on `medicines` |
| One active admission per patient | Partial unique index on `admissions(patient_id) WHERE status = 'ACTIVE'` |
| Payment amount positive | `CHECK (amount > 0)` on `payments` |

Rules requiring cross-row reads (overlap checks, state-machine transitions,
ownership checks) live in each feature's `domain.py` and are enforced in
`service.py`. The constraints above are the last line of defense against
races or bypassed application logic.

## Migrations

```powershell
alembic revision --autogenerate -m "description"
alembic upgrade head
```

Always review the generated migration file before running `upgrade` --
autogenerate is a draft, not a guarantee, particularly for partial indexes
and `CHECK` constraints.
