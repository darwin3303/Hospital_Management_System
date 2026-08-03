# ADR-002: Repository pattern applied selectively

## Status
Accepted

## Context
Full repository interfaces (abstract base classes) for every feature add
ceremony without proportional benefit for simple lookup-heavy features.

## Decision
Introduce repository interfaces only where they provide real value for
testability or where multiple implementations are plausible -- currently
`pharmacy` (stock/dispense logic) and `billing` (invoice/payment logic).
All other features use a direct, concrete repository class.

## Consequences
Pharmacy and billing services can be unit-tested against fake in-memory
repositories. Other features are simpler at the cost of a slightly less
uniform pattern across the codebase -- judged an acceptable trade-off.
