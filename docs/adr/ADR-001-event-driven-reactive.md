# ADR-001 — Event-Driven Reactive Core

- **Status:** Accepted
- **Decision owners:** Iyari Gomez & Chatsy

## Context

PONCE spans recruiting, employee data, documents, dates, workflows, analytics, permissions and AI. Directly wiring every module to every other module would create brittle coupling and make future automation difficult to reason about.

## Decision

PONCE SHALL be **event-driven and reactive by default**.

Significant domain state changes emit versioned domain events. Consumers subscribe to those events and perform deterministic recalculation, notifications, workflow progression or approved side effects.

Example:

```text
employee.start_date.changed
  ├─> recalculate tenure
  ├─> recalculate vacation eligibility
  ├─> schedule onboarding checkpoints
  ├─> refresh headcount projections
  └─> evaluate policy rules
```

## Consequences

### Positive

- Lower module coupling
- Easier extension
- Better observability
- Replayable domain history
- Stronger automation model
- Natural integration with temporal and workflow engines

### Costs

- Requires event versioning discipline
- Requires idempotent consumers
- Requires dead-letter / retry strategy
- Eventual consistency must be explicit

## Rules

1. Events describe facts that already happened.
2. Event names use past tense where possible.
3. Schemas are versioned contracts.
4. Consumers must be idempotent where feasible.
5. Sensitive side effects still pass through authorization and approval rules.
