# Task 4 — Reliable LLM Application APIs

## Goal
Task 4 turns the raw Gemini integration from Task 3 into application-facing APIs that are predictable, validated, testable, and easier to operate.

## Endpoints

### `POST /ai/summarize`
Returns a schema-validated summary, key points, model name, and token-usage metadata.

The request supports three explicit styles:
- `concise`
- `executive`
- `technical`

An optional `focus` field can guide attention without allowing unsupported facts.

### `POST /ai/extract`
Extracts explicitly stated:
- people
- organizations
- dates
- monetary amounts
- keywords

Duplicate/blank values are normalized deterministically after schema validation.

## Reliability features
- Pydantic validation on requests and model outputs.
- Gemini structured JSON output through `response_schema`.
- Centralized, testable prompt templates.
- Grounding instruction: do not invent facts not present in the supplied text.
- Bounded SDK retries for transient provider failures.
- Configurable request timeout.
- Application-specific LLM exceptions mapped to predictable HTTP 502/503 responses.
- Token usage returned with successful API responses.
- Mocked tests so automated tests do not consume Gemini quota.

## Why this is stronger than raw prompting
A raw LLM call returns arbitrary text and exposes provider behavior directly to the application. Task 4 adds explicit contracts around both input and output, normalizes structured values, and turns provider failures into stable API behavior.

## Run

```powershell
python -m uvicorn src.api:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Example summary request

```json
{
  "text": "Google Cloud provides managed infrastructure and AI services. Cloud Run executes containerized workloads without requiring users to manage servers.",
  "max_sentences": 2,
  "style": "technical",
  "focus": "Cloud Run"
}
```

## Example extraction request

```json
{
  "text": "Alice from Example GmbH approved an invoice of 100 EUR on October 21, 2026."
}
```
