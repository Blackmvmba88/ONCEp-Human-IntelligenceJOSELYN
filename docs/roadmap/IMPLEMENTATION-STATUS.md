# Implementation Status

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

## Local verification

```bash
python -m pip install -e .
python -m unittest discover -s tests -v

joselyn status
joselyn version
joselyn event demo --type employee.created --format json
```

## Next executable slice

**People Core vertical path:**

```text
Employee command
    ↓
validation
    ↓
authoritative state change
    ↓
employee.created / employee.updated
    ↓
audit
    ↓
projection handler
```

Recommended next deliverables:

1. SQLite development repository behind a storage interface.
2. Employee aggregate and repository contract.
3. `joselyn employee create/list/show`.
4. immutable employee history entries.
5. RBAC policy interface with deny-by-default behavior.
6. approval boundary scaffolding for sensitive mutations.

This keeps the roadmap order intact: domain truth → permissions → events → deterministic automation → audit → AI assistance.
