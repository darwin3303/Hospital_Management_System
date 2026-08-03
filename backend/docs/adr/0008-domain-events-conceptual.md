# ADR-008: Domain events documented conceptually, not implemented as a bus

## Status
Accepted

## Context
Naming key workflow events (AppointmentCompleted, PrescriptionDispensed,
etc.) clarifies boundaries even without a message broker, which would be
disproportionate infrastructure for this project's scale.

## Decision
Document the conceptual domain events in docs/architecture.md. Implement
them today as plain, direct function/service calls within the same
transaction -- e.g. appointments.service.complete() directly calls
emr.service.has_record_for(...).

## Consequences
No operational complexity from a broker (Kafka, etc.) that the project
doesn't need. If async processing is ever justified later, the documented
event names mark the exact seam where an outbox pattern could be
introduced without redesigning the workflow.
