# Rules Engine

## Goal

Allow PONCE to react to business facts without hard-coding every combination of conditions and consequences.

## Model

```text
WHEN <event or state condition>
IF   <optional guards>
THEN <one or more actions>
```

Example:

```yaml
name: contract-expiry-30d
when:
  event: contract.expiring
if:
  days_remaining: 30
  employee_status: active
then:
  - notify: hr
  - notify: manager
  - create_task: contract-renewal-review
```

## Rule types

### Reactive rules

Triggered by domain events.

### Temporal rules

Triggered by dates, offsets, recurrence or business calendars.

### State rules

Triggered when authoritative state satisfies a condition.

### Reconciliation rules

Triggered when two or more sources disagree.

## Action categories

```text
READ
CALCULATE
NOTIFY
GENERATE
SCHEDULE
TRANSITION
REQUEST_APPROVAL
EXECUTE
```

Each action category maps to an automation safety level.

## Required properties

Every rule should have:

- stable id
- human-readable name
- version
- owner
- enabled state
- trigger
- conditions
- actions
- permission requirements
- automation level
- retry policy
- audit policy
- test fixtures

## Determinism

Rules that perform calculations should be deterministic whenever possible. AI may enrich or recommend, but AI should not silently alter the truth conditions of a deterministic business rule.

## Explainability

The engine must be able to answer:

```text
Why did this rule run?
Which facts matched?
Which conditions failed?
Which actions were produced?
Which actions require approval?
```

## Dry-run

Rules must support evaluation without side effects.

```text
input event
  ↓
rule evaluation
  ↓
planned actions
  ↓
NO EXECUTION
```

## Conflict handling

When multiple rules produce contradictory actions, the runtime must not pick arbitrarily. It should apply explicit priority / policy rules or raise a conflict for reconciliation.

## Anti-pattern

Do not use the rules engine to hide core domain invariants. Invariants belong in domain logic. Rules are for configurable policy and orchestration behavior.
