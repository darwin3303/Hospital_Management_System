# ADR-006: Strict per-feature database ownership

## Status
Accepted

## Context
Without an explicit rule, it's easy for one feature's service to reach
directly into another feature's table for convenience, creating hidden
coupling that makes the codebase harder to reason about as it grows.

## Decision
A feature writes only to tables it owns. Cross-feature reads go through
the owning feature's service/repository, never direct table access. This
is documented per-feature in docs/architecture.md's module boundaries table.

## Consequences
Changing a feature's internal schema doesn't silently break another
feature, as long as its service interface stays stable. Requires
discipline to maintain as the codebase grows -- not mechanically enforced
by tooling, currently a code-review convention.
