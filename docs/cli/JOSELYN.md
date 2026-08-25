# JOSELYN CLI

> Command-line interface for PONCE — Human Intelligence Platform.

## Purpose

JOSELYN CLI provides a direct, scriptable and auditable interface to PONCE for administrators, developers, automation pipelines and authorized operators.

It is not a bypass around permissions. Every command uses the same authorization, audit and approval rules as other PONCE clients.

## Command shape

```bash
joselyn <domain> <action> [target] [flags]
```

## Core commands

### System

```bash
joselyn status
joselyn health
joselyn version
joselyn whoami
```

### Employees

```bash
joselyn employee list
joselyn employee show EMP-204
joselyn employee history EMP-204
joselyn employee transfer EMP-204 --department finance
```

Sensitive modifications should enter approval workflows when required.

### Contracts

```bash
joselyn contract list
joselyn contract expiring --days 30
joselyn contract show CON-102
joselyn contract renewal prepare CON-102
```

### Recruitment

```bash
joselyn vacancy list
joselyn candidate list --vacancy VAC-018
joselyn candidate show CAN-992
joselyn interview schedule CAN-992
```

### Workflows

```bash
joselyn workflow list
joselyn workflow run onboarding EMP-204
joselyn workflow inspect WF-112
joselyn workflow retry WF-112 --step notify-it
```

### Rules

```bash
joselyn rule list
joselyn rule explain RULE-014
joselyn rule test RULE-014 --fixture fixtures/contract-expiring.json
```

### Events

```bash
joselyn event tail
joselyn event show EVT-...
joselyn event replay EVT-... --dry-run
```

Event replay must be constrained by permissions and idempotency safeguards.

### Analytics

```bash
joselyn analytics turnover --department sales
joselyn analytics headcount --as-of 2026-09-01
joselyn analytics time-to-hire --period 90d
```

### Audit

```bash
joselyn audit employee EMP-204
joselyn audit actor USER-19
joselyn audit correlation CORR-...
```

### Natural-language assistance

```bash
joselyn ask "what contracts expire this month?"
joselyn ask "show onboarding workflows currently blocked"
```

Natural-language commands resolve into explicit structured operations before execution. Sensitive operations require confirmation and approval.

## Output modes

```bash
--format table
--format json
--format yaml
--quiet
```

## Dry run

Any mutating command SHOULD support dry-run when feasible:

```bash
joselyn employee transfer EMP-204 --department finance --dry-run
```

Expected output:

```text
Would change:
- employee.department
- reporting line projection
- approval chain projection
- analytics projections

Would emit:
- employee.department_changed.v1

Would require:
- HR Manager approval

No changes executed.
```

## Exit codes

Suggested initial contract:

```text
0  success
1  generic failure
2  invalid arguments
3  authorization denied
4  approval required
5  validation failed
6  conflict detected
7  dependency unavailable
8  workflow failed
```

## Security

JOSELYN must never print secrets by default. Personal data fields should support masking according to role and environment.

## Principle

> JOSELYN is the technical cockpit of PONCE — powerful enough for operators, constrained enough for enterprise use.
