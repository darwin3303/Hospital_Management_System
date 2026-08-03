# ADR-007: Audit logging is synchronous and transactional

## Status
Accepted

## Context
Audit records need to be trustworthy -- an audit log entry that exists
without its corresponding action having actually happened (or vice versa)
undermines the entire point of auditing.

## Decision
Every state-changing service method writes its AuditLog row as part of
the same database transaction as the business operation itself, not via
a background task or async event.

## Consequences
Audit log writes cannot silently fail independently of the action they
describe -- they succeed or roll back together. Adds a small amount of
write overhead to every mutating call, judged worth it for an audit
trail on clinical/financial data.
