# ADR-003 — Human-in-the-Loop for Sensitive Employment Actions

- **Status:** Accepted
- **Decision owners:** Iyari Gomez & Chatsy

## Context

PONCE can automate large portions of HR operations, but some actions materially affect people and require accountable human authority.

## Decision

Sensitive employment actions SHALL require explicit human approval unless a future legal, policy and product review deliberately changes that rule.

Default sensitive actions include:

- hiring
- termination
- disciplinary sanctions
- compensation changes
- promotion decisions
- final candidate rejection based on AI analysis
- policy exceptions with material employee impact

## Automation levels

```text
L0 Read only
L1 Deterministic recalculation
L2 Recommendation
L3 Prepare action
L4 Human approval required
L5 Authorized automatic execution
```

## Requirements

1. AI analysis must be distinguishable from factual system data.
2. Approval events must identify actor, timestamp and decision context.
3. The system must preserve the explanation and evidence shown at approval time.
4. A model score alone must never be treated as sufficient authority for a sensitive employment action.
5. Sensitive workflows must expose rejection, cancellation and rollback paths where technically possible.
