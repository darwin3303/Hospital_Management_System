# ADR-005: Single aggregate overview endpoint for Admin

## Status
Accepted

## Context
The Admin dashboard needs several cross-feature numbers at once (patient
count, today's appointments, revenue). Composing these client-side from
three separate report calls means three round trips and duplicated
aggregation logic on the frontend.

## Decision
Add a single `GET /reports/overview` endpoint that composes these numbers
server-side in one query pass, owned by the `reports` feature (which,
per its own boundary rule, owns no tables and only reads others').

## Consequences
One network round trip for the dashboard's summary cards. Adds a small
amount of coupling in `reports/service.py` to the shape of what the
overview needs, acceptable since `reports` already has read access to
everything by design.
