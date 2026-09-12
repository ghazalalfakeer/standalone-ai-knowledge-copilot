# Standalone AI Knowledge Copilot

A modular Python project that progressively evolves into a standalone AI-powered Knowledge Copilot.

This repository currently contains:

- **Task 1 / Week 1:** Python Engineering Foundations
- **Task 2 / Week 2:** Backend API Fundamentals

## Task 2 Features

- FastAPI REST backend
- `GET /health` health-check endpoint
- `GET /knowledge` endpoint backed by the Task 1 `JsonStorage`
- `POST /knowledge/search` deterministic non-AI search endpoint
- Pydantic request and response models
- `.env` configuration via `pydantic-settings`
- Structured JSON application logging
- HTTP error handling
- Automated API tests with Pytest
- Basic Dockerfile and `.dockerignore`
- Swagger/OpenAPI documentation

## Project Structure

```text
standalone-ai-knowledge-copilot/
├── data/
│   └── sample_knowledge.json
├── src/
│   ├── __init__.py
│   ├── api.py
│   ├── config.py
│   ├── logging_config.py
│   ├── models.py
│   └── storage.py
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── main.py
├── README.md
└── requirements.txt
```

## Local Setup

Python 3.10+ is required. Python 3.12 is recommended.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

### Run Task 1 CLI

```powershell
python main.py
```

### Run Task 2 API

```powershell
python -m uvicorn src.api:app --reload
```

Open:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/knowledge`

Example `POST /knowledge/search` request:

```json
{
  "query": "json",
  "tag": "python"
}
```

## Tests

```powershell
python -m pytest -v
```

The suite verifies the health endpoint, knowledge endpoint, search endpoint, and Pydantic request validation.

## Docker

Build:

```bash
docker build -t standalone-ai-knowledge-copilot:task2 .
```

Run:

```bash
docker run --rm -p 8000:8000 --env-file .env standalone-ai-knowledge-copilot:task2
```

## Git: Add Task 2 on Top of Task 1

Task 1 remains in Git history. Task 2 is a new commit on top of it.

Recommended branch workflow:

```bash
git checkout main
git pull origin main
git checkout -b task-2-backend-api
```

After copying the Task 2 files and testing:

```bash
git status
git add .
git commit -m "Complete Task 2 backend API fundamentals"
git push -u origin task-2-backend-api
```

Then create a Pull Request on GitHub and merge `task-2-backend-api` into `main`.

If you intentionally work directly on `main` instead:

```bash
git checkout main
git pull origin main
git add .
git commit -m "Complete Task 2 backend API fundamentals"
git push origin main
```

The existing Task 1 commit is not replaced; the repository history now contains Task 1 followed by Task 2.
