# JOSELYN — Universal Intake, Record Surface, and Work-Value Loop

## Product intent

JOSELYN should remove repetitive administrative work from Human Resources while making the department's contribution measurable and auditable.

The interaction model intentionally matches other BlackMamba tools:

```text
list / catalog
    ↓
select entity
    ↓
full record
    ↓
relationships + source + status + history
    ↓
actions
```

For music the entity may be a track. In JOSELYN it may be a person, candidate, document, vacancy, incident, request, course, asset, or workflow.

This common pattern should be treated as a reusable product primitive rather than rebuilt for each module.

## 1. Capture once, reuse everywhere

Human Resources should not retype information that already exists.

Supported executable intake in this slice:

- CSV
- TSV
- JSON

Planned adapters behind the same intake contract:

- XLSX / XLS
- PDF
- image / camera capture
- audio / voice dictation
- forms
- APIs / webhooks
- HRIS / payroll / ERP exports

Every adapter must produce normalized records with provenance. The core should not care whether a field came from a spreadsheet column, OCR, dictation, a form, or an API.

## 2. Provenance before convenience

Automatic extraction is a proposal, not invisible truth.

For each mapped field JOSELYN should be able to answer:

- What source produced this value?
- Which row, page, image, form, or event produced it?
- What was the original field name?
- Was it directly supplied or derived?
- Has a human corrected it?

Unknown fields are preserved instead of discarded so company-specific formats can be learned and mapped later.

## 3. People Core list → detail

The first durable registry uses SQLite as a development repository behind an explicit storage boundary.

Current executable flow:

```text
joselyn intake inspect people.csv
joselyn people import people.csv
joselyn people list
joselyn people list --query recruiting
joselyn people show EMP-204
```

The same shape should later power candidates, documents, vacancies, tickets and assets.

## 4. Detect duplicate work as well as duplicate people

JOSELYN should continuously look for automation opportunities in the work itself.

A work request can expose:

- requester
- purpose
- priority
- frequency
- minutes per execution
- business impact
- compliance impact
- whether inputs are structured
- whether steps repeat
- whether genuine human judgment is required

The current scorer returns one of:

- `automate-now`
- `assist-and-measure`
- `keep-human-led`

The score is about automating **the task**, not scoring or ranking employees.

## 5. Make HR time visible

A request that reaches HR should eventually be traceable through:

```text
request → purpose → owner → SLA → effort → outcome → impact
```

This makes capacity visible without turning JOSELYN into employee surveillance.

Useful measures include:

- hours saved by automation
- requests completed
- SLA compliance
- time-to-hire
- onboarding completion
- missing-document reduction
- expiration risks resolved
- repeated manual steps removed
- correction / rework rate
- automation coverage

The goal is to show the value of HR and protect specialist time from unnecessary administrative repetition.

## 6. Human decision boundary

JOSELYN may assist with extraction, organization, summarization, scheduling, reminders, document preparation, workflow routing and evidence gathering.

High-impact employment decisions remain human decisions. JOSELYN must not silently decide hiring, firing, promotion, compensation, discipline or other consequential employment outcomes. Where AI assists, evidence, uncertainty and approval boundaries must remain visible.

## 7. Automation discovery loop

Every repeated workflow should be challenged:

```text
Does this step need to exist?
Can trusted data derive it?
Can an adapter capture it automatically?
Can JOSELYN prefill it?
Can a deterministic rule handle it?
Does a human need to approve it?
How much time would automation return?
How do we prove the result is correct?
```

This keeps the platform focused on reducing work rather than digitizing inefficient work.

## 8. Next adapters

Priority order:

1. XLSX import with sheet selection and column mapping.
2. Export back to CSV/XLSX for organizations that still depend on spreadsheets.
3. Document/image intake with field proposals and human confirmation.
4. Voice dictation into structured HR requests and notes.
5. Folder/watch integration for recurring exports.
6. API/webhook connectors for source systems.
7. Mapping profiles per company so recurring file formats become zero-configuration after approval.

## Definition of done for an intake adapter

An adapter is not complete merely because it can read a file. It must prove:

- supported format/version is explicit;
- data is normalized into the common contract;
- provenance is preserved;
- unknown fields are retained;
- duplicates are detected;
- invalid or ambiguous rows are visible;
- imports can be dry-run before persistence;
- repeated imports are safe;
- tests cover representative input;
- sensitive mutations remain auditable.
