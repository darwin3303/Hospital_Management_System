# ADR-010: Standard error envelope via a single global exception handler

## Status
Accepted

## Context
Without a shared convention, different endpoints tend to return
inconsistent error shapes, which pushes error-handling complexity onto
every frontend call site.

## Decision
Every service raises a shared AppError (or a feature-specific subclass,
see the exceptions.py files introduced after v1) rather than a raw
HTTPException. A single FastAPI exception handler translates any AppError
into the standard envelope: `{success, code, message, details}`.

## Consequences
The frontend can handle errors generically in one place (see
ErrorAlert.tsx) rather than per-endpoint. Requires every service to raise
AppError subclasses rather than reaching for a quick HTTPException --
enforced by convention and code review, not the type system.
