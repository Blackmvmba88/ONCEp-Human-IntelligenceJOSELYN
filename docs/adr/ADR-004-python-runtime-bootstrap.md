# ADR-004 — Python for JOSELYN Runtime Bootstrap

## Status

Accepted for bootstrap only.

## Context

PONCE is specification-first and has not yet committed the whole platform to one implementation language. The first executable slice needs to validate the most important contracts quickly:

- canonical domain-event envelope
- event routing
- idempotent handling
- visible failures
- correlation / causation metadata
- audit traces
- JOSELYN command shape

This decision must not prematurely lock web, API, analytics or long-term messaging infrastructure.

## Decision

Use Python 3.11+ and the standard library for the initial JOSELYN CLI and local Human Intelligence Runtime bootstrap.

The bootstrap will remain deliberately small and dependency-light. Production infrastructure choices such as database, broker, distributed workflow engine and API framework require separate ADRs.

## Consequences

### Positive

- Fast executable feedback on architecture contracts.
- Minimal dependency surface.
- Easy local testing and scripting.
- Runtime semantics can be validated before introducing infrastructure complexity.

### Negative

- The in-memory event bus is not durable and is not a production broker.
- The bootstrap does not decide the language of every PONCE service.
- Interfaces must remain explicit so components can later move behind network or broker boundaries.

## Guardrails

1. Event schemas remain platform contracts, not Python-only objects.
2. Side effects must remain auditable.
3. Sensitive actions must not bypass approval policy.
4. Event handlers should be idempotent or explicitly non-replayable.
5. Any production broker or persistent runtime requires a new ADR.

## Exit criteria

This bootstrap is successful when CI proves that:

- canonical events validate;
- one event can be delivered to subscribers;
- replay of the same event does not repeat a successful handler;
- transient handler failure remains visible and can be retried;
- audit records preserve the event correlation identifier;
- JOSELYN can report runtime status from an installed package.
