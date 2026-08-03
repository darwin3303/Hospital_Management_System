# ADR-011: Feature-specific exception classes

## Status
Accepted (post-v1 addition)

## Context
V1 raised the shared AppError subclasses (ConflictError, ValidationAppError,
etc.) directly with an inline `code=` string per call site, e.g.
`raise ValidationAppError("...", code="MEDICINE_EXPIRED")`. This works but
scatters a feature's error vocabulary across its service.py as string
literals, which are easy to typo and hard to grep for all at once.

## Decision
Each feature that has domain-specific error conditions gets its own
exceptions.py defining named subclasses of the shared base errors, e.g.
`pharmacy/exceptions.py` defines `MedicineExpiredError(ValidationAppError)`.
Services raise `raise MedicineExpiredError()` instead of the inline-code
form. The shared AppError base and generic subclasses (NotFoundError,
ConflictError, etc.) stay in core/errors.py unchanged.

## Consequences
A feature's full error vocabulary is visible in one file. Slightly more
files, but each is small and mechanical. Existing inline-code call sites
are migrated feature-by-feature, not all at once -- both forms may
coexist temporarily during that migration without breaking anything,
since both ultimately raise an AppError the global handler already knows
how to translate.
