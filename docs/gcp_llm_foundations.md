# Task 3 Notes: GCP + AI/LLM Foundations

These notes cover the concepts required by Week 3 of the training plan. The
project does **not** provision paid Google Cloud resources automatically.
A personal/sandbox project can be used for exploration.

## 1. Google Cloud Resource Hierarchy

A common Google Cloud hierarchy is:

```text
Organization
    ↓
Folders (optional)
    ↓
Projects
    ↓
Service Resources
```

- **Organization**: top-level administrative boundary for a company/domain.
- **Folder**: optional grouping layer for departments, environments, or teams.
- **Project**: the main boundary used to enable services, apply IAM, track
  quotas, and associate usage with billing.
- **Resources**: service-specific objects such as Cloud Storage buckets,
  BigQuery datasets, and Cloud Run services.

An important idea is **inheritance**: IAM policies applied at higher container
levels can affect descendant resources.

Official reference:
https://cloud.google.com/resource-manager/docs/cloud-platform-resource-hierarchy

## 2. IAM and Service Accounts

IAM answers three basic questions:

```text
Who?       → principal
Can do what? → role / permissions
On which resource? → project, bucket, service, etc.
```

Use the **principle of least privilege**: grant only the permissions required
for a task.

A **service account** is an identity normally used by an application or
compute workload rather than a human user. In later deployment stages, a
Cloud Run service could execute as a service account and receive only the
permissions it needs.

Avoid committing service-account keys or API keys to Git. Prefer managed or
short-lived credentials when a Google Cloud workload supports them.

Official references:
https://cloud.google.com/iam/docs/overview
https://cloud.google.com/iam/docs/service-account-overview

## 3. Cloud Storage

Cloud Storage is managed **object storage**. Data is stored as objects inside
buckets.

Potential future use in this Knowledge Copilot:

```text
PDF / Markdown / Text documents
            ↓
      Cloud Storage bucket
            ↓
      ingestion pipeline
            ↓
     chunking / embeddings
```

Task 3 does not need to create a bucket; understanding the concept is enough.

Official reference:
https://cloud.google.com/storage/docs/introduction

## 4. BigQuery

BigQuery is Google's fully managed analytics/data platform. It is optimized
for analytical workloads and can be queried with SQL.

Possible future uses for this training project include:

- evaluation results
- aggregated request metrics
- synthetic usage/cost reports
- analytics over retrieval or model-call logs

Task 3 does not require a BigQuery dataset or table.

Official reference:
https://cloud.google.com/bigquery/docs/introduction

## 5. Cloud Run

Cloud Run is a fully managed platform for running applications and containers.
The Dockerized FastAPI service from Task 2 is a natural future candidate for
Cloud Run deployment.

```text
GitHub source
    ↓
Docker / build
    ↓
Cloud Run service
    ↓
HTTPS FastAPI backend
```

Actual cloud deployment is intentionally deferred to a later task.

Official reference:
https://cloud.google.com/run/docs/overview/what-is-cloud-run

## 6. Vertex AI and Gemini

**Gemini** refers to Google's generative AI model family. A model can receive a
prompt and generate text or other supported outputs.

**Vertex AI** is Google Cloud's managed AI platform. It provides enterprise
Google Cloud integration for building and operating AI applications.

For the Week 3 first-call exercise, this repository uses the **Gemini Developer
API** through the official Google Gen AI Python SDK. This keeps the first model
call small while still associating the API key with a Google Cloud project.
Later stages can move to a managed cloud deployment when required.

Official references:
https://ai.google.dev/gemini-api/docs/get-started
https://cloud.google.com/vertex-ai/generative-ai/docs/overview

## 7. Tokens

LLMs do not process text as human words directly. Input is broken into units
called **tokens**.

Token counts matter because they affect:

- how much text fits into the model request
- latency
- usage limits
- price on paid tiers

Task 3 calls the SDK's token-count operation before generation and also records
the usage metadata returned after generation.

Official reference:
https://ai.google.dev/gemini-api/docs/tokens

## 8. Context Window

The **context window** is the amount of tokenized information the model can
consider in one interaction/context. The exact limit depends on the selected
model.

A large context window does not remove the need for good retrieval design.
Later RAG tasks will select only relevant document chunks rather than blindly
sending all available documents to the model.

## 9. Temperature

**Temperature** controls sampling variability.

Conceptually:

- lower temperature → more deterministic/focused responses
- higher temperature → more varied/creative responses

Task 3 uses a conservative default of `0.2` because this project is intended
to become a knowledge assistant rather than a creative-writing system.

Temperature does not guarantee factual correctness.

## 10. Hallucinations

A **hallucination** is generated content that sounds plausible but is not
supported by reliable evidence or is incorrect.

Important mitigation ideas for later weeks include:

- retrieval from known documents
- source references
- structured validation
- unsupported-answer fallbacks
- evaluation questions

Task 3 intentionally demonstrates only a simple model call. It does not yet
claim that the generated answer is grounded in the local Knowledge Base.

## 11. Token and Cost Awareness in This Project

Each successful Task 3 run records:

```text
model
prompt
response
prompt token pre-count
input tokens
output tokens
thinking tokens (when exposed)
total tokens
temperature
optional estimated cost
```

The source code **does not hardcode pricing**, because pricing depends on model,
tier, and date. Optional environment variables can be supplied after checking
the current official pricing page:

```text
GEMINI_INPUT_COST_PER_1M_USD
GEMINI_OUTPUT_COST_PER_1M_USD
```

Current pricing should always be verified here before calculating an estimate:
https://ai.google.dev/gemini-api/docs/pricing

The calculation is only an educational estimate, not a billing statement.

## 12. Task 3 Architecture

```text
Local .env
(GEMINI_API_KEY)
      ↓
Settings / config.py
      ↓
GeminiLLMClient
      ↓
Google Gen AI SDK
      ↓
Gemini API
      ↓
LLMRunResult
      ↓
artifacts/llm_runs/*.json
```

Tasks 1 and 2 remain intact:

```text
Task 1: JSON storage foundation
Task 2: FastAPI backend
Task 3: GCP/LLM foundations + first model call
```

## Current Gemini 3.8 compatibility note
The training plan includes temperature as an LLM concept. Gemini 3.8 Flash deprecates sampling controls such as `temperature`, so the client keeps the setting for educational/backward-compatible models but intentionally omits it from requests whose model ID starts with `gemini-3.8`.
