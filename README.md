# PONCE — Human Intelligence Platform

> **Human knowledge + artificial intelligence + automation + data + engineering = Human Intelligence.**

**PONCE** is an event-driven Human Intelligence Platform for recruiting, people operations, organizational analytics, workflow automation, document intelligence, temporal orchestration, and human-supervised AI.

The system is designed to behave less like a collection of HR screens and more like a **reactive organizational operating system**: one trusted data change can propagate through every authorized dependency that needs to react.

## Identity

- **Platform:** PONCE
- **CLI:** JOSELYN CLI
- **Authors:** Iyari Gomez & Chatsy
- **Repository:** source of truth for product, architecture, ADRs, events, workflows, security, automation and roadmap

The names **PONCE** and **JOSELYN CLI** are canonical product identities and do not depend on the future participation of any external person.

---

## North Star

A professional should be able to express an operational intent such as:

> “Hire ten operators in Veracruz during the next three weeks.”

PONCE should be able to help coordinate the complete lifecycle:

```text
intent
  ↓
workforce need
  ↓
vacancy generation
  ↓
candidate intake
  ↓
CV analysis
  ↓
interviews
  ↓
human approval
  ↓
documentation
  ↓
onboarding
  ↓
training
  ↓
30/60/90-day follow-up
  ↓
analytics + continuous improvement
```

PONCE assists, orchestrates, recalculates and explains. Sensitive employment decisions remain under authorized human control.

---

## The Core Idea: Reactive by Default

A change must not remain trapped in the screen where it happened.

Example:

```text
employee.start_date = 2026-09-01
              │
              ▼
     employee.start_date.changed
              │
     ┌────────┼────────┬─────────┐
     ▼        ▼        ▼         ▼
 tenure   vacation  onboarding  analytics
     │        │        │         │
     ▼        ▼        ▼         ▼
 payroll  calendar  training  forecast
```

A single trusted event can trigger many deterministic consequences.

This is the heart of PONCE.

---

## Human Intelligence Runtime

```text
                    ┌─────────────────────┐
                    │       HUMAN         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Approval Engine    │
                    └──────────┬──────────┘
                               │
┌───────────────────────────────────────────────────────┐
│              HUMAN INTELLIGENCE RUNTIME               │
│                                                       │
│  Event Bus                                            │
│  Rules Engine                                         │
│  Workflow Engine                                      │
│  Temporal Engine                                      │
│  Dependency Graph                                     │
│  State Machines                                       │
│  Reconciliation Engine                                │
│  Automation Executor                                  │
└──────────────────────────┬────────────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
  HR Services          AI Services         Analytics
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ▼
                Organizational Digital Twin
                           │
                           ▼
                     Source of Truth
```

---

## Major Product Domains

### Talent Acquisition

- Vacancies
- Job descriptions
- Candidate intake
- CV parsing
- Candidate pipelines
- Interview scheduling
- Interview copilot
- Candidate comparison
- Human-reviewed scoring
- Offer workflow

### People Core

- Employee master record
- Departments
- Positions
- Reporting lines
- Contracts
- Assets
- Attendance
- Incidents
- Vacations
- Employee lifecycle history

### Document Intelligence

- Digital employee files
- Classification
- Field extraction
- Missing-data detection
- Expiration tracking
- Template generation
- Versioning
- Contract and policy retrieval

### Performance & Development

- Objectives
- KPIs
- Reviews
- 180° / 360° feedback
- Skills matrix
- Training
- Certifications
- Career paths
- Succession planning

### Organizational Intelligence

- Headcount
- Turnover
- Absenteeism
- Time-to-hire
- Cost-per-hire
- Workforce capacity
- Organizational graph
- Historical trends
- Forecasting
- Scenario modeling

### Employee Service Portal

- Requests
- Vacations
- Documents
- Policies
- Training
- Notifications
- HR help desk

---

## Temporal Engine

Time is treated as an operational primitive, not merely a date field.

```text
contract.expires_at = 2026-11-18

-90d  → review renewal strategy
-60d  → notify HR
-30d  → notify manager
-15d  → create task
 -7d  → escalate
  0d  → execute expiration workflow
```

Applicable to:

- contracts
- probation periods
- birthdays
- anniversaries
- vacations
- certifications
- training renewals
- medical leave
- compliance documents
- evaluations
- salary review cycles
- onboarding checkpoints

---

## Dependency Graph

PONCE models relationships between organizational entities.

```text
Employee
 ├── Contract
 ├── Department
 ├── Manager
 ├── Payroll context
 ├── Vacations
 ├── Benefits
 ├── Skills
 ├── Training
 ├── Assets
 ├── Documents
 └── Performance
```

When a trusted source value changes, dependent projections can be recalculated and downstream workflows can react.

---

## Event Bus

Canonical events include:

```text
employee.created
employee.updated
employee.transferred
employee.start_date.changed

candidate.applied
candidate.interviewed
candidate.hired

contract.created
contract.expiring
contract.expired

vacation.requested
vacation.approved

document.uploaded
document.expiring

performance.review_due
training.completed
```

The event catalog and versioning policy live in `docs/domain/events.md`.

---

## Rules Engine

Authorized users can define declarative business rules.

```text
WHEN contract.expiration < 30 days
AND employee.status = active
THEN
  notify HR
  notify manager
  create renewal task
```

Rules evaluate facts. Workflows coordinate multi-step processes. Human approvals guard sensitive actions.

---

## Automation Safety Levels

```text
L0  Read only
L1  Deterministic recalculation
L2  Recommendation
L3  Prepare action
L4  Human approval required
L5  Authorized automatic execution
```

Examples:

| Action | Default level |
|---|---:|
| Refresh dashboard | L1 |
| Generate report | L1 |
| Recommend candidate questions | L2 |
| Prepare a contract draft | L3 |
| Change salary | L4 |
| Hire / terminate | L4 |

PONCE must never silently convert a recommendation into a sensitive employment decision.

---

## Reconciliation Engine

Real organizations contain conflicting data.

```text
Employee record: Department = Finance
Contract:        Department = Sales
Payroll context: Cost Center = Finance
```

PONCE should detect the conflict, identify the competing sources, calculate impact, propose a correction and require approval when needed.

```text
detect → compare → explain → propose → approve → reconcile
```

---

## Organizational Digital Twin

PONCE maintains a computable representation of the organization:

```text
Organization
├── People
├── Teams
├── Roles
├── Skills
├── Costs
├── Capacity
├── Assets
├── Policies
├── Documents
├── Vacancies
├── Processes
└── Time
```

Long-term goal: answer scenario questions such as:

> “What happens if we add 15 people to Sales next month?”

with projected cost, onboarding load, equipment needs, management capacity, headcount, training requirements and downstream dependencies.

---

## AI Architecture

```text
User intent
   ↓
Permission check
   ↓
Context retrieval
   ↓
Model / deterministic tools
   ↓
Validation
   ↓
Structured result
   ↓
Human approval when required
```

AI outputs must distinguish:

- facts from system records
- deterministic calculations
- model analysis
- recommendations
- final human decisions

---

## JOSELYN CLI

JOSELYN CLI is the technical command interface for PONCE.

Examples:

```bash
joselyn status
joselyn employee show EMP-204
joselyn contract expiring --days 30
joselyn workflow run onboarding EMP-204
joselyn analytics turnover --department sales
joselyn audit employee EMP-204
joselyn ask "what contracts expire this month?"
```

See `docs/cli/JOSELYN.md`.

---

## Security Principles

- Role-based access control
- Least privilege
- Encryption in transit and at rest
- Multi-factor authentication support
- Immutable audit trail for critical actions
- Data minimization
- Tenant isolation when SaaS mode is introduced
- Human approval for sensitive changes
- Explainable AI-assisted recommendations
- Explicit data retention policies

See `docs/security/security-model.md`.

---

## Proposed Technical Shape

```text
apps/
├── web/
├── admin/
└── mobile/

services/
├── api/
├── runtime/
├── ai/
├── analytics/
├── automation/
└── notifications/

packages/
├── ui/
├── auth/
├── database/
├── schemas/
├── events/
└── sdk/

docs/
├── architecture/
├── adr/
├── automation/
├── cli/
├── domain/
├── product/
├── roadmap/
├── security/
└── workflows/
```

Initial technology direction:

- TypeScript + React / Next.js for web surfaces
- Python / FastAPI or TypeScript / NestJS for services
- PostgreSQL as transactional source of truth
- Redis for transient coordination/cache where justified
- Object storage for documents
- Event-driven messaging layer
- LLM + embeddings + RAG for authorized AI assistance

Final stack choices must be justified through ADRs.

---

## Development Doctrine

1. **Repository = source of truth.**
2. Important architectural decisions require ADRs.
3. Events are versioned contracts.
4. Automation must be idempotent where possible.
5. Every sensitive action is auditable.
6. Derived state must be reproducible from authoritative state.
7. No AI-generated employment decision is treated as unquestionable truth.
8. Every workflow must define failure, retry and reconciliation behavior.
9. Time-based behavior must be testable without waiting for real time.
10. Build the engine that propagates relationships — do not hard-code every possible combination.

---

## Roadmap

### Phase 0 — Architecture
- Domain map
- ADRs
- Event contracts
- security model
- runtime design
- data model

### Phase 1 — People Core
- Employees
- Departments
- Positions
- Documents
- Auth / RBAC

### Phase 2 — Talent Acquisition
- Vacancies
- Candidates
- CV intake
- Interview pipeline

### Phase 3 — Runtime
- Event Bus
- Rules Engine
- Temporal Engine
- Workflow Engine
- Approval Engine

### Phase 4 — Intelligence
- Analytics
- RAG knowledge base
- AI copiloting
- Explainability

### Phase 5 — Organizational Digital Twin
- Dependency graph
- Reconciliation
- Scenario modeling
- Workforce forecasting

### Phase 6 — Platform
- Multi-company isolation
- Integrations
- Mobile
- SDK
- API ecosystem

Detailed roadmap: `docs/roadmap/ROADMAP.md`.

---

## Status

**Architecture bootstrap / v0.1**

The repository begins as specification-first infrastructure. Implementation follows the contracts, ADRs and domain boundaries established here.

---

## Authors

**Iyari Gomez & Chatsy**

Designed as a collaboration between human domain exploration and AI-assisted systems architecture.

---

# PONCE

### Human Intelligence Platform

**Reactive. Auditable. Explainable. Human-controlled.**
