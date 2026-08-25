# Architecture Overview

## System intent

PONCE is designed as a reactive Human Intelligence Platform rather than a passive HR database.

The architecture separates authoritative state, derived state, event propagation, automation, AI assistance and human approval so the system can scale without coupling every module directly to every other module.

## Core layers

```text
Clients
  │
  ▼
API Gateway / BFF
  │
  ├───────────────┐
  ▼               ▼
Domain APIs    JOSELYN CLI
  │               │
  └───────┬───────┘
          ▼
Human Intelligence Runtime
          │
 ┌────────┼─────────┬──────────┐
 ▼        ▼         ▼          ▼
Events   Rules   Workflows   Temporal
 │        │         │          │
 └────────┴────┬────┴──────────┘
               ▼
       Approval / Executor
               │
      ┌────────┼────────┐
      ▼        ▼        ▼
  HR Core      AI    Analytics
      │        │        │
      └────────┼────────┘
               ▼
      Organizational Graph
               │
               ▼
        Authoritative Data
```

## Architectural principles

### 1. Event-driven by default

Significant domain changes produce versioned events. Consumers react without requiring hard-coded point-to-point orchestration.

### 2. Authoritative vs derived state

Every important value must be classified as one of:

- authoritative input
- deterministic derived value
- AI-derived suggestion
- cached projection

Derived state must be reproducible from authoritative state.

### 3. Human control over sensitive actions

Employment decisions, compensation changes, termination, hiring and disciplinary actions require explicit human authority.

### 4. Idempotency

Event handlers and workflows should tolerate retries without duplicating side effects.

### 5. Auditability

Critical reads, writes, approvals and automated actions emit audit records.

### 6. Temporal correctness

Dates and deadlines are first-class triggers. Time-based behavior must be testable with a controllable clock.

### 7. Reconciliation over silent drift

Conflicting records are surfaced and reconciled rather than silently overwritten.

## Primary runtime components

### Event Bus

Carries domain facts such as `employee.created`, `contract.expiring`, and `vacation.approved`.

### Rules Engine

Evaluates declarative conditions over facts and state.

### Workflow Engine

Coordinates long-running multi-step business processes with retries, compensation and approvals.

### Temporal Engine

Schedules future actions relative to dates, durations, calendars and policy windows.

### Dependency Graph

Tracks which entities and projections depend on which authoritative facts.

### Approval Engine

Stops sensitive actions until an authorized human approves or rejects them.

### Reconciliation Engine

Detects conflicting state, explains impact and drives controlled correction.

### Automation Executor

Executes approved and permitted side effects such as notifications, document generation and state transitions.

## Non-goals for v0

- Fully autonomous hiring or firing
- Silent AI-driven ranking without explanation
- Hard-coded country-specific legal advice presented as authoritative
- Replacing payroll/accounting systems before integration contracts exist
- Direct coupling between every HR module

## Long-term architecture target

PONCE should evolve into an organizational digital twin where people, roles, skills, costs, workflows, documents and time form one computable graph that can support simulation, forecasting and operational planning.
