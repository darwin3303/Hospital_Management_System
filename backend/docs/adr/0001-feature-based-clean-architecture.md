# ADR-001: Feature-Based Clean Architecture

## Status
Accepted

## Context
Needed an architecture that enforces separation of concerns (business rules
independent of framework/ORM) while staying practical for a one-week
project. Full Hexagonal Architecture was considered but judged to add more
ceremony than the project's scope justifies.

## Decision
Organize code by feature first (patients/, appointments/, billing/, etc.),
with a consistent internal layering per feature: domain -> service ->
repository -> router. Business rules live in domain.py, which imports
nothing from FastAPI or SQLAlchemy.

## Consequences
Related logic stays physically together. Cross-feature dependencies must be
explicit (a feature reads another only through its service, never its
repository). Slightly more boilerplate per feature than a flat layered
structure, in exchange for testable, framework-independent business logic.
