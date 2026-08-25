# PONCE Roadmap

## Phase 0 — Product & Architecture Foundation

Deliverables:

- canonical naming
- README
- architecture overview
- domain map
- event catalog
- security model
- ADRs
- automation safety levels
- initial workflow definitions
- initial JOSELYN CLI contract

Exit criteria:

- repository is the source of truth
- every major runtime component has a written responsibility
- sensitive actions have approval boundaries

## Phase 1 — People Core MVP

Build:

- authentication
- RBAC
- employees
- departments
- positions
- reporting lines
- employee history
- documents
- audit trail

Exit criteria:

- a complete employee record can be created, viewed and audited
- document access obeys permissions

## Phase 2 — Talent Acquisition MVP

Build:

- vacancies
- candidates
- CV upload
- pipeline stages
- interviews
- evaluation notes
- offer preparation

Exit criteria:

- candidate lifecycle can be managed end-to-end without AI

## Phase 3 — Reactive Runtime

Build:

- event envelope
- event bus
- event registry
- idempotent handlers
- retry/dead-letter strategy
- rules engine
- temporal engine
- workflow engine
- approval engine

Exit criteria:

- one authoritative change can safely propagate to multiple dependent projections

## Phase 4 — Document Intelligence

Build:

- document classification
- structured field extraction
- expiration detection
- missing-field detection
- template generation
- policy/document search

Exit criteria:

- document outputs are traceable to source files and validation state

## Phase 5 — HR Analytics

Build:

- headcount
- turnover
- absenteeism
- time-to-hire
- cost-per-hire
- open vacancies
- department projections
- report generation

Exit criteria:

- executive KPIs are reproducible from authoritative data

## Phase 6 — AI Assistance

Build:

- CV extraction
- explainable candidate comparison
- interview copilot
- policy assistant
- natural-language analytics
- RAG knowledge base
- JOSELYN `ask`

Exit criteria:

- AI facts, analysis and recommendations are clearly differentiated
- AI cannot bypass permissions or approvals

## Phase 7 — Reconciliation & Dependency Graph

Build:

- source-of-truth registry
- dependency graph
- conflict detector
- reconciliation proposals
- impact analysis
- replay / recalculation tools

Exit criteria:

- conflicting organizational state is detected instead of silently drifting

## Phase 8 — Organizational Digital Twin

Build:

- people graph
- roles
- skills
- costs
- capacity
- workflows
- assets
- documents
- time dependencies

Scenario examples:

```text
What changes if we add 15 sales employees next month?
What roles become bottlenecks if a manager leaves?
How much onboarding capacity is required next quarter?
```

## Phase 9 — Multi-Company Platform

Build:

- tenant isolation
- tenant configuration
- tenant-specific policy/rules
- integrations
- SDK
- webhooks
- mobile
- enterprise SSO

## Phase 10 — Continuous Organizational Intelligence

Target capabilities:

- workforce forecasting
- capacity planning
- anomaly detection
- proactive temporal planning
- explainable scenario simulation
- continuous process improvement recommendations

## Development sequence rule

Never skip from UI directly to autonomous AI.

Preferred order:

```text
Domain truth
   ↓
Permissions
   ↓
Events
   ↓
Deterministic automation
   ↓
Audit / reconciliation
   ↓
AI assistance
   ↓
Human approval
   ↓
Execution
```
