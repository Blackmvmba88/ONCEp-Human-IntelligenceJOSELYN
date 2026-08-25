# ADR-002 — Time as a First-Class Runtime Primitive

- **Status:** Accepted
- **Decision owners:** Iyari Gomez & Chatsy

## Context

Human operations are dominated by dates: start dates, probation windows, contract expirations, certifications, vacations, reviews, renewals and deadlines. Treating time as passive metadata would force each module to reinvent scheduling logic.

## Decision

PONCE SHALL provide a shared **Temporal Engine**.

The engine will support:

- absolute dates
- relative offsets
- recurrence
- business calendars
- policy windows
- reminders
- escalations
- temporal conditions
- deterministic testing with a controllable clock

Example:

```text
contract.expires_at = 2026-11-18
-90d -> review
-60d -> notify HR
-30d -> notify manager
-15d -> create task
 -7d -> escalate
  0d -> execute expiration workflow
```

## Consequences

- Time-driven behavior becomes centralized and testable.
- Modules publish temporal intent rather than implementing their own schedulers.
- Scheduling failures become observable runtime failures instead of silent business-process drift.
