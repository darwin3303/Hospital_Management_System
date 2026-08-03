# ADR-009: Caching intentionally deferred

## Status
Accepted

## Context
An application-level cache adds complexity and a class of staleness bugs
that are hard to justify at this project's scale and correctness
requirements (clinical/financial data).

## Decision
No caching layer. Rely on Postgres's own query planning plus the indexing
strategy documented in docs/database.md.

## Consequences
Simpler system, fewer failure modes. Revisit only if a specific query
pattern is measured to be a genuine bottleneck -- not before.
