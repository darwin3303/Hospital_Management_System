# Architecture

## Principles

1. Feature-first organization -- code is grouped by workflow capability, not technical layer
2. Business rules are framework-independent -- `domain.py` never imports FastAPI or SQLAlchemy
3. Thin routers, rich services -- routers validate shape and delegate; services own logic
4. Explicit, not incidental, coupling -- cross-feature reads are declared, never silent
5. Database integrity enforced at multiple layers -- application rules + constraints as backstop
6. Security by default -- auth, RBAC, ownership checks, and audit logging are present from the first commit
7. Workflow-driven, not CRUD-driven -- the clinical/financial pipeline is the organizing unit

## Layout

Each feature under `app/features/<name>/` contains:

```
domain.py       # entities, value objects, pure business rules -- no SQLAlchemy, no FastAPI
schemas.py       # Pydantic request/response models
service.py       # use-case orchestration, calls domain + repository
repository.py    # data access -- SQLAlchemy queries, only place ORM is used
router.py        # FastAPI routes, thin, delegates to service.py
models.py        # SQLAlchemy table definitions
exceptions.py     # feature-specific AppError subclasses (added post-v1)
```

Repository interfaces (abstract base classes) are introduced only where they
provide real value for testability -- currently `pharmacy` and `billing`.
Simple lookup-heavy repositories are implemented directly.

## Module boundaries

| Feature | Owns | May read | Must not modify |
|---|---|---|---|
| `auth` | users, refresh_tokens | -- | any clinical/financial data |
| `staff` | departments, employees, attendance, leave_requests | auth | appointments, billing |
| `doctors` | doctors, doctor_availability | staff | appointments, emr |
| `patients` | patients, documents | -- | appointments, emr, billing |
| `appointments` | appointments | doctors, patients, emr | emr, laboratory, pharmacy, billing |
| `emr` | medical_records, amendments, prescriptions, prescription_items | appointments, patients, doctors | laboratory, pharmacy, billing |
| `laboratory` | lab_requests | emr | pharmacy, billing |
| `pharmacy` | medicines, pharmacy_dispenses | emr | billing, laboratory |
| `billing` | invoices, invoice_line_items, payments | appointments, laboratory, pharmacy | laboratory, pharmacy, emr |
| `inpatient` | admissions | patients, emr | billing |
| `reports` | none (read-only) | all features | everything |

A feature may **read** another feature's data through its public service
interface, never its repository directly. A feature may only **write** to
tables it owns.

## Domain events (conceptual)

No message broker. These are documented to clarify workflow boundaries and
handled as direct synchronous calls today:

`PatientRegistered`, `AppointmentBooked`, `AppointmentCompleted`,
`MedicalRecordCreated`, `LabResultGenerated`, `PrescriptionDispensed`,
`InvoiceGenerated`, `PaymentRecorded`, `RefreshTokenRevoked`.

## Error handling

Every endpoint returns one consistent envelope:

```json
{
  "success": false,
  "code": "APPOINTMENT_OVERLAP",
  "message": "...",
  "details": {}
}
```

A single FastAPI exception handler translates any `AppError` subclass
(raised from a service) into this envelope. See `docs/adr/` for the
decision record.

## Security

- Password hashing: bcrypt
- Access tokens: JWT, short-lived, held in-memory on the frontend only
- Refresh tokens: httpOnly cookie, server-tracked in `refresh_tokens` for real revocation
- RBAC: `require_role()` FastAPI dependency, backed by a shared `Role` enum
- Ownership checks: a second dependency layer beyond role (e.g. doctor scoping on EMR)
- Audit logging: every state-changing service call writes an `AuditLog` row inside the same transaction as the action
