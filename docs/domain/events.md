# Domain Event Catalog

## Purpose

This file defines the first canonical event vocabulary for PONCE. Events represent facts that already occurred and are contracts between bounded contexts.

## Naming

Preferred form:

```text
<entity>.<fact>
```

Examples:

```text
employee.created
contract.expiring
vacation.approved
```

## Envelope

Every event SHOULD include:

```json
{
  "event_id": "uuid",
  "event_type": "employee.created",
  "event_version": 1,
  "occurred_at": "ISO-8601",
  "actor": {
    "type": "user|system|integration",
    "id": "..."
  },
  "tenant_id": "...",
  "correlation_id": "...",
  "causation_id": "...",
  "payload": {}
}
```

## People Core

```text
employee.created
employee.updated
employee.activated
employee.suspended
employee.terminated
employee.transferred
employee.manager_changed
employee.department_changed
employee.position_changed
employee.start_date_changed
employee.compensation_change_requested
employee.compensation_changed
```

## Recruitment

```text
vacancy.created
vacancy.published
vacancy.closed
candidate.created
candidate.applied
candidate.screened
candidate.interview_scheduled
candidate.interviewed
candidate.moved_stage
candidate.offer_prepared
candidate.offer_approved
candidate.hired
candidate.rejected
```

## Contracts

```text
contract.created
contract.signed
contract.updated
contract.expiring
contract.expired
contract.renewal_requested
contract.renewed
contract.terminated
```

## Documents

```text
document.uploaded
document.classified
document.extracted
document.validation_failed
document.expiring
document.expired
document.deleted
```

## Time / Attendance / Leave

```text
attendance.recorded
attendance.corrected
incident.created
vacation.requested
vacation.approved
vacation.rejected
vacation.cancelled
leave.started
leave.ended
```

## Talent Development

```text
performance.review_due
performance.review_started
performance.review_completed
training.assigned
training.started
training.completed
certification.expiring
certification.renewed
skill.assessed
```

## Automation

```text
rule.evaluated
rule.matched
workflow.started
workflow.step_completed
workflow.paused
workflow.failed
workflow.completed
approval.requested
approval.approved
approval.rejected
scheduled_action.created
scheduled_action.triggered
scheduled_action.failed
```

## Reconciliation

```text
conflict.detected
conflict.explained
reconciliation.proposed
reconciliation.approved
reconciliation.completed
```

## AI Assistance

```text
ai.analysis_requested
ai.analysis_completed
ai.recommendation_generated
ai.output_rejected
ai.output_accepted
```

AI events never imply authority to execute sensitive employment actions.

## Versioning policy

- Additive compatible payload changes may remain on the same event version.
- Breaking schema changes require a new version.
- Consumers must declare supported versions.
- Event payloads must not leak data that a consumer is not authorized to receive.
