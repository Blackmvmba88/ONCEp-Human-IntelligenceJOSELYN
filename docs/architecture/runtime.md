# Human Intelligence Runtime

## Purpose

The Human Intelligence Runtime is the execution heart of PONCE. It turns domain facts into safe, observable and auditable consequences.

## Runtime pipeline

```text
Authoritative change
      ↓
Domain validation
      ↓
Event emission
      ↓
Event routing
      ↓
Rules evaluation
      ↓
Dependency recalculation
      ↓
Workflow progression
      ↓
Temporal scheduling
      ↓
Approval checks
      ↓
Execution
      ↓
Audit + projections
```

## Event Bus

Responsibilities:

- publish domain events
- preserve ordering where required
- support retries
- expose dead-letter failures
- attach correlation / causation identifiers
- prevent unauthorized event publication

## Dependency Graph

The graph records dependencies such as:

```text
employee.start_date
  ├─> employee.tenure
  ├─> vacation.eligibility
  ├─> onboarding.timeline
  ├─> probation.review_dates
  └─> workforce.analytics
```

Dependency recomputation should be deterministic when based on deterministic inputs.

## Temporal Engine

Stores scheduled intent, not just reminders.

A scheduled action contains:

```text
id
source entity
trigger time
policy version
action type
automation level
status
retry policy
correlation id
```

## Workflow Engine

A workflow is a durable state machine.

Example:

```text
NEW
 ↓
DOCUMENTS_PENDING
 ↓
APPROVAL_PENDING
 ↓
READY
 ↓
RUNNING
 ↓
COMPLETED
```

Possible terminal / exceptional states:

```text
FAILED
CANCELLED
REJECTED
REQUIRES_RECONCILIATION
```

## Approval Engine

Approval request fields:

```text
requested_action
resource
requested_by
required_role
reason
impact_summary
evidence_snapshot
expires_at
status
```

Approval results emit domain events.

## Reconciliation Engine

When competing sources conflict, PONCE records a conflict object rather than hiding the disagreement.

```text
conflict
├── field
├── sources[]
├── candidate values[]
├── authoritative policy
├── downstream impact[]
└── resolution status
```

## Automation Executor

The executor performs side effects after authorization.

Examples:

- send notification
- create task
- generate document
- update projection
- call integration
- start workflow
- transition state

Every side effect should produce a result record and audit trace.

## Failure model

PONCE must make failure visible.

```text
transient failure  → retry
permanent failure  → dead-letter / manual action
conflict            → reconciliation
unauthorized        → deny + audit
approval required   → pause
invalid state       → reject
```

## Replay

Events may be replayed only when:

- schema version is supported
- consumer is idempotent or replay-safe
- side effects are disabled or explicitly authorized
- audit records identify replay origin

## Observability

Runtime metrics should include:

- events published / consumed
- consumer lag
- rule evaluations
- rule matches
- workflow duration
- workflow failures
- pending approvals
- scheduled actions overdue
- reconciliation conflicts
- retry counts
- dead-letter volume

## Runtime invariant

> A change is complete only when its domain truth, dependent projections, required workflows, approvals and audit trail reach a known state.
