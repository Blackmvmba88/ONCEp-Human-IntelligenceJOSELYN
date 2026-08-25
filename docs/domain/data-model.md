# Conceptual Data Model

## Goal

Define the first domain entities and their relationships before locking implementation details.

## Core entities

```text
Tenant
├── Users
├── Employees
├── Departments
├── Positions
├── Vacancies
├── Candidates
├── Contracts
├── Documents
├── Workflows
├── Rules
├── Approvals
└── Audit Events
```

## People Core

### Employee

Key fields:

```text
id
external_id
status
legal_name
preferred_name
start_date
end_date
department_id
position_id
manager_id
location_id
employment_type
created_at
updated_at
```

Sensitive attributes should be separated or access-controlled by field group.

### Department

```text
id
name
parent_department_id
cost_center
manager_employee_id
status
```

### Position

```text
id
title
level
job_family
reports_to_position_id
required_skills[]
status
```

## Recruitment

### Vacancy

```text
id
position_id
department_id
status
openings
owner_user_id
opened_at
target_start_date
```

### Candidate

```text
id
status
source
profile_summary
consent_state
created_at
```

### Application

```text
id
candidate_id
vacancy_id
stage
status
applied_at
```

## Contracts

### Contract

```text
id
employee_id
type
start_date
end_date
status
template_version
signed_at
document_id
```

## Documents

### Document

```text
id
owner_type
owner_id
category
storage_ref
classification
status
issued_at
expires_at
version
```

## Runtime

### DomainEvent

```text
event_id
event_type
event_version
occurred_at
actor
correlation_id
causation_id
payload
```

### WorkflowInstance

```text
id
workflow_type
workflow_version
subject_type
subject_id
state
started_at
completed_at
correlation_id
```

### ScheduledAction

```text
id
subject_type
subject_id
trigger_at
action_type
automation_level
status
retry_policy
```

### Approval

```text
id
action_type
subject_type
subject_id
requested_by
required_role
status
requested_at
decided_at
decided_by
```

### Conflict

```text
id
subject_type
subject_id
field
sources[]
values[]
status
resolution
```

## Talent Development

### Skill

```text
id
name
category
```

### EmployeeSkill

```text
employee_id
skill_id
level
source
assessed_at
```

### PerformanceReview

```text
id
employee_id
reviewer_id
period_start
period_end
status
completed_at
```

### TrainingAssignment

```text
id
employee_id
course_id
status
assigned_at
due_at
completed_at
```

## Audit

### AuditRecord

```text
id
actor_type
actor_id
action
resource_type
resource_id
occurred_at
correlation_id
summary
```

Sensitive before/after values must be minimized or masked.

## Relationship rule

The database schema is not the dependency graph. Relational foreign keys describe storage integrity; the PONCE dependency graph describes operational consequences.

Example:

```text
employee.start_date
```

may affect tenure, probation, vacation eligibility, onboarding schedule and analytics even though those dependencies are not represented by one foreign key.

## Source-of-truth rule

Every field that can be derived must document its authoritative inputs. If two systems can claim authority over the same value, reconciliation policy must be explicit.
