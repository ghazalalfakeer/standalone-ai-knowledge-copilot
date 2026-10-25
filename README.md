# Standalone AI Knowledge Copilot

A progressively developed AI knowledge assistant built with Python, FastAPI, Google Gemini, and modern software-engineering practices.

The project is developed incrementally. Each task extends the previous stage instead of replacing it.

## Current Progress

- Task 1: Python Engineering Foundations
- Task 2: Backend API Fundamentals
- Task 3: GCP and AI/LLM Foundations
- Task 4: Reliable LLM Application APIs

---

# Project Overview

The Standalone AI Knowledge Copilot is designed as a modular application that gradually evolves from a local Python program into a reliable AI-powered knowledge system.

The current architecture includes:

```text
Local Knowledge Data
        ↓
Python Storage Layer
        ↓
FastAPI Backend
        ↓
Gemini LLM Integration
        ↓
Reliable AI API Layer
        ↓
Structured Responses
        ↓
Validation + Resilience
        ↓
Usage Metadata
```

Future stages will extend the application with embeddings, vector search, retrieval-augmented generation, tools, controlled workflows, deployment, and agentic AI concepts.

---

# Project Structure

```text
standalone-ai-knowledge-copilot/
│
├── artifacts/
│   └── llm_runs/
│       └── README.md
│
├── data/
│   └── sample_knowledge.json
│
├── docs/
│   ├── gcp_llm_foundations.md
│   └── task4_reliable_llm_apis.md
│
├── scripts/
│   ├── __init__.py
│   └── llm_demo.py
│
├── src/
│   ├── __init__.py
│   ├── ai_models.py
│   ├── ai_prompts.py
│   ├── ai_service.py
│   ├── api.py
│   ├── config.py
│   ├── llm_client.py
│   ├── llm_records.py
│   ├── logging_config.py
│   ├── models.py
│   └── storage.py
│
├── tests/
│   ├── __init__.py
│   ├── test_ai_api.py
│   ├── test_ai_fallback.py
│   ├── test_ai_prompts.py
│   ├── test_ai_resilience.py
│   ├── test_ai_structured_completion.py
│   ├── test_api.py
│   ├── test_llm_client.py
│   └── test_structured_llm.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── main.py
├── README.md
└── requirements.txt
```

---

# Setup

## 1. Create a Virtual Environment

Python 3.12 is recommended.

```powershell
py -3.12 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## 2. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

---

## 3. Create Local Environment Configuration

Create a local `.env` file based on `.env.example`.

Example:

```env
APP_NAME=Standalone AI Knowledge Copilot
APP_ENV=development
LOG_LEVEL=INFO
DATA_FILE=data/sample_knowledge.json

GEMINI_API_KEY=YOUR_REAL_API_KEY
GEMINI_MODEL=gemini-3.8-flash
GEMINI_FALLBACK_MODEL=gemini-3.6-flash

LLM_TEMPERATURE=0.2
LLM_MAX_OUTPUT_TOKENS=768
LLM_STRUCTURED_MAX_OUTPUT_TOKENS=2048
LLM_THINKING_LEVEL=low

LLM_TIMEOUT_SECONDS=60
LLM_MAX_RETRIES=2
```

The real `.env` file is excluded from Git and must never be committed.

The repository contains only `.env.example` as a safe configuration template.

---

# Task 1 - Python Engineering Foundations

Task 1 establishes the core Python application structure.

The purpose of this stage is to build a clean and reusable foundation before introducing APIs or AI services.

## Objectives

Task 1 focuses on:

- Python project organization
- modular code
- JSON data persistence
- file handling
- reusable storage logic
- logging
- error handling
- type hints
- clean separation of responsibilities

---

## Knowledge Data

The local knowledge base is stored in:

```text
data/sample_knowledge.json
```

This allows the application to work with structured local data without requiring an external database.

---

## Storage Layer

The storage functionality is implemented in:

```text
src/storage.py
```

The storage layer separates data-access logic from the rest of the application.

This makes it easier to replace the local JSON storage with another storage technology later.

---

## Configuration

Application configuration is centralized in:

```text
src/config.py
```

Configuration values can be loaded from environment variables instead of being hardcoded inside application logic.

---

## Logging

Logging configuration is separated into:

```text
src/logging_config.py
```

This provides a consistent logging strategy across the application.

---

## Task 1 Demo

Run:

```powershell
python main.py
```

The demonstration verifies:

- valid JSON loading
- knowledge item creation
- updates
- deletion
- missing-file handling
- malformed JSON handling
- data validation

A successful execution finishes with:

```text
TASK 1 DEMO COMPLETED
All demonstrations finished.
```

---

# Task 2 - Backend API Fundamentals

Task 2 exposes the local knowledge functionality through a REST API using FastAPI.

This transforms the Task 1 Python application into a backend service.

## Objectives

Task 2 focuses on:

- FastAPI fundamentals
- REST API design
- request and response models
- validation with Pydantic
- API error handling
- automated API testing
- interactive API documentation
- basic containerization

---

## API Implementation

The backend API is implemented in:

```text
src/api.py
```

Data models are defined in:

```text
src/models.py
```

The API reuses the storage layer created in Task 1 instead of duplicating data-access logic.

---

## Main API Endpoints

### Health Check

```http
GET /health
```

Used to verify that the backend service is running.

### Knowledge Retrieval

```http
GET /knowledge
```

Returns the available knowledge records.

### Knowledge Search

```http
POST /knowledge/search
```

Accepts a search request and returns matching knowledge content.

---

## Run the API

Start the FastAPI server with:

```powershell
python -m uvicorn src.api:app --reload
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

OpenAPI schema:

```text
http://127.0.0.1:8000/openapi.json
```

---

## API Testing

API tests are implemented in:

```text
tests/test_api.py
```

Run the test suite with:

```powershell
python -m pytest -v
```

---

## Docker Support

Task 2 introduces:

```text
Dockerfile
.dockerignore
```

This prepares the application for containerized deployment in later cloud-related stages.

---

# Task 3 - GCP and AI/LLM Foundations

Task 3 introduces the first real Large Language Model integration into the Standalone AI Knowledge Copilot.

The application communicates with Google Gemini while preserving the storage and backend layers created in Tasks 1 and 2.

## Objectives

Task 3 focuses on:

- Google Cloud fundamentals
- IAM concepts
- service accounts
- Cloud Storage
- BigQuery
- Cloud Run
- Vertex AI and Gemini concepts
- LLM fundamentals
- tokens
- context windows
- temperature
- hallucinations
- prompt execution
- token usage tracking
- basic cost awareness
- secure API-key management
- LLM run traceability
- testable AI integrations

---

## Task 3 Architecture

```text
CLI Demo
   ↓
GeminiLLMClient
   ↓
Google Gemini API
   ↓
Model Response
   ↓
Usage Metadata
   ↓
LLMRunResult
   ↓
JSON Run Record
```

---

## Gemini Integration

The Gemini integration is implemented in:

```text
src/llm_client.py
```

The `GeminiLLMClient` provides a dedicated abstraction around the Google Gen AI SDK.

Its responsibilities include:

- prompt validation
- prompt token pre-counting
- Gemini API communication
- response validation
- usage metadata extraction
- application-specific error handling
- optional cost estimation
- dependency injection for testing

Keeping LLM-specific logic inside a dedicated client prevents AI-provider logic from being scattered throughout the application.

---

## LLM Error Handling

The LLM integration defines dedicated application-level exceptions for different failure scenarios.

Examples include:

```text
LLMError
LLMConfigurationError
LLMRequestError
LLMResponseError
```

Later tasks extend these exception types with more specific provider and reliability errors.

---

## Secure Gemini Configuration

Gemini settings are loaded from environment variables.

Example:

```env
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.8-flash
LLM_TEMPERATURE=0.2
LLM_MAX_OUTPUT_TOKENS=768
```

The real API key is stored only in:

```text
.env
```

The `.env` file is excluded from Git.

The repository contains:

```text
.env.example
```

as a safe configuration template without credentials.

---

## First Real Gemini Call

The Task 3 demonstration is implemented in:

```text
scripts/llm_demo.py
```

Run it with:

```powershell
python -m scripts.llm_demo
```

The demo performs the following flow:

```text
Load configuration
        ↓
Create Gemini client
        ↓
Validate prompt
        ↓
Count prompt tokens
        ↓
Send prompt to Gemini
        ↓
Receive model response
        ↓
Extract usage metadata
        ↓
Create LLM run result
        ↓
Save JSON run record
```

---

## Token Awareness

The application records several token measurements:

```text
Prompt tokens
Input tokens
Output tokens
Thinking tokens
Total tokens
```

This provides visibility into model usage rather than treating the LLM as a black box.

---

## Context Window

A context window represents the amount of information an LLM can process within a request.

It may include:

- the user prompt
- conversation history
- supplied context
- retrieved documents
- generated output

Understanding context-window limitations becomes increasingly important in later retrieval-based stages.

---

## Temperature

Temperature is an LLM generation parameter related to randomness and output variation.

The application keeps temperature as part of the configuration:

```env
LLM_TEMPERATURE=0.2
```

The client can choose whether to send this parameter depending on model compatibility.

---

## Cost Awareness

Token usage is tracked and optional cost estimation is supported.

Model prices are intentionally not hardcoded into the Python source because provider pricing can change.

Optional pricing values can be configured with environment variables.

If pricing values are not configured, token usage is still recorded while cost estimation remains disabled.

---

## LLM Run Records

Successful LLM executions can be stored as timestamped JSON records inside:

```text
artifacts/llm_runs/
```

Run records can contain:

- timestamp
- model
- prompt
- response
- generation configuration
- token usage
- optional estimated cost

The API key is never stored inside these records.

---

## Task 3 Testing Strategy

Task 3 tests are implemented in:

```text
tests/test_llm_client.py
```

The tests do not require real Gemini API calls.

Dependency injection allows fake clients and responses to be used during automated testing.

---

## GCP and LLM Foundations Documentation

The theoretical material for Task 3 is documented in:

```text
docs/gcp_llm_foundations.md
```

Topics include:

### Google Cloud

- resource hierarchy
- projects
- IAM
- roles and permissions
- service accounts
- Cloud Storage
- BigQuery
- Cloud Run
- Vertex AI
- Gemini

### Large Language Models

- tokens
- tokenization
- context windows
- temperature
- hallucinations
- prompt design
- token usage
- cost awareness

---

# Task 4 - Reliable LLM Application APIs

Task 4 transforms the basic Gemini integration from Task 3 into a more reliable, structured, and production-oriented application API layer.

Instead of using the LLM only through a command-line demo, the application now exposes dedicated FastAPI endpoints with structured outputs, schema validation, resilience mechanisms, usage metadata, and automated tests.

## Objectives

Task 4 focuses on:

- reliable LLM application APIs
- reusable prompt templates
- structured JSON output
- Pydantic request and response validation
- configurable summarization behavior
- information extraction
- timeout handling
- bounded retries
- controlled fallback-model behavior
- provider-specific error handling
- structured-output recovery
- token-usage visibility
- automated API and LLM tests

---

## Task 4 Architecture

```text
Client Request
      ↓
FastAPI Endpoint
      ↓
Pydantic Input Validation
      ↓
AIService
      ↓
Prompt Template
      ↓
GeminiLLMClient
      ↓
Primary Gemini Model
      ↓
Structured JSON Response
      ↓
Pydantic Output Validation
      ↓
Normalization
      ↓
Usage Metadata
      ↓
Reliable API Response
```

For selected temporary provider failures, the application can use a controlled fallback model:

```text
Primary Model
      ↓
Temporary Provider Failure
      ↓
Fallback Model
      ↓
Validated Structured Response
```

---

## AI API Endpoints

Task 4 introduces:

```text
POST /ai/summarize
POST /ai/extract
```

Both endpoints use structured LLM outputs instead of unrestricted free-text responses.

---

## Summarization API

Endpoint:

```http
POST /ai/summarize
```

Example request:

```json
{
  "text": "Google Cloud provides managed infrastructure and artificial intelligence services. Cloud Run executes containerized applications without requiring developers to manage servers.",
  "max_sentences": 2,
  "style": "technical",
  "focus": "Cloud Run"
}
```

The endpoint supports configurable behavior through:

```text
max_sentences
style
focus
```

Supported summary styles include:

```text
concise
executive
technical
```

The optional `focus` field allows a request to emphasize a particular topic.

Example response structure:

```json
{
  "summary": "Structured summary generated by the model.",
  "key_points": [
    "Key point one",
    "Key point two"
  ],
  "model": "gemini-3.8-flash",
  "usage": {
    "prompt_tokens_precount": 0,
    "input_tokens": 0,
    "output_tokens": 0,
    "thinking_tokens": 0,
    "total_tokens": 0,
    "estimated_cost_usd": null
  }
}
```

Actual usage values depend on each request.

---

## Structured Extraction API

Endpoint:

```http
POST /ai/extract
```

Example request:

```json
{
  "text": "Alice Müller from Example GmbH approved an invoice of 100 EUR on October 21, 2026 for the Cloud Run migration project."
}
```

The endpoint extracts structured information into categories such as:

```text
people
organizations
dates
amounts
keywords
```

Example response structure:

```json
{
  "people": [
    "Alice Müller"
  ],
  "organizations": [
    "Example GmbH"
  ],
  "dates": [
    "October 21, 2026"
  ],
  "amounts": [
    "100 EUR"
  ],
  "keywords": [
    "Cloud Run",
    "migration"
  ],
  "model": "gemini-3.8-flash",
  "usage": {
    "prompt_tokens_precount": 0,
    "input_tokens": 0,
    "output_tokens": 0,
    "thinking_tokens": 0,
    "total_tokens": 0,
    "estimated_cost_usd": null
  }
}
```

Extracted list values are normalized to reduce unnecessary duplicates and inconsistent whitespace.

---

## Prompt Templates

Task 4 separates prompt construction from API and service logic.

Prompt templates are implemented in:

```text
src/ai_prompts.py
```

This keeps prompt engineering:

- reusable
- testable
- independent from HTTP handling
- easier to maintain

The summarization prompt includes instructions for:

- requested summary style
- maximum sentence count
- optional topic focus
- grounding the result in supplied text
- structured output requirements

The extraction prompt defines the expected information categories and instructs the model to return empty lists when information is not present instead of inventing values.

---

## Structured Output

A major Task 4 improvement is structured LLM generation.

Instead of accepting arbitrary text, the application expects a predefined JSON structure.

```text
Gemini
   ↓
Structured JSON
   ↓
Pydantic Schema
   ↓
Validated Python Object
   ↓
API Response
```

If model output does not match the required schema, the application rejects it instead of silently returning malformed data.

---

## Input and Output Validation

Pydantic models validate both sides of the AI interaction.

### Request Validation

Invalid requests are rejected before reaching Gemini.

Examples include:

- text that is too short
- unsupported summary styles
- invalid field values

### Response Validation

Generated structured output is validated against the expected schema before it is returned to the API client.

This protects the rest of the application from malformed or unexpected LLM responses.

---

## Reliability and Error Handling

External LLM providers can temporarily fail, become overloaded, exceed quota limits, respond slowly, or return incomplete output.

Task 4 handles these scenarios explicitly.

```text
429 Too Many Requests
Provider quota or rate limit reached

502 Bad Gateway
Invalid or unusable upstream model response

503 Service Unavailable
AI provider temporarily unavailable

504 Gateway Timeout
AI provider failed to complete the request within the allowed time
```

This is more informative than returning a generic `500 Internal Server Error`.

---

## Timeout Handling

LLM requests use a configurable timeout:

```env
LLM_TIMEOUT_SECONDS=60
```

This prevents API requests from waiting indefinitely when the external provider becomes slow or unresponsive.

Both local network timeout conditions and provider-side deadline failures are handled as temporary upstream failures.

---

## Retry Strategy

Temporary failures may be retried automatically.

The retry count is intentionally bounded:

```env
LLM_MAX_RETRIES=2
```

Bounded retries improve reliability without allowing uncontrolled repeated requests.

---

## Controlled Fallback Model

Task 4 supports a primary model and an optional fallback model.

Example:

```env
GEMINI_MODEL=gemini-3.8-flash
GEMINI_FALLBACK_MODEL=gemini-3.6-flash
```

The fallback is used only for selected temporary failures such as:

- provider unavailability
- connection/read timeout
- provider-side deadline exceeded

The application does not automatically fan out every error to another model.

For example, provider quota or rate-limit errors are handled separately.

When the fallback model successfully handles a request, the actual model used is returned in the API response.

---

## Structured Output Completion Strategy

Structured JSON must be complete before it can be parsed and validated.

Task 4 therefore uses a dedicated output-token budget:

```env
LLM_STRUCTURED_MAX_OUTPUT_TOKENS=2048
```

For these focused structured tasks, the application uses:

```env
LLM_THINKING_LEVEL=low
```

This helps reserve more generation capacity for the final structured response.

If a structured response reaches the output limit before completion, the client can perform one bounded recovery attempt using a larger generation budget.

Recovery is intentionally limited to avoid uncontrolled repeated model calls.

---

## Token Usage Metadata

Successful AI responses include usage information.

Tracked values include:

```text
Prompt token pre-count
Input tokens
Output tokens
Thinking tokens
Total tokens
Optional estimated cost
```

This improves observability and makes LLM resource usage visible to the application.

---

## Task 4 Configuration

Relevant Task 4 configuration values include:

```env
GEMINI_MODEL=gemini-3.8-flash
GEMINI_FALLBACK_MODEL=gemini-3.6-flash

LLM_MAX_OUTPUT_TOKENS=768
LLM_STRUCTURED_MAX_OUTPUT_TOKENS=2048
LLM_THINKING_LEVEL=low

LLM_TIMEOUT_SECONDS=60
LLM_MAX_RETRIES=2
```

The real Gemini API key remains only in `.env` and is never committed to Git.

---

## Task 4 Testing Strategy

Task 4 includes automated tests for successful behavior and failure scenarios.

The suite covers areas such as:

```text
AI API response structure
Request validation
Unknown summary styles
Prompt-template behavior
Structured-output validation
Entity normalization
Provider 503 handling
Provider 429 handling
Network timeout handling
Provider 504 handling
Fallback after temporary failures
No fallback fan-out for rate limits
Structured-output completion recovery
OpenAPI reliability responses
Token-usage handling
```

Fake or mocked model clients are used where appropriate.

This avoids consuming live Gemini quota during normal automated testing and makes the test suite deterministic.

Run all tests with:

```powershell
python -m pytest -v
```

At the completion of Task 4:

```text
27 tests passed
```

---

## Live Validation

Both Task 4 AI endpoints were also tested against the real Gemini service.

Successful live requests were confirmed for:

```text
POST /ai/summarize → 200 OK
POST /ai/extract   → 200 OK
```

During development, real provider failure scenarios were observed, including:

- temporary provider unavailability
- request timeouts
- provider-side deadline exceeded
- quota exhaustion
- incomplete structured generation

These real scenarios helped validate and improve the reliability layer.

---

# Running the Project

## Task 1 Demo

```powershell
python main.py
```

## FastAPI Backend

```powershell
python -m uvicorn src.api:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Current endpoints include:

```text
GET  /health
GET  /knowledge
POST /knowledge/search

POST /ai/summarize
POST /ai/extract
```

## Task 3 Gemini CLI Demo

```powershell
python -m scripts.llm_demo
```

## Run All Automated Tests

```powershell
python -m pytest -v
```

---

# Security

Sensitive credentials must never be committed to Git.

The following file remains local:

```text
.env
```

The repository contains only:

```text
.env.example
```

Before every commit, verify the repository state with:

```powershell
git status
```

The `.env` file must not appear in staged files.

Generated local LLM run records are also excluded from normal commits.

---

# Engineering Principles

The project currently follows several software-engineering principles:

- modular architecture
- separation of concerns
- reusable components
- environment-based configuration
- structured logging
- dedicated data models
- explicit error handling
- automated testing
- dependency injection
- secure secret handling
- structured LLM outputs
- bounded retries
- timeout protection
- controlled fallback behavior
- provider-specific error handling
- usage observability
- incremental development

---

# Development Progress

```text
Task 1
Python Engineering Foundations
        ↓
Task 2
Backend API Fundamentals
        ↓
Task 3
GCP and AI/LLM Foundations
        ↓
Task 4
Reliable LLM Application APIs
        ↓
Future Tasks
Embeddings, Vector Search, RAG,
Agent Workflows, Deployment and Evaluation
```

Tasks 1 through 4 are currently implemented and tested.

Each new task builds on the existing project rather than replacing previous work.