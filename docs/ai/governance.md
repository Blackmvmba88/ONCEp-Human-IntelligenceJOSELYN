# AI Governance

## Purpose

PONCE uses AI to assist human work, not to erase accountability.

## Output classes

Every AI-assisted surface should distinguish:

```text
FACT
CALCULATION
AI ANALYSIS
RECOMMENDATION
HUMAN DECISION
```

## Principles

1. Facts must remain traceable to source records.
2. Deterministic calculations should not be delegated to an LLM when a deterministic implementation exists.
3. Recommendations should include rationale and relevant evidence.
4. Sensitive decisions require human authority.
5. Model outputs are not persisted as unquestioned truth.
6. AI context must obey the same authorization model as the user.
7. Prompt injection from documents must be treated as untrusted input.
8. Evaluation datasets must be maintained for critical AI tasks.

## Candidate analysis

AI may assist with:

- CV extraction
- skill normalization
- job-description comparison
- interview question generation
- structured summaries

AI should not silently make final employment decisions.

## Explainability contract

For important recommendations PONCE should be able to answer:

```text
What did you conclude?
Why?
Which sources were used?
Which factors mattered?
What uncertainty remains?
What action is being suggested?
Does that action require approval?
```

## RAG flow

```text
question
  ↓
permission scope
  ↓
authorized retrieval
  ↓
context assembly
  ↓
model
  ↓
validation
  ↓
citations / evidence
  ↓
response
```

## Evaluation

Critical AI features should measure:

- extraction accuracy
- groundedness
- citation correctness
- hallucination rate
- permission leakage
- bias indicators
- consistency
- refusal / escalation quality

## Model independence

PONCE should isolate provider-specific AI code behind a service boundary so models can be upgraded, evaluated or replaced without rewriting the HR domain.
