# Workflow — Employee Onboarding

## Trigger

```text
candidate.hired
```

or

```text
employee.created
```

with an approved employment start state.

## Goal

Coordinate every onboarding dependency from one authoritative lifecycle event.

## State machine

```text
CREATED
  ↓
IDENTITY_PENDING
  ↓
DOCUMENTS_PENDING
  ↓
ACCESS_PENDING
  ↓
ASSETS_PENDING
  ↓
TRAINING_PENDING
  ↓
READY_FOR_START
  ↓
ACTIVE
  ↓
30_DAY_REVIEW
  ↓
60_DAY_REVIEW
  ↓
90_DAY_REVIEW
  ↓
COMPLETED
```

Exceptional states:

```text
BLOCKED
FAILED
CANCELLED
REQUIRES_RECONCILIATION
```

## Initial propagation

When `employee.start_date` is confirmed:

```text
employee.start_date.changed
  ├─> calculate tenure baseline
  ├─> calculate probation milestones
  ├─> calculate vacation policy dates
  ├─> schedule 30/60/90-day reviews
  ├─> request missing documents
  ├─> notify manager
  ├─> create IT access task
  ├─> create asset assignment task
  ├─> assign mandatory training
  ├─> update projected headcount
  └─> update projected labor cost inputs
```

## Checklist model

Each onboarding item should include:

```text
id
category
owner
required
due_at
status
depends_on[]
automation_level
evidence
```

## Example checklist

```text
[required] identity verified
[required] contract signed
[required] payroll profile prepared
[required] system account provisioned
[required] manager confirmed
[required] mandatory training assigned
[optional] welcome package prepared
```

## Approvals

Actions with material legal, payroll, security or employment impact must follow their domain approval policy.

## Retry behavior

Notifications and integration calls may retry. Human tasks do not auto-complete on retry.

## Reconciliation examples

- start date differs between contract and employee record
- department differs between offer and employee record
- manager is inactive
- required document expired before start
- asset assignment conflicts with inventory state

These conditions should pause or flag the workflow rather than silently continuing.

## Completion criteria

Onboarding is complete only when all required checklist items, required approvals and required temporal checkpoints are in a known completed or deliberately waived state.
