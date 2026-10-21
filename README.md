# Standalone AI Knowledge Copilot

A modular Python project that progressively evolves into a standalone AI-powered Knowledge Copilot.

The project is developed incrementally, with each task building on the previous one.

Current completed stages:

- Task 1 / Week 1: Python Engineering Foundations
- Task 2 / Week 2: Backend API Fundamentals

---

# Task 1 - Python Engineering Foundations

Task 1 established the basic software-engineering foundation of the project.

## Main Objectives

The first task focused on:

- Modular Python project structure
- Virtual environment setup
- Dependency management
- JSON file storage
- Data validation
- Error handling
- Custom exceptions
- Type hints
- Safe file writing
- Git/GitHub-ready project structure

## Project Structure Introduced in Task 1

```text
standalone-ai-knowledge-copilot/
│
├── data/
│   └── sample_knowledge.json
│
├── src/
│   ├── __init__.py
│   └── storage.py
│
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```

## JSON Storage Layer

Task 1 introduced:

```text
src/storage.py
```

This module provides a reusable JSON storage layer.

It supports:

```text
Read JSON
Write JSON
Update root-level data
Add knowledge items
Update knowledge items
Delete knowledge items
Validate data
Handle storage errors
```

The main storage class is:

```python
JsonStorage
```

Example:

```python
from src.storage import (
    JsonStorage,
    validate_knowledge_data,
)

storage = JsonStorage(
    "data/sample_knowledge.json",
    validator=validate_knowledge_data,
)

data = storage.read()
```

## Data Validation

The project validates the knowledge-base structure before accepting data.

Each knowledge item requires:

```text
id
title
content
tags
```

The optional field is:

```text
source
```

The validator checks for invalid or empty fields and also prevents duplicate IDs.

## Custom Exceptions

Task 1 introduced custom exceptions:

```python
StorageError
StorageReadError
StorageWriteError
StorageValidationError
StorageItemNotFoundError
```

This allows the application to distinguish between different failure scenarios instead of using one generic exception.

## Atomic JSON Writing

The JSON storage layer uses an atomic-write strategy:

```text
Create temporary file
        ↓
Write new JSON
        ↓
Writing succeeds
        ↓
Replace destination file
```

This reduces the risk of corrupting the original JSON file if a write operation fails.

## Task 1 Demo

Run:

```bash
python main.py
```

The demo tests:

```text
Valid JSON reading
Add item
Update item
Delete item
Missing file handling
Malformed JSON handling
Validation error handling
```

---

# Task 2 - Backend API Fundamentals

Task 2 builds a REST backend on top of the storage layer created in Task 1.

The existing `JsonStorage` module is reused instead of rewriting the storage logic.

## Main Technologies

Task 2 introduces:

```text
FastAPI
Pydantic
pydantic-settings
Uvicorn
Pytest
HTTPX
Docker
Structured Logging
```

## Updated Architecture

```text
HTTP Client
     ↓
FastAPI
     ↓
API Layer
     ↓
JsonStorage
     ↓
sample_knowledge.json
```

## API Endpoints

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "ok",
  "service": "Standalone AI Knowledge Copilot",
  "environment": "development"
}
```

### Get Knowledge Base

```http
GET /knowledge
```

This endpoint retrieves knowledge data using the storage layer implemented in Task 1.

### Search Knowledge

```http
POST /knowledge/search
```

Example request:

```json
{
  "query": "json",
  "tag": "python"
}
```

This endpoint performs deterministic non-AI search over:

```text
ID
Title
Content
Tags
```

Artificial intelligence is intentionally not used yet at this stage.

## Pydantic Models

Task 2 uses Pydantic to define request and response schemas.

Examples include:

```text
HealthResponse
KnowledgeItem
KnowledgeResponse
KnowledgeSearchRequest
KnowledgeSearchResponse
```

Pydantic provides automatic validation and integrates with FastAPI's OpenAPI documentation.

## Environment Configuration

Application configuration is stored using environment variables.

Example:

```text
APP_NAME=Standalone AI Knowledge Copilot
APP_ENV=development
LOG_LEVEL=INFO
DATA_FILE=data/sample_knowledge.json
```

The real `.env` file is excluded from Git.

A safe template is provided:

```text
.env.example
```

## Structured Logging

Task 2 replaces application-level `print()` debugging with structured logging.

Example events include:

```text
Health check
Knowledge loaded
Knowledge search
Storage failure
```

## Automated Tests

Run:

```bash
python -m pytest -v
```

The test suite verifies:

```text
GET /health
GET /knowledge
POST /knowledge/search
Pydantic validation
```

## Running the FastAPI Backend

Activate the virtual environment and install dependencies:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the API:

```powershell
python -m uvicorn src.api:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Other endpoints:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/knowledge
```

---

# Docker

Build the Docker image:

```bash
docker build -t standalone-ai-knowledge-copilot:task2 .
```

Run the container:

```bash
docker run --rm -p 8000:8000 --env-file .env standalone-ai-knowledge-copilot:task2
```

---

# Current Project Structure

```text
standalone-ai-knowledge-copilot/
│
├── data/
│   └── sample_knowledge.json
│
├── src/
│   ├── __init__.py
│   ├── api.py
│   ├── config.py
│   ├── logging_config.py
│   ├── models.py
│   └── storage.py
│
├── tests/
│   ├── __init__.py
│   └── test_api.py
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
Future AI / RAG / Agentic stages
```

Each task builds on the previous stage instead of replacing it.