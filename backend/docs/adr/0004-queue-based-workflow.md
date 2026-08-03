# ADR-004: Queue-based worklists from day one

## Status
Accepted

## Context
Doctor, Laboratory, and Pharmacist roles need to find their pending work
without manually looking up or pasting record IDs.

## Decision
Build denormalized, filterable list endpoints for each of these roles
from the start (Doctor Queue, Lab Queue, Pharmacy dispense queue), using
SQLAlchemy eager loading to avoid N+1 queries, rather than treating this
as a later enhancement.

## Consequences
Slightly more upfront work per feature (an extra query method + endpoint),
but the resulting UX is dramatically better for the roles that use these
screens daily, and better matches how these tasks are done in a real
clinical setting.
