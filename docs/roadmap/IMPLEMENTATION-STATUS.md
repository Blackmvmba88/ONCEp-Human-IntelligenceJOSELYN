# Implementation Status

## v0.3 — People Core authorization + immutable history

Status: **implemented on `feat/joselyn-people-core-v2`; pending merge**.

This slice moves People Core from a local registry toward a security-aware execution boundary.

### Implemented

- deny-by-default `Principal` authorization;
- explicit role/permission map based on the documented PONCE roles;
- field-level read boundaries for basic, contact, extra and provenance data;
- masking of contact fields for roles without contact permission;
- lookup/search restrictions that prevent email-address probing by roles without contact access;
- explicit import/update authorization;
- immutable `people_history` rows for accepted creates/updates;
- actor ID, actor role and correlation ID persisted with each history entry;
- `employee.created` / `employee.updated` runtime events correlated with People history;
- no-op re-imports from the same source skip mutation/history;
- `joselyn people history`;
- explicit `--actor` + `--role` context for People CLI commands;
- tests covering denial, masking, history, event correlation, idempotence and contact-identity probing.

### Current boundary

This remains a local SQLite development implementation. Authentication, tenant-aware ABAC, employee self-service subject binding, approval workflows and production persistence are still separate decisions.

GitHub-hosted CI is currently blocked before workflow steps start. See `docs/ci/CI-RECOVERY.md`. Local unit tests and CLI smoke tests are the temporary execution gate.

## v0.2 — JOSELYN Intake + People Registry + Work-Value Loop

Status: **merged to `main`**.

This slice turns the People Core roadmap into a first useful HR data workflow without pretending OCR, speech, enterprise RBAC, or production persistence already exist.

### Implemented

- Common intake contract for structured HR records.
- CSV ingestion.
- TSV ingestion.
- JSON object / array ingestion.
- Spanish/English header aliases for common employee fields.
- Preservation of unmapped company-specific fields.
- Per-field source provenance.
- Duplicate detection using employee ID or email.
- Visible warnings when stable identity or name is missing.
- Format capability registry for implemented and planned adapters.
- SQLite development People Store.
- Idempotent upsert by stable identity.
- `joselyn formats`.
- `joselyn intake inspect <path>`.
- `joselyn people import <path>`.
- `joselyn people list [--query ...]`.
- `joselyn people show <id|email|identity-key>`.
- HR work-request model with purpose, requester, effort and impact.
- Automation-opportunity scoring for repetitive work.
- Explicit human-judgment and compliance penalties in automation scoring.
- Unit tests for intake normalization, duplicates, persistence, update behavior and automation assessment.
- Product spec for universal list → detail → relationships/source → actions interaction.

### Planned adapters behind the same intake contract

- XLSX / XLS
- PDF
- image / camera capture
- audio / voice dictation
- forms
- APIs / webhooks
- watched folders / recurring exports

### Current boundary

The SQLite registry is a local development implementation. It is not presented as enterprise production storage. Image OCR and speech-to-structured-data are intentionally listed as adapters until a real implementation and validation path exists.

Employment decisions remain human decisions; automation scoring applies to **tasks and workflows**, not to employee worthiness or hiring/promotion/termination decisions.

## Example local verification

```bash
python -m pip install -e .
python -m unittest discover -s tests -v

joselyn formats
joselyn intake inspect people.csv --format json
joselyn people import people.csv --db joselyn.db
joselyn people list --db joselyn.db
joselyn people show EMP-204 --db joselyn.db --format json
joselyn work assess \
  --title "Consolidar incidencias" \
  --purpose "Preparar pre-nomina" \
  --requester "HR Manager" \
  --frequency 8 \
  --minutes 45 \
  --structured-inputs \
  --repeated-steps \
  --format json
```

## v0.1 — JOSELYN Runtime Bootstrap

Status: **implemented on feature branch**.

This slice converts the specification-first repository into its first executable contract testbed without pretending the production platform is finished.

### Implemented

- Python 3.11+ package bootstrap.
- Installable `joselyn` command.
- `joselyn status`.
- `joselyn version`.
- `joselyn event demo`.
- Canonical `DomainEvent` model.
- Actor, tenant, correlation and causation metadata.
- In-memory event routing for local contract tests.
- Per-event/per-handler idempotency.
- Visible handler failures with retry behavior.
- Runtime audit records correlated to emitted events.
- Unit tests for envelope/audit, idempotency and retryable failure.
- GitHub Actions CI across Python 3.11, 3.12 and 3.13.

### Deliberately not production-ready

- durable event broker
- PostgreSQL persistence
- authentication / RBAC
- approval engine
- workflow persistence
- temporal scheduler
- dead-letter storage
- reconciliation persistence
- distributed tracing
- external integrations

Those components remain governed by the roadmap and require their own implementation decisions.

## Next executable slice

Recommended next deliverables:

1. XLSX adapter with explicit sheet/column mapping.
2. immutable employee history entries.
3. dry-run import diff before persistence.
4. deny-by-default RBAC scaffold.
5. approval boundary scaffolding for sensitive mutations.
6. image/document adapter producing proposed fields plus provenance.
7. speech/dictation adapter producing structured notes and requests.
8. reusable catalog/detail surface for candidates, documents, vacancies, tickets and assets.

This keeps the roadmap order intact: domain truth → permissions → events → deterministic automation → audit → AI assistance.
