# Standalone AI Knowledge Copilot

A progressively developed AI knowledge assistant built with Python, FastAPI, Google Gemini, and modern software-engineering practices.

The project is developed incrementally. Each task extends the previous stage instead of replacing it.

## Current Progress

- Task 1 / Week 1: Python Engineering Foundations
- Task 2 / Week 2: Backend API Fundamentals
- Task 3 / Week 3: GCP and LLM Foundations

---

# Project Overview

The Standalone AI Knowledge Copilot is designed as a modular application that gradually evolves from a local Python program into an AI-powered knowledge system.

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
Response + Token Metadata
        ↓
JSON Run Records
```

Future stages will extend the application with embeddings, vector search, RAG, tools, workflows, and agentic AI concepts.

---

# Project Structure

```text
standalone-ai-knowledge-copilot/
│
├── artifacts/
│   └── llm_runs/
│
├── data/
│   └── sample_knowledge.json
│
├── docs/
│   └── gcp_llm_foundations.md
│
├── scripts/
│   ├── __init__.py
│   └── llm_demo.py
│
├── src/
│   ├── __init__.py
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
│   ├── test_api.py
│   └── test_llm_client.py
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
LLM_TEMPERATURE=0.2
LLM_MAX_OUTPUT_TOKENS=768
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
- clean separation of responsibilities

## Knowledge Data

The local knowledge base is stored in:

```text
data/sample_knowledge.json
```

This allows the application to work with structured local data without requiring an external database.

## Storage Layer

The storage functionality is implemented in:

```text
src/storage.py
```

The storage layer separates data-access logic from the rest of the application.

This makes it easier to replace the local JSON storage with another storage technology later.

## Configuration

Application configuration is centralized in:

```text
src/config.py
```

Configuration values can be loaded from environment variables instead of being hardcoded inside application logic.

## Logging

Logging configuration is separated into:

```text
src/logging_config.py
```

This provides a consistent logging strategy across the application.

## Task 1 Demo

Run:

```powershell
python main.py
```

The demonstration verifies that the local application and storage layer are working correctly.

A successful execution should finish without errors and demonstrate the basic Python application functionality.

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

## Run the API

Start the FastAPI server with:

```powershell
python -m uvicorn src.api:app --reload
```

The interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

The OpenAPI schema is available at:

```text
http://127.0.0.1:8000/openapi.json
```

## API Testing

API tests are implemented in:

```text
tests/test_api.py
```

Run the test suite with:

```powershell
python -m pytest -v
```

## Docker Support

Task 2 also introduces:

```text
Dockerfile
.dockerignore
```

This prepares the backend for containerized deployment in later cloud-related stages.

---

# Task 3 - GCP and LLM Foundations

Task 3 adds the first real Large Language Model integration to the Standalone AI Knowledge Copilot.

The application now communicates with Google Gemini while preserving the storage and backend layers created in Tasks 1 and 2.

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

# Gemini Integration

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

# LLM Error Handling

The LLM integration defines dedicated application-level exceptions for different failure scenarios.

Examples include:

```text
LLMError
LLMConfigurationError
LLMRequestError
LLMResponseError
```

This makes failures easier to understand and handle than exposing raw SDK exceptions directly to the application.

---

# Gemini Configuration

Gemini settings are loaded from environment variables.

Example:

```env
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.8-flash
LLM_TEMPERATURE=0.2
LLM_MAX_OUTPUT_TOKENS=768
```

The real API key is stored only in the local:

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

# First Real Gemini Call

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

A successful execution displays:

```text
Task 3 - First Gemini LLM Call

MODEL RESPONSE
...

TOKEN USAGE
...

Run record saved to: artifacts/llm_runs/...

Task 3 LLM demo completed successfully.
```

---

# Example Prompt

The demonstration uses a simple educational prompt:

```text
Explain in three concise bullet points what a context window is in a large language model.
```

The purpose is not to build a complex AI feature yet.

The goal of Task 3 is to prove that the project can successfully communicate with a real LLM and capture useful metadata about the request.

---

# Token Awareness

The application records several token measurements.

These include:

```text
Prompt tokens (pre-count)
Input tokens
Output tokens
Thinking tokens
Total tokens
```

This provides visibility into model usage rather than treating the LLM as a black box.

A real successful Task 3 execution can therefore show information such as:

```text
Prompt tokens (pre-count): 18
Input tokens (usage metadata): 18
Output tokens: ...
Thinking tokens: ...
Total tokens: ...
```

---

# Context Window

A context window represents the amount of information an LLM can process within a request.

It includes information such as:

- the user prompt
- conversation history
- provided context
- retrieved documents
- generated output

Understanding context-window limitations becomes especially important in later RAG stages where retrieved documents will be inserted into model prompts.

---

# Temperature

Temperature is an LLM generation parameter related to randomness and output variation.

The project keeps temperature as part of the application configuration:

```env
LLM_TEMPERATURE=0.2
```

For the currently selected Gemini model, the application can intentionally avoid sending this parameter when required for model compatibility.

The configuration is still retained because temperature is an important LLM concept and may be used by other models or later project stages.

---

# Cost Awareness

The application tracks token usage and supports optional cost estimation.

Current model prices are intentionally not hardcoded into the Python source code because provider pricing may change.

Optional prices can be configured using:

```env
GEMINI_INPUT_COST_PER_1M_USD=
GEMINI_OUTPUT_COST_PER_1M_USD=
```

If these values are not configured, the application still records token usage but reports:

```text
Estimated cost: not calculated
```

This avoids presenting stale or incorrect pricing information.

---

# LLM Run Records

Each successful LLM execution can be saved as a timestamped JSON record inside:

```text
artifacts/llm_runs/
```

The run record contains information such as:

- timestamp
- model
- prompt
- model response
- generation configuration
- token usage
- optional estimated cost

The API key is never stored inside the run record.

This provides basic traceability and observability for LLM interactions.

---

# Task 3 Testing Strategy

Automated Task 3 tests are implemented in:

```text
tests/test_llm_client.py
```

The tests do not need to make real Gemini API calls.

Instead, the LLM client supports dependency injection so fake clients and responses can be supplied during testing.

This allows functionality such as the following to be tested safely:

- configuration validation
- prompt handling
- response processing
- token metadata extraction
- cost calculations
- error handling
- run-record persistence

without consuming live Gemini quota.

Run all tests with:

```powershell
python -m pytest -v
```

---

# GCP and LLM Foundations Documentation

The theoretical material for Task 3 is documented in:

```text
docs/gcp_llm_foundations.md
```

Topics include:

## Google Cloud

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

## Large Language Models

- tokens
- tokenization
- context windows
- temperature
- hallucinations
- prompt design
- token usage
- cost awareness

This documentation supports the practical Gemini integration with the cloud and AI concepts required for Task 3.

---

# Running the Project

## Task 1 Demo

```powershell
python main.py
```

## Task 2 API

```powershell
python -m uvicorn src.api:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## Task 3 Gemini Demo

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

The repository only contains:

```text
.env.example
```

Before every commit, verify the repository state with:

```powershell
git status
```

The `.env` file should not appear in files staged for commit.

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
- observability of LLM usage
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
GCP and LLM Foundations
        ↓
Task 4
Reliable LLM APIs
        ↓
Task 5
Embeddings and Vector Search
        ↓
Task 6
Basic RAG
        ↓
Task 7
RAG Evaluation
        ↓
Task 8
LangChain Tools
        ↓
Task 9
LangGraph Workflow
        ↓
Task 10
Agentic AI and Cloud Architecture
```

Tasks 1 through 3 are currently implemented.

Each new task builds on the existing project rather than replacing previous work.