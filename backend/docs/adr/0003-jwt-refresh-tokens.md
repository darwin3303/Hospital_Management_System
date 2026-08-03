# ADR-003: JWT access tokens + server-tracked refresh tokens

## Status
Accepted

## Context
Needed stateless request authentication with the ability to actually
revoke a session before its natural expiry (e.g. staff offboarding).

## Decision
Short-lived JWT access tokens (default 30 min), held in memory on the
frontend only, never localStorage. Refresh tokens delivered via httpOnly
cookie and additionally tracked server-side (hashed, in a refresh_tokens
table with a revoked_at column), enabling real revocation.

## Consequences
A stolen access token is only useful for a short window. An admin can
revoke a specific session immediately by marking its refresh token
revoked. Requires an extra table and a rotate-on-refresh flow, more
complex than pure stateless JWT, justified by the revocation requirement.
